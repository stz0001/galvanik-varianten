#!/usr/bin/env python3
"""
Analysiert die Struktur der VFAHEAD/VFALINE Tabellen in AS400
"""
import pyodbc

def analyze_table_structure(dsn, schema):
    """Analyze VFAHEAD/VFALINE structure"""
    print(f"\n{'='*60}")
    print(f"Analysiere {dsn} - Schema {schema}")
    print('='*60)
    
    try:
        conn = pyodbc.connect(f"DSN={dsn};UID=ODBCUSER;PWD=transfer", timeout=30)
        cursor = conn.cursor()
        
        # VFAHEAD Struktur
        print("\nVFAHEAD Struktur:")
        print("-" * 40)
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, LENGTH, NUMERIC_SCALE
            FROM QSYS2.SYSCOLUMNS
            WHERE TABLE_SCHEMA = '{schema}'
            AND TABLE_NAME = 'VFAHEAD'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]:20} {col[1]:10} ({col[2]},{col[3] if col[3] else 0})")
        
        # VFALINE Struktur
        print("\nVFALINE Struktur:")
        print("-" * 40)
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, LENGTH, NUMERIC_SCALE
            FROM QSYS2.SYSCOLUMNS
            WHERE TABLE_SCHEMA = '{schema}'
            AND TABLE_NAME = 'VFALINE'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]:20} {col[1]:10} ({col[2]},{col[3] if col[3] else 0})")
        
        # Sample VFAHEAD data
        print("\nBeispiel VFAHEAD Daten (erste 3 Einträge):")
        print("-" * 40)
        cursor.execute(f"""
            SELECT * FROM {schema}.VFAHEAD
            FETCH FIRST 3 ROWS ONLY
        """)
        
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        print("  Spalten:", ', '.join(col_names[:5]), "...")
        
        rows = cursor.fetchall()
        for i, row in enumerate(rows, 1):
            print(f"  Zeile {i}:", str(row[:5])[:80], "...")
        
        # Count records
        cursor.execute(f"SELECT COUNT(*) FROM {schema}.VFAHEAD")
        count = cursor.fetchone()[0]
        print(f"\n  Gesamt VFAHEAD Einträge: {count}")
        
        cursor.execute(f"SELECT COUNT(*) FROM {schema}.VFALINE")
        count = cursor.fetchone()[0]
        print(f"  Gesamt VFALINE Einträge: {count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Fehler: {e}")

def main():
    # Analyze both systems
    analyze_table_structure("MV_Prod", "M01_DAT_LB")
    analyze_table_structure("PB_Prod", "D01_DAT_LB")

if __name__ == "__main__":
    main()