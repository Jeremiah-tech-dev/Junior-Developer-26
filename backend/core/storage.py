import json
import os
from datetime import datetime
from typing import List, Dict, Any

class LedgerStorage:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.schemas = {}
    
    def _table_path(self, table_name: str):
        return os.path.join(self.data_dir, f"{table_name}.json")
    
    def _schema_path(self):
        return os.path.join(self.data_dir, "schemas.json")
    
    def load_schemas(self):
        if os.path.exists(self._schema_path()):
            with open(self._schema_path(), 'r') as f:
                self.schemas = json.load(f)
    
    def save_schemas(self):
        with open(self._schema_path(), 'w') as f:
            json.dump(self.schemas, f, indent=2)
    
    def create_table(self, table_name: str, columns: List[Dict], is_ledger: bool):
        if table_name in self.schemas:
            raise ValueError(f"Table {table_name} already exists")
        
        self.schemas[table_name] = {
            'columns': columns,
            'is_ledger': is_ledger
        }
        self.save_schemas()
        
        with open(self._table_path(table_name), 'w') as f:
            json.dump([], f)
    
    def insert_row(self, table_name: str, row: Dict):
        rows = self._read_table(table_name)
        
        if self.schemas[table_name]['is_ledger']:
            row['_version'] = len([r for r in rows if self._match_pk(r, row)]) + 1
            row['_created_at'] = datetime.now().isoformat()
            row['_is_active'] = True
        
        rows.append(row)
        self._write_table(table_name, rows)
    
    def update_rows(self, table_name: str, set_clause: Dict, where: Dict):
        rows = self._read_table(table_name)
        is_ledger = self.schemas[table_name]['is_ledger']
        updated = False
        new_rows = []
        
        for row in rows:
            if self._match_where(row, where) and row.get('_is_active', True):
                updated = True
                if is_ledger:
                    # Mark old row as inactive
                    row['_is_active'] = False
                    new_rows.append(row)
                    # Create new version
                    new_row = row.copy()
                    new_row.update(set_clause)
                    new_row['_version'] = row.get('_version', 1) + 1
                    new_row['_created_at'] = datetime.now().isoformat()
                    new_row['_is_active'] = True
                    new_rows.append(new_row)
                else:
                    row.update(set_clause)
                    new_rows.append(row)
            else:
                new_rows.append(row)
        
        self._write_table(table_name, new_rows)
        return updated
    
    def delete_rows(self, table_name: str, where: Dict):
        rows = self._read_table(table_name)
        is_ledger = self.schemas[table_name]['is_ledger']
        
        if is_ledger:
            for row in rows:
                if self._match_where(row, where) and row.get('_is_active', True):
                    row['_is_active'] = False
        else:
            rows = [r for r in rows if not self._match_where(r, where)]
        
        self._write_table(table_name, rows)
    
    def select_rows(self, table_name: str, where: Dict = None, history: bool = False):
        rows = self._read_table(table_name)
        is_ledger = self.schemas[table_name]['is_ledger']
        
        if is_ledger and not history:
            rows = [r for r in rows if r.get('_is_active', True)]
        
        if where:
            rows = [r for r in rows if self._match_where(r, where)]
        
        return rows
    
    def _read_table(self, table_name: str):
        if not os.path.exists(self._table_path(table_name)):
            return []
        with open(self._table_path(table_name), 'r') as f:
            return json.load(f)
    
    def _write_table(self, table_name: str, rows: List[Dict]):
        with open(self._table_path(table_name), 'w') as f:
            json.dump(rows, f, indent=2)
    
    def _match_where(self, row: Dict, where: Dict):
        if not where:
            return True
        for k, v in where.items():
            row_val = row.get(k)
            # Handle type conversions for comparison
            if row_val is None:
                return False
            # Convert both to same type for comparison
            if isinstance(v, (int, float)) and isinstance(row_val, (int, float)):
                if float(row_val) != float(v):
                    return False
            elif str(row_val) != str(v):
                return False
        return True
    
    def _match_pk(self, row1: Dict, row2: Dict):
        # Find the table name by checking which schema we're working with
        for table_name, schema in self.schemas.items():
            pk_cols = [c['name'] for c in schema['columns'] if c.get('primary_key')]
            if pk_cols and all(k in row1 and k in row2 for k in pk_cols):
                return all(row1.get(k) == row2.get(k) for k in pk_cols)
        return False
