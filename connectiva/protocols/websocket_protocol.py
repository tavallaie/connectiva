import websockets
import json
from typing import Dict, Any
from ..interfaces import CommunicationMethod
from ..message import Message

class WebSocketProtocol(CommunicationMethod):
    """
    WebSocket communication class.
    """

    def __init__(self, **kwargs):
        self.websocket_url = kwargs.get("websocket_url")
        self.ws = None

    def connect(self):
        print(f"Connecting to WebSocket at {self.websocket_url}...")
        try:
            self.ws = websockets.create_connection(self.websocket_url)
            print("Connected to WebSocket!")
        except Exception as e:
            print(f"Failed to connect to WebSocket: {e}")

    def send(self, message: Message) -> Dict[str, Any]:
        print("Sending message via WebSocket...")
        try:
            self.ws.send(json.dumps(message.__dict__))
            print("Message sent successfully!")
            return {"status": "sent"}
        except Exception as e:
            print(f"Failed to send message: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        print("Receiving message via WebSocket...")
        try:
            message = self.ws.recv()
            print("Message received successfully!")
            return Message(action="receive", data=json.loads(message))
        except Exception as e:
            print(f"Failed to receive message: {e}")
            return Message(action="error", data={}, metadata={"error": str(e)})

    def disconnect(self):
        print("Disconnecting from WebSocket...")
        if self.ws:
            self.ws.close()
