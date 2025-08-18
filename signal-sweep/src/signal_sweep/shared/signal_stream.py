import json
import hashlib

from dataclasses import dataclass, asdict
import redis.asyncio as redis

from ..shared.logger import logger

DEFAULT_STREAM_NAME = "signal-stream"
DEFAULT_SET_NAME = "signal-stream-set"


@dataclass(frozen=True)
class StreamData:
    ip: str
    source_url: str


class SignalStream:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def write_stream_data(self, stream_data: StreamData) -> str:
        try:
            data = asdict(stream_data)
            hash_id = hashlib.sha256(
                json.dumps(data, sort_keys=True).encode()
            ).hexdigest()

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
