"""
The default handler for txt files.
This handler tries to find strings that look like IPV4 addresses in a txt file.
"""

from concurrent.futures import ProcessPoolExecutor
import asyncio
import re

import httpx

from radar_core.models import StreamData

from .base_handler import Handler
from ..models import Source
from ...shared.constants import IP_V4_REGEX


class TextHandler(Handler):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        process_executor: ProcessPoolExecutor,
    ):
        self.http_client = http_client
        self.process_executor = process_executor

    async def handle(self, data_source: Source):
        response = await self.http_client.get(data_source.url)
        parsed = await asyncio.get_event_loop().run_in_executor(
            self.process_executor, _parse_text, response.text
        )
        return [
            StreamData(
                ip=ip,
                source_url=data_source.url,
            )
            for ip in parsed
        ]


def _parse_text(raw_text: str):
    return list(dict.fromkeys(re.findall(IP_V4_REGEX, raw_text)))
