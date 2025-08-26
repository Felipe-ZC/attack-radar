import redis.asyncio as redis
from dependency_injector import containers, providers

from .logger import setup_logger
from .signal_stream import SignalStream
from .constants import DEFAULT_REDIS_DB, DEFAULT_REDIS_HOST, DEFAULT_REDIS_PORT


class CoreContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Factory(
        setup_logger,
        name=config.service_name,
        log_level=(config.log_level)
    )

    config.redis_host.from_env("REDIS_HOST", DEFAULT_REDIS_HOST)
    config.redis_port.from_env("REDIS_PORT", DEFAULT_REDIS_PORT)
    config.redis_db.from_env("REDIS_DB", DEFAULT_REDIS_DB)

    redis_client = providers.Resource(
        redis.Redis,
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        decode_responses=True,
    )

    signal_stream = providers.Factory(SignalStream, redis_client=redis_client)
