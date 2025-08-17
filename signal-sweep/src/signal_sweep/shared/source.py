from dataclasses import dataclass
from enum import Enum

from ..handlers.base_handler import BaseHandler


class SourceType(Enum):
    CSV = "csv"
    JSON = "json"
    TXT = "txt"
    # PARQUET = "parquet"
    # EXCEL = "xlsx"
    # TSV = "tsv"


@dataclass
class Source:
    url: str
    type: SourceType
    handler: BaseHandler
