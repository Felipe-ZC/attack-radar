from dataclasses import dataclass

from ..shared.constants import SourceType


@dataclass
class Source:
    url: str
    type: SourceType


@dataclass(frozen=True)
class StreamData:
    ip: str
    source_url: str
