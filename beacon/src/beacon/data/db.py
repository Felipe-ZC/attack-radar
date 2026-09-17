import logging

import asyncpg

from beacon.data.models import AbuseReport, HostMetadata
from beacon.shared.config import settings

logger = logging.getLogger(__name__)

PoolOrConnection = asyncpg.Pool | asyncpg.Connection


async def create_pool() -> asyncpg.Pool:
    logger.info(
        "Creating connection pool to %s:%s/%s",
        settings.POSTGRES_HOST,
        settings.POSTGRES_PORT,
        settings.POSTGRES_DB,
    )
    pool = await asyncpg.create_pool(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
    )
    logger.info(
        "Connection pool to %s:%s/%s created",
        settings.POSTGRES_HOST,
        settings.POSTGRES_PORT,
        settings.POSTGRES_DB,
    )

    return pool


async def upsert_host_metadata(
    conn: PoolOrConnection, metadata: HostMetadata
) -> None:
    await conn.execute(
        """
        INSERT INTO host_metadata
            (ip_address, country_code, country_name, usage_type, domain, isp, lat, lon)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (ip_address) DO UPDATE SET
            country_code = EXCLUDED.country_code,
            country_name = EXCLUDED.country_name,
            usage_type = EXCLUDED.usage_type,
            domain = EXCLUDED.domain,
            isp = EXCLUDED.isp,
            lat = EXCLUDED.lat,
            lon = EXCLUDED.lon
        """,
        metadata.ip_address,
        metadata.country_code,
        metadata.country_name,
        metadata.usage_type,
        metadata.domain,
        metadata.isp,
        metadata.lat,
        metadata.lon,
    )


async def insert_abuse_reports(
    conn: PoolOrConnection, reports: list[AbuseReport]
) -> None:
    if not reports:
        return

    await conn.executemany(
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


async def write_signal_data(
    pool: asyncpg.Pool,
    metadata: HostMetadata,
    reports: list[AbuseReport],
) -> None:
    async with pool.acquire() as conn:
        async with conn.transaction():
            await upsert_host_metadata(conn, metadata)
            await insert_abuse_reports(conn, reports)
