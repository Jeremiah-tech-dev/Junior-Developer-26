from .parser import *
from .storage import LedgerStorage
from .index import Index

class QueryExecutor:
    def __init__(self, storage: LedgerStorage):
        self.storage = storage
        self.index = Index()
        self.storage.load_schemas()
    
    def execute(self, stmt):
        if isinstance(stmt, CreateTableStmt):
            return self._exec_create(stmt)
        elif isinstance(stmt, InsertStmt):
            return self._exec_insert(stmt)
        elif isinstance(stmt, SelectStmt):
            return self._exec_select(stmt)
        elif isinstance(stmt, UpdateStmt):
            return self._exec_update(stmt)
        elif isinstance(stmt, DeleteStmt):
            return self._exec_delete(stmt)
    
    def _exec_create(self, stmt: CreateTableStmt):
        cols = [{'name': c.name, 'type': c.type, 'primary_key': c.primary_key, 'unique': c.unique} 
                for c in stmt.columns]
        self.storage.create_table(stmt.table_name, cols, stmt.is_ledger)
        
        for col in stmt.columns:
            if col.primary_key or col.unique:
                self.index.create_index(stmt.table_name, col.name, col.unique or col.primary_key)
        
        return {"message": f"Table {stmt.table_name} created"}
    
    def _exec_insert(self, stmt: InsertStmt):
        schema = self.storage.schemas[stmt.table_name]
        row = {col['name']: val for col, val in zip(schema['columns'], stmt.values)}
        
        for col in schema['columns']:
            if col.get('primary_key') or col.get('unique'):
                existing = self.index.lookup(stmt.table_name, col['name'], row[col['name']])
                if existing:
                    raise ValueError(f"Constraint violation on {col['name']}")
        
        self.storage.insert_row(stmt.table_name, row)
        return {"message": "Row inserted"}
    
    def _exec_select(self, stmt: SelectStmt):
        rows = self.storage.select_rows(stmt.table_name, stmt.where, stmt.history)
        
        if stmt.join:
            rows = self._exec_join(rows, stmt)
        
        if stmt.columns != ['*']:
            rows = [{k: r[k] for k in stmt.columns if k in r} for r in rows]
        
        return {"rows": rows}
    
    def _exec_update(self, stmt: UpdateStmt):
        if not stmt.where:
            raise ValueError("UPDATE requires WHERE clause")
        self.storage.update_rows(stmt.table_name, stmt.set_clause, stmt.where)
        return {"message": "Rows updated"}
    
    def _exec_delete(self, stmt: DeleteStmt):
        self.storage.delete_rows(stmt.table_name, stmt.where)
        return {"message": "Rows deleted"}
    
    def _exec_join(self, left_rows, stmt: SelectStmt):
        join_table = stmt.join['table']
        join_on = stmt.join['on']
        
        left_col, right_col = join_on.split('=')
        left_col = left_col.strip().split('.')[-1]
        right_col = right_col.strip().split('.')[-1]
        
        right_rows = self.storage.select_rows(join_table)
        
        result = []
        for left in left_rows:
            for right in right_rows:
                if left.get(left_col) == right.get(right_col):
                    merged = {f"{stmt.table_name}.{k}": v for k, v in left.items()}
                    merged.update({f"{join_table}.{k}": v for k, v in right.items()})
                    result.append(merged)
        
        return result
