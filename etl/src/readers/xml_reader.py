import xml.etree.ElementTree as ET
from typing import Iterator, Dict, Any
from .base_reader import BaseReader

class XMLReader(BaseReader):
    def __init__(self, file_path: str, config: Dict[str, Any]):
        super().__init__(file_path, config)
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        # Assuming the root contains a list of records. 
        # We might need to make the record tag configurable.
        self.record_tag = config.get('record_tag', 'record') 

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        # If record_tag is not specified, iterate over all children of root
        if self.record_tag:
             elements = self.root.findall(self.record_tag)
        else:
             elements = self.root

        for elem in elements:
            record = {}
            for child in elem:
                record[child.tag] = child.text
            yield record

    def close(self):
        pass
