#!/usr/bin/env python3
"""
Spezielles Mapping für A60-Codes.
A60 verwendet andere Types: VTROCK, TROCKEN, BESCHPROG statt VOR, HAUPT, PASSIV, NACHBEHAND
"""

import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'varianten',
    'user': 'postgres',
    'password': 'postgres'
}

def map_a60_codes():
    """Map A60 codes with special logic"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("Special A60 Mapping...")
    print("=" * 50)
    
    # Get all A60 codes
    cursor.execute("SELECT * FROM codes WHERE anlage = 'A60' ORDER BY code")
    codes = cursor.fetchall()
    
    print(f"Processing {len(codes)} A60 codes...")
    
    for code in codes:
        code_id = code[0]
        code_str = code[2]
        vb = code[3]
        hb = code[4]
        pas = code[5]
        nb = code[6]
        
        print(f"\nCode: {code_str}")
        
        updates = {}
        
        # VB: Use G1 entries or generic ones
        if vb:
            cursor.execute("""
                SELECT vfahead_inr, vfahead_beschreibung
                FROM vfahead
                WHERE TRIM(vfahead_type) = 'VOR'
                AND TRIM(vfahead_bmdvariante) = %s
                AND vfahead_g1aktiv = 'T'
                LIMIT 1
            """, (vb,))
            result = cursor.fetchone()
            if result:
                updates['vb_vfahead_inr'] = result[0]
                updates['vb_beschreibung'] = result[1].strip()
                print(f"  VB={vb}: Found G1 entry - {result[1].strip()}")
        
        # HB: For HB=60 (dual process), we need special handling
        # For others, use G1 entries
        if hb == '60':
            # Dual process - no direct VFAHEAD entry exists
            print(f"  HB=60: Dual-Process (no VFAHEAD)")
            # Maybe create a synthetic entry or use a default
        elif hb:
            cursor.execute("""
                SELECT vfahead_inr, vfahead_beschreibung
                FROM vfahead
                WHERE TRIM(vfahead_type) = 'HAUPT'
                AND TRIM(vfahead_bmdvariante) = %s
                AND vfahead_g1aktiv = 'T'
                LIMIT 1
            """, (hb,))
            result = cursor.fetchone()
            if result:
                updates['hb_vfahead_inr'] = result[0]
                updates['hb_beschreibung'] = result[1].strip()
                print(f"  HB={hb}: Found G1 entry - {result[1].strip()}")
        
        # PAS: Use G1 entries
        if pas:
            cursor.execute("""
                SELECT vfahead_inr, vfahead_beschreibung
                FROM vfahead
                WHERE TRIM(vfahead_type) = 'PASSIV'
                AND TRIM(vfahead_bmdvariante) = %s
                AND vfahead_g1aktiv = 'T'
                LIMIT 1
            """, (pas,))
            result = cursor.fetchone()
            if result:
                updates['pas_vfahead_inr'] = result[0]
                updates['pas_beschreibung'] = result[1].strip()
                print(f"  PAS={pas}: Found G1 entry - {result[1].strip()}")
        
        # NB: Try A60-specific BESCHPROG first, then fallback to G1
        if nb:
            # First try A60-specific BESCHPROG
            cursor.execute("""
                SELECT vfahead_inr, vfahead_beschreibung
                FROM vfahead
                WHERE TRIM(vfahead_type) = 'BESCHPROG'
                AND TRIM(vfahead_bmdvariante) = %s
                AND vfahead_beschreibung LIKE '%%A60%%'
                ORDER BY 
                    CASE 
                        WHEN vfahead_beschreibung LIKE '%%Standard%%' THEN 0
                        ELSE 1
                    END
                LIMIT 1
            """, (nb,))
            result = cursor.fetchone()
            
            if result:
                updates['nb_vfahead_inr'] = result[0]
                updates['nb_beschreibung'] = result[1].strip()
                print(f"  NB={nb}: Found A60 BESCHPROG - {result[1].strip()}")
            else:
                # Fallback to G1 NACHBEHAND
                cursor.execute("""
                    SELECT vfahead_inr, vfahead_beschreibung
                    FROM vfahead
                    WHERE TRIM(vfahead_type) IN ('NACH', 'NACHBEHAND')
                    AND TRIM(vfahead_bmdvariante) = %s
                    AND vfahead_g1aktiv = 'T'
                    LIMIT 1
                """, (nb,))
                result = cursor.fetchone()
                if result:
                    updates['nb_vfahead_inr'] = result[0]
                    updates['nb_beschreibung'] = result[1].strip()
                    print(f"  NB={nb}: Found G1 NACH - {result[1].strip()}")
        
        # Update the code record
        if updates:
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [code_id]
            cursor.execute(f"""
                UPDATE codes SET {set_clause}
                WHERE id = %s
            """, values)
    
    conn.commit()
    
    # Show results
    print("\n" + "=" * 50)
    print("A60 Mapping Results:")
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(vb_vfahead_inr) as vb_mapped,
            COUNT(hb_vfahead_inr) as hb_mapped,
            COUNT(pas_vfahead_inr) as pas_mapped,
            COUNT(nb_vfahead_inr) as nb_mapped
        FROM codes
        WHERE anlage = 'A60'
    """)
    
    stats = cursor.fetchone()
    print(f"  Total: {stats[0]} codes")
    print(f"  VB:  {stats[1]}/{stats[0]} mapped")
    print(f"  HB:  {stats[2]}/{stats[0]} mapped")
    print(f"  PAS: {stats[3]}/{stats[0]} mapped")
    print(f"  NB:  {stats[4]}/{stats[0]} mapped")
    
    # Show parameter counts
    print("\nParameter counts for A60 mappings:")
    cursor.execute("""
        SELECT DISTINCT c.nb_vfahead_inr, c.nb_beschreibung, COUNT(v.vfaline_inr) as params
        FROM codes c
        LEFT JOIN vfaline v ON v.vfaline_vfahead_inr = c.nb_vfahead_inr
        WHERE c.anlage = 'A60' AND c.nb_vfahead_inr IS NOT NULL
        GROUP BY c.nb_vfahead_inr, c.nb_beschreibung
    """)
    
    for row in cursor.fetchall():
        if row[2] > 0:
            print(f"  {row[1]}: {row[2]} parameters")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    map_a60_codes()