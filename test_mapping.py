#!/usr/bin/env python3
"""
Test the mapping query
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'database': 'varianten',
    'user': 'postgres',
    'password': 'postgres'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Test the query
types = ['VOR']
bmdvariante = '10'
anlage = 'G2'
anlage_field = f"vfahead_{anlage.lower()}aktiv"

# Build the query with f-string
query = f"""
    SELECT vfahead_inr, vfahead_beschreibung
    FROM vfahead
    WHERE TRIM(vfahead_type) = ANY(%s)
    AND TRIM(vfahead_bmdvariante) = %s
    AND {anlage_field} = 'T'
    AND vfahead_status IN ('A', 'P')
    ORDER BY vfahead_inr
    LIMIT 1
"""

print(f"Query: {query}")
print(f"Parameters: types={types}, bmdvariante={bmdvariante}")

try:
    cursor.execute(query, (types, bmdvariante))
    result = cursor.fetchone()
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")

cursor.close()
conn.close()