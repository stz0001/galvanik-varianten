#!/usr/bin/env python3
"""
Import VFAHEAD und VFALINE für A60
Aus MV_Prod (D01/M01)
NUR Status 'A' und MIT BMD-Variantencode
"""

import psycopg2
import pyodbc
import os
from datetime import datetime

# AS400 Verbindung (DSN mit integrierten Credentials)
dsn_name = 'MV_Prod'  # A60

# PostgreSQL Verbindung
pg_conn = psycopg2.connect(
    host='localhost',
    database='varianten',
    user='postgres',
    password='postgres'
)
pg_cursor = pg_conn.cursor()

print(f"\n=== Import A60 VFAHEAD/VFALINE aus {dsn_name} ===")
print(f"Start: {datetime.now()}")

# AS400 Verbindung
db2_conn = pyodbc.connect(f'DSN={dsn_name}')
db2_cursor = db2_conn.cursor()

# 1. Import VFAHEAD - NUR Status 'A', MIT BMD-Code UND A60-spezifisch
print("\n1. Importiere VFAHEAD (nur Status A, mit BMD-Code und A60)...")
db2_cursor.execute("""
    SELECT * FROM VFAHEAD 
    WHERE VFAHEAD_STATUS = 'A' 
    AND VFAHEAD_BMDVARIANTE IS NOT NULL 
    AND VFAHEAD_BMDVARIANTE <> ''
    AND VFAHEAD_BMDVARIANTE <> ' '
    AND (VFAHEAD_BESCHREIBUNG LIKE '%A60%' OR VFAHEAD_BESCHREIBUNG LIKE '%A6%')
""")

columns = [column[0] for column in db2_cursor.description]
print(f"Spalten: {columns}")

vfahead_count = 0
vfahead_ids = []

for row in db2_cursor:
    # Erstelle INSERT mit allen Spalten
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join([col.lower() for col in columns])
    
    insert_sql = f"INSERT INTO vfahead ({column_names}) VALUES ({placeholders})"
    
    try:
        pg_cursor.execute(insert_sql, row)
        vfahead_count += 1
        vfahead_ids.append(row[0])  # VFAHEAD_INR
        
        # Debug für die ersten paar Einträge
        if vfahead_count <= 3:
            idx_type = columns.index('VFAHEAD_TYPE')
            idx_bmd = columns.index('VFAHEAD_BMDVARIANTE')
            idx_beschr = columns.index('VFAHEAD_BESCHREIBUNG')
            print(f"  - INR: {row[0]}, Type: {row[idx_type]}, BMD: {row[idx_bmd]}, Beschr: {row[idx_beschr][:50]}")
    except Exception as e:
        print(f"Fehler bei VFAHEAD {row[0]}: {e}")
        pg_conn.rollback()
        continue

pg_conn.commit()
print(f"✓ {vfahead_count} VFAHEAD Einträge importiert")

# Prüfe die Typen
pg_cursor.execute("""
    SELECT vfahead_type, COUNT(*) 
    FROM vfahead 
    WHERE vfahead_beschreibung LIKE '%A60%' OR vfahead_beschreibung LIKE '%A6%'
    GROUP BY vfahead_type 
    ORDER BY COUNT(*) DESC
""")
print("\nA60 VFAHEAD Typen:")
for row in pg_cursor.fetchall():
    print(f"  - {row[0]}: {row[1]}")

# 2. Import VFALINE für die importierten VFAHEAD
print(f"\n2. Importiere VFALINE für {len(vfahead_ids)} VFAHEAD Einträge...")

vfaline_count = 0
batch_size = 100

for i in range(0, len(vfahead_ids), batch_size):
    batch_ids = vfahead_ids[i:i+batch_size]
    placeholders = ', '.join(['?'] * len(batch_ids))
    
    db2_cursor.execute(f"""
        SELECT * FROM VFALINE 
        WHERE VFALINE_VFAHEAD_INR IN ({placeholders})
    """, batch_ids)
    
    if i == 0:  # Erste Batch für Spalten-Info
        columns = [column[0] for column in db2_cursor.description]
        print(f"VFALINE Spalten: {columns[:5]}...")  # Zeige nur erste 5
    
    for row in db2_cursor:
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([col.lower() for col in columns])
        
        insert_sql = f"INSERT INTO vfaline ({column_names}) VALUES ({placeholders})"
        
        try:
            pg_cursor.execute(insert_sql, row)
            vfaline_count += 1
        except Exception as e:
            print(f"Fehler bei VFALINE: {e}")
            pg_conn.rollback()
            continue
    
    pg_conn.commit()
    print(f"  Batch {i//batch_size + 1}: {vfaline_count} Zeilen importiert...")

print(f"✓ {vfaline_count} VFALINE Einträge importiert")

# 3. Statistik
print("\n=== Import-Statistik ===")
pg_cursor.execute("SELECT COUNT(*) FROM vfahead WHERE vfahead_beschreibung LIKE '%A60%' OR vfahead_beschreibung LIKE '%A6%'")
print(f"A60 VFAHEAD: {pg_cursor.fetchone()[0]}")

pg_cursor.execute("""
    SELECT COUNT(DISTINCT vfaline_vfahead_inr) 
    FROM vfaline v
    JOIN vfahead h ON h.vfahead_inr = v.vfaline_vfahead_inr
    WHERE h.vfahead_beschreibung LIKE '%A60%' OR h.vfahead_beschreibung LIKE '%A6%'
""")
print(f"A60 VFAHEAD mit Parametern: {pg_cursor.fetchone()[0]}")

# Cleanup
db2_cursor.close()
db2_conn.close()
pg_cursor.close()
pg_conn.close()

print(f"\n✓ Import abgeschlossen: {datetime.now()}")