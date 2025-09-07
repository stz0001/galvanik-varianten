#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(host='localhost', database='varianten', user='postgres', password='postgres')
cursor = conn.cursor()

# Get first A60 code
cursor.execute("SELECT * FROM codes WHERE anlage = 'A60' LIMIT 1")
code = cursor.fetchone()
print(f"Code: {code[2]}, anlage: {code[1]}, vb: {code[3]}")

# Try the mapping query
types = ['VOR']
bmdvariante = code[3]  # '10'
anlage = code[1]  # 'A60'

print(f"\nMapping with anlage={anlage}, types={types}, bmdvariante={bmdvariante}")

# Build query for A60
type_conditions = " OR ".join(["TRIM(vfahead_type) = %s" for _ in types])
query_template = """
    SELECT vfahead_inr, vfahead_beschreibung
    FROM vfahead
    WHERE ({})
    AND TRIM(vfahead_bmdvariante) = %s
    AND vfahead_status IN ('A', 'P')
    AND (vfahead_beschreibung LIKE '%%A60%%' OR vfahead_beschreibung LIKE '%%A6%%')
    ORDER BY vfahead_inr
    LIMIT 1
"""
query = query_template.format(type_conditions)
params = types + [bmdvariante]

print(f"Query: {query}")
print(f"Params: {params}")
print(f"Placeholders in query: {query.count('%s')}")

try:
    cursor.execute(query, params)
    result = cursor.fetchone()
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

cursor.close()
conn.close()