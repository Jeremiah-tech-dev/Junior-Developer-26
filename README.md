# LedgerDB - Append-Only Payment Ledger RDBMS

A minimal relational database optimized for financial transactions, where data is append-only, auditable, and tamper-evident.

## 🎯 Why LedgerDB?

Real payment systems like Pesapal don't delete or overwrite transaction data. They append entries to a ledger. LedgerDB models this real-world behavior, making it ideal for:

- **Payments** - Every transaction is preserved
- **Audits** - Complete history of all changes
- **Reconciliation** - Reconstruct state at any point in time
- **Trust** - Tamper-evident by design

## 🏗️ Architecture

### Core Components

1. **SQL Parser** - Handles CREATE, INSERT, SELECT, UPDATE, DELETE, JOIN
2. **Ledger Storage** - Append-only JSON-based storage with versioning
3. **Indexing** - Primary key and unique constraint enforcement
4. **Query Executor** - CRUD operations with join support
5. **REPL** - Interactive SQL shell
6. **REST API** - Flask backend for web applications

### Ledger Semantics

Tables created with the `LEDGER` keyword have special behavior:

- **INSERT** - Creates new ledger entry
- **UPDATE** - Marks old row inactive, appends new version
- **DELETE** - Soft delete (marks inactive, preserves history)
- **SELECT** - Returns only active records by default
- **SELECT ... HISTORY** - Returns complete audit trail

Every ledger row includes:
- `_version` - Version number
- `_created_at` - Timestamp
- `_is_active` - Active status

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Seed database with sample data (20+ transactions)
python seed.py

# Start REPL
python repl.py

# Or start API server (auto-seeds if empty)
python api.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

## 📝 SQL Examples

### Create Tables

```sql
CREATE TABLE users (id INT PRIMARY KEY, name TEXT) LEDGER;
CREATE TABLE wallets (wallet_id INT PRIMARY KEY, user_id INT, balance FLOAT) LEDGER;
```

### Insert Data

```sql
INSERT INTO users VALUES (1, 'Alice');
INSERT INTO wallets VALUES (1, 1, 500.00);
```

### Update (Append-Only)

```sql
UPDATE wallets SET balance = 650.00 WHERE wallet_id = 1;
```

This doesn't overwrite - it creates a new version and marks the old one inactive.

### Query Current State

```sql
SELECT * FROM wallets;
```

Returns only the latest active records.

### Query History (Audit Trail)

```sql
SELECT * FROM wallets HISTORY WHERE wallet_id = 1;
```

Returns all versions, including inactive ones.

### Joins

```sql
SELECT users.name, wallets.balance 
FROM users 
JOIN wallets ON users.id = wallets.user_id;
```

## 🎨 Demo Application

The included wallet system demonstrates:

- **Create User** - Creates user and wallet
- **Credit/Debit** - Modify wallet balance
- **Audit Trail** - View complete transaction history

The "Audit Trail" button shows the killer feature: complete versioned history of every balance change.

## ✅ Challenge Requirements

| Requirement | Implementation |
|------------|----------------|
| Simple RDBMS | ✅ Tables, columns, typed data |
| CREATE TABLE | ✅ With LEDGER keyword support |
| CRUD Operations | ✅ All implemented with ledger semantics |
| Basic Indexing | ✅ Primary key + unique constraints |
| Primary/Unique Keys | ✅ Enforced at insert/update |
| Joins | ✅ Nested-loop join implementation |
| SQL Interface | ✅ SQL-like with extensions |
| REPL Mode | ✅ Interactive shell |
| Demo Web App | ✅ React wallet system |

## 🧠 Design Decisions

### Why Append-Only?

In financial systems, you never want to lose data. Append-only storage ensures:
- Complete audit trail
- Ability to reconstruct past states
- Tamper-evidence
- Regulatory compliance

### Tradeoffs

**Pros:**
- Perfect for financial/audit use cases
- Simple to implement
- Easy to understand
- Naturally supports time-travel queries

**Cons:**
- Storage grows faster than traditional RDBMS
- Queries may be slower on large histories
- More complex garbage collection (not implemented in MVP)

### Why JSON Storage?

For an MVP, JSON provides:
- Human-readable data
- Easy debugging
- Simple implementation
- No external dependencies

Production systems would use binary formats or existing storage engines.

## 🔮 Future Enhancements

- Transaction support (ACID)
- More join types (LEFT, RIGHT, OUTER)
- Aggregations (SUM, COUNT, AVG)
- Indexes on non-key columns
- Query optimization
- Binary storage format
- Concurrent access control

## 🏆 Why This Fits Pesapal

Pesapal processes payments. Payments require:

1. **Auditability** - LedgerDB preserves every change
2. **Trust** - Append-only prevents tampering
3. **Reconciliation** - Historical queries reconstruct any state
4. **Compliance** - Complete audit trail for regulators

LedgerDB isn't just a database - it's a financial ledger engine.

## 📄 License

MIT

## 👤 Author

Built for the Pesapal Junior Developer Challenge 2026
