# connectiva/connectiva.py

import logging
from typing import Dict, Any, List, Optional
from connectiva import CommunicationFactory, Message , setup_logging


class Connectiva:
    """
    Connectiva manages the orchestration of different communication protocols.
    """

    def __init__(self,
                 log: bool = False,
                 log_file: Optional[str] = None,
                 custom_logging_handlers: Optional[List[logging.Handler]] = None,
                 log_level: str = "INFO",
                 **kwargs):
        """
        Initializes Connectiva with given keyword arguments.

        :param log: Flag to log to stdout if True.
        :param log_file: File path to save logs if provided.
        :param custom_logging_handlers: List of custom logging handlers.
        :param log_level: Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        :param kwargs: Other keyword arguments for configuration.
        """
        setup_logging(
            log_to_stdout=log,
            log_file=log_file,
            custom_handlers=custom_logging_handlers,
            log_level=log_level
        )

        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = kwargs
        self.strategy = self.create_strategy(**kwargs)
        self.logger.info("Connectiva initialized with configuration: %s", self.config)

    def create_strategy(self, **kwargs) -> CommunicationFactory:
        """
        Creates the appropriate communication strategy based on the configuration.

        :param kwargs: Keyword arguments for configuration.
        :return: An instance of CommunicationMethod.
        """
        self.logger.debug("Creating communication strategy...")
        return CommunicationFactory.create_communication(**kwargs)

    def connect(self):
        self.logger.info("Connecting to communication endpoint...")
        self.strategy.connect()

    def send(self, message: Message) -> Dict[str, Any]:
        self.logger.info("Sending message: %s", message)
        return self.strategy.send(message)

    def receive(self) -> Message:
        self.logger.info("Receiving message...")
        return self.strategy.receive()

    def disconnect(self):
        self.logger.info("Disconnecting from communication endpoint...")
        self.strategy.disconnect()
