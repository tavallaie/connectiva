from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class Message:
    """
    Represents a message to be sent or received.
    """
    action: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)