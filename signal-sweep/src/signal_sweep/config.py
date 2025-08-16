"""
Configuration classes and other config utilites.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List
from pathlib import Path

import yaml


class SourceType(Enum):
    CSV = "csv"
    JSON = "json"
    TXT = "txt"
    # PARQUET = "parquet"
    # EXCEL = "xlsx"
    # TSV = "tsv"


# TODO: Implement this later...
class SourceHandler:
    pass


@dataclass
class Source:
    url: str
    type: SourceType
    handler: SourceHandler


def load_config(config_file_path: Path) -> List[Source]:
    file_path = config_file_path.resolve()

    with open(file_path, mode="r") as config_file:
        config_dict = yaml.safe_load(config_file)

    return [
        Source(
            url=source.get("url", ""),
            type=source.get("type", ""),
            # TODO: Add handler...
            handler=SourceHandler(),
        )
        for source in config_dict.get("sources", [])
    ]
