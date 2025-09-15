from logging import Logger
import os

import httpx

API_URL = "https://api.abuseipdb.com/api/v2/check"


class AbuseIPDB:
    def __init__(self, http_client: httpx.AsyncClient, logger: Logger):
        self.http_client = http_client
        self.logger = logger

    async def check(
        self, ip: str, api_key: str = os.getenv("IPDB_API_KEY", "")
    ) -> dict:
        response = await self.http_client.get(
            API_URL,
            params={"ipAddress": ip, "maxAgeInDays": 90, "verbose": ""},
            headers={"key": api_key},
        )
        return response.json()
