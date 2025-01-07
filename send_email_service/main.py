import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Lock
import pika
import json

# smtp4dev configuration
SMTP_SERVER = os.getenv("EMAIL_HOST", "smtp4dev")
SMTP_PORT = int(os.getenv("EMAIL_PORT", 25))  # smtp4dev typically uses port 25
EMAIL_ADDRESS = os.getenv("EMAIL_HOST_USER", "")  # Not needed for smtp4dev
EMAIL_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")  # Not needed for smtp4dev


class RabbitMQConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host="localhost", username="guest", password="guest"):
        if not hasattr(self, "connection"):
            try:
                credentials = pika.PlainCredentials(username, password)
                parameters = pika.ConnectionParameters(
                    host=host,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                print("Successfully connected to RabbitMQ", file=sys.stderr)
            except Exception as e:
                print(f"Failed to connect to RabbitMQ: {e}", file=sys.stderr)
                raise


def send_email(ch, method, properties, body):
    try:
        if isinstance(body, bytes):
            body = body.decode("utf-8")

        try:
            email_data = json.loads(body)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON body: {e}", file=sys.stderr)
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return

        recipients = email_data.get("recipients", [])
        if not isinstance(recipients, list):
            print("Recipients must be a list", file=sys.stderr)
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return

        if (
            not recipients
            or not email_data.get("sender")
            or not email_data.get("email_body")
        ):
            print("Missing required fields", file=sys.stderr)
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return

        message = MIMEMultipart("alternative")
        message["From"] = email_data["sender"]
        message["To"] = ", ".join(recipients)
        message["Subject"] = email_data.get("subject", "Todoapp admin email")

        message.attach(MIMEText(email_data["email_body"], "html"))

        with smtplib.SMTP(host=SMTP_SERVER, port=SMTP_PORT) as server:
            server.send_message(
                message, from_addr=email_data["sender"], to_addrs=recipients
            )
            print("Email sent successfully!", file=sys.stderr)

            ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error sending email: {e}", file=sys.stderr)
        ch.basic_nack(delivery_tag=method.delivery_tag)


def main():
    try:
        connection = RabbitMQConnection(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            username=os.getenv("RABBITMQ_USER", "guest"),
            password=os.getenv("RABBITMQ_PASS", "guest"),
        )

        connection.channel.exchange_declare(
            exchange="email", exchange_type="direct", durable=True
        )

        connection.channel.queue_declare(queue="send_email", durable=True)

        connection.channel.queue_bind(
            exchange="email", queue="send_email", routing_key="send_email"
        )

        connection.channel.basic_qos(prefetch_count=1)

        connection.channel.basic_consume(
            queue="send_email", on_message_callback=send_email
        )

        print("Started consuming messages...", file=sys.stderr)
        connection.channel.start_consuming()

    except KeyboardInterrupt:
        print("Shutting down...", file=sys.stderr)
        try:
            connection.channel.stop_consuming()
            connection.connection.close()
        except:
            pass
    except Exception as e:
        print(f"Error in main: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
