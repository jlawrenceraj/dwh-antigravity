import pandas as pd
from typing import List, Dict, Any
from .base_validator import BaseValidator
from .validators import DuplicateRowValidator, DataTypeValidator, LengthValidator

class FileValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validators = self._initialize_validators()

    def _initialize_validators(self) -> List[BaseValidator]:
        validators = []
        validator_configs = self.config.get('validators', [])
        
        for v_conf in validator_configs:
            v_type = v_conf.get('type')
            if v_type == 'duplicate':
                validators.append(DuplicateRowValidator(v_conf['columns']))
            elif v_type == 'datatype':
                validators.append(DataTypeValidator(v_conf['columns']))
            elif v_type == 'length':
                validators.append(LengthValidator(v_conf['columns']))
            else:
                print(f"Warning: Unknown validator type '{v_type}'")
        
        return validators

    def validate_file(self, file_path: str) -> List[str]:
        try:
            # Read CSV
            # Using dtype=str to preserve original format for validation (e.g. leading zeros, etc)
            # But for DataType validation we might want to infer, or handle inside validator.
            # Let's read as default and let validators handle types, or read as object.
            # Reading as object is safer for length validation.
            df = pd.read_csv(file_path)
        except Exception as e:
            return [f"Error reading file {file_path}: {str(e)}"]

        all_errors = []
        for validator in self.validators:
            try:
                errors = validator.validate(df)
                all_errors.extend(errors)
            except Exception as e:
                all_errors.append(f"Validator {type(validator).__name__} failed: {str(e)}")
        
        return all_errors
