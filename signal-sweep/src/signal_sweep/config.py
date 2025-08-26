"""
Configuration classes and other config utilites.
"""

import argparse

from typing import List
from pathlib import Path

import yaml

from .core.models import Source
from .shared.constants import SourceType


def get_config_file_path() -> Path:
    parser = argparse.ArgumentParser(
        description="The data ingestion service for attack-radar"
    )
    parser.add_argument(
        "--config", help="The path to the data_sources.yml file", required=True
    )
    args = parser.parse_args()
    print(f"in get_config_file_path, args are: {args}")
    return Path(args.config)


# TODO: This should be called load_sources not load_config...
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
