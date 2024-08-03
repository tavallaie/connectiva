# connectiva/protocols/broker_protocol.py

import pika
import json
from typing import Dict, Any
from ..interfaces import CommunicationMethod
from ..message import Message

class BrokerProtocol(CommunicationMethod):
    """
    Message broker communication class (e.g., RabbitMQ).
    """

    def __init__(self, **kwargs):
        self.broker_url = kwargs.get("broker_list")
        self.queue_name = kwargs.get("queue_name")
        self.connection = None
        self.channel = None

    def connect(self):
        print(f"Connecting to message broker at {self.broker_url}...")
        self.connection = pika.BlockingConnection(pika.URLParameters(self.broker_url))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        print("Connected to message broker!")

    def send(self, message: Message) -> Dict[str, Any]:
        print(f"Sending message to queue '{self.queue_name}'...")
        try:
            self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(message.__dict__))
            print("Message sent successfully!")
            return {"status": "sent"}
        except Exception as e:
            print(f"Failed to send message: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        print(f"Receiving message from queue '{self.queue_name}'...")
        method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
        if method_frame:
            self.channel.basic_ack(method_frame.delivery_tag)
            print("Message received successfully!")
            return Message(action="receive", data=json.loads(body))
        else:
            print("No message received.")
            return Message(action="error", data={}, metadata={"error": "No message found"})

    def disconnect(self):
        print("Disconnecting from message broker...")
        if self.connection:
            self.connection.close()
