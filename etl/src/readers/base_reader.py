from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any

class BaseReader(ABC):
    def __init__(self, file_path: str, config: Dict[str, Any]):
        self.file_path = file_path
        self.config = config

    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Yields records as dictionaries."""
        pass

    @abstractmethod
    def close(self):
        """Closes any open file handles."""
        pass
