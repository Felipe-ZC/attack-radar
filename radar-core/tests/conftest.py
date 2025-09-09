from unittest.mock import AsyncMock, Mock

import pytest
from radar_core.models import StreamData
import redis.asyncio as redis


@pytest.fixture
def mock_logger():
    return Mock(spec=["debug", "info", "warning", "error", "critical"])


@pytest.fixture
def mock_redis_client() -> AsyncMock:
    """Mock Redis client with all async methods used by SignalStream."""
    mock_client = AsyncMock(spec=redis.Redis)

    # Mock Redis methods used by SignalStream
    mock_client.sismember = AsyncMock(
        return_value=False
    )  # Item not in set by default
    mock_client.sadd = AsyncMock(return_value=1)  # Added to set
    mock_client.xadd = AsyncMock(
        return_value=b"1234567890-0"
    )  # Stream message ID

    return mock_client


@pytest.fixture
def sample_stream_data() -> list[StreamData]:
    """Sample StreamData objects for testing."""
    return [
        StreamData(
            ip="192.168.1.1", source_url="https://example.com/test.txt"
        ),
        StreamData(ip="10.0.0.1", source_url="https://example.com/test.txt"),
        StreamData(ip="172.16.0.1", source_url="https://example.com/test.txt"),
    ]
