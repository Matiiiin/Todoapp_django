import pika
import time
from threading import Lock

class RabbitMQConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host="localhost", username="guest", password="guest", retries=5, delay=5):
        if not hasattr(self, "connection"):
            self._connect_with_retries(host, username, password, retries, delay)

    def _connect_with_retries(self, host, username, password, retries, delay):
        credentials = pika.PlainCredentials(username, password)
        for attempt in range(retries):
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=host, credentials=credentials)
                )
                self.channel = self.connection.channel()
                print("Connected to RabbitMQ")
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to connect to RabbitMQ after {retries} attempts")
