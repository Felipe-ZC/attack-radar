import asyncio
import argparse
from pathlib import Path
from typing import List

import httpx

from .shared.source import Source
from .shared.signal_stream import StreamData, SignalStream, get_redis_client
from .shared.constants import SOURCE_TYPE_TO_HANDLER_DICT
from .shared.utils import AsyncProcessPoolExecutor
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


# TODO: Inject httpx async client as a dependency...
# TODO: Maybe we can setup context managers for the SignalStream & Async HTTP Client services...
async def main(
    data_sources: List[Source],
    http_client: httpx.AsyncClient,
    process_executor: AsyncProcessPoolExecutor,
    signal_stream: SignalStream,
) -> None:
    # Process data_source...
    for idx in range(0, len(data_sources), DEFAULT_BATCH_SIZE):
        next_data_sources = data_sources[idx : idx + DEFAULT_BATCH_SIZE]
        handlers = [
            SOURCE_TYPE_TO_HANDLER_DICT[data_source.type]
            for data_source in next_data_sources
        ]
        tasks = [
            handler(data_source, http_client, process_executor).handle()
            for data_source, handler in zip(next_data_sources, handlers)
        ]
        for coro in asyncio.as_completed(tasks):
            stream_data_list: List[StreamData] = await coro
            write_stream_tasks = [
                signal_stream.write_stream_data(stream_data)
                for stream_data in stream_data_list
            ]
            await asyncio.gather(*write_stream_tasks)


async def bootstrap() -> None:
    config_file_path: Path = get_config_file_path()
    data_sources: List[Source] = load_config(config_file_path)

    async with (
        httpx.AsyncClient() as http_client,
        get_redis_client() as redis_client,
        AsyncProcessPoolExecutor(max_workers=2) as process_executor,
    ):
        print(redis_client)
        signal_stream = SignalStream(redis_client)
        await main(data_sources, http_client, process_executor, signal_stream)


if __name__ == "__main__":
    asyncio.run(bootstrap())
