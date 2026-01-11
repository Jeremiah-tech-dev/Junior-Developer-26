#!/usr/bin/env python3
from core.parser import SQLParser
from core.storage import LedgerStorage
from core.executor import QueryExecutor
import json

def main():
    storage = LedgerStorage()
    executor = QueryExecutor(storage)
    parser = SQLParser()
    
    print("LedgerDB v1.0 - Append-Only Payment Ledger RDBMS")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            sql = input("ledgerdb> ").strip()
            
            if sql.lower() == 'exit':
                break
            
            if not sql:
                continue
            
            stmt = parser.parse(sql)
            result = executor.execute(stmt)
            
            if 'rows' in result:
                print(json.dumps(result['rows'], indent=2))
            else:
                print(result['message'])
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()
