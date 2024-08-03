# connectiva/protocol_detector.py

import os
import re

class ProtocolDetector:
    """
    ProtocolDetector detects the appropriate communication protocol
    based on input parameters or environment configuration.
    """

    # Mapping from URL scheme to protocol name
    _protocol_map = {
        "http://": "REST",
        "https://": "REST",
        "grpc://": "GRPC",
        "amqp://": "AMQP",
        "kafka://": "Kafka",
        "ws://": "WebSocket",
        "wss://": "WebSocket",
        "graphql://": "GraphQL",
    }

    @staticmethod
    def detect_protocol(endpoint: str) -> str:
        """
        Detect the communication protocol based on the endpoint URL or other criteria.

        :param endpoint: The communication endpoint URL or identifier.
        :return: The detected protocol type as a string.
        """
        # Use the mapping to detect protocols by URL scheme
        for scheme, protocol in ProtocolDetector._protocol_map.items():
            if endpoint.startswith(scheme):
                return protocol

        # Check if it's a file path
        if os.path.exists(endpoint):
            return "File"

        # Check environment variables for preferred protocol
        preferred_protocol = os.getenv("PREFERRED_PROTOCOL")
        if preferred_protocol:
            return preferred_protocol

        # Default fallback
        return "REST"
