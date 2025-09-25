from unittest.mock import AsyncMock, Mock

import pytest
import redis.asyncio as redis

from radar_core.models import StreamData


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


@pytest.fixture
def mock_duckdb_connection():
    """Mock DuckDB connection with all methods used by AsyncDuckDb."""
    mock_conn = Mock()

    # Mock DuckDB connection methods
    mock_conn.close = Mock()
    mock_conn.register = Mock()
    mock_conn.execute = Mock()

    # Configure default return values
    mock_conn.execute.return_value = Mock()  # Mock query result
    mock_conn.register.return_value = None  # Register doesn't return anything

    return mock_conn


@pytest.fixture
def mock_async_thread_pool_executor():
    """Mock AsyncThreadPoolExecutor for testing async database operations."""
    from radar_core.utils import AsyncThreadPoolExecutor

    executor = Mock(spec=AsyncThreadPoolExecutor)
    executor.submit = AsyncMock()

    # Configure default behavior - submit just returns what was passed to it
    # async def default_submit(func, *args, **kwargs):
    #     # if callable(func):
    #     #     return func(*args, **kwargs)
    #     return Mock()
    #
    # executor.submit.side_effect = default_submit

    return executor
