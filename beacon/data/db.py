from dataclasses import dataclass
from datetime import datetime
import logging
import os

import asyncpg

logger = logging.getLogger(__name__)


@dataclass
class HostMetadata:
    ip_address: str
    country_code: str | None
    country_name: str | None
    usage_type: str | None
    domain: str | None
    isp: str | None


@dataclass
class AbuseReport:
    ip_address: str
    report_timestamp: datetime
    report_comment: str | None
    report_categories: list[int]


def parse_abuse_response(
    payload: dict,
) -> tuple[HostMetadata | None, list[AbuseReport]]:
    data = payload.get("data")
    if not data:
        logger.warning("AbuseIPDB response has no 'data' field: %s", payload)
        return None, []

    ip_address = data["ipAddress"]

    metadata = HostMetadata(
        ip_address=ip_address,
        country_code=data.get("countryCode"),
        country_name=data.get("countryName"),
        usage_type=data.get("usageType"),
        domain=data.get("domain"),
        isp=data.get("isp"),
    )

    reports = [
        AbuseReport(
            ip_address=ip_address,
            report_timestamp=datetime.fromisoformat(report["reportedAt"]),
            report_comment=report.get("comment"),
            report_categories=report.get("categories", []),
        )
        for report in data.get("reports", [])
    ]

    return metadata, reports


async def create_pool() -> asyncpg.Pool:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    database = os.getenv("POSTGRES_DB")

    logger.info("Creating connection pool to %s:%s/%s", host, port, database)
    pool = await asyncpg.create_pool(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=database,
        host=host,
        port=port,
    )
    logger.info("Connection pool to %s:%s/%s created", host, port, database)

    return pool


async def upsert_host_metadata(
    pool: asyncpg.Pool, metadata: HostMetadata
) -> None:
    await pool.execute(
        """
        INSERT INTO host_metadata
            (ip_address, country_code, country_name, usage_type, domain, isp)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (ip_address) DO UPDATE SET
            country_code = EXCLUDED.country_code,
            country_name = EXCLUDED.country_name,
            usage_type = EXCLUDED.usage_type,
            domain = EXCLUDED.domain,
            isp = EXCLUDED.isp
        """,
        metadata.ip_address,
        metadata.country_code,
        metadata.country_name,
        metadata.usage_type,
        metadata.domain,
        metadata.isp,
    )


async def insert_abuse_reports(
    pool: asyncpg.Pool, reports: list[AbuseReport]
) -> None:
    if not reports:
        return

    await pool.executemany(
        """
        INSERT INTO abuse_ipdb_reports
            (ip_address, report_timestamp, report_comment, report_categories)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (ip_address, report_timestamp) DO NOTHING
        """,
        [
            (
                report.ip_address,
                report.report_timestamp,
                report.report_comment,
                report.report_categories,
            )
            for report in reports
        ],
    )


async def write_signal_data(pool: asyncpg.Pool, payload: dict) -> None:
    metadata, reports = parse_abuse_response(payload)
    if metadata is None:
        return

    await upsert_host_metadata(pool, metadata)
    await insert_abuse_reports(pool, reports)
