# connectiva/protocols/amqp_protocol.py

import pika
import json
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

    def connect(self):
        print(f"Connecting to AMQP broker at {self.endpoint}...")
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.endpoint))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name)
            print("Connected to AMQP broker!")
        except Exception as e:
            print(f"Failed to connect to AMQP broker: {e}")

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
        try:
            method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
            if method_frame:
                self.channel.basic_ack(method_frame.delivery_tag)
                print("Message received successfully!")
                return Message(action="receive", data=json.loads(body))
            else:
                print("No message received.")
                return Message(action="error", data={}, metadata={"error": "No message found"})
        except Exception as e:
            print(f"Failed to receive message: {e}")
            return Message(action="error", data={}, metadata={"error": str(e)})

    def disconnect(self):
        print("Disconnecting from AMQP broker...")
        if self.connection:
            self.connection.close()
            print("Disconnected from AMQP broker.")
