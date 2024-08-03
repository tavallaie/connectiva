import os
import json
from typing import Dict, Any
from ..interfaces import CommunicationMethod
from ..message import Message

class FileProtocol(CommunicationMethod):
    """
    File sharing communication class.
    """

    def __init__(self, **kwargs):
        self.file_path = kwargs.get("file_path")

    def connect(self):
        print(f"Accessing file at {self.file_path}...")

    def send(self, message: Message) -> Dict[str, Any]:
        print(f"Writing message to file {self.file_path}...")
        try:
            with open(self.file_path, 'w') as file:
                json.dump(message.__dict__, file)
            print("Message written successfully!")
            return {"status": "file_written"}
        except Exception as e:
            print(f"Failed to write message: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        print(f"Reading message from file {self.file_path}...")
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as file:
                    print("Message read successfully!")
                    return Message(action="receive", data=json.load(file))
            else:
                print("File does not exist.")
                return Message(action="error", data={}, metadata={"error": "File not found"})
        except Exception as e:
            print(f"Failed to read message: {e}")
            return Message(action="error", data={}, metadata={"error": str(e)})

    def disconnect(self):
        print("Closing file access...")
