import pandas as pd
import logging

class DataValidator:
    def __init__(self, schema):
        self.schema = schema
        self.logger = logging.getLogger(__name__)

    def validate(self, df: pd.DataFrame):
        self.logger.info("Starting validation...")
        
        # Initialize error column
        df['error_message'] = ''
        
        # 1. Mandatory Check
        self._validate_mandatory(df)
        
        # 2. Type Check (Basic implementation)
        self._validate_types(df)
        
        # 3. Length Check
        self._validate_lengths(df)
        
        # 4. Duplicate Check
        self._validate_duplicates(df)
        
        # Split into valid and error
        error_mask = df['error_message'] != ''
        error_df = df[error_mask].copy()
        valid_df = df[~error_mask].drop(columns=['error_message']).copy()
        
        self.logger.info(f"Validation complete. Valid records: {len(valid_df)}, Error records: {len(error_df)}")
        return valid_df, error_df

    def _validate_mandatory(self, df):
        for col_def in self.schema.get('columns', []):
            if col_def.get('mandatory', False):
                col_name = col_def['name']
                if col_name in df.columns:
                    # Check for empty strings or None
                    mask = (df[col_name].isna()) | (df[col_name].astype(str).str.strip() == '')
                    df.loc[mask, 'error_message'] += f"Missing mandatory field: {col_name}; "

    def _validate_types(self, df):
        # In a real scenario, we might try to cast and catch exceptions
        # For now, we assume everything is read as string.
        # We can implement specific checks (e.g., is_numeric, is_date) based on schema types
        for col_def in self.schema.get('columns', []):
            col_name = col_def['name']
            data_type = col_def.get('type', 'string')
            
            if col_name in df.columns:
                if data_type == 'integer':
                    # Check if it contains only digits
                    mask = ~df[col_name].astype(str).str.match(r'^-?\d+$') & (df[col_name] != '')
                    df.loc[mask, 'error_message'] += f"Invalid integer format: {col_name}; "
                # Add more type checks as needed

    def _validate_lengths(self, df):
        for col_def in self.schema.get('columns', []):
            col_name = col_def['name']
            max_len = col_def.get('length')
            
            if max_len and col_name in df.columns:
                mask = df[col_name].astype(str).str.len() > max_len
                df.loc[mask, 'error_message'] += f"Length exceeds {max_len}: {col_name}; "

    def _validate_duplicates(self, df):
        unique_cols = [col['name'] for col in self.schema.get('columns', []) if col.get('unique', False)]
        
        if unique_cols:
            # Check if all unique columns exist in dataframe
            existing_unique_cols = [col for col in unique_cols if col in df.columns]
            
            if existing_unique_cols:
                # Find duplicates based on these columns
                # keep=False marks all duplicates as True
                dup_mask = df.duplicated(subset=existing_unique_cols, keep=False)
                df.loc[dup_mask, 'error_message'] += f"Duplicate record based on keys: {existing_unique_cols}; "
