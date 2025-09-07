#!/usr/bin/env python3
"""
1:1 Import der VFAHEAD und VFALINE Tabellen aus AS400/DB2
ECHTE DATEN - KEINE MANIPULATION!
"""

import pyodbc
import psycopg2
from datetime import datetime
import sys

# Ziel-Datenbank
VARIANTEN_DB = {
    'host': 'localhost',
    'database': 'varianten', 
    'user': 'postgres',
    'password': 'postgres'
}

def create_tables(cursor):
    """Erstellt VFAHEAD und VFALINE mit EXAKTER Struktur aus AS400"""
    
    print("Lösche alte Tabellen...")
    cursor.execute("DROP TABLE IF EXISTS vfaline CASCADE")
    cursor.execute("DROP TABLE IF EXISTS vfahead CASCADE")
    
    print("Erstelle VFAHEAD...")
    cursor.execute("""
        CREATE TABLE vfahead (
            vfahead_inr BIGINT PRIMARY KEY,
            vfahead_status CHAR(1),
            vfahead_type VARCHAR(20),
            vfahead_nummer VARCHAR(20),
            vfahead_beschreibung VARCHAR(50),
            vfahead_bmdvariante VARCHAR(20),
            vfahead_kurzzeichen VARCHAR(10),
            vfahead_g1aktiv CHAR(1),
            vfahead_g2aktiv CHAR(1),
            vfahead_g3aktiv CHAR(1),
            vfahead_g4aktiv CHAR(1),
            vfahead_g5aktiv CHAR(1),
            vfahead_steuerdaten VARCHAR(512),
            vfahead_berechtigung VARCHAR(10),
            vfahead_ersteller VARCHAR(10),
            vfahead_erstelltam TIMESTAMP,
            vfahead_aenderer VARCHAR(10),
            vfahead_aenderung_index TIMESTAMP,
            vfahead_vfamtrx_inr BIGINT
        )
    """)
    
    print("Erstelle VFALINE...")
    cursor.execute("""
        CREATE TABLE vfaline (
            vfaline_inr BIGINT PRIMARY KEY,
            vfaline_status CHAR(1),
            vfaline_anlage VARCHAR(20),
            vfaline_type VARCHAR(20),
            vfaline_nummer VARCHAR(20),
            vfaline_gruppe VARCHAR(20),
            vfaline_parameter VARCHAR(20),
            vfaline_beschreibung VARCHAR(50),
            vfaline_daten_char VARCHAR(50),
            vfaline_daten_dec DECIMAL(18,6),
            vfaline_daten_numm INTEGER,
            vfaline_daten_time TIME,
            vfaline_steuerdaten VARCHAR(512),
            vfaline_berechtigung VARCHAR(10),
            vfaline_ersteller VARCHAR(10),
            vfaline_erstelltam TIMESTAMP,
            vfaline_aenderer VARCHAR(10),
            vfaline_aenderung_index TIMESTAMP,
            vfaline_vfahead_inr BIGINT REFERENCES vfahead(vfahead_inr),
            vfaline_vfamtrx_inr BIGINT
        )
    """)
    
    # Indizes für Performance
    cursor.execute("CREATE INDEX idx_vfahead_type ON vfahead(vfahead_type)")
    cursor.execute("CREATE INDEX idx_vfahead_bmdvariante ON vfahead(vfahead_bmdvariante)")
    cursor.execute("CREATE INDEX idx_vfahead_status ON vfahead(vfahead_status)")
    cursor.execute("CREATE INDEX idx_vfaline_vfahead_inr ON vfaline(vfaline_vfahead_inr)")
    cursor.execute("CREATE INDEX idx_vfaline_gruppe ON vfaline(vfaline_gruppe)")
    cursor.execute("CREATE INDEX idx_vfaline_parameter ON vfaline(vfaline_parameter)")

def import_from_as400(dsn, schema):
    """Importiert VFAHEAD und VFALINE aus AS400"""
    
    print(f"\n{'='*60}")
    print(f"Importiere aus {dsn} - Schema {schema}")
    print('='*60)
    
    # AS400 Verbindung
    db2_conn = pyodbc.connect(f"DSN={dsn};UID=ODBCUSER;PWD=transfer", timeout=30)
    db2_cursor = db2_conn.cursor()
    
    # PostgreSQL Verbindung
    pg_conn = psycopg2.connect(**VARIANTEN_DB)
    pg_cursor = pg_conn.cursor()
    
    try:
        # Import VFAHEAD
        print("\nImportiere VFAHEAD...")
        db2_cursor.execute(f"""
            SELECT 
                VFAHEAD_INR,
                VFAHEAD_STATUS,
                VFAHEAD_TYPE,
                VFAHEAD_NUMMER,
                VFAHEAD_BESCHREIBUNG,
                VFAHEAD_BMDVARIANTE,
                VFAHEAD_KURZZEICHEN,
                VFAHEAD_G1AKTIV,
                VFAHEAD_G2AKTIV,
                VFAHEAD_G3AKTIV,
                VFAHEAD_G4AKTIV,
                VFAHEAD_G5AKTIV,
                VFAHEAD_STEUERDATEN,
                VFAHEAD_BERECHTIGUNG,
                VFAHEAD_ERSTELLER,
                VFAHEAD_ERSTELLTAM,
                VFAHEAD_AENDERER,
                VFAHEAD_AENDERUNG_INDEX,
                VFAHEAD_VFAMTRX_INR
            FROM {schema}.VFAHEAD
            WHERE VFAHEAD_STATUS IN ('A', 'P')
        """)
        
        vfahead_count = 0
        while True:
            rows = db2_cursor.fetchmany(100)
            if not rows:
                break
                
            for row in rows:
                # Handle timestamps
                erstelltam = row[15] if row[15] else None
                aenderung = row[17] if row[17] else None
                
                pg_cursor.execute("""
                    INSERT INTO vfahead (
                        vfahead_inr, vfahead_status, vfahead_type, vfahead_nummer,
                        vfahead_beschreibung, vfahead_bmdvariante, vfahead_kurzzeichen,
                        vfahead_g1aktiv, vfahead_g2aktiv, vfahead_g3aktiv,
                        vfahead_g4aktiv, vfahead_g5aktiv, vfahead_steuerdaten,
                        vfahead_berechtigung, vfahead_ersteller, vfahead_erstelltam,
                        vfahead_aenderer, vfahead_aenderung_index, vfahead_vfamtrx_inr
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (vfahead_inr) DO NOTHING
                """, (
                    int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], row[8], row[9], row[10], row[11], row[12],
                    row[13], row[14], erstelltam, row[16], aenderung, 
                    int(row[18]) if row[18] else None
                ))
                vfahead_count += 1
                
            if vfahead_count % 100 == 0:
                print(f"  {vfahead_count} VFAHEAD importiert...")
                pg_conn.commit()
        
        pg_conn.commit()
        print(f"  ✓ {vfahead_count} VFAHEAD Einträge importiert")
        
        # Import VFALINE (nur für existierende VFAHEAD)
        print("\nImportiere VFALINE...")
        db2_cursor.execute(f"""
            SELECT 
                L.VFALINE_INR,
                L.VFALINE_STATUS,
                L.VFALINE_ANLAGE,
                L.VFALINE_TYPE,
                L.VFALINE_NUMMER,
                L.VFALINE_GRUPPE,
                L.VFALINE_PARAMETER,
                L.VFALINE_BESCHREIBUNG,
                L.VFALINE_DATEN_CHAR,
                L.VFALINE_DATEN_DEC,
                L.VFALINE_DATEN_NUMM,
                L.VFALINE_DATEN_TIME,
                L.VFALINE_STEUERDATEN,
                L.VFALINE_BERECHTIGUNG,
                L.VFALINE_ERSTELLER,
                L.VFALINE_ERSTELLTAM,
                L.VFALINE_AENDERER,
                L.VFALINE_AENDERUNG_INDEX,
                L.VFALINE_VFAHEAD_INR,
                L.VFALINE_VFAMTRX_INR
            FROM {schema}.VFALINE L
            INNER JOIN {schema}.VFAHEAD H ON L.VFALINE_VFAHEAD_INR = H.VFAHEAD_INR
            WHERE L.VFALINE_STATUS IN ('A', 'P')
            AND H.VFAHEAD_STATUS IN ('A', 'P')
        """)
        
        vfaline_count = 0
        while True:
            rows = db2_cursor.fetchmany(500)
            if not rows:
                break
                
            for row in rows:
                # Handle timestamps and time
                erstelltam = row[15] if row[15] else None
                aenderung = row[17] if row[17] else None
                daten_time = row[11] if row[11] else None
                
                pg_cursor.execute("""
                    INSERT INTO vfaline (
                        vfaline_inr, vfaline_status, vfaline_anlage, vfaline_type,
                        vfaline_nummer, vfaline_gruppe, vfaline_parameter,
                        vfaline_beschreibung, vfaline_daten_char, vfaline_daten_dec,
                        vfaline_daten_numm, vfaline_daten_time, vfaline_steuerdaten,
                        vfaline_berechtigung, vfaline_ersteller, vfaline_erstelltam,
                        vfaline_aenderer, vfaline_aenderung_index, vfaline_vfahead_inr,
                        vfaline_vfamtrx_inr
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (vfaline_inr) DO NOTHING
                """, (
                    int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], row[8], row[9], row[10] if row[10] else None,
                    daten_time, row[12], row[13], row[14], erstelltam,
                    row[16], aenderung, int(row[18]) if row[18] else None,
                    int(row[19]) if row[19] else None
                ))
                vfaline_count += 1
                
            if vfaline_count % 500 == 0:
                print(f"  {vfaline_count} VFALINE importiert...")
                pg_conn.commit()
        
        pg_conn.commit()
        print(f"  ✓ {vfaline_count} VFALINE Einträge importiert")
        
    except Exception as e:
        print(f"FEHLER: {e}")
        pg_conn.rollback()
        raise
    finally:
        db2_cursor.close()
        db2_conn.close()
        pg_cursor.close()
        pg_conn.close()

def main():
    print("=" * 60)
    print("1:1 IMPORT VFAHEAD/VFALINE AUS AS400")
    print("=" * 60)
    
    # PostgreSQL Verbindung für Tabellen-Erstellung
    pg_conn = psycopg2.connect(**VARIANTEN_DB)
    pg_cursor = pg_conn.cursor()
    
    # Tabellen erstellen
    create_tables(pg_cursor)
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    
    # Import aus beiden AS400 Systemen
    import_from_as400("MV_Prod", "M01_DAT_LB")
    import_from_as400("PB_Prod", "D01_DAT_LB")
    
    # Statistik
    pg_conn = psycopg2.connect(**VARIANTEN_DB)
    pg_cursor = pg_conn.cursor()
    
    pg_cursor.execute("SELECT COUNT(*) FROM vfahead")
    vfahead_total = pg_cursor.fetchone()[0]
    
    pg_cursor.execute("SELECT COUNT(*) FROM vfaline")
    vfaline_total = pg_cursor.fetchone()[0]
    
    print("\n" + "=" * 60)
    print("IMPORT ABGESCHLOSSEN")
    print("=" * 60)
    print(f"Gesamt VFAHEAD: {vfahead_total}")
    print(f"Gesamt VFALINE: {vfaline_total}")
    
    # Beispiele zeigen
    print("\nBeispiel VFAHEAD Einträge:")
    pg_cursor.execute("""
        SELECT vfahead_type, vfahead_bmdvariante, vfahead_beschreibung 
        FROM vfahead 
        WHERE vfahead_status = 'A'
        LIMIT 5
    """)
    for row in pg_cursor.fetchall():
        print(f"  {row[0]:20} {row[1]:10} {row[2]}")
    
    pg_cursor.close()
    pg_conn.close()

if __name__ == "__main__":
    main()