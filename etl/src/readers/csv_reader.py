import csv
from typing import Iterator, Dict, Any
from .base_reader import BaseReader

class CSVReader(BaseReader):
    def __init__(self, file_path: str, config: Dict[str, Any]):
        super().__init__(file_path, config)
        self.delimiter = config.get('delimiter', ',')
        self.file = open(self.file_path, mode='r', encoding='utf-8', newline='')
        self.reader = csv.DictReader(self.file, delimiter=self.delimiter)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        for row in self.reader:
            yield row

    def close(self):
        if self.file:
            self.file.close()
