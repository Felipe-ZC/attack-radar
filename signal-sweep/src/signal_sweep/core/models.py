from dataclasses import dataclass

from ..shared.constants import SourceType


@dataclass
class Source:
    url: str
    type: SourceType


# Note: Maybe instead of saving the source_url we save the whole Source object here?
@dataclass(frozen=True)
class StreamData:
    ip: str
    source_url: str
