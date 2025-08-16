import asyncio
import argparse
from pathlib import Path
from typing import List
from .config import load_config, Source


def get_config_file_path() -> Path:
    parser = argparse.ArgumentParser(description="The data ingestion service for attack-radar")
    parser.add_argument("--config", help="The path to the data_sources.yml file", required=True)
    args = parser.parse_args()
    return Path(args.config)


async def main(data_sources: List[Source]):
    print(data_sources)


if __name__ == "__main__":
    config_file_path: Path = get_config_file_path()
    data_sources: List[Source] = load_config(config_file_path)
    asyncio.run(main(data_sources))
