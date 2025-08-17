from dataclasses import dataclass, asdict
import redis.asyncio as redis

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
            print("wrote a new message to the stream!")
            print(message_id)
        except Exception as e:
            print(e)
        finally:
            await self.redis_svc.close()
