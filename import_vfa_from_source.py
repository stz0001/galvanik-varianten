#!/usr/bin/env python3
"""
1:1 Import der VFAHEAD und VFALINE Tabellen aus der Original-Datenquelle
KEINE Datenmanipulation - nur direkter Import!

WICHTIG: Die Quelle der VFAHEAD/VFALINE Daten muss noch definiert werden:
- Option 1: AS400/DB2 über ODBC (MV_Prod oder PB_Prod)
- Option 2: Andere PostgreSQL DB
- Option 3: CSV/Excel Files
- Option 4: Andere Quelle?
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pyodbc
import sys

# Ziel-Datenbank (varianten)
VARIANTEN_DB = {
    'host': 'localhost',
    'database': 'varianten',
    'user': 'postgres',
    'password': 'postgres'
}

# TODO: QUELLE DEFINIEREN!
# Option 1: AS400/DB2
# DB2_DSN = "MV_Prod"  # oder "PB_Prod"
# DB2_SCHEMA = "M01_DAT_LB"  # oder "D01_DAT_LB"

def create_tables_from_source_structure(cursor):
    """
    Erstellt VFAHEAD und VFALINE Tabellen mit EXAKT der Struktur aus der Quelle
    TODO: Anpassen basierend auf echter Quell-Struktur!
    """
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS vfaline CASCADE")
    cursor.execute("DROP TABLE IF EXISTS vfahead CASCADE")
    
    # Create VFAHEAD - EXAKTE Struktur aus Quelle übernehmen!
    # TODO: Diese Struktur muss der Original-Tabelle entsprechen
    cursor.execute("""
        CREATE TABLE vfahead (
            vfahead_inr INTEGER PRIMARY KEY,
            type VARCHAR(20),
            bmdvariante VARCHAR(10),
            anlage_codes TEXT[],  -- oder einzelne Felder wenn nicht als Array
            beschreibung TEXT,
            kurzzeichen VARCHAR(20),
            status CHAR(1),
            erstellung_dat DATE,
            aenderung_dat DATE
            -- TODO: Weitere Felder aus Original-Tabelle ergänzen!
        )
    """)
    
    # Create VFALINE - EXAKTE Struktur aus Quelle übernehmen!
    cursor.execute("""
        CREATE TABLE vfaline (
            id INTEGER PRIMARY KEY,
            vfahead_inr INTEGER REFERENCES vfahead(vfahead_inr),
            gruppe VARCHAR(20),
            parameter VARCHAR(30),
            daten_char VARCHAR(50),
            daten_dec DECIMAL(10,2),
            beschreibung TEXT
            -- TODO: Weitere Felder aus Original-Tabelle ergänzen!
        )
    """)
    
    print("Tabellen-Struktur erstellt")

def import_from_db2():
    """
    Import aus AS400/DB2 über ODBC
    """
    print("Verbinde mit AS400/DB2...")
    
    # TODO: Korrekte DSN und Schema definieren
    DB2_DSN = "MV_Prod"  # oder "PB_Prod"
    DB2_SCHEMA = "M01_DAT_LB"  # Schema wo VFAHEAD/VFALINE liegen
    
    try:
        # Connect to DB2
        db2_conn = pyodbc.connect(f"DSN={DB2_DSN};UID=ODBCUSER;PWD=transfer", timeout=30)
        db2_cursor = db2_conn.cursor()
        
        # Connect to varianten
        pg_conn = psycopg2.connect(**VARIANTEN_DB)
        pg_cursor = pg_conn.cursor()
        
        # Create tables
        create_tables_from_source_structure(pg_cursor)
        
        # Import VFAHEAD - 1:1 KOPIE!
        print(f"Importiere VFAHEAD aus {DB2_SCHEMA}...")
        db2_cursor.execute(f"""
            SELECT * FROM {DB2_SCHEMA}.VFAHEAD
            WHERE STATUS = 'A'
        """)
        
        vfahead_count = 0
        for row in db2_cursor.fetchall():
            # TODO: Feldnamen anpassen an echte Struktur
            pg_cursor.execute("""
                INSERT INTO vfahead (
                    vfahead_inr, type, bmdvariante, anlage_codes,
                    beschreibung, kurzzeichen, status, 
                    erstellung_dat, aenderung_dat
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row.VFAHEAD_INR,
                row.TYPE,
                row.BMDVARIANTE,
                # TODO: anlage_codes richtig mappen
                [row.ANLAGE] if hasattr(row, 'ANLAGE') else None,
                row.BESCHREIBUNG,
                row.KURZZEICHEN,
                row.STATUS,
                row.ERSTELLUNG_DAT,
                row.AENDERUNG_DAT
            ))
            vfahead_count += 1
        
        print(f"  {vfahead_count} VFAHEAD Einträge importiert")
        
        # Import VFALINE - 1:1 KOPIE!
        print(f"Importiere VFALINE aus {DB2_SCHEMA}...")
        db2_cursor.execute(f"""
            SELECT * FROM {DB2_SCHEMA}.VFALINE
        """)
        
        vfaline_count = 0
        for row in db2_cursor.fetchall():
            pg_cursor.execute("""
                INSERT INTO vfaline (
                    id, vfahead_inr, gruppe, parameter,
                    daten_char, daten_dec, beschreibung
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row.ID if hasattr(row, 'ID') else vfaline_count,
                row.VFAHEAD_INR,
                row.GRUPPE,
                row.PARAMETER,
                row.DATEN_CHAR,
                row.DATEN_DEC,
                row.BESCHREIBUNG
            ))
            vfaline_count += 1
        
        print(f"  {vfaline_count} VFALINE Einträge importiert")
        
        # Commit
        pg_conn.commit()
        print("\n✓ Import erfolgreich abgeschlossen!")
        
        # Cleanup
        db2_cursor.close()
        db2_conn.close()
        pg_cursor.close()
        pg_conn.close()
        
    except Exception as e:
        print(f"FEHLER beim Import: {e}")
        sys.exit(1)

def import_from_postgres():
    """
    Import aus einer anderen PostgreSQL Datenbank
    """
    print("Import aus PostgreSQL Quelle...")
    
    # TODO: Quell-DB definieren
    SOURCE_DB = {
        'host': 'localhost',
        'database': 'galvanik',  # oder andere DB?
        'user': 'postgres',
        'password': 'postgres'
    }
    
    try:
        # Connect to source
        source_conn = psycopg2.connect(**SOURCE_DB)
        source_cursor = source_conn.cursor(cursor_factory=RealDictCursor)
        
        # Connect to target
        target_conn = psycopg2.connect(**VARIANTEN_DB)
        target_cursor = target_conn.cursor()
        
        # Check if tables exist in source
        source_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('vfahead', 'vfaline')
        """)
        
        tables = [row['table_name'] for row in source_cursor.fetchall()]
        
        if 'vfahead' not in tables or 'vfaline' not in tables:
            print("FEHLER: VFAHEAD/VFALINE Tabellen nicht in Quell-DB gefunden!")
            print("Gefundene Tabellen:", tables)
            sys.exit(1)
        
        # Create tables
        create_tables_from_source_structure(target_cursor)
        
        # Copy VFAHEAD
        print("Kopiere VFAHEAD...")
        source_cursor.execute("SELECT * FROM vfahead")
        vfahead_data = source_cursor.fetchall()
        
        for row in vfahead_data:
            target_cursor.execute("""
                INSERT INTO vfahead (
                    vfahead_inr, type, bmdvariante, anlage_codes,
                    beschreibung, kurzzeichen, status, 
                    erstellung_dat, aenderung_dat
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['vfahead_inr'],
                row['type'],
                row['bmdvariante'],
                row['anlage_codes'],
                row['beschreibung'],
                row['kurzzeichen'],
                row['status'],
                row['erstellung_dat'],
                row['aenderung_dat']
            ))
        
        print(f"  {len(vfahead_data)} VFAHEAD Einträge kopiert")
        
        # Copy VFALINE
        print("Kopiere VFALINE...")
        source_cursor.execute("SELECT * FROM vfaline")
        vfaline_data = source_cursor.fetchall()
        
        for row in vfaline_data:
            target_cursor.execute("""
                INSERT INTO vfaline (
                    id, vfahead_inr, gruppe, parameter,
                    daten_char, daten_dec, beschreibung
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row['id'],
                row['vfahead_inr'],
                row['gruppe'],
                row['parameter'],
                row['daten_char'],
                row['daten_dec'],
                row['beschreibung']
            ))
        
        print(f"  {len(vfaline_data)} VFALINE Einträge kopiert")
        
        # Commit
        target_conn.commit()
        print("\n✓ Import erfolgreich abgeschlossen!")
        
        # Cleanup
        source_cursor.close()
        source_conn.close()
        target_cursor.close()
        target_conn.close()
        
    except Exception as e:
        print(f"FEHLER beim Import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    print("=" * 60)
    print("1:1 IMPORT VFAHEAD/VFALINE AUS ORIGINAL-QUELLE")
    print("=" * 60)
    print()
    print("WARNUNG: Die Datenquelle muss noch definiert werden!")
    print()
    print("Optionen:")
    print("1. AS400/DB2 über ODBC")
    print("2. PostgreSQL Datenbank")
    print("3. CSV/Excel Dateien")
    print()
    
    # TODO: Richtige Import-Methode aktivieren!
    
    # Option 1: Von AS400/DB2
    # import_from_db2()
    
    # Option 2: Von PostgreSQL
    # import_from_postgres()
    
    print("FEHLER: Keine Import-Methode aktiviert!")
    print("Bitte definiere die Datenquelle und aktiviere die entsprechende Methode.")

if __name__ == "__main__":
    main()