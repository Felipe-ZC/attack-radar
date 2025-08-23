from typing import List
from unittest.mock import AsyncMock
from dataclasses import asdict

from src.shared.signal_stream import (
    SignalStream,
    _get_dict_str_hash,
)
from src.shared.models import StreamData
from src.shared.constants import (
    DEFAULT_SET_NAME,
    DEFAULT_STREAM_NAME,
)


async def test_write_stream_data(
    mock_redis_client: AsyncMock,
    sample_stream_data: List[StreamData],
):
    signal_stream = SignalStream(mock_redis_client)

    for stream_data in sample_stream_data:
        await signal_stream.write_stream_data(stream_data)
        stream_data_as_dict = asdict(stream_data)
        hash_id = _get_dict_str_hash(stream_data_as_dict)

        mock_redis_client.sismember.assert_called_with(
            DEFAULT_SET_NAME, hash_id
        )

        mock_redis_client.sadd.assert_called_with(DEFAULT_SET_NAME, hash_id)

        mock_redis_client.xadd.assert_called_with(
            DEFAULT_STREAM_NAME, stream_data_as_dict
        )


async def test_write_stream_data_dedupe(
    mock_redis_client: AsyncMock,
    sample_stream_data: List[StreamData],
):
    mock_redis_client.sismember = AsyncMock(return_value=True)
    signal_stream = SignalStream(mock_redis_client)

    for stream_data in sample_stream_data:
        await signal_stream.write_stream_data(stream_data)
        stream_data_as_dict = asdict(stream_data)
        hash_id = _get_dict_str_hash(stream_data_as_dict)

        mock_redis_client.sismember.assert_called_with(
            DEFAULT_SET_NAME, hash_id
        )
        mock_redis_client.sadd.assert_not_called()
        mock_redis_client.xadd.assert_not_called()
