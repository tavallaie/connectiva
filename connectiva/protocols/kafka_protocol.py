from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from typing import Dict, Any
from ..interfaces import CommunicationMethod
from ..message import Message
import json

class KafkaProtocol(CommunicationMethod):
    """
    Kafka communication class for producing and consuming messages from Kafka topics.
    """

    def __init__(self, **kwargs):
        self.broker_list = kwargs.get("broker_list").split(',')
        self.topic = kwargs.get("topic")
        self.group_id = kwargs.get("group_id")
        self.producer = None
        self.consumer = None

    def connect(self):
        print(f"Connecting to Kafka brokers at {self.broker_list}...")
        try:
            # Initialize Kafka producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.broker_list,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Kafka producer connected.")

            # Initialize Kafka consumer
            if self.group_id:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.broker_list,
                    group_id=self.group_id,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                print("Kafka consumer connected.")
            else:
                print("No consumer group ID provided; skipping consumer initialization.")

        except KafkaError as e:
            print(f"Failed to connect to Kafka: {e}")

    def send(self, message: Message) -> Dict[str, Any]:
        print(f"Sending message to Kafka topic '{self.topic}'...")
        try:
            future = self.producer.send(self.topic, value=message.__dict__)
            result = future.get(timeout=10)  # Block until a single message is sent
            print("Message sent successfully!")
            return {"status": "sent", "offset": result.offset}
        except KafkaError as e:
            print(f"Failed to send message: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        print(f"Receiving message from Kafka topic '{self.topic}'...")
        try:
            for message in self.consumer:
                print("Message received successfully!")
                return Message(action="receive", data=message.value)  # Return the first message received
        except KafkaError as e:
            print(f"Failed to receive message: {e}")
            return Message(action="error", data={}, metadata={"error": str(e)})

    def disconnect(self):
        print("Disconnecting from Kafka...")
        if self.producer:
            self.producer.close()
            print("Kafka producer disconnected.")
        if self.consumer:
            self.consumer.close()
            print("Kafka consumer disconnected.")
