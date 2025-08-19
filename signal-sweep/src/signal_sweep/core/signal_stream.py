import json
import hashlib

from dataclasses import asdict
import redis.asyncio as redis

from .models import StreamData
from ..shared.logger import logger
from ..shared.constants import DEFAULT_STREAM_NAME, DEFAULT_SET_NAME


def _get_json_str_hash(json_str: str) -> str:
    return hashlib.sha256(json_str).hexdigest()


class SignalStream:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        print(self.redis_client)

    async def write_stream_data(self, stream_data: StreamData) -> str:
        try:
            data = asdict(stream_data)
            hash_id = _get_json_str_hash(
                json.dumps(data, sort_keys=True).encode()
            )
            if not await self.redis_client.sismember(
                DEFAULT_SET_NAME, hash_id
            ):
                await self.redis_client.sadd(DEFAULT_SET_NAME, hash_id)
                message_id = await self.redis_client.xadd(
                    DEFAULT_STREAM_NAME, data
                )
                return str(message_id)
        except Exception as e:
            logger.error(
                "Error while trying to write new message to signal-stream, error is %s",
                e,
            )
            raise e
        return ""
