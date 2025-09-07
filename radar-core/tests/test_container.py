import os
from unittest.mock import patch

from radar_core.constants import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_REDIS_DB,
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
)
from radar_core.container import CoreContainer, configure_container_from_env
from radar_core.logger import LOG_LEVEL_MAP
from radar_core.signal_stream import SignalStream
import redis.asyncio as redis

MOCK_ENV = {
    "LOG_LEVEL": "INFO",
    "REDIS_HOST": "MOCK_REDIS_HOST",
    "REDIS_PORT": "MOCK_REDIS_PORT",
    "REDIS_DB": "MOCK_REDIS_DB",
}


async def test_container_creation_with_default_values():
    container = CoreContainer()
    container.config.service_name.from_value(
        "test_container_creation_with_default_values"
    )

    assert container.config.log_level() == DEFAULT_LOG_LEVEL
    assert container.config.redis_port() == DEFAULT_REDIS_PORT
    assert container.config.redis_host() == DEFAULT_REDIS_HOST
    assert container.config.redis_db() == DEFAULT_REDIS_DB

    logger = container.logger()
    assert (
        logger.level == LOG_LEVEL_MAP[DEFAULT_LOG_LEVEL]
    )

    # NOTE: redis.Redis() does not immedieately estbalish a connection to Redis...
    redis_client = await container.redis_client()
    assert isinstance(redis_client, redis.Redis)

    host = redis_client.connection_pool.connection_kwargs["host"]
    port = redis_client.connection_pool.connection_kwargs["port"]
    db = redis_client.connection_pool.connection_kwargs["db"]

    assert host == DEFAULT_REDIS_HOST
    assert port == DEFAULT_REDIS_PORT
    assert db == DEFAULT_REDIS_DB

    signal_stream = await container.signal_stream()
    assert isinstance(signal_stream, SignalStream)
    assert signal_stream.redis_client is redis_client


async def test_container_creation_with_env_vars():
    with patch.dict(os.environ, MOCK_ENV):
        container = CoreContainer()
        container.config.service_name.from_value(
            "test_container_creation_with_env_vars_logger"
        )

        configure_container_from_env(container)

        assert container.config.log_level() == os.getenv("LOG_LEVEL")
        assert container.config.redis_port() == os.getenv("REDIS_PORT")
        assert container.config.redis_host() == os.getenv("REDIS_HOST")
        assert container.config.redis_db() == os.getenv("REDIS_DB")

        logger = container.logger()
        assert (
            logger.level == LOG_LEVEL_MAP[os.getenv("LOG_LEVEL")]
        )
        # NOTE: redis.Redis() does not immedieately estbalish a connection to Redis...
        redis_client = await container.redis_client()
        assert isinstance(redis_client, redis.Redis)

        host = redis_client.connection_pool.connection_kwargs["host"]
        port = redis_client.connection_pool.connection_kwargs["port"]
        db = redis_client.connection_pool.connection_kwargs["db"]

        assert host == os.getenv("REDIS_HOST")
        assert port == os.getenv("REDIS_PORT")
        assert db == os.getenv("REDIS_DB")

        signal_stream = await container.signal_stream()
        assert isinstance(signal_stream, SignalStream)
        assert signal_stream.redis_client is redis_client


def test_configure_container_from_env():
    with patch.dict(os.environ, MOCK_ENV):
        container = CoreContainer()
        configure_container_from_env(container)

        for env_var, value in MOCK_ENV.items():
            config_env_var = container.config[(env_var.lower(),)]
            assert config_env_var() == value
