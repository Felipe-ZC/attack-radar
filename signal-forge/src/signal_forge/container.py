from dependency_injector import providers
from radar_core import CoreContainer

from .ipdb import AbuseIPDB


class ApplicationContainer(CoreContainer):
    abuse_ipdb = providers.Factory(
        AbuseIPDB,
        http_client=CoreContainer.http_client,
        logger=CoreContainer.logger,
    )

    def __init__(self):
        super().__init__()
        self.config.redis_host.from_env("REDIS_HOST")
        self.config.redis_port.from_env("REDIS_PORT")
        self.config.redis_db.from_env("REDIS_DB")
        self.config.service_name.from_value("signal_forge")
