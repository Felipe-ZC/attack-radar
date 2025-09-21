from pathlib import Path

import duckdb
import pandas as pd

from .utils import AsyncThreadPoolExecutor


class AsyncDuckDb:
    def __init__(
        self, db_path: Path, thread_pool_exectuor: AsyncThreadPoolExecutor
    ):
        self.db_path = db_path.resolve()
        self.async_exectuor = thread_pool_exectuor
        self.conn = None

    async def __aenter__(self):
        self.conn = await self.async_exectuor.submit(
            duckdb.connect, self.db_path
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "conn") and self.conn:
            await self.async_exectuor.submit(self.conn.close)

    async def register_dataframe(self, name: str, dataframe: pd.DataFrame):
        return await self.async_exectuor.submit(
            self.conn.register, name, dataframe
        )

    async def execute_query(self, query: str, params: list[any] = ()):
        args = (query, params) if params else (query,)
        return await self.async_exectuor.submit(self.conn.execute, *args)

    async def bulk_insert_from_dataframe(
        self,
        table_name: str,
        df_name: str,
        df: pd.DataFrame,
        has_primary_key: bool = False,
    ):
        await self.async_exectuor.submit(self.conn.register, df_name, df)
        query = f"INSERT {"OR IGNORE" if has_primary_key else ""} INTO {table_name} SELECT * FROM {df_name}"
        return await self.execute_query(query)
