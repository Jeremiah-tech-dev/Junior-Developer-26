from flask import Flask, request, jsonify
from flask_cors import CORS
from core.parser import SQLParser
from core.storage import LedgerStorage
from core.executor import QueryExecutor
import os

app = Flask(__name__)
CORS(app)

storage = LedgerStorage()
executor = QueryExecutor(storage)
parser = SQLParser()

# Auto-seed if database is empty
if not storage.schemas:
    print("Database empty, seeding with sample data...")
    from seed import seed_database
    seed_database()

@app.route('/api/query', methods=['POST'])
def execute_query():
    try:
        sql = request.json.get('sql')
        print(f"\n=== Executing SQL ===")
        print(f"Query: {sql}")
        stmt = parser.parse(sql)
        print(f"Parsed: {stmt}")
        result = executor.execute(stmt)
        print(f"Result: {result}")
        print(f"===================\n")
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        print(f"\n!!! ERROR !!!")
        print(f"Query: {sql}")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"=============\n")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/tables', methods=['GET'])
def get_tables():
    return jsonify({'tables': list(storage.schemas.keys())})

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"\n🚀 LedgerDB Backend running on http://localhost:{port}\n")
    app.run(debug=True, port=port)
