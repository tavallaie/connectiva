from .protocol_detector import ProtocolDetector
from .interfaces import CommunicationMethod
from .protocols import (
    RestProtocol,
    GrpcProtocol,
    BrokerProtocol,
    KafkaProtocol,
    FileProtocol,
    WebSocketProtocol,
    GraphQLProtocol
)

class CommunicationFactory:
    """
    Factory for creating communication objects.
    """

    _protocol_map = {
        "REST": RestProtocol,
        "GRPC": GrpcProtocol,
        "Broker": BrokerProtocol,
        "Kafka": KafkaProtocol,
        "File": FileProtocol,
        "WebSocket": WebSocketProtocol,
        "GraphQL": GraphQLProtocol
    }

    @staticmethod
    def create_communication(**kwargs) -> CommunicationMethod:
        """
        Create a communication object based on the detected protocol.

        :param kwargs: Keyword arguments for configuration.
        :return: An instance of CommunicationMethod.
        """
        protocol = ProtocolDetector.detect_protocol(kwargs.get("endpoint"))
        print(f"Detected protocol: {protocol}")

        communication_class = CommunicationFactory._protocol_map.get(protocol)
        if communication_class is None:
            raise ValueError(f"Unsupported communication protocol: {protocol}")

        return communication_class(**kwargs)