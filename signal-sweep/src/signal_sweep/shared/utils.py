import asyncio

from concurrent.futures import ProcessPoolExecutor
from typing import Optional, List, Callable


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


async def async_batch_process_list(
    list_data: List, batch_size: int, process: Callable
):
    results = []
    for i in range(0, len(list_data), batch_size):
        tasks = [
            process(batch_item) for batch_item in list_data[i : i + batch_size]
        ]
        results.extend(await asyncio.gather(*tasks))
    return results
