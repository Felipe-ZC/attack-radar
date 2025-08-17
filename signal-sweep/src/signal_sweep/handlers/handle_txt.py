"""
The default handler for txt files.
This handler tries to find strings that look like IPV4 addresses in a txt file.
"""

from typing import List
import time
import re
import httpx

from .base_handler import BaseHandler
from ..shared.redis_stream import StreamData

IP_V4_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"


class TextHandler(BaseHandler):
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def handle(self, url: str) -> List[StreamData]:
        async with self.http_client() as client:
            response = await client.get(url)
        parsed = _parse_text(response.text)
        print(parsed)
        return [
            StreamData(ip=ip, source_url=url, timestamp=int(time.time()))
            for ip in parsed
        ]


# TODO: Regex parsing is a CPU intensive task, I don't know how big these text files can get but
# we should run this _parse_text function in a ProcessPoolExecutor to avoid blocking other async calls
def _parse_text(raw_text: str):
    return list(dict.fromkeys(re.findall(IP_V4_REGEX, raw_text)))
