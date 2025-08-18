from concurrent.futures import ProcessPoolExecutor
from typing import Optional


class AsyncProcessPoolExecutor:
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers
        self.executor = None

    async def __aenter__(self):
        self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        return self.executor

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.executor:
            self.executor.shutdown(wait=True)
