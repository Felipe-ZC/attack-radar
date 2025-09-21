import asyncio
from logging import Logger
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from radar_core import AsyncDuckDb, SignalStream, get_log_level_from_env

from .container import ApplicationContainer
from .ipdb import AbuseIPDB
from .signal_processor import SignalProcessor


@inject
async def main(
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
    container.config.duck_db_path.override(Path("./test_db"))
    container.wire(modules=[__name__])

    try:
        await main()
    finally:
        container.shutdown_resources()


if __name__ == "__main__":
    asyncio.run(bootstrap())
