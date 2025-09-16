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
            duckdb.connect, self.database_path
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "conn") and self.conn:
            await self.async_exectuor.submit(self.conn.close)

    async def execute_query(self, query: str, params: tuple[any] = ()):
        args = (
            query,
            params if params else query,
        )
        return await self.async_exectuor.submit(self.conn.execute, args)

    async def load_from_dataframe(self, dataframe: pd.DataFrame):
        pass
