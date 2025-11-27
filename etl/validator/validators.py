from typing import List, Dict, Union
import pandas as pd
from .base_validator import BaseValidator

class DuplicateRowValidator(BaseValidator):
    def __init__(self, columns: List[str]):
        self.columns = columns

    def validate(self, df: pd.DataFrame) -> List[str]:
        errors = []
        # Check if columns exist
        missing_cols = [col for col in self.columns if col not in df.columns]
        if missing_cols:
            errors.append(f"DuplicateRowValidator: Missing columns for validation: {missing_cols}")
            return errors

        duplicates = df[df.duplicated(subset=self.columns, keep=False)]
        if not duplicates.empty:
            # Group by the columns to show which combinations are duplicated
            dup_groups = duplicates.groupby(self.columns).size()
            # Filter for those with count > 1 (though keep=False already does this, this is for reporting)
            dup_groups = dup_groups[dup_groups > 1]
            
            for index, count in dup_groups.items():
                 errors.append(f"Duplicate rows found for key {dict(zip(self.columns, index if isinstance(index, tuple) else [index]))}: {count} occurrences")
        
        return errors

class DataTypeValidator(BaseValidator):
    def __init__(self, columns: Dict[str, str]):
        self.columns = columns

    def validate(self, df: pd.DataFrame) -> List[str]:
        errors = []
        for col, expected_type in self.columns.items():
            if col not in df.columns:
                errors.append(f"DataTypeValidator: Column '{col}' not found.")
                continue
            
            if expected_type == 'int':
                # Check if can be converted to numeric and has no non-integer values
                # We use pd.to_numeric with errors='coerce' to find non-numerics
                non_numeric = pd.to_numeric(df[col], errors='coerce').isna() & df[col].notna()
                if non_numeric.any():
                    bad_indices = df.index[non_numeric].tolist()
                    errors.append(f"DataTypeValidator: Column '{col}' contains non-integer values at indices {bad_indices[:5]}...")
                
                # Also check if they are floats that are not integers (e.g. 1.5)
                # This is a bit stricter. If the CSV loads as object or float, we need to check.
                # If it's already int64, it's fine.
                if pd.api.types.is_float_dtype(df[col]):
                     non_integers = df[col] % 1 != 0
                     if non_integers.any():
                         bad_indices = df.index[non_integers].tolist()
                         errors.append(f"DataTypeValidator: Column '{col}' contains non-integer float values at indices {bad_indices[:5]}...")

            elif expected_type == 'float':
                non_numeric = pd.to_numeric(df[col], errors='coerce').isna() & df[col].notna()
                if non_numeric.any():
                     bad_indices = df.index[non_numeric].tolist()
                     errors.append(f"DataTypeValidator: Column '{col}' contains non-float values at indices {bad_indices[:5]}...")
            
            # Add more types as needed

        return errors

class LengthValidator(BaseValidator):
    def __init__(self, columns: Dict[str, int]):
        self.columns = columns

    def validate(self, df: pd.DataFrame) -> List[str]:
        errors = []
        for col, max_length in self.columns.items():
            if col not in df.columns:
                errors.append(f"LengthValidator: Column '{col}' not found.")
                continue
            
            # Convert to string to check length, handle NaNs
            lengths = df[col].astype(str).str.len()
            # Note: astype(str) converts NaN to 'nan', which has length 3. 
            # If we want to ignore NaNs for length check, we should handle them.
            # Assuming we validate actual values.
            
            # A better way might be to only check non-nulls
            mask = df[col].notna()
            long_values = df.loc[mask, col].astype(str).str.len() > max_length
            
            if long_values.any():
                bad_indices = df.index[mask][long_values].tolist()
                errors.append(f"LengthValidator: Column '{col}' exceeds max length of {max_length} at indices {bad_indices[:5]}...")
        
        return errors
