#!/usr/bin/env python3
"""
Import ALLE VFAHEAD und VFALINE aus beiden DSNs
Filter: NUR Status 'A' und MIT BMD-Variantencode
Keine Trennung nach Anlagen - das machen wir beim Mapping
"""

import psycopg2
import pyodbc
from datetime import datetime

# PostgreSQL Verbindung
pg_conn = psycopg2.connect(
    host='localhost',
    database='varianten',
    user='postgres',
    password='postgres'
)
pg_cursor = pg_conn.cursor()

print(f"\n=== Import ALLE VFAHEAD/VFALINE aus beiden DSNs ===")
print(f"Start: {datetime.now()}")

# DSNs
dsn_names = ['PB_Prod', 'MV_Prod']

all_vfahead_ids = []
total_vfahead = 0
total_vfaline = 0

for dsn_name in dsn_names:
    print(f"\n--- Importiere aus {dsn_name} ---")
    
    # AS400 Verbindung
    db2_conn = pyodbc.connect(f'DSN={dsn_name}')
    db2_cursor = db2_conn.cursor()
    
    # 1. Import VFAHEAD - NUR Status 'A' UND mit BMD-Variantencode
    print(f"Importiere VFAHEAD (nur Status A und mit BMD-Code)...")
    db2_cursor.execute("""
        SELECT * FROM VFAHEAD 
        WHERE VFAHEAD_STATUS = 'A' 
        AND VFAHEAD_BMDVARIANTE IS NOT NULL 
        AND VFAHEAD_BMDVARIANTE <> ''
        AND VFAHEAD_BMDVARIANTE <> ' '
    """)
    
    columns = [column[0] for column in db2_cursor.description]
    vfahead_count = 0
    vfahead_ids = []
    
    for row in db2_cursor:
        # Check if already exists
        pg_cursor.execute("SELECT 1 FROM vfahead WHERE vfahead_inr = %s", (row[0],))
        if pg_cursor.fetchone():
            continue  # Skip duplicates
            
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([col.lower() for col in columns])
        
        insert_sql = f"INSERT INTO vfahead ({column_names}) VALUES ({placeholders})"
        
        try:
            pg_cursor.execute(insert_sql, row)
            vfahead_count += 1
            vfahead_ids.append(row[0])  # VFAHEAD_INR
            
            # Debug für die ersten paar Einträge
            if vfahead_count <= 2:
                idx_type = columns.index('VFAHEAD_TYPE')
                idx_bmd = columns.index('VFAHEAD_BMDVARIANTE')
                idx_beschr = columns.index('VFAHEAD_BESCHREIBUNG')
                print(f"  - Type: {row[idx_type]}, BMD: {row[idx_bmd]}, Beschr: {row[idx_beschr][:40]}")
        except Exception as e:
            print(f"Fehler bei VFAHEAD {row[0]}: {e}")
            pg_conn.rollback()
            continue
    
    pg_conn.commit()
    print(f"✓ {vfahead_count} VFAHEAD Einträge importiert")
    total_vfahead += vfahead_count
    all_vfahead_ids.extend(vfahead_ids)
    
    # 2. Import VFALINE
    if vfahead_ids:
        print(f"Importiere VFALINE für {len(vfahead_ids)} VFAHEAD Einträge...")
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
            
            for row in db2_cursor:
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([col.lower() for col in columns])
                
                insert_sql = f"INSERT INTO vfaline ({column_names}) VALUES ({placeholders})"
                
                try:
                    pg_cursor.execute(insert_sql, row)
                    vfaline_count += 1
                except Exception as e:
                    # Ignore duplicates
                    if 'duplicate key' not in str(e):
                        print(f"Fehler bei VFALINE: {e}")
                    pg_conn.rollback()
                    continue
            
            pg_conn.commit()
        
        print(f"✓ {vfaline_count} VFALINE Einträge importiert")
        total_vfaline += vfaline_count
    
    # Cleanup
    db2_cursor.close()
    db2_conn.close()

# 3. Statistik
print("\n=== Import-Statistik ===")
print(f"VFAHEAD Total: {total_vfahead}")
print(f"VFALINE Total: {total_vfaline}")

# Typen-Übersicht
pg_cursor.execute("""
    SELECT vfahead_type, COUNT(*) 
    FROM vfahead 
    GROUP BY vfahead_type 
    ORDER BY COUNT(*) DESC
""")
print("\nVFAHEAD Typen:")
for row in pg_cursor.fetchall():
    print(f"  - {row[0]:20}: {row[1]}")

# Anlagen-Verteilung
pg_cursor.execute("""
    SELECT 
        COUNT(CASE WHEN vfahead_g2aktiv = 'T' THEN 1 END) as G2,
        COUNT(CASE WHEN vfahead_g3aktiv = 'T' THEN 1 END) as G3,
        COUNT(CASE WHEN vfahead_g4aktiv = 'T' THEN 1 END) as G4,
        COUNT(CASE WHEN vfahead_g5aktiv = 'T' THEN 1 END) as G5,
        COUNT(CASE WHEN vfahead_beschreibung LIKE '%A60%' OR vfahead_beschreibung LIKE '%A6 %' THEN 1 END) as A60
    FROM vfahead
""")
row = pg_cursor.fetchone()
print(f"\nAnlagen-Verteilung:")
print(f"  G2: {row[0]}, G3: {row[1]}, G4: {row[2]}, G5: {row[3]}, A60: {row[4]}")

pg_cursor.close()
pg_conn.close()

print(f"\n✓ Import abgeschlossen: {datetime.now()}")