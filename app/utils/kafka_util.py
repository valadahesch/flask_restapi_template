import json
from confluent_kafka import Producer
from app.config import  KafkaConfig


class KafkaProducer:

    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': KafkaConfig['host'],
            'socket.timeout.ms': 10000,
            })

    def produce_message(self, topic: str, message: dict) -> bool:
        self.producer.produce(topic, value=json.dumps(message))
        self.producer.flush()
        return True
    