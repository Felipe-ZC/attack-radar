from abc import ABC, abstractmethod
from typing import List

from radar_core.models import StreamData


class Handler(ABC):
    @abstractmethod
    def handle(self, url: str) -> List[StreamData]:
        pass
