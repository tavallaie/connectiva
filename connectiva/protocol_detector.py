import os
import re

class ProtocolDetector:
    """
    ProtocolDetector detects the appropriate communication protocol
    based on input parameters or environment configuration.
    """

    @staticmethod
    def detect_protocol(endpoint: str) -> str:
        """
        Detect the communication protocol based on the endpoint URL or other criteria.

        :param endpoint: The communication endpoint URL or identifier.
        :return: The detected protocol type as a string.
        """
        # Check for specific URL patterns
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return "REST"
        elif endpoint.startswith("grpc://"):
            return "GRPC"
        elif re.match(r"amqp://|mqtt://", endpoint):
            return "Broker"
        elif endpoint.startswith("kafka://"):
            return "Kafka"
        elif os.path.exists(endpoint):
            return "File"
        elif endpoint.startswith("ws://") or endpoint.startswith("wss://"):
            return "WebSocket"
        elif endpoint.startswith("graphql://"):
            return "GraphQL"
        
        # Check environment variables for preferred protocol
        preferred_protocol = os.getenv("PREFERRED_PROTOCOL")
        if preferred_protocol:
            return preferred_protocol
        
        # Default fallback
        return "REST"
