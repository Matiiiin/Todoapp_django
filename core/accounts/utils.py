import pika
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

    def __init__(self, host='localhost', username='guest', password='guest'):
        if not hasattr(self, 'connection'):
            credentials = pika.PlainCredentials(username, password)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, credentials=credentials)
            )
            self.channel = self.connection.channel()

