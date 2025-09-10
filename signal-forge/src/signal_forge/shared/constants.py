from enum import Enum


class SourceType(Enum):
    CSV = "csv"
    JSON = "json"
    TXT = "txt"


# Default values
DEFAULT_BATCH_SIZE = 5
MAX_BATCH_SIZE = 10

# Regular expressions
IP_V4_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
