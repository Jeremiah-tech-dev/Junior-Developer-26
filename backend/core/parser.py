import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Column:
    name: str
    type: str
    primary_key: bool = False
    unique: bool = False

@dataclass
class CreateTableStmt:
    table_name: str
    columns: List[Column]
    is_ledger: bool = False

@dataclass
class InsertStmt:
    table_name: str
    values: List[Any]

@dataclass
class SelectStmt:
    table_name: str
    columns: List[str]
    where: Optional[Dict] = None
    history: bool = False
    join: Optional[Dict] = None

@dataclass
class UpdateStmt:
    table_name: str
    set_clause: Dict[str, Any]
    where: Optional[Dict] = None

@dataclass
class DeleteStmt:
    table_name: str
    where: Optional[Dict] = None

class SQLParser:
    def parse(self, sql: str):
        sql = sql.strip().rstrip(';')
        tokens = sql.split()
        cmd = tokens[0].upper()
        
        if cmd == 'CREATE':
            return self._parse_create(sql)
        elif cmd == 'INSERT':
            return self._parse_insert(sql)
        elif cmd == 'SELECT':
            return self._parse_select(sql)
        elif cmd == 'UPDATE':
            return self._parse_update(sql)
        elif cmd == 'DELETE':
            return self._parse_delete(sql)
        else:
            raise ValueError(f"Unknown command: {cmd}")
    
    def _parse_create(self, sql: str):
        match = re.match(r'CREATE TABLE (\w+) \((.*?)\)(?: (LEDGER))?', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1)
        cols_str = match.group(2)
        is_ledger = match.group(3) is not None
        
        columns = []
        for col_def in cols_str.split(','):
            col_def = col_def.strip()
            parts = col_def.split()
            name = parts[0]
            type_ = parts[1]
            pk = 'PRIMARY' in col_def.upper()
            uniq = 'UNIQUE' in col_def.upper()
            columns.append(Column(name, type_, pk, uniq))
        
        return CreateTableStmt(table_name, columns, is_ledger)
    
    def _parse_insert(self, sql: str):
        match = re.match(r'INSERT INTO (\w+) VALUES \((.*?)\)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1)
        values_str = match.group(2)
        values = [self._parse_value(v.strip()) for v in values_str.split(',')]
        
        return InsertStmt(table_name, values)
    
    def _parse_select(self, sql: str):
        history = 'HISTORY' in sql.upper()
        sql = sql.replace(' HISTORY', '').replace(' history', '')
        
        match = re.match(r'SELECT (.*?) FROM (\w+)(?: JOIN (\w+) ON (.*?))?(?: WHERE (.*))?', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        cols_str = match.group(1).strip()
        columns = ['*'] if cols_str == '*' else [c.strip() for c in cols_str.split(',')]
        table_name = match.group(2)
        join_table = match.group(3)
        join_on = match.group(4)
        where_str = match.group(5)
        
        where = self._parse_where(where_str) if where_str else None
        join = {'table': join_table, 'on': join_on} if join_table else None
        
        return SelectStmt(table_name, columns, where, history, join)
    
    def _parse_update(self, sql: str):
        match = re.match(r'UPDATE (\w+) SET (.*?)(?: WHERE (.*))?$', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1)
        set_str = match.group(2).strip()
        where_str = match.group(3)
        
        set_clause = {}
        for pair in set_str.split(','):
            pair = pair.strip()
            if '=' not in pair:
                raise ValueError(f"Invalid SET clause: {pair}")
            parts = pair.split('=', 1)
            k = parts[0].strip()
            v = parts[1].strip() if len(parts) > 1 else ''
            set_clause[k] = self._parse_value(v)
        
        where = self._parse_where(where_str) if where_str else None
        return UpdateStmt(table_name, set_clause, where)
    
    def _parse_delete(self, sql: str):
        match = re.match(r'DELETE FROM (\w+)(?: WHERE (.*))?', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1)
        where_str = match.group(2)
        where = self._parse_where(where_str) if where_str else None
        
        return DeleteStmt(table_name, where)
    
    def _parse_where(self, where_str: str):
        match = re.match(r'(\w+)\s*=\s*(.+)', where_str.strip())
        if match:
            return {match.group(1): self._parse_value(match.group(2))}
        return {}
    
    def _parse_value(self, val: str):
        val = val.strip().strip("'\"")
        if val.isdigit():
            return int(val)
        try:
            return float(val)
        except:
            return val
