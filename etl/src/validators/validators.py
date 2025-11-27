from typing import Dict, Any, List, Set, Tuple
from .base_validator import BaseValidator
import re

class MandatoryValidator(BaseValidator):
    def __init__(self, columns: List[Dict[str, Any]]):
        super().__init__()
        self.mandatory_columns = [col['name'] for col in columns if col.get('mandatory')]

    def validate(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        for col in self.mandatory_columns:
            if col not in record or not str(record[col]).strip():
                errors.append(f"Missing mandatory column: {col}")
        return errors

class DataTypeValidator(BaseValidator):
    def __init__(self, columns: List[Dict[str, Any]]):
        super().__init__()
        self.column_types = {col['name']: col.get('type') for col in columns if col.get('type')}

    def validate(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        for col, type_name in self.column_types.items():
            val = record.get(col)
            if val is None or val == '':
                continue # Skip empty, handled by MandatoryValidator
            
            try:
                if type_name == 'int':
                    int(val)
                elif type_name == 'float':
                    float(val)
                # Add more types as needed
            except ValueError:
                errors.append(f"Invalid type for column {col}: expected {type_name}, got {val}")
        return errors

class LengthValidator(BaseValidator):
    def __init__(self, columns: List[Dict[str, Any]]):
        super().__init__()
        self.column_lengths = {col['name']: col.get('length') for col in columns if col.get('length')}

    def validate(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        for col, length in self.column_lengths.items():
            val = record.get(col)
            if val and len(str(val)) > length:
                errors.append(f"Length exceeded for column {col}: max {length}, got {len(str(val))}")
        return errors

class DuplicateValidator(BaseValidator):
    def __init__(self, unique_constraints: List[List[str]]):
        super().__init__()
        self.unique_constraints = unique_constraints
        self.seen_keys: Dict[Tuple[str, ...], Set[Tuple[Any, ...]]] = {
            tuple(constraint): set() for constraint in unique_constraints
        }

    def validate(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        for constraint in self.unique_constraints:
            key = tuple(record.get(col) for col in constraint)
            constraint_tuple = tuple(constraint)
            if key in self.seen_keys[constraint_tuple]:
                errors.append(f"Duplicate record found for unique constraint {constraint}: {key}")
            else:
                self.seen_keys[constraint_tuple].add(key)
        return errors
