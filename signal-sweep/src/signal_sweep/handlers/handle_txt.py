"""
The default handler for txt files.
This handler tries to find strings that look like IPV4 addresses in a txt file.
"""

from concurrent.futures import ProcessPoolExecutor
from typing import List
import asyncio
import time
import re

import httpx

from .base_handler import BaseHandler
from ..shared.signal_stream import StreamData
from ..shared.source import Source

IP_V4_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

"""
NOTE: Data Sources are not necessarily just URLs, they could also be a path to some file.
We should handle this data by separating the data fetching & processing protions of the handle function.
Create an abstraction for fetching the data, this fetch function can look at the type of data and choose 
the correct function from there
"""

"""
We could use a fetch function 
process(fetch(source.url))
"""


class TextHandler(BaseHandler):
    def __init__(
        self,
        data_source: Source,
        http_client: httpx.AsyncClient,
        process_executor: ProcessPoolExecutor,
    ):
        self.http_client = http_client
        self.process_executor = process_executor
        self.data_source = data_source

    async def handle(self):
        return await self.process(await self.fetch(self.data_source.url))

    async def fetch(self, url: str):
        response = await self.http_client.get(url)
        return response.text

    async def process(self, raw_text: str) -> List[StreamData]:
        parsed = await asyncio.get_event_loop().run_in_executor(
            self.process_executor, _parse_text, raw_text
        )
        print(parsed)
        return [
            StreamData(
                ip=ip,
                source_url=self.data_source.url,
                timestamp=int(time.time()),
            )
            for ip in parsed
        ]

    # async def handle(self, url: str) -> List[StreamData]:
    #     async with self.http_client() as client:
    #         response = await client.get(url)
    #     parsed = _parse_text(response.text)
    #     print(parsed)
    #     return [
    #         StreamData(ip=ip, source_url=url, timestamp=int(time.time()))
    #         for ip in parsed
    #     ]
    #


# TODO: Regex parsing is a CPU intensive task, I don't know how big these text files can get but
# we should run this _parse_text function in a ProcessPoolExecutor to avoid blocking other async calls
def _parse_text(raw_text: str):
    return list(dict.fromkeys(re.findall(IP_V4_REGEX, raw_text)))
