#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Database connections
GALVANIK_DB = {
    'host': 'localhost',
    'database': 'galvanik',
    'user': 'postgres',
    'password': 'postgres'
}

VARIANTEN_DB = {
    'host': 'localhost',
    'database': 'varianten',
    'user': 'postgres',
    'password': 'postgres'
}

def decode_code(code):
    """Decode a G or A code into its components"""
    if len(code) < 12:
        return None
    
    return {
        'anlage': code[0:2] if code.startswith('A') else code[0:2],
        'vb': code[2:4],
        'hb': code[4:6],
        'pas': code[6:8],
        'nb': code[8:10]
    }

def get_mapping(cursor, position, wert):
    """Get text description for a position/value combination"""
    cursor.execute(
        "SELECT text FROM mappings WHERE position = %s AND wert = %s",
        (position, wert)
    )
    result = cursor.fetchone()
    return result['text'] if result else f"Code {wert}"

def main():
    print("Starting import process...")
    
    # Connect to both databases
    galvanik_conn = psycopg2.connect(**GALVANIK_DB)
    varianten_conn = psycopg2.connect(**VARIANTEN_DB)
    
    galvanik_cur = galvanik_conn.cursor(cursor_factory=RealDictCursor)
    varianten_cur = varianten_conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Clear existing codes
        varianten_cur.execute("DELETE FROM codes")
        
        # Get all distinct codes from galvanik
        galvanik_cur.execute("""
            SELECT stueckliste as code, anlage, COUNT(*) as count
            FROM artikel 
            WHERE stueckliste IS NOT NULL 
              AND (stueckliste LIKE 'G%' OR stueckliste LIKE 'A6%')
            GROUP BY stueckliste, anlage
            ORDER BY anlage, stueckliste
        """)
        
        codes = galvanik_cur.fetchall()
        print(f"Found {len(codes)} unique codes")
        
        # Process each code
        for row in codes:
            code = row['code']
            decoded = decode_code(code)
            
            if not decoded:
                print(f"Skipping invalid code: {code}")
                continue
            
            # Get text descriptions from mappings
            vb_text = get_mapping(varianten_cur, 'VB', decoded['vb'])
            hb_text = get_mapping(varianten_cur, 'HB', decoded['hb'])
            pas_text = get_mapping(varianten_cur, 'PAS', decoded['pas'])
            nb_text = get_mapping(varianten_cur, 'NB', decoded['nb'])
            
            # Insert into codes table (with trimmed anlage)
            varianten_cur.execute("""
                INSERT INTO codes (
                    anlage, code, vb, hb, pas, nb,
                    vb_text, hb_text, pas_text, nb_text,
                    artikel_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['anlage'].strip() if row['anlage'] else row['anlage'], code,
                decoded['vb'], decoded['hb'], decoded['pas'], decoded['nb'],
                vb_text, hb_text, pas_text, nb_text,
                row['count']
            ))
        
        # Commit changes
        varianten_conn.commit()
        print(f"Successfully imported {len(codes)} codes")
        
        # Show statistics
        varianten_cur.execute("""
            SELECT anlage, COUNT(*) as code_count, SUM(artikel_count) as artikel_total
            FROM codes
            GROUP BY anlage
            ORDER BY anlage
        """)
        
        print("\nStatistics by Anlage:")
        print("-" * 40)
        for stat in varianten_cur.fetchall():
            print(f"{stat['anlage']:5} - {stat['code_count']:4} codes, {stat['artikel_total']:5} articles")
        
    except Exception as e:
        print(f"Error: {e}")
        varianten_conn.rollback()
        sys.exit(1)
    
    finally:
        galvanik_cur.close()
        varianten_cur.close()
        galvanik_conn.close()
        varianten_conn.close()

if __name__ == "__main__":
    main()