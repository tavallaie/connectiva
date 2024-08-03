# connectiva/protocols/rest_protocol.py

import requests
from typing import Dict, Any
from connectiva import Message, CommunicationMethod

class RestProtocol(CommunicationMethod):
    """
    REST API communication class.
    """

    def __init__(self, **kwargs):
        self.base_url = kwargs.get("endpoint")

    def connect(self):
        print(f"Connecting to REST API at {self.base_url}...")

    def send(self, message: Message) -> Dict[str, Any]:
        print(f"Sending message to {self.base_url}/endpoint...")
        try:
            response = requests.post(f"{self.base_url}/endpoint", json=message.__dict__)
            response.raise_for_status()
            print("Message sent successfully!")
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to send message: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        print(f"Receiving message from {self.base_url}/endpoint...")
        try:
            response = requests.get(f"{self.base_url}/endpoint")
            response.raise_for_status()
            print("Message received successfully!")
            return Message(action="receive", data=response.json())
        except requests.RequestException as e:
            print(f"Failed to receive message: {e}")
            return Message(action="error", data={}, metadata={"error": str(e)})

    def disconnect(self):
        print("Disconnecting from REST API...")
