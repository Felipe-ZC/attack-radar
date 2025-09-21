from dependency_injector import providers
from radar_core import AsyncDuckDb, AsyncThreadPoolExecutor, CoreContainer

from .core.ipdb import AbuseIPDB

DEFAULT_MAX_WORKERS = 5


class ApplicationContainer(CoreContainer):
    config = providers.Configuration()

    abuse_ipdb = providers.Factory(
        AbuseIPDB,
        http_client=CoreContainer.http_client,
        logger=CoreContainer.logger,
    )
    async_thread_pool = providers.Resource(
        AsyncThreadPoolExecutor,
        max_workers=config.max_workers or DEFAULT_MAX_WORKERS,
    )
    async_duck_db = providers.Resource(
        AsyncDuckDb,
        db_path=config.duck_db_path,
        thread_pool_exectuor=async_thread_pool,
    )

    def __init__(self):
        super().__init__()
        self.config.redis_host.from_env("REDIS_HOST")
        self.config.redis_port.from_env("REDIS_PORT")
        self.config.redis_db.from_env("REDIS_DB")
        self.config.service_name.from_value("signal_forge")
