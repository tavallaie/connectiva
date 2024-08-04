from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from typing import Dict, Any
from connectiva import CommunicationMethod, Message
import json
import logging
import re

class KafkaProtocol(CommunicationMethod):
    """
    Kafka communication class for producing and consuming messages from Kafka topics.
    """

    def __init__(self, **kwargs):
        # Set up logger first
        self.logger = logging.getLogger(self.__class__.__name__)

        # Extract configuration from kwargs
        self.endpoint = kwargs.get("endpoint")
        self.topic = kwargs.get("topic")
        self.group_id = kwargs.get("group_id")
        self.producer = None
        self.consumer = None

        # Parse the endpoint to get broker list
        self.broker_list = self._parse_endpoint(self.endpoint)

    def _parse_endpoint(self, endpoint: str) -> list:
        """
        Parse the Kafka endpoint into a list of brokers.
        :param endpoint: The endpoint URL in the form 'kafka://host1:port1,host2:port2'
        :return: List of broker addresses ['host1:port1', 'host2:port2']
        """
        if not endpoint.startswith("kafka://"):
            raise ValueError("Invalid Kafka endpoint. Must start with 'kafka://'")
        
        # Strip the protocol prefix and split by comma to get individual brokers
        broker_string = endpoint[len("kafka://"):]
        brokers = re.split(r',\s*', broker_string)
        self.logger.debug(f"Parsed brokers: {brokers}")
        return brokers

    def connect(self):
        self.logger.info(f"Connecting to Kafka brokers at {self.broker_list}...")
        try:
            # Initialize Kafka producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.broker_list,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            self.logger.info("Kafka producer connected.")

            # Initialize Kafka consumer
            if self.group_id:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.broker_list,
                    group_id=self.group_id,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                self.logger.info("Kafka consumer connected.")
            else:
                self.logger.info("No consumer group ID provided; skipping consumer initialization.")

        except KafkaError as e:
            self.logger.error(f"Failed to connect to Kafka: {e}")
            raise

    def send(self, message: Message) -> Dict[str, Any]:
        self.logger.info(f"Sending message to Kafka topic '{self.topic}'...")
        try:
            future = self.producer.send(self.topic, value=message.__dict__)
            result = future.get(timeout=10)  # Block until a single message is sent
            self.logger.info("Message sent successfully!")
            return {"status": "sent", "offset": result.offset}
        except KafkaError as e:
            self.logger.error(f"Failed to send message: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        self.logger.info(f"Receiving message from Kafka topic '{self.topic}'...")
        try:
            for message in self.consumer:
                self.logger.info("Message received successfully!")
                return Message(action="receive", data=message.value)  # Return the first message received
        except KafkaError as e:
            self.logger.error(f"Failed to receive message: {e}")
            return Message(action="error", data={}, metadata={"error": str(e)})

    def disconnect(self):
        self.logger.info("Disconnecting from Kafka...")
        try:
            if self.producer:
                self.producer.close()
                self.logger.info("Kafka producer disconnected.")
            if self.consumer:
                self.consumer.close()
                self.logger.info("Kafka consumer disconnected.")
        except Exception as e:
            self.logger.error(f"Failed to disconnect Kafka: {e}")
