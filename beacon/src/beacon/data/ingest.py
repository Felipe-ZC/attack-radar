import asyncio
import logging
import os
import re
import sys

import asyncpg
import httpx
import yaml

from beacon.data import db
from beacon.data.models import AbuseReport, HostMetadata

# Configuration
IPDB_API_KEY = os.getenv("IPDB_API_KEY")
IP_REGEX = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
DEFAULT_DATA_SOURCES_PATH = "./data_sources.yaml"
IP_GEOLOCATION_API_BASE_URL = "https://ipwho.is"

logger = logging.getLogger(__name__)


# Data Ingestion
async def fetch_ips_from_url(
    url: str, http_client: httpx.AsyncClient
) -> list[str]:
    logger.info("Fetching IPs from %s", url)
    response = await http_client.get(url)
    return list(set(re.findall(IP_REGEX, response.text)))


async def ingest_sources(sources: list[dict], pool: asyncpg.Pool):
    async with httpx.AsyncClient(timeout=30) as http:
        for source in sources:
            ips = await fetch_ips_from_url(source["url"], http)
            for ip in ips:
                await process_signal(ip, source["url"], pool, http)


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
        return {}


async def geolocate(
    ip: str, http_client: httpx.AsyncClient
) -> tuple[float, float] | None:
    logger.info("Geoloacting IP %s", ip)
    response = await http_client.get(f"{IP_GEOLOCATION_API_BASE_URL}/{ip}")
    data = response.json()
    if data.get("success"):
        return data.get("latitude"), data.get("longitude")
    else:
        logger.error("Failed to geolocate IP %s: %s", ip, data.get("message"))
        return None


def parse_abuse_response(
    payload: dict,
    geolocation: tuple[float, float] | None = None,
) -> tuple[HostMetadata | None, list[AbuseReport]]:
    data = payload.get("data")
    if not data:
        logger.warning("AbuseIPDB response has no 'data' field: %s", payload)
        return None, []

    ip_address = data["ipAddress"]
    lat, lon = geolocation if geolocation else (None, None)

    metadata = HostMetadata(
        ip_address=ip_address,
        country_code=data.get("countryCode"),
        country_name=data.get("countryName"),
        usage_type=data.get("usageType"),
        domain=data.get("domain"),
        isp=data.get("isp"),
        lat=lat,
        lon=lon,
    )

    reports = [
        AbuseReport(
            ip_address=ip_address,
            report_timestamp=report["reportedAt"],
            report_comment=report.get("comment"),
            report_categories=report.get("categories", []),
        )
        for report in data.get("reports", [])
    ]

    return metadata, reports


async def process_signal(
    ip_addr: str,
    source: str,
    pool: asyncpg.Pool,
    http_client: httpx.AsyncClient,
):
    logger.info("Processing signal for %s from %s", ip_addr, source)

    abuse_data = await check_ip_abuse(ip_addr, http_client)
    geolocation = await geolocate(ip_addr, http_client)

    metadata, reports = parse_abuse_response(abuse_data, geolocation)
    if metadata is None:
        return

    await db.write_signal_data(pool, metadata, reports)


async def ingest(sources: list[dict]):
    logger.info("Creating connection pool...")
    pool = await db.create_pool()
    try:
        await ingest_sources(sources, pool)
    finally:
        await pool.close()


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Loading sources...")

    config_file = os.getenv("DATA_SOURCES_PATH", DEFAULT_DATA_SOURCES_PATH)

    with open(config_file) as f:
        sources = yaml.safe_load(f)["sources"]

    asyncio.run(ingest(sources))
