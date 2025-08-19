"""
Pytest configuration and fixtures for signal_sweep tests.
Provides comprehensive mocking for all external dependencies.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Generator
from unittest.mock import AsyncMock, MagicMock, patch, create_autospec
from concurrent.futures import ProcessPoolExecutor, Executor

import pytest
import httpx
import redis.asyncio as redis

from signal_sweep.core.signal_stream import StreamData, SignalStream
from signal_sweep.core.source import Source
from signal_sweep.shared.constants import SourceType
from signal_sweep.shared.utils import AsyncProcessPoolExecutor
from signal_sweep.core.handlers.text_handler import TextHandler
from signal_sweep.container import ApplicationContainer


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
def mock_http_response() -> MagicMock:
    """Mock HTTP response with sample IP data."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.text = """
    # Sample threat intelligence data
    192.168.1.1
    10.0.0.1
    172.16.0.1
    Some other text here
    192.168.2.100
    """
    mock_response.status_code = 200
    return mock_response


@pytest.fixture
def mock_http_client(mock_http_response: MagicMock) -> AsyncMock:
    """Mock httpx.AsyncClient with configurable responses."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(return_value=mock_http_response)
    return mock_client


@pytest.fixture
def mock_process_executor() -> MagicMock:
    """Mock AsyncProcessPoolExecutor for CPU-bound tasks."""
    mock_async_executor = MagicMock(spec=AsyncProcessPoolExecutor)
    mock_executor = create_autospec(ProcessPoolExecutor, instance=True)
    mock_process_executor.submit = MagicMock()

    # Set up the async context manager behavior
    mock_async_executor.__aenter__ = AsyncMock(
        return_value=mock_process_executor
    )
    mock_async_executor.__aexit__ = AsyncMock(return_value=None)

    # Also set the executor attribute for completeness
    mock_async_executor.executor = mock_process_executor

    return mock_async_executor


@pytest.fixture
def mock_env_vars() -> Generator[Dict[str, str], None, None]:
    """Mock environment variables for Redis configuration."""
    env_vars = {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_config_data() -> Dict[str, List[Dict[str, str]]]:
    """Sample configuration data for testing."""
    return {
        "sources": [
            {
                "url": "https://example.com/threat-data.txt",
                "type": "txt",
                "handler": "someHandler",
            },
            {
                "url": "https://example.com/other-data.txt",
                "type": "txt",
                "handler": "someHandler",
            },
        ]
    }


@pytest.fixture
def mock_yaml_load(
    sample_config_data: Dict[str, List[Dict[str, str]]],
) -> Generator[Dict[str, List[Dict[str, str]]], None, None]:
    """Mock yaml.safe_load to return sample config."""
    with patch(
        "signal_sweep.config.yaml.safe_load", return_value=sample_config_data
    ):
        yield sample_config_data


@pytest.fixture
def mock_file_open() -> Generator[MagicMock, None, None]:
    """Mock file opening for config loading."""
    mock_file = MagicMock()
    mock_file.__enter__ = MagicMock(return_value=mock_file)
    mock_file.__exit__ = MagicMock(return_value=None)

    with patch("builtins.open", return_value=mock_file):
        yield mock_file


@pytest.fixture
def sample_stream_data() -> List[StreamData]:
    """Sample StreamData objects for testing."""
    return [
        StreamData(
            ip="192.168.1.1", source_url="https://example.com/test.txt"
        ),
        StreamData(ip="10.0.0.1", source_url="https://example.com/test.txt"),
        StreamData(ip="172.16.0.1", source_url="https://example.com/test.txt"),
    ]


@pytest.fixture
def sample_sources() -> List[Source]:
    """Sample Source objects for testing."""
    from signal_sweep.core.handlers.text_handler import TextHandler

    handler = TextHandler(
        http_client=MagicMock(), process_executor=MagicMock()
    )

    return [
        Source(
            url="https://example.com/threat-data.txt",
            type=SourceType.TXT,
        ),
        Source(
            url="https://example.com/other-data.txt",
            type=SourceType.TXT,
        ),
    ]


@pytest.fixture
def signal_stream(mock_redis_client: AsyncMock) -> SignalStream:
    """SignalStream instance with mocked Redis client."""
    return SignalStream(redis_client=mock_redis_client)


@pytest.fixture
def text_handler(
    mock_http_client: AsyncMock, mock_process_executor: MagicMock
) -> TextHandler:
    """TextHandler instance with mocked dependencies."""
    return TextHandler(
        http_client=mock_http_client, process_executor=mock_process_executor
    )


@pytest.fixture
def mock_container(
    mock_redis_client: AsyncMock,
    mock_http_client: AsyncMock,
    mock_process_executor: MagicMock,
    mock_env_vars: Dict[str, str],
    sample_sources: List[Source],
) -> ApplicationContainer:
    """ApplicationContainer with all dependencies mocked."""
    container = ApplicationContainer()

    # Override providers with mocks
    container.redis_client.override(mock_redis_client)
    container.http_client.override(mock_http_client)
    container.process_executor.override(mock_process_executor)

    # Override config
    container.config.redis_host.override(mock_env_vars["REDIS_HOST"])
    container.config.redis_port.override(int(mock_env_vars["REDIS_PORT"]))
    container.config.redis_db.override(int(mock_env_vars["REDIS_DB"]))
    container.config.max_workers.override(5)
    container.config.sources.override(sample_sources)

    return container


@pytest.fixture
def mock_config_file_path() -> Path:
    """Mock config file path for testing."""
    return Path("/fake/path/to/data_sources.yml")


@pytest.fixture(autouse=True)
def mock_argparse() -> Generator[MagicMock, None, None]:
    """Auto-use fixture to mock command line argument parsing."""
    mock_args = MagicMock()
    mock_args.config = "/fake/path/to/data_sources.yml"

    with patch("signal_sweep.main.argparse.ArgumentParser") as mock_parser:
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance
        yield mock_args


# Test utilities
@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Mock patches for modules that need to be mocked at import time
@pytest.fixture(autouse=True, scope="session")
def mock_imports() -> Generator[None, None, None]:
    """Mock imports that might cause issues during testing."""
    with patch("signal_sweep.shared.utils.ProcessPoolExecutor") as mock_pool:
        mock_pool.return_value.__enter__ = MagicMock()
        mock_pool.return_value.__exit__ = MagicMock()
        yield
