from dataclasses import dataclass


@dataclass
class StreamData:
    ip: str
    source_url: str
    timestamp: int
