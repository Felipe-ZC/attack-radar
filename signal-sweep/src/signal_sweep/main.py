import asyncio
import argparse
from pathlib import Path
from typing import List, Dict

from dependency_injector.wiring import Provide, inject

from .core.models import Source
from .shared.constants import SourceType, DEFAULT_BATCH_SIZE
from .shared.logger import logger
from .core.handlers.base_handler import Handler
from .container import ApplicationContainer
from .core.signal_stream import SignalStream
from .core.models import StreamData
from .shared.utils import async_batch_process_list

from .config import load_config


def get_config_file_path() -> Path:
    parser = argparse.ArgumentParser(
        description="The data ingestion service for attack-radar"
    )
    parser.add_argument(
        "--config", help="The path to the data_sources.yml file", required=True
    )
    args = parser.parse_args()
    return Path(args.config)


@inject
async def handle_data_source(
    source: Source,
    handler_mapping: Dict[SourceType, Handler] = Provide[
        ApplicationContainer.handler_mapping
    ],
    signal_stream: SignalStream = Provide[ApplicationContainer.signal_stream],
) -> List[StreamData]:
    handler = handler_mapping[source.type]
    return await handler.handle(source)


@inject
async def ingest_stream_data(
    stream_data: StreamData,
    signal_stream: SignalStream = Provide[ApplicationContainer.signal_stream],
) -> List[StreamData]:
    logger.info("Trying to write %s", stream_data)
    return await signal_stream.write_stream_data(stream_data)


@inject
async def main(
    data_sources: List[Source] = Provide[ApplicationContainer.config.sources],
) -> None:
    stream_data_list_generator = async_batch_process_list(
        data_sources, DEFAULT_BATCH_SIZE, handle_data_source
    )
    async for stream_data_list in stream_data_list_generator:
        ingest_stream_data_result_generator = async_batch_process_list(
            stream_data_list, DEFAULT_BATCH_SIZE, ingest_stream_data
        )
        async for message_id in ingest_stream_data_result_generator:
            if message_id:
                logger.info(
                    "Wrote new message to singal-stream, ID is: %s", message_id
                )
            else:
                logger.info("Already exists in stream!")


async def bootstrap() -> None:
    container = ApplicationContainer()

    container.config.redis_host.from_env("REDIS_HOST")
    container.config.redis_port.from_env("REDIS_PORT")
    container.config.redis_db.from_env("REDIS_DB")

    container.config.max_workers.override(DEFAULT_BATCH_SIZE)
    container.config.sources.override(load_config(get_config_file_path()))
    container.wire(modules=[__name__])

    await main()


if __name__ == "__main__":
    asyncio.run(bootstrap())
