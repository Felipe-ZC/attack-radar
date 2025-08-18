import asyncio
import argparse
from pathlib import Path
from typing import List, Dict

from dependency_injector.wiring import Provide, inject

from .shared.source import Source, SourceType
from .handlers.base_handler import Handler
from .container import ApplicationContainer
from .shared.signal_stream import SignalStream, StreamData

from .config import load_config

DEFAULT_BATCH_SIZE = 5


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
async def ingest_data_source(
    source: Source,
    handler_mapping: Dict[SourceType, Handler] = Provide[
        ApplicationContainer.handler_mapping
    ],
    signal_stream: SignalStream = Provide[ApplicationContainer.signal_stream],
):
    handler = handler_mapping[source.type]
    stream_data_list: List[StreamData] = await handler.handle(source)
    # TODO: Maybe use a batch writer instead?
    write_stream_tasks = [
        signal_stream.write_stream_data(stream_data)
        for stream_data in stream_data_list
    ]
    await asyncio.gather(*write_stream_tasks)


# @inject
@inject
async def main(
    data_sources: List[Source] = Provide[ApplicationContainer.config.sources],
) -> None:
    tasks = [ingest_data_source(source) for source in data_sources]
    await asyncio.gather(*tasks)


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
