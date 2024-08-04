from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError
from kafka.structs import TopicPartition
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
        self.partitions = kwargs.get("partitions", 1)
        self.replication_factor = kwargs.get("replication_factor", 1)
        self.producer = None
        self.consumer = None
        self.admin_client = None

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

    def create_topic(self):
        """
        Create Kafka topic if it does not exist.
        """
        try:
            self.admin_client = KafkaAdminClient(bootstrap_servers=self.broker_list)
            topic_list = self.admin_client.list_topics()
            if self.topic not in topic_list:
                self.logger.info(f"Creating topic {self.topic}...")
                new_topic = NewTopic(
                    name=self.topic,
                    num_partitions=self.partitions,
                    replication_factor=self.replication_factor
                )
                self.admin_client.create_topics([new_topic])
                self.logger.info(f"Topic {self.topic} created successfully!")
            else:
                self.logger.info(f"Topic {self.topic} already exists.")
        except TopicAlreadyExistsError:
            self.logger.info(f"Topic {self.topic} already exists.")
        except KafkaError as e:
            self.logger.error(f"Failed to create topic: {e}")
            raise
        finally:
            if self.admin_client:
                self.admin_client.close()

    def connect(self):
        self.logger.info(f"Connecting to Kafka brokers at {self.broker_list}...")
        try:
            # Create the topic if it doesn't exist
            self.create_topic()

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
                    auto_offset_reset='earliest',  # Start from the earliest message
                    enable_auto_commit=True,  # Automatically commit offsets
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                self.logger.info("Kafka consumer connected.")
                self.consumer.subscribe([self.topic])  # Subscribe to the topic
            else:
                self.logger.info("No consumer group ID provided; skipping consumer initialization.")

        except KafkaError as e:
            self.logger.error(f"Failed to connect to Kafka: {e}")
            raise

    def send(self, message: Message) -> Dict[str, Any]:
        self.logger.info(f"Sending message to Kafka topic '{self.topic}'...")
        try:
            future = self.producer.send(self.topic, value=message.__dict__)  # Send the entire message
            result = future.get(timeout=10)  # Block until a single message is sent
            self.logger.info(f"Message sent successfully! Offset: {result.offset}")
            return {"status": "sent", "offset": result.offset}
        except KafkaError as e:
            self.logger.error(f"Failed to send message: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        self.logger.info(f"Receiving message from Kafka topic '{self.topic}'...")
        try:
            for message in self.consumer:
                self.logger.info(f"Message received successfully! Message: {message.value}")
                return Message(action="receive", data=message.value)  # Return the entire message
        except StopIteration:
            self.logger.info("No message received.")
            return Message(action="error", data={}, metadata={"error": "No message found"})
        except KafkaError as e:
            self.logger.error(f"Failed to receive message: {e}")
            return Message(action="error", data={}, metadata={"error": str(e)})

    def seek_to_end(self):
        """Move the consumer to the end of the log for the current topic."""
        if self.consumer:
            try:
                partitions = self.consumer.partitions_for_topic(self.topic)
                if not partitions:
                    self.logger.error(f"No partitions found for topic {self.topic}.")
                    return

                topic_partitions = [TopicPartition(self.topic, p) for p in partitions]
                self.consumer.assign(topic_partitions)  # Ensure partitions are assigned
                self.consumer.seek_to_end()
                self.logger.info("Moved consumer to the end of the log.")
            except Exception as e:
                self.logger.error(f"Failed to seek to end: {e}")

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
