from typing import List
from unittest.mock import AsyncMock

from src.signal_sweep.core.signal_stream import SignalStream
from src.signal_sweep.core.models import StreamData


async def test_signal_stream(
    mock_redis_client: AsyncMock,
    sample_stream_data: List[StreamData],
):
    signal_stream = SignalStream(mock_redis_client)
    for stream_data in sample_stream_data:
        await signal_stream.write_stream_data(stream_data)
        #
        # mock_redis_client.sismember.assert_called(
        #
        # )        mock_redis_client.sadd.assert_called()
        #
        # mock_redis_client.xadd.assert_called()
