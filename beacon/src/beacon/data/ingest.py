import asyncio
import logging
from pathlib import Path
import re

import geoip2.database
import geoip2.errors
import httpx
import yaml

from beacon.data import db
from beacon.data.models import AbuseReport, HostMetadata
from beacon.shared.config import settings

# Configuration
IP_REGEX = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
IP_GEOLOCATION_API_BASE_URL = "https://ipwho.is"
DEFAULT_DATA_SOURCES_PATH = "./data_sources.yaml"
GEOLITE_DB_PATH = Path(__file__).parent / "GeoLite2-City.mmdb"

logger = logging.getLogger(__name__)

# Expensive to construct, so build it once and reuse across lookups.
_geoip_reader = geoip2.database.Reader(GEOLITE_DB_PATH)


# Data Ingestion
def handle_json_response(response: httpx.Response, source: dict) -> list[str]:
    try:
        data = response.json()
        if source.get("json_key"):
            data = data.get(source["json_key"], [])
        if source.get("json_array_key"):
            data = [item.get(source["json_array_key"]) for item in data]
        return list(set(data))
    except ValueError as e:
        logger.error(
            "Failed to parse JSON response from %s: %s", source["url"], e
        )
        return []


async def fetch_ips_from_url(
    source: dict, http_client: httpx.AsyncClient
) -> list[str]:
    logger.info("Fetching IPs from %s", source["url"])
    response = await http_client.get(source["url"], headers=source["headers"])
    if source.get("type") == "json":
        return handle_json_response(response, source)
    return list(set(re.findall(IP_REGEX, response.text)))


async def ingest_sources(sources: list[dict], db_client: db.DBClient):
    async with httpx.AsyncClient(timeout=30) as http:
        for source in sources:
            ips = await fetch_ips_from_url(source, http)
            for ip in ips:
                await process_signal(ip, source["url"], db_client, http)


# Data Processing
async def check_ip_abuse(ip: str, http_client: httpx.AsyncClient):
    logger.info("Checking abuse status for %s", ip)
    try:
        response = await http_client.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90, "verbose": ""},
            headers={"key": settings.IPDB_API_KEY},
        )
        return response.json()
    except httpx.ReadTimeout:
        logger.error(
            "Error while fetching abuse reports for host with IP %s", ip
        )
        return {}


def geolocate(ip: str) -> tuple[float | None, float | None] | None:
    logger.info("Geolocating IP %s", ip)
    try:
        result = _geoip_reader.city(ip)
    except geoip2.errors.AddressNotFoundError:
        logger.error("Failed to geolocate IP %s: address not found", ip)
        return None
    return result.location.latitude, result.location.longitude


def parse_abuse_response(
    payload: dict,
    geolocation: tuple[float | None, float | None] | None = None,
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
    db_client: db.DBClient,
    http_client: httpx.AsyncClient,
):
    logger.info("Processing signal for %s from %s", ip_addr, source)

    abuse_data = await check_ip_abuse(ip_addr, http_client)
    geolocation = geolocate(ip_addr)

    metadata, reports = parse_abuse_response(abuse_data, geolocation)
    if metadata is None:
        return

    await db_client.write_signal_data(metadata, reports)


async def ingest(sources: list[dict]):
    async with db.DBClient(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    ) as db_client:
        await ingest_sources(sources, db_client)


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Loading sources...")

    with open(settings.DATA_SOURCES_PATH) as f:
        sources = yaml.safe_load(f)["sources"]

    asyncio.run(ingest(sources))
