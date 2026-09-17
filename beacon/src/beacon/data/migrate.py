import argparse
import asyncio
import logging
from pathlib import Path

import asyncpg

from beacon.shared.config import settings

logger = logging.getLogger(__name__)

_BOOTSTRAP_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version    TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def discover_migrations(migrations_dir: Path) -> list[Path]:
    return sorted(migrations_dir.glob("*.sql"), key=lambda p: p.name)


async def get_applied_versions(conn: asyncpg.Connection) -> set[str]:
    rows = await conn.fetch("SELECT version FROM schema_migrations")
    return {row["version"] for row in rows}


async def apply_migration(conn: asyncpg.Connection, path: Path) -> None:
    version = path.stem
    sql_text = path.read_text()
    async with conn.transaction():
        await conn.execute(sql_text)
        await conn.execute(
            "INSERT INTO schema_migrations (version) VALUES ($1)", version
        )
    logger.info("Applied migration %s", version)


async def run_migrations(migrations_dir: Path) -> None:
    conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
    )
    try:
        await conn.execute(_BOOTSTRAP_SQL)
        applied = await get_applied_versions(conn)
        pending = [
            p for p in discover_migrations(migrations_dir) if p.stem not in applied
        ]
        if not pending:
            logger.info("No pending migrations. Database is up to date.")
            return
        for path in pending:
            await apply_migration(conn, path)
        logger.info("Applied %d migration(s).", len(pending))
    finally:
        await conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply pending SQL migrations.")
    parser.add_argument(
        "--migrations-dir",
        type=Path,
        default=Path("../docker/migrations"),
        help=(
            "Path to the directory of numbered .sql migration files "
            "(default assumes cwd=beacon/, matching `uv run migrate`)."
        ),
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    if not args.migrations_dir.is_dir():
        raise SystemExit(f"Migrations directory not found: {args.migrations_dir}")
    asyncio.run(run_migrations(args.migrations_dir))


if __name__ == "__main__":
    main()
