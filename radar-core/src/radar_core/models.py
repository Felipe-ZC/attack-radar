from dataclasses import dataclass


# Note: Maybe instead of saving the source_url we save the whole Source object here?
@dataclass(frozen=True)
class StreamData:
    ip: str
    source_url: str
