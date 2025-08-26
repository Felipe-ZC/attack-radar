import asyncio
from logging import Logger

from dependency_injector.wiring import Provide, inject
from radar_core import SignalStream, get_log_level_from_env
from radar_core.models import StreamData

from .config import get_config_file_path, load_config
from .container import ApplicationContainer
from .core.handlers.base_handler import Handler
from .core.models import Source
from .shared.constants import DEFAULT_BATCH_SIZE, SourceType
from .shared.utils import async_batch_process_list


@inject
async def handle_data_source(
    source: Source,
    signal_stream: SignalStream = Provide[ApplicationContainer.signal_stream],
    logger: Logger = Provide[ApplicationContainer.logger],
    handler_mapping: dict[SourceType, Handler] = Provide[
        ApplicationContainer.handler_mapping
    ],
) -> list[StreamData]:
    logger.info("Handling data source %s", source)
    handler = handler_mapping[source.type]
    return await handler.handle(source)


@inject
async def ingest_stream_data(
    stream_data: StreamData,
    signal_stream: SignalStream = Provide[ApplicationContainer.signal_stream],
    logger: Logger = Provide[ApplicationContainer.logger],
) -> list[StreamData]:
    logger.info("Ingesting data %s", stream_data)
    return await signal_stream.write_stream_data(stream_data)


@inject
async def main(
    data_sources: list[Source] = Provide[ApplicationContainer.config.sources],
) -> list[str]:
    stream_data_lists: list[list[StreamData]] = await async_batch_process_list(
        data_sources, DEFAULT_BATCH_SIZE, handle_data_source
    )
    flattend_stream_data_list: list[StreamData] = [
        stream_data
        for stream_data_list in stream_data_lists
        for stream_data in stream_data_list
    ]
    message_ids: list[str] = await async_batch_process_list(
        flattend_stream_data_list, DEFAULT_BATCH_SIZE * 10, ingest_stream_data
    )
    return message_ids


async def bootstrap() -> None:
    container = ApplicationContainer()
    container.config.sources.from_value(load_config(get_config_file_path()))
    container.config.service_name.from_value("SignalSweep")
    container.config.log_level.from_value(get_log_level_from_env())
    container.wire(modules=[__name__])
    await main()


if __name__ == "__main__":
    asyncio.run(bootstrap())
