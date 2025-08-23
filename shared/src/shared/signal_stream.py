import json
import hashlib
import logging
from typing import Dict

from dataclasses import asdict
import redis.asyncio as redis

from .logger import setup_logger, get_log_level_from_env
from .models import StreamData
from .constants import DEFAULT_STREAM_NAME, DEFAULT_SET_NAME


def get_dict_str_hash(some_dict: Dict) -> str:
    return hashlib.sha256(
        json.dumps(some_dict, sort_keys=True).encode()
    ).hexdigest()


class SignalStream:
    def __init__(
        self,
        redis_client: redis.Redis,
        logger: logging.Logger = setup_logger(
            name="SignalStream", log_level=get_log_level_from_env()
        ),
    ):
        self.redis_client = redis_client
        self.logger = logger

    async def write_stream_data(self, stream_data: StreamData) -> str:
        try:
            data = asdict(stream_data)
            hash_id = get_dict_str_hash(data)
            if not await self.redis_client.sismember(
                DEFAULT_SET_NAME, hash_id
            ):
                self.logger.info("Writing new entry to stream %s", stream_data)
                await self.redis_client.sadd(DEFAULT_SET_NAME, hash_id)
                message_id = await self.redis_client.xadd(
                    DEFAULT_STREAM_NAME, data
                )
                return str(message_id)
        except Exception as e:
            self.logger.error(
                "Error while trying to write new message to signal-stream, error is %s",
                e,
            )
            raise e
        return ""
