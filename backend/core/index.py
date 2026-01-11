from typing import Dict, Any, List

class Index:
    def __init__(self):
        self.indexes = {}
    
    def create_index(self, table_name: str, column: str, unique: bool = False):
        key = f"{table_name}.{column}"
        self.indexes[key] = {'unique': unique, 'data': {}}
    
    def add_to_index(self, table_name: str, column: str, value: Any, row_id: int):
        key = f"{table_name}.{column}"
        if key not in self.indexes:
            return
        
        if self.indexes[key]['unique'] and value in self.indexes[key]['data']:
            raise ValueError(f"Unique constraint violation on {column}")
        
        if value not in self.indexes[key]['data']:
            self.indexes[key]['data'][value] = []
        self.indexes[key]['data'][value].append(row_id)
    
    def lookup(self, table_name: str, column: str, value: Any):
        key = f"{table_name}.{column}"
        if key not in self.indexes:
            return None
        return self.indexes[key]['data'].get(value, [])
