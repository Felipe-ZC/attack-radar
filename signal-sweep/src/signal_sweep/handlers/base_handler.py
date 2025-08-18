from abc import ABC, abstractmethod
from typing import List

from ..shared.signal_stream import StreamData


class BaseHandler(ABC):

    @abstractmethod
    def handle(self, url: str) -> List[StreamData]:
        pass

    @abstractmethod
    def fetch(self, url: str) -> List[StreamData]:
        pass

    @abstractmethod
    def process(self, url: str) -> List[StreamData]:
        pass
