"""
Configuration classes and other config utilites.
"""
import os

from typing import List
from pathlib import Path

import redis.asyncio as redis
import yaml

from .shared.source import Source, SourceType
from .shared.constants import SOURCE_TYPE_TO_HANDLER_DICT


def load_config(config_file_path: Path) -> List[Source]:
    file_path = config_file_path.resolve()

    with open(file_path, mode="r") as config_file:
        config_dict = yaml.safe_load(config_file)

    return [
        Source(
            url=source.get("url", ""),
            type=SourceType(source.get("type", "")),
            # TODO: Add handler...
            handler=SOURCE_TYPE_TO_HANDLER_DICT.get(SourceType(source.get("type", ""))),
        )
        for source in config_dict.get("sources", [])
    ]


def get_redis_config() -> redis.Redis:
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=os.getenv('REDIS_PORT', 6379),
        db=os.getenv('SIGNAL_STREAM_DB', 0)
    )
