from .communication_factory import CommunicationFactory
from .message import Message
from typing import Dict, Any

class Connectiva:
    """
    Connectiva manages the orchestration of different communication protocols.
    """

    def __init__(self, **kwargs):
        """
        Initializes Connectiva with given keyword arguments.

        :param kwargs: Keyword arguments for configuration.
        """
        self.config = kwargs
        self.strategy = self.create_strategy(**kwargs)

    def create_strategy(self, **kwargs) -> CommunicationFactory:
        """
        Creates the appropriate communication strategy based on the configuration.

        :param kwargs: Keyword arguments for configuration.
        :return: An instance of CommunicationMethod.
        """
        return CommunicationFactory.create_communication(**kwargs)

    def connect(self):
        self.strategy.connect()

    def send(self, message: Message) -> Dict[str, Any]:
        return self.strategy.send(message)

    def receive(self) -> Message:
        return self.strategy.receive()

    def disconnect(self):
        self.strategy.disconnect()
