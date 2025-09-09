from dataclasses import asdict
import hashlib
import json
import logging

import redis.asyncio as redis
import redis.exceptions

from .constants import DEFAULT_LOG_LEVEL, DEFAULT_SET_NAME, DEFAULT_STREAM_NAME
from .logger import setup_logger
from .models import StreamData


def get_dict_str_hash(some_dict: dict) -> str:
    return hashlib.sha256(
        json.dumps(some_dict, sort_keys=True).encode()
    ).hexdigest()


def log_error(
    logger: logging.Logger, error_name: str, error_message: str
) -> None:
    logger.error(
        "%s raised when trying to write a new message to signal-stream, error is: %s",
        error_name,
        error_message,
    )


class SignalStream:
    def __init__(
        self,
        redis_client: redis.Redis,
        logger: logging.Logger = setup_logger(
            name="SignalStream", log_level_str=DEFAULT_LOG_LEVEL
        ),
    ):
        self.redis_client = redis_client
        self.logger = logger

    async def write_stream_data(self, stream_data: StreamData) -> str:
        try:
            print(f"in write_stream_data, stream_data is {stream_data}")
            data: dict[str, str] = asdict(stream_data)
            hash_id: str = get_dict_str_hash(data)
            if not await self.redis_client.sismember(
                DEFAULT_SET_NAME, hash_id
            ):
                self.logger.info("Writing new entry to stream %s", stream_data)
                await self.redis_client.sadd(DEFAULT_SET_NAME, hash_id)
                message_id: str = await self.redis_client.xadd(
                    DEFAULT_STREAM_NAME, data
                )
                return message_id
        # TODO: Add re-try logic for the two redis exceptions...
        except redis.exceptions.ConnectionError as connection_err:
            log_error(
                self.logger, "Redis connection error", str(connection_err)
            )
        except redis.exceptions.TimeoutError as timeout_err:
            log_error(self.logger, "Redis timeout error", str(timeout_err))
        except Exception as unhandled_err:
            log_error(self.logger, "Unhandled error", str(unhandled_err))
        return ""
