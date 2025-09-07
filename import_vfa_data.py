#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'database': 'varianten',
    'user': 'postgres',
    'password': 'postgres'
}

def create_vfahead_entries(cursor):
    """Create VFAHEAD entries based on unique position/value combinations from codes"""
    
    # Get all unique combinations of positions and values
    cursor.execute("""
        SELECT DISTINCT anlage, vb, hb, pas, nb 
        FROM codes 
        ORDER BY anlage, vb, hb, pas, nb
    """)
    
    codes = cursor.fetchall()
    vfahead_map = {}
    
    # Process each unique combination
    for code in codes:
        anlage = code['anlage']
        
        # Create VFAHEAD entries for each position
        positions = [
            ('VB', code['vb'], 'VOR', 'Vorbehandlung'),
            ('HB', code['hb'], 'HAUPT', 'Hauptbehandlung'),
            ('PAS', code['pas'], 'PASSIV', 'Passivierung'),
            ('NB', code['nb'], 'NACHBEHAND', 'Nachbehandlung')
        ]
        
        for pos_name, value, type_name, desc_prefix in positions:
            if value:
                key = f"{anlage}_{type_name}_{value}"
                
                if key not in vfahead_map:
                    # Get description from mappings
                    cursor.execute(
                        "SELECT text FROM mappings WHERE position = %s AND wert = %s",
                        (pos_name, value)
                    )
                    mapping = cursor.fetchone()
                    desc = mapping['text'] if mapping else f"Code {value}"
                    
                    # Insert VFAHEAD entry with better descriptions
                    full_desc = f"{desc}"
                    if type_name == 'VOR':
                        full_desc = f"Vorbehandlung {desc}"
                    elif type_name == 'HAUPT':
                        full_desc = f"Verzinkung {desc}"
                        if value == '60':
                            full_desc = "Dual-Prozess Alkalisch/Sauer Verzinkung"
                    elif type_name == 'PASSIV':
                        full_desc = f"Passivierung {desc}"
                    elif type_name == 'NACHBEHAND':
                        full_desc = f"Nachbehandlung {desc}"
                        if value == '22':
                            full_desc = "Nachbehandlung mit Versiegelung Typ 3"
                    
                    cursor.execute("""
                        INSERT INTO vfahead (type, bmdvariante, anlage_codes, beschreibung, kurzzeichen, status)
                        VALUES (%s, %s, %s, %s, %s, 'A')
                        RETURNING vfahead_inr
                    """, (
                        type_name, 
                        value,
                        [anlage],  # PostgreSQL array
                        full_desc,
                        f"{pos_name}{value}",
                    ))
                    
                    vfahead_inr = cursor.fetchone()['vfahead_inr']
                    vfahead_map[key] = vfahead_inr
                    
                    # Create sample VFALINE parameters based on type
                    create_vfaline_parameters(cursor, vfahead_inr, type_name, value)
    
    return vfahead_map

def create_vfaline_parameters(cursor, vfahead_inr, type_name, value):
    """Create sample VFALINE parameters for a VFAHEAD entry"""
    
    # Define parameters based on type
    if type_name == 'VOR':
        parameters = [
            ('STANDARD', 'SCHALTER', None, 1, 'Aktivierung'),
            ('STANDARD', 'TEMP_1', None, 60, 'Temperatur Station 1'),
            ('STANDARD', 'DREHZAHL_1', None, 25, 'Drehzahl Station 1'),
            ('STANDARD', 'ZEIT', None, 120, 'Behandlungszeit in Sekunden')
        ]
    elif type_name == 'HAUPT':
        if value == '60':  # Dual-Prozess
            parameters = [
                ('ALKZN', 'WIRKGRAD', None, 65, 'Wirkungsgrad Alkalisch'),
                ('ALKZN', 'ABSFAK', None, 0.23, 'Abscheidefaktor Alkalisch'),
                ('SZN', 'WIRKGRAD', None, 95, 'Wirkungsgrad Sauer'),
                ('SZN', 'ABSFAK', None, 0.45, 'Abscheidefaktor Sauer'),
                ('STANDARD', 'TAKTE', None, 8, 'Anzahl Takte')
            ]
        else:
            parameters = [
                ('ALKZN', 'WIRKGRAD', None, 75, 'Wirkungsgrad'),
                ('ALKZN', 'ABSFAK', None, 0.30, 'Abscheidefaktor'),
                ('STANDARD', 'TEMP_1', None, 25, 'Badtemperatur'),
                ('STANDARD', 'TAKTE', None, int(value) // 10 * 2, 'Anzahl Takte')
            ]
    elif type_name == 'PASSIV':
        parameters = [
            ('PASSIV', 'TEMP_1', None, 35, 'Temperatur'),
            ('PASSIV', 'ZEIT', None, 120 if value in ['22', '23'] else 60, 'Passivierzeit'),
            ('PASSIV', 'PH_WERT', None, 2.0 if value == '10' else 1.8, 'pH-Wert'),
            ('STANDARD', 'SCHALTER', None, 1, 'Aktivierung')
        ]
    elif type_name in ['NACHBEHAND', 'BESCHPROG']:
        parameters = [
            ('VERSIEG', 'TYPE', '3' if value == '22' else '1', None, 'Versiegelungstyp'),
            ('VERSIEG', 'TEMP', None, 80, 'Temperatur'),
            ('ABTROPFEN', 'ZEIT', None, 30, 'Abtropfzeit'),
            ('STANDARD', 'SCHALTER', None, 1, 'Aktivierung')
        ]
    else:
        parameters = []
    
    # Insert parameters
    for gruppe, param, char_val, dec_val, beschr in parameters:
        cursor.execute("""
            INSERT INTO vfaline (vfahead_inr, gruppe, parameter, daten_char, daten_dec, beschreibung)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (vfahead_inr, gruppe, param, char_val, dec_val, beschr))

def update_codes_with_vfahead_refs(cursor, vfahead_map):
    """Add reference columns to codes table linking to VFAHEAD entries"""
    
    # Add columns if they don't exist
    cursor.execute("""
        ALTER TABLE codes 
        ADD COLUMN IF NOT EXISTS vb_vfahead_inr INTEGER REFERENCES vfahead(vfahead_inr),
        ADD COLUMN IF NOT EXISTS hb_vfahead_inr INTEGER REFERENCES vfahead(vfahead_inr),
        ADD COLUMN IF NOT EXISTS pas_vfahead_inr INTEGER REFERENCES vfahead(vfahead_inr),
        ADD COLUMN IF NOT EXISTS nb_vfahead_inr INTEGER REFERENCES vfahead(vfahead_inr)
    """)
    
    # Update codes with references
    cursor.execute("SELECT * FROM codes")
    codes = cursor.fetchall()
    
    for code in codes:
        updates = []
        params = []
        
        # Build update query
        for pos, col in [('VOR', 'vb'), ('HAUPT', 'hb'), ('PASSIV', 'pas'), ('NACHBEHAND', 'nb')]:
            key = f"{code['anlage']}_{pos}_{code[col]}"
            if key in vfahead_map:
                updates.append(f"{col}_vfahead_inr = %s")
                params.append(vfahead_map[key])
        
        if updates:
            params.append(code['id'])
            cursor.execute(
                f"UPDATE codes SET {', '.join(updates)} WHERE id = %s",
                params
            )

def main():
    print("Starting VFAHEAD/VFALINE data import...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Clear existing data
        cursor.execute("DELETE FROM vfaline")
        cursor.execute("DELETE FROM vfahead")
        
        # Create VFAHEAD entries and parameters
        vfahead_map = create_vfahead_entries(cursor)
        print(f"Created {len(vfahead_map)} VFAHEAD entries")
        
        # Update codes table with references
        update_codes_with_vfahead_refs(cursor, vfahead_map)
        print("Updated codes table with VFAHEAD references")
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) as count FROM vfahead")
        vfahead_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM vfaline")
        vfaline_count = cursor.fetchone()['count']
        
        print(f"\nStatistics:")
        print(f"- VFAHEAD entries: {vfahead_count}")
        print(f"- VFALINE parameters: {vfaline_count}")
        
        # Show sample data
        cursor.execute("""
            SELECT h.type, h.bmdvariante, h.beschreibung, COUNT(l.id) as param_count
            FROM vfahead h
            LEFT JOIN vfaline l ON h.vfahead_inr = l.vfahead_inr
            GROUP BY h.vfahead_inr, h.type, h.bmdvariante, h.beschreibung
            ORDER BY h.type, h.bmdvariante
            LIMIT 10
        """)
        
        print("\nSample VFAHEAD entries with parameter counts:")
        for row in cursor.fetchall():
            print(f"  {row['type']:12} {row['bmdvariante']:3} - {row['beschreibung'][:40]:40} ({row['param_count']} params)")
        
        conn.commit()
        print("\nImport completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()