from abc import ABC, abstractmethod
from typing import List

from ..shared.redis_stream import StreamData


class BaseHandler(ABC):

    @abstractmethod
    def handle(self, url: str) -> List[StreamData]:
        pass

    def write_stream_data(self, stream_data: List[StreamData]):
        pass
