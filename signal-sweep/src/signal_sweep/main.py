import asyncio
import argparse
from pathlib import Path
from typing import List

import httpx

from .shared.source import Source
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


async def main(data_sources: List[Source]):
    # Process data_source...
    for idx in range(len(data_sources)):
        next_data_sources = data_sources[idx : idx + DEFAULT_BATCH_SIZE]
        tasks = [
            data_source.handler(httpx.AsyncClient).handle(data_source.url)
            for data_source in next_data_sources
        ]
        for coro in asyncio.as_completed(tasks):
            stream_data: List[StreamData] = await coro
            # write_stream_data to signal-stream...
        # await asyncio.gather(*tasks)


if __name__ == "__main__":
    config_file_path: Path = get_config_file_path()
    data_sources: List[Source] = load_config(config_file_path)
    asyncio.run(main(data_sources))
