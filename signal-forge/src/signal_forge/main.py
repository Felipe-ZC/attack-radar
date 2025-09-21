import asyncio
from logging import Logger

# from pathlib import Path
from dependency_injector.wiring import Provide, inject
from radar_core import AsyncDuckDb, SignalStream, get_log_level_from_env

from .container import ApplicationContainer
from .core.ipdb import AbuseIPDB
from .core.signal_processor import SignalProcessor


@inject
async def process_signals(
    abuse_ipdb: AbuseIPDB = Provide[ApplicationContainer.abuse_ipdb],
    async_duck_db: AsyncDuckDb = Provide[ApplicationContainer.async_duck_db],
    signal_stream: SignalStream = Provide[ApplicationContainer.signal_stream],
    logger: Logger = Provide[ApplicationContainer.logger],
) -> list[str]:
    signal_processor = SignalProcessor(
        abuse_ipdb=abuse_ipdb,
        duck_db=async_duck_db,
        logger=logger,
        signal_stream=signal_stream,
    )
    await signal_processor.process_signals()


async def bootstrap() -> None:
    container = ApplicationContainer()
    container.config.service_name.from_value("SignalForge")
    container.config.log_level.from_value(get_log_level_from_env())
    container.config.duck_db_path.from_env("DUCK_DB_PATH")
    container.wire(modules=[__name__])

    try:
        await process_signals()
    finally:
        container.shutdown_resources()


def main() -> None:
    asyncio.run(bootstrap())


if __name__ == "__main__":
    main()
