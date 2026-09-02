import logging
import os

import asyncpg

from beacon.data.models import AbuseReport, HostMetadata

logger = logging.getLogger(__name__)

PoolOrConnection = asyncpg.Pool | asyncpg.Connection


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
