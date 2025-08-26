from dependency_injector import providers

import httpx

from radar_core import CoreContainer
from radar_core.models import SourceType

from .config import load_config, get_config_file_path
from .core.handlers import TextHandler
from .shared.utils import AsyncProcessPoolExecutor
from .shared.constants import DEFAULT_BATCH_SIZE


class ApplicationContainer(CoreContainer):
    def __init__(self):
        super().__init__()

        self.config.redis_host.from_env("REDIS_HOST")
        self.config.redis_port.from_env("REDIS_PORT")
        self.config.redis_db.from_env("REDIS_DB")

        self.config.max_workers.from_value(DEFAULT_BATCH_SIZE)
        self.config.sources.from_value(load_config(get_config_file_path()))

        self.config.service_name.from_value("signal_sweep")
        self.http_client = providers.Resource(httpx.AsyncClient, timeout=30.0)
        self.process_executor = providers.Resource(
            AsyncProcessPoolExecutor, max_workers=self.config.max_workers
        )

        # Services
        self.text_handler = providers.Factory(
            TextHandler, http_client=self.http_client, process_executor=self.process_executor
        )

        # Utilities
        self.handler_mapping = providers.Dict({SourceType.TXT: self.text_handler})

