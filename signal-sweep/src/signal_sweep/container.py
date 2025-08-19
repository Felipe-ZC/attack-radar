# src/signal_sweep/container.py
from dependency_injector import containers, providers

import httpx
import redis.asyncio as redis

from .shared.signal_stream import SignalStream
from .shared.source import SourceType
from .shared.utils import AsyncProcessPoolExecutor
from .handlers.text_handler import TextHandler


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Resources
    redis_client = providers.Resource(
        redis.Redis,
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        decode_responses=True,
    )
    http_client = providers.Resource(httpx.AsyncClient, timeout=30.0)
    process_executor = providers.Resource(
        AsyncProcessPoolExecutor, max_workers=config.max_workers
    )

    # Services
    signal_stream = providers.Factory(SignalStream, redis_client=redis_client)
    text_handler = providers.Factory(
        TextHandler, http_client=http_client, process_executor=process_executor
    )

    # Utilities
    handler_mapping = providers.Dict({SourceType.TXT: text_handler})
