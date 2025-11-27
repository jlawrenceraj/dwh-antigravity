from typing import Iterator, Dict, Any
from .base_reader import BaseReader

class FixedWidthReader(BaseReader):
    def __init__(self, file_path: str, config: Dict[str, Any]):
        super().__init__(file_path, config)
        self.columns = config.get('columns', [])
        self.file = open(self.file_path, mode='r', encoding='utf-8')

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        for line in self.file:
            record = {}
            for col in self.columns:
                start = col.get('start')
                length = col.get('length')
                name = col.get('name')
                if start is not None and length is not None:
                    val = line[start:start+length].strip()
                    record[name] = val
            yield record

    def close(self):
        if self.file:
            self.file.close()
