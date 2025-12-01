import pandas as pd
from abc import ABC, abstractmethod
import logging

class FileIngestor(ABC):
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def read_file(self, file_path: str) -> pd.DataFrame:
        pass

class DelimitedIngestor(FileIngestor):
    def read_file(self, file_path: str) -> pd.DataFrame:
        sep = self.config.get('separator', ',')
        self.logger.info(f"Reading delimited file: {file_path} with separator '{sep}'")
        # Read all as string to preserve format for validation
        return pd.read_csv(file_path, sep=sep, dtype=str, keep_default_na=False)

class FixedWidthIngestor(FileIngestor):
    def read_file(self, file_path: str) -> pd.DataFrame:
        # Extract col_specs and names from schema columns if not directly provided
        col_specs = self.config.get('col_specs')
        names = self.config.get('names')
        
        if not col_specs and 'columns' in self.config:
            col_specs = []
            names = []
            for col in self.config['columns']:
                if 'position' in col:
                    col_specs.append(tuple(col['position']))
                    names.append(col['name'])
        
        if not col_specs:
            raise ValueError("Configuration for fixed-width file must include 'col_specs' or 'columns' with 'position'.")

        self.logger.info(f"Reading fixed width file: {file_path}")
        return pd.read_fwf(file_path, colspecs=col_specs, names=names, dtype=str, keep_default_na=False)

def get_ingestor(file_type: str, config: dict) -> FileIngestor:
    if file_type == 'csv':
        config['separator'] = ','
        return DelimitedIngestor(config)
    elif file_type == 'pipe':
        config['separator'] = '|'
        return DelimitedIngestor(config)
    elif file_type == 'fixed' or file_type == 'dat':
        return FixedWidthIngestor(config)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
