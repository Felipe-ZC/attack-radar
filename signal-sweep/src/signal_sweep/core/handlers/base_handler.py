from abc import ABC, abstractmethod
from typing import List

from ..models import StreamData


class Handler(ABC):
    @abstractmethod
    def handle(self, url: str) -> List[StreamData]:
        pass
