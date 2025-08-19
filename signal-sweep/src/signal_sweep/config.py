"""
Configuration classes and other config utilites.
"""

from typing import List
from pathlib import Path

import yaml

from .core.models import Source
from .shared.constants import SourceType


def load_config(config_file_path: Path) -> List[Source]:
    file_path = config_file_path.resolve()

    with open(file_path, mode="r") as config_file:
        config_dict = yaml.safe_load(config_file)

    return [
        Source(
            url=source.get("url", ""),
            type=SourceType(source.get("type", "")),
        )
        for source in config_dict.get("sources", [])
    ]
