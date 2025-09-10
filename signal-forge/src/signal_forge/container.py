# from dependency_injector import providers
# import httpx
from radar_core import CoreContainer

# from .core.handlers.text_handler import TextHandler
# from .shared.constants import DEFAULT_BATCH_SIZE, SourceType
# from .shared.utils import AsyncProcessPoolExecutor


class ApplicationContainer(CoreContainer):
    # http_client = providers.Resource(httpx.AsyncClient, timeout=30.0)
    # process_executor = providers.Resource(
    #     AsyncProcessPoolExecutor, max_workers=DEFAULT_BATCH_SIZE
    # )
    # text_handler = providers.Factory(
    #     TextHandler, http_client=http_client, process_executor=process_executor
    # )
    # handler_mapping = providers.Dict({SourceType.TXT: text_handler})
    #
    def __init__(self):
        super().__init__()
        self.config.redis_host.from_env("REDIS_HOST")
        self.config.redis_port.from_env("REDIS_PORT")
        self.config.redis_db.from_env("REDIS_DB")
        self.config.service_name.from_value("signal_forge")
