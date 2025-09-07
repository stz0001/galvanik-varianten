#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'database': 'varianten',
    'user': 'postgres',
    'password': 'postgres'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()  # Use regular cursor

# Test simple case
types = ['VOR']
bmdvariante = '10'

# Build dynamic query - but carefully
type_conditions = " OR ".join(["TRIM(vfahead_type) = %s" for _ in types])
query_template = """
    SELECT vfahead_inr, vfahead_beschreibung
    FROM vfahead
    WHERE ({})
    AND TRIM(vfahead_bmdvariante) = %s
    AND vfahead_status IN ('A', 'P')
    ORDER BY vfahead_inr
    LIMIT 1
"""
query = query_template.format(type_conditions)
params = types + [bmdvariante]

print(f"Query: {query}")
print(f"Params: {params}")
print(f"Placeholders: {query.count('%s')}")

try:
    # Try with tuple
    cursor.execute(query, tuple(params))
    result = cursor.fetchone()
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

cursor.close()
conn.close()