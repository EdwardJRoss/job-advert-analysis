from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractDatasource(ABC):
    name: str = ""

    @abstractmethod
    def extract(self, html: bytes, uri: str, view_date: str) -> List[Dict[Any, Any]]:
        pass

    @abstractmethod
    def normalise(self, *args, **kwargs) -> Dict[str, Any]:
        pass
