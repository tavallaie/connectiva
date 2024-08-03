from abc import ABC, abstractmethod
from typing import Dict, Any
from connectiva import Message

class CommunicationMethod(ABC):
    """
    Abstract base class for different communication methods.
    """

    @abstractmethod
    def connect(self):
        """
        Establishes a connection to the communication endpoint.
        """
        pass

    @abstractmethod
    def send(self, message: Message) -> Dict[str, Any]:
        """
        Sends a message to the communication endpoint.

        :param message: The message to be sent.
        :return: A dictionary containing the response.
        """
        pass

    @abstractmethod
    def receive(self) -> Message:
        """
        Receives a message from the communication endpoint.

        :return: The received message.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Closes the connection to the communication endpoint.
        """
        pass
