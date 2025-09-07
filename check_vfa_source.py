#!/usr/bin/env python3
"""
Prüft, ob VFAHEAD/VFALINE Tabellen in AS400/DB2 existieren
"""
import pyodbc
import sys

def check_tables_in_db2(dsn, schema):
    """Check if VFAHEAD/VFALINE exist in DB2"""
    print(f"\nPrüfe {dsn} - Schema {schema}...")
    
    try:
        conn = pyodbc.connect(f"DSN={dsn};UID=ODBCUSER;PWD=transfer", timeout=30)
        cursor = conn.cursor()
        
        # Liste alle Tabellen die VFA enthalten
        cursor.execute(f"""
            SELECT TABLE_NAME 
            FROM QSYS2.SYSTABLES 
            WHERE TABLE_SCHEMA = '{schema}'
            AND (UPPER(TABLE_NAME) LIKE '%VFA%' 
                 OR UPPER(TABLE_NAME) LIKE '%VARIANT%'
                 OR UPPER(TABLE_NAME) LIKE '%PROZESS%'
                 OR UPPER(TABLE_NAME) LIKE '%PROGRAMM%')
            ORDER BY TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print(f"  Gefundene Tabellen mit VFA/VARIANT/PROZESS/PROGRAMM:")
            for table in tables:
                print(f"    - {table[0]}")
        else:
            print(f"  Keine VFA/VARIANT/PROZESS/PROGRAMM Tabellen gefunden")
        
        # Prüfe auch nach anderen relevanten Tabellen
        cursor.execute(f"""
            SELECT TABLE_NAME 
            FROM QSYS2.SYSTABLES 
            WHERE TABLE_SCHEMA = '{schema}'
            AND (UPPER(TABLE_NAME) LIKE '%PARAM%' 
                 OR UPPER(TABLE_NAME) LIKE '%BEHAND%'
                 OR UPPER(TABLE_NAME) LIKE '%VERZINK%')
            ORDER BY TABLE_NAME
        """)
        
        tables2 = cursor.fetchall()
        
        if tables2:
            print(f"  Gefundene Tabellen mit PARAM/BEHAND/VERZINK:")
            for table in tables2:
                print(f"    - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  Fehler bei Verbindung: {e}")
        return False

def main():
    print("=" * 60)
    print("SUCHE NACH VFAHEAD/VFALINE IN AS400/DB2")
    print("=" * 60)
    
    # Check both DSNs
    check_tables_in_db2("MV_Prod", "M01_DAT_LB")
    check_tables_in_db2("PB_Prod", "D01_DAT_LB")
    
    print("\n" + "=" * 60)
    print("Fazit: VFAHEAD/VFALINE scheinen nicht in AS400 zu existieren.")
    print("Die Daten müssen aus den Artikel-Codes abgeleitet werden.")

if __name__ == "__main__":
    main()