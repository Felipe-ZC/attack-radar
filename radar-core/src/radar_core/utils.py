import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from enum import Enum
from functools import partial
from typing import Any, Callable, Optional, Union


class PoolType(Enum):
    THREAD = "ThreadPoolExecutor"
    PROCESS = "ProcessPoolExecutor"


def create_executor(
    pool_type: PoolType, max_workers: int
) -> Union[ThreadPoolExecutor, ProcessPoolExecutor]:
    pool_type_dict = {
        PoolType.THREAD: ThreadPoolExecutor,
        PoolType.PROCESS: ProcessPoolExecutor,
    }
    return pool_type_dict[pool_type](max_workers=max_workers)


class AsyncPoolExecutor:
    def __init__(self, pool_type: PoolType, max_workers: Optional[int] = None):
        self.max_workers = max_workers
        self.pool_type = pool_type
        self.executor = None

    async def __aenter__(self):
        self.executor = create_executor(
            self.pool_type, max_workers=self.max_workers
        )
        return self

    # TODO: Implement graceful shutdown...
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.executor:
            self.executor.shutdown(wait=False)

    async def submit(self, func: Callable, *args, **kwargs) -> Any:
        """Submit a function to run in the thread pool"""
        if not self.executor:
            raise RuntimeError("Executor not initialized!")
        loop = asyncio.get_event_loop()
        if kwargs:
            func = partial(func, **kwargs)
        return await loop.run_in_executor(self.executor, func, *args)


class AsyncThreadPoolExecutor(AsyncPoolExecutor):
    def __init__(self, max_workers: Optional[int] = None):
        super().__init__(PoolType.THREAD, max_workers)


# class AsyncProcessPoolExecutor(AsyncPoolExecutor):
#     def __init__(self, max_workers: Optional[int] = None):
#         super().__init__(PoolType.PROCESS, max_workers)
