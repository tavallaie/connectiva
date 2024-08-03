import requests
from typing import Dict, Any
from ..interfaces import CommunicationMethod
from ..message import Message

class GraphQLProtocol(CommunicationMethod):
    """
    GraphQL communication class.
    """

    def __init__(self, **kwargs):
        self.graphql_url = kwargs.get("graphql_url")

    def connect(self):
        print(f"Connecting to GraphQL endpoint at {self.graphql_url}...")

    def send(self, message: Message) -> Dict[str, Any]:
        print("Sending GraphQL query...")
        try:
            response = requests.post(self.graphql_url, json=message.__dict__)
            response.raise_for_status()
            print("Query sent successfully!")
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to send query: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        print("Receiving data from GraphQL is query-based, usually not applicable.")
        return Message(action="receive", data={})

    def disconnect(self):
        print("Disconnecting from GraphQL endpoint...")
