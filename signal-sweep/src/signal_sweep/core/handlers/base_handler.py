from abc import ABC, abstractmethod

from radar_core.models import StreamData


class Handler(ABC):
    @abstractmethod
    def handle(self, url: str) -> list[StreamData]:
        pass
