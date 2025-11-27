from abc import ABC, abstractmethod
import pandas as pd
from typing import List

class BaseValidator(ABC):
    """
    Abstract base class for all validators.
    """
    
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> List[str]:
        """
        Validates the given DataFrame and returns a list of error messages.
        
        Args:
            df: The pandas DataFrame to validate.
            
        Returns:
            A list of strings, where each string is an error message.
            Returns an empty list if validation passes.
        """
        pass
