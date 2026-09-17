import logging

import asyncpg

from beacon.data.models import AbuseReport, HostMetadata

PoolOrConnection = asyncpg.Pool | asyncpg.Connection


class DBClient:
    """Owns the asyncpg connection pool and beacon's DB write operations.

    Supports ``async with`` so it can be wired into a FastAPI lifespan:

        async with DBClient(...) as db_client:
            app.state.db = db_client
            yield
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        logger: logging.Logger | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._logger = logger or logging.getLogger(__name__)
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self._logger.info(
            "Creating connection pool to %s:%s/%s", self.host, self.port, self.database
        )
        self.pool = await asyncpg.create_pool(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port,
        )
        self._logger.info(
            "Connection pool to %s:%s/%s created", self.host, self.port, self.database
        )

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()

    async def __aenter__(self) -> "DBClient":
        await self.connect()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.disconnect()

    async def _upsert_host_metadata(
        self, conn: PoolOrConnection, metadata: HostMetadata
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

    async def _insert_abuse_reports(
        self, conn: PoolOrConnection, reports: list[AbuseReport]
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
        self, metadata: HostMetadata, reports: list[AbuseReport]
    ) -> None:
        if not self.pool:
            self._logger.error("Database pool is not initialized.")
            raise RuntimeError("Database pool is not initialized.")

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await self._upsert_host_metadata(conn, metadata)
                await self._insert_abuse_reports(conn, reports)
