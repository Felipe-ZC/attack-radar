import asyncio
import logging
import os
import re

import asyncpg
import db
import httpx
import yaml

# Configuration
IPDB_API_KEY = os.getenv("IPDB_API_KEY")
IP_REGEX = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
DEFAULT_DATA_SOURCES_PATH = "./data/data_sources.yaml"

logger = logging.getLogger(__name__)


# Data Ingestion
async def fetch_ips_from_url(url: str) -> list[str]:
    logger.info("Fetching IPs from %s", url)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return list(set(re.findall(IP_REGEX, response.text)))


async def ingest_sources(sources: list[dict], pool: asyncpg.Pool):
    for source in sources:
        ips = await fetch_ips_from_url(source["url"])
        for ip in ips:
            await process_signal(ip, source["url"], pool)


# Data Processing
async def check_ip_abuse(ip: str, http_client: httpx.AsyncClient):
    logger.info("Checking abuse status for %s", ip)
    try:
        response = await http_client.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90, "verbose": ""},
            headers={"key": IPDB_API_KEY or ""},
        )
        return response.json()
    except httpx.ReadTimeout:
        logger.error(
            "Error while fetching abuse reports for host with IP %s", ip
        )
        return None


async def process_signal(ip_addr: str, source: str, pool: asyncpg.Pool):
    logger.info("Processing signal for %s from %s", ip_addr, source)

    async with httpx.AsyncClient(timeout=30) as http:
        abuse_data = await check_ip_abuse(ip_addr, http)

    await db.write_signal_data(pool, abuse_data)


async def main(config_file: str = ""):
    logger.info("Loading sources...")

    with open(config_file) as f:
        sources = yaml.safe_load(f)["sources"]

    logger.info("Creating connection pool...")
    pool = await db.create_pool()
    try:
        await ingest_sources(sources, pool)
    finally:
        await pool.close()


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        main(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DATA_SOURCES_PATH)
    )
