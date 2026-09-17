from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryRecord:
    memory_id: str
    source_type: str
    source_name: str
    content: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)