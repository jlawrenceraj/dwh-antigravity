from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseValidator(ABC):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def validate(self, record: Dict[str, Any]) -> List[str]:
        """
        Validates a single record.
        Returns a list of error messages.
        """
        pass
