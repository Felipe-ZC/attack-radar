from collections.abc import Generator
import os
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from radar_core import AsyncDuckDb, SignalStream
from signal_forge.container import ApplicationContainer
from signal_forge.core.ipdb import AbuseIPDB
from signal_forge.core.models import AbuseIPDBReport, HostMetadata
from signal_forge.core.signal_processor import SignalProcessor


# Define missing fixtures that signal-sweep's mock_http_client depends on
@pytest.fixture
def mock_http_response():
    """Mock HTTP response for httpx client."""
    from unittest.mock import MagicMock

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.text = "Sample response text"
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "sample"}
    return mock_response


@pytest.fixture
def mock_http_client(mock_http_response):
    """Mock httpx.AsyncClient with configurable responses."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(return_value=mock_http_response)
    return mock_client


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for configuration."""
    return {"REDIS_HOST": "localhost", "REDIS_PORT": "6379", "REDIS_DB": "0"}


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_abuse_ipdb_response() -> dict:
    """Sample AbuseIPDB API response for testing."""
    return {
        "data": {
            "ipAddress": "192.168.1.100",
            "countryCode": "US",
            "countryName": "United States",
            "usageType": "Commercial",
            "domain": "example.com",
            "isp": "Example ISP",
            "reports": [
                {
                    "reportedAt": "2024-01-15T10:30:00Z",
                    "comment": "Suspicious activity detected",
                    "categories": [18, 20],
                },
                {
                    "reportedAt": "2024-01-14T15:45:00Z",
                    "comment": "Port scanning attempt",
                    "categories": [14],
                },
            ],
        }
    }


@pytest.fixture
def mock_abuse_ipdb(
    mock_http_client: AsyncMock,
    mock_logger: Mock,
    sample_abuse_ipdb_response: dict,
) -> AbuseIPDB:
    """Mock AbuseIPDB service with sample response."""
    # Configure the http client to return our sample response
    mock_response = Mock()
    mock_response.json.return_value = sample_abuse_ipdb_response
    mock_http_client.get = AsyncMock(return_value=mock_response)

    return AbuseIPDB(http_client=mock_http_client, logger=mock_logger)


@pytest.fixture
def mock_async_duck_db(
    mock_duckdb_connection: Mock, mock_async_thread_pool_executor: Mock
) -> AsyncMock:
    """Mock AsyncDuckDb composed from radar-core fixtures."""
    mock_duck_db = AsyncMock(spec=AsyncDuckDb)

    # Mock AsyncDuckDb methods
    mock_duck_db.execute_query = AsyncMock(return_value=None)
    mock_duck_db.bulk_insert_from_dataframe = AsyncMock(return_value=None)
    mock_duck_db.connection = mock_duckdb_connection
    mock_duck_db.thread_pool_executor = mock_async_thread_pool_executor

    return mock_duck_db


@pytest.fixture
def mock_signal_processor(
    mock_abuse_ipdb: AbuseIPDB,
    mock_logger: Mock,
    mock_redis_client: AsyncMock,
    mock_async_duck_db: AsyncMock,
) -> SignalProcessor:
    """Mock SignalProcessor with all dependencies."""
    signal_stream = SignalStream(redis_client=mock_redis_client)

    return SignalProcessor(
        abuse_ipdb=mock_abuse_ipdb,
        logger=mock_logger,
        signal_stream=signal_stream,
        duck_db=mock_async_duck_db,
    )


@pytest.fixture
def signal_forge_env_vars() -> Generator[dict[str, str], None, None]:
    """Environment variables specific to signal-forge."""
    env_vars = {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
        "DUCK_DB_PATH": "/tmp/test_signal_forge.db",
        "IPDB_API_KEY": "test-api-key-12345",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_host_metadata() -> HostMetadata:
    """Sample HostMetadata object for testing."""
    return HostMetadata(
        ip_address="192.168.1.100",
        country_code="US",
        country_name="United States",
        usage_type="Commercial",
        domain="example.com",
        isp="Example ISP",
    )


@pytest.fixture
def sample_abuse_reports() -> list[AbuseIPDBReport]:
    """Sample AbuseIPDBReport objects for testing."""
    from datetime import datetime

    return [
        AbuseIPDBReport(
            ip_address="192.168.1.100",
            report_timestamp=datetime.fromisoformat(
                "2024-01-15T10:30:00+00:00"
            ),
            report_comment="Suspicious activity detected",
            report_categories=[18, 20],
        ),
        AbuseIPDBReport(
            ip_address="192.168.1.100",
            report_timestamp=datetime.fromisoformat(
                "2024-01-14T15:45:00+00:00"
            ),
            report_comment="Port scanning attempt",
            report_categories=[14],
        ),
    ]


@pytest.fixture
def sample_redis_stream_messages() -> list:
    """Sample Redis stream messages for testing SignalProcessor."""
    return [
        (
            "signals:stream",
            [
                ("1234567890-0", {"ip": b"192.168.1.100"}),
                ("1234567890-1", {"ip": b"10.0.0.1"}),
            ],
        )
    ]


@pytest.fixture
def mock_application_container(
    mock_abuse_ipdb: AbuseIPDB,
    mock_async_duck_db: AsyncMock,
    mock_redis_client: AsyncMock,
    mock_logger: Mock,
    signal_forge_env_vars: dict[str, str],
) -> ApplicationContainer:
    """ApplicationContainer with all providers mocked."""
    container = ApplicationContainer()

    # Override providers with mocks
    container.abuse_ipdb.override(mock_abuse_ipdb)
    container.async_duck_db.override(mock_async_duck_db)
    container.redis_client.override(mock_redis_client)
    container.logger.override(mock_logger)

    # Override config
    container.config.service_name.override("test-signal-forge")
    container.config.log_level.override("DEBUG")
    container.config.duck_db_path.override(
        signal_forge_env_vars["DUCK_DB_PATH"]
    )
    container.config.redis_host.override(signal_forge_env_vars["REDIS_HOST"])
    container.config.redis_port.override(
        int(signal_forge_env_vars["REDIS_PORT"])
    )
    container.config.redis_db.override(int(signal_forge_env_vars["REDIS_DB"]))

    return container
