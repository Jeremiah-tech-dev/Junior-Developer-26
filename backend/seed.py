#!/usr/bin/env python3
from core.parser import SQLParser
from core.storage import LedgerStorage
from core.executor import QueryExecutor

def seed_database():
    storage = LedgerStorage()
    executor = QueryExecutor(storage)
    parser = SQLParser()
    
    queries = [
        # Create tables
        "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, email TEXT UNIQUE) LEDGER",
        "CREATE TABLE wallets (wallet_id INT PRIMARY KEY, user_id INT, balance FLOAT) LEDGER",
        "CREATE TABLE transactions (tx_id INT PRIMARY KEY, wallet_id INT, amount FLOAT, type TEXT) LEDGER",
        
        # Insert users
        "INSERT INTO users VALUES (1, 'Alice Johnson', 'alice@example.com')",
        "INSERT INTO users VALUES (2, 'Bob Smith', 'bob@example.com')",
        "INSERT INTO users VALUES (3, 'Carol White', 'carol@example.com')",
        "INSERT INTO users VALUES (4, 'David Brown', 'david@example.com')",
        "INSERT INTO users VALUES (5, 'Eve Davis', 'eve@example.com')",
        
        # Create wallets
        "INSERT INTO wallets VALUES (1, 1, 1000.00)",
        "INSERT INTO wallets VALUES (2, 2, 500.00)",
        "INSERT INTO wallets VALUES (3, 3, 750.00)",
        "INSERT INTO wallets VALUES (4, 4, 2000.00)",
        "INSERT INTO wallets VALUES (5, 5, 300.00)",
        
        # Initial transactions
        "INSERT INTO transactions VALUES (1, 1, 1000.00, 'deposit')",
        "INSERT INTO transactions VALUES (2, 2, 500.00, 'deposit')",
        "INSERT INTO transactions VALUES (3, 3, 750.00, 'deposit')",
        "INSERT INTO transactions VALUES (4, 4, 2000.00, 'deposit')",
        "INSERT INTO transactions VALUES (5, 5, 300.00, 'deposit')",
        
        # Alice transactions
        "UPDATE wallets SET balance = 1200.00 WHERE wallet_id = 1",
        "INSERT INTO transactions VALUES (6, 1, 200.00, 'credit')",
        "UPDATE wallets SET balance = 1050.00 WHERE wallet_id = 1",
        "INSERT INTO transactions VALUES (7, 1, 150.00, 'debit')",
        
        # Bob transactions
        "UPDATE wallets SET balance = 800.00 WHERE wallet_id = 2",
        "INSERT INTO transactions VALUES (8, 2, 300.00, 'credit')",
        "UPDATE wallets SET balance = 650.00 WHERE wallet_id = 2",
        "INSERT INTO transactions VALUES (9, 2, 150.00, 'debit')",
        
        # Carol transactions
        "UPDATE wallets SET balance = 1250.00 WHERE wallet_id = 3",
        "INSERT INTO transactions VALUES (10, 3, 500.00, 'credit')",
        "UPDATE wallets SET balance = 950.00 WHERE wallet_id = 3",
        "INSERT INTO transactions VALUES (11, 3, 300.00, 'debit')",
        
        # David transactions
        "UPDATE wallets SET balance = 2500.00 WHERE wallet_id = 4",
        "INSERT INTO transactions VALUES (12, 4, 500.00, 'credit')",
        "UPDATE wallets SET balance = 2200.00 WHERE wallet_id = 4",
        "INSERT INTO transactions VALUES (13, 4, 300.00, 'debit')",
        
        # Eve transactions
        "UPDATE wallets SET balance = 600.00 WHERE wallet_id = 5",
        "INSERT INTO transactions VALUES (14, 5, 300.00, 'credit')",
        "UPDATE wallets SET balance = 450.00 WHERE wallet_id = 5",
        "INSERT INTO transactions VALUES (15, 5, 150.00, 'debit')",
        
        # More transactions
        "UPDATE wallets SET balance = 1350.00 WHERE wallet_id = 1",
        "INSERT INTO transactions VALUES (16, 1, 300.00, 'credit')",
        "UPDATE wallets SET balance = 900.00 WHERE wallet_id = 2",
        "INSERT INTO transactions VALUES (17, 2, 250.00, 'credit')",
        "UPDATE wallets SET balance = 1150.00 WHERE wallet_id = 3",
        "INSERT INTO transactions VALUES (18, 3, 200.00, 'credit')",
        "UPDATE wallets SET balance = 2100.00 WHERE wallet_id = 4",
        "INSERT INTO transactions VALUES (19, 4, 100.00, 'debit')",
        "UPDATE wallets SET balance = 550.00 WHERE wallet_id = 5",
        "INSERT INTO transactions VALUES (20, 5, 100.00, 'credit')",
    ]
    
    print("Seeding LedgerDB with sample data...")
    for i, sql in enumerate(queries, 1):
        try:
            stmt = parser.parse(sql)
            executor.execute(stmt)
            print(f"[{i}/{len(queries)}] {sql[:60]}...")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n✅ Database seeded successfully!")
    print(f"   - 5 users created")
    print(f"   - 5 wallets created")
    print(f"   - 20+ transactions executed")
    print(f"   - Multiple updates showing ledger versioning")
    print("\nTry these queries:")
    print("  SELECT * FROM wallets;")
    print("  SELECT * FROM wallets HISTORY WHERE wallet_id = 1;")
    print("  SELECT users.name, wallets.balance FROM users JOIN wallets ON users.id = wallets.user_id;")

if __name__ == '__main__':
    seed_database()
