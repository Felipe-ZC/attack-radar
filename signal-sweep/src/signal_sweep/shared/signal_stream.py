import os

from dataclasses import dataclass, asdict
import redis.asyncio as redis

from ..shared.logger import logger

DEFAULT_STREAM_NAME = "signal-stream"


@dataclass
class StreamData:
    ip: str
    source_url: str
    timestamp: int


class SignalStream:
    def __init__(self, redis_svc: redis.Redis):
        self.redis_svc = redis_svc

    async def write_stream_data(self, stream_data: StreamData):
        try:
            stream_name = DEFAULT_STREAM_NAME
            data = asdict(stream_data)
            message_id = await self.redis_svc.xadd(stream_name, data)
            logger.info(
                "Wrote new message to singal-stream, ID is: %s", str(message_id)
            )
        except Exception as e:
            logger.error(
                "Error while trying to write new message to signal-stream, error is %s",
                e,
            )
        finally:
            await self.redis_svc.close()


def get_redis_client() -> redis.Redis:
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=os.getenv("REDIS_PORT", 6379),
        db=os.getenv("SIGNAL_STREAM_DB", 0),
    )
