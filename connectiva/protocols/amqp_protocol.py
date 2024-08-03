# connectiva/protocols/amqp_protocol.py

import pika
import json
import logging
from typing import Dict, Any
from connectiva import CommunicationMethod, Message

class AMQPProtocol(CommunicationMethod):
    """
    AMQP communication class (e.g., RabbitMQ).
    """

    def __init__(self, **kwargs):
        self.endpoint = kwargs.get("endpoint")
        self.queue_name = kwargs.get("queue_name")
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def connect(self):
        self.logger.info("Connecting to AMQP broker at %s...", self.endpoint)
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.endpoint))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name)
            self.logger.info("Connected to AMQP broker!")
        except Exception as e:
            self.logger.error("Failed to connect to AMQP broker: %s", e)
            raise

    def send(self, message: Message) -> Dict[str, Any]:
        self.logger.info("Sending message to queue '%s'...", self.queue_name)
        try:
            self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(message.__dict__))
            self.logger.info("Message sent successfully!")
            return {"status": "sent"}
        except Exception as e:
            self.logger.error("Failed to send message: %s", e)
            return {"error": str(e)}

    def receive(self) -> Message:
        self.logger.info("Receiving message from queue '%s'...", self.queue_name)
        try:
            method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
            if method_frame:
                self.channel.basic_ack(method_frame.delivery_tag)
                self.logger.info("Message received successfully!")
                return Message(action="receive", data=json.loads(body))
            else:
                self.logger.warning("No message received.")
                return Message(action="error", data={}, metadata={"error": "No message found"})
        except Exception as e:
            self.logger.error("Failed to receive message: %s", e)
            return Message(action="error", data={}, metadata={"error": str(e)})

    def disconnect(self):
        self.logger.info("Disconnecting from AMQP broker...")
        if self.connection:
            self.connection.close()
            self.logger.info("Disconnected from AMQP broker.")
