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


def get_next_batch(list_data: List, batch_size: int):
    for batch_start in range(0, len(list_data), batch_size):
        yield list_data[batch_start : batch_start + batch_size]


async def async_batch_process_list(
    list_data: List, batch_size: int, process: Callable
):
    for next_batch in get_next_batch(list_data, batch_size):
        tasks = [process(batch_item) for batch_item in next_batch]
        for completed_task in asyncio.as_completed(tasks):
            yield await completed_task
