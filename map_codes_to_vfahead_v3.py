#!/usr/bin/env python3
"""
Mappt die Artikel-Codes zu den echten VFAHEAD Einträgen.
Version 3: G1 komplett ignorieren (alte Anlage)
"""

import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'varianten',
    'user': 'postgres',
    'password': 'postgres'
}

def get_vfahead_for_position(cursor, anlage, position_type, bmdvariante):
    """Find VFAHEAD entry for a specific position and anlage"""
    
    if not bmdvariante:
        return (None, None)
    
    # Map position to type
    type_mapping = {
        'VB': ['VOR'],
        'HB': ['HAUPT'],
        'PAS': ['PASSIV'],
        'NB': ['NACH', 'NACHBEHAND', 'BESCHPROG']
    }
    
    types = type_mapping.get(position_type, [])
    if not types:
        return (None, None)
    
    # Build WHERE clause for types
    type_conditions = " OR ".join(["TRIM(vfahead_type) = %s" for _ in types])
    
    # Build query based on anlage - EXCLUDE G1!
    if anlage == 'G2':
        anlage_condition = "vfahead_g2aktiv = 'T' AND (vfahead_g1aktiv IS NULL OR vfahead_g1aktiv != 'T')"
    elif anlage == 'G3':
        anlage_condition = "vfahead_g3aktiv = 'T' AND (vfahead_g1aktiv IS NULL OR vfahead_g1aktiv != 'T')"
    elif anlage == 'G4':
        anlage_condition = "vfahead_g4aktiv = 'T' AND (vfahead_g1aktiv IS NULL OR vfahead_g1aktiv != 'T')"
    elif anlage == 'G5':
        anlage_condition = "vfahead_g5aktiv = 'T' AND (vfahead_g1aktiv IS NULL OR vfahead_g1aktiv != 'T')"
    elif anlage in ['A60', 'A6']:
        # For A60: Look for A60-specific entries OR entries without any G-flags (including G1)
        anlage_condition = """(
            vfahead_beschreibung LIKE '%%A60%%' 
            OR vfahead_beschreibung LIKE '%%A6%%'
            OR (
                (vfahead_g1aktiv IS NULL OR vfahead_g1aktiv != 'T')
                AND (vfahead_g2aktiv IS NULL OR vfahead_g2aktiv != 'T')
                AND (vfahead_g3aktiv IS NULL OR vfahead_g3aktiv != 'T')
                AND (vfahead_g4aktiv IS NULL OR vfahead_g4aktiv != 'T')
                AND (vfahead_g5aktiv IS NULL OR vfahead_g5aktiv != 'T')
            )
        )"""
    else:
        return (None, None)
    
    # Build complete query using format instead of f-string
    query_template = """
        SELECT vfahead_inr, vfahead_beschreibung
        FROM vfahead
        WHERE ({})
        AND TRIM(vfahead_bmdvariante) = %s
        AND {}
        AND vfahead_status IN ('A', 'P')
        ORDER BY 
            CASE 
                WHEN vfahead_beschreibung LIKE '%%Standard%%' THEN 0
                WHEN vfahead_beschreibung LIKE '%%Schrauben%%' THEN 1
                ELSE 2
            END,
            vfahead_inr DESC
        LIMIT 1
    """
    
    query = query_template.format(type_conditions, anlage_condition)
    params = types + [bmdvariante]
    cursor.execute(query, params)
    result = cursor.fetchone()
    
    if result:
        return result[0], result[1]
    
    return (None, None)

def main():
    print("Mapping Codes to VFAHEAD (Version 3 - NO G1)...")
    print("Excluding all G1 entries (obsolete plant)")
    print("=" * 60)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # First, show how many G1 entries we're excluding
    cursor.execute("SELECT COUNT(*) FROM vfahead WHERE vfahead_g1aktiv = 'T'")
    g1_count = cursor.fetchone()[0]
    print(f"Excluding {g1_count} G1 entries from mapping")
    
    # Get all codes
    cursor.execute("SELECT * FROM codes ORDER BY anlage, code")
    codes = cursor.fetchall()
    
    # Clear existing mappings first
    print("\nClearing existing mappings...")
    cursor.execute("""
        UPDATE codes SET 
            vb_vfahead_inr = NULL,
            hb_vfahead_inr = NULL,
            pas_vfahead_inr = NULL,
            nb_vfahead_inr = NULL,
            vb_beschreibung = NULL,
            hb_beschreibung = NULL,
            pas_beschreibung = NULL,
            nb_beschreibung = NULL
    """)
    conn.commit()
    
    updated = 0
    not_found = []
    
    print(f"\nProcessing {len(codes)} codes...")
    
    for code in codes:
        # code columns: 0=id, 1=anlage, 2=code, 3=vb, 4=hb, 5=pas, 6=nb
        code_id = code[0]
        anlage = code[1]
        code_str = code[2]
        
        # Find VFAHEAD for each position
        vb_inr, vb_desc = get_vfahead_for_position(cursor, anlage, 'VB', code[3])
        hb_inr, hb_desc = get_vfahead_for_position(cursor, anlage, 'HB', code[4])
        pas_inr, pas_desc = get_vfahead_for_position(cursor, anlage, 'PAS', code[5])
        nb_inr, nb_desc = get_vfahead_for_position(cursor, anlage, 'NB', code[6])
        
        # Update code with references
        cursor.execute("""
            UPDATE codes SET
                vb_vfahead_inr = %s,
                hb_vfahead_inr = %s,
                pas_vfahead_inr = %s,
                nb_vfahead_inr = %s,
                vb_beschreibung = %s,
                hb_beschreibung = %s,
                pas_beschreibung = %s,
                nb_beschreibung = %s
            WHERE id = %s
        """, (
            vb_inr, hb_inr, pas_inr, nb_inr,
            vb_desc.strip() if vb_desc else None,
            hb_desc.strip() if hb_desc else None,
            pas_desc.strip() if pas_desc else None,
            nb_desc.strip() if nb_desc else None,
            code_id
        ))
        
        # Track missing mappings
        missing = []
        if not vb_inr and code[3]:
            missing.append(f"VB={code[3]}")
        if not hb_inr and code[4]:
            missing.append(f"HB={code[4]}")
        if not pas_inr and code[5]:
            missing.append(f"PAS={code[5]}")
        if not nb_inr and code[6]:
            missing.append(f"NB={code[6]}")
        
        if missing:
            not_found.append(f"{code_str} ({anlage}): {', '.join(missing)}")
        else:
            updated += 1
        
        if len(codes) > 10 and (code_id % 10 == 0):
            print(f"  Processed {code_id}/{len(codes)}...")
            conn.commit()
    
    conn.commit()
    
    print(f"\n✓ Mapped {updated}/{len(codes)} codes successfully")
    
    if not_found:
        print(f"\n⚠ Could not find VFAHEAD for {len(not_found)} positions:")
        for item in not_found[:10]:
            print(f"  - {item}")
        if len(not_found) > 10:
            print(f"  ... and {len(not_found) - 10} more")
    
    # Show statistics per anlage
    print("\nMapping Statistics by Anlage:")
    for anlage in ['G2', 'G3', 'G4', 'G5', 'A60']:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(vb_vfahead_inr) as vb_mapped,
                COUNT(hb_vfahead_inr) as hb_mapped,
                COUNT(pas_vfahead_inr) as pas_mapped,
                COUNT(nb_vfahead_inr) as nb_mapped
            FROM codes
            WHERE anlage = %s
        """, (anlage,))
        
        stats = cursor.fetchone()
        if stats[0] > 0:
            print(f"\n  {anlage}:")
            print(f"    Total: {stats[0]} codes")
            print(f"    VB:  {stats[1]}/{stats[0]} ({100*stats[1]//stats[0] if stats[0] > 0 else 0}%)")
            print(f"    HB:  {stats[2]}/{stats[0]} ({100*stats[2]//stats[0] if stats[0] > 0 else 0}%)")
            print(f"    PAS: {stats[3]}/{stats[0]} ({100*stats[3]//stats[0] if stats[0] > 0 else 0}%)")
            print(f"    NB:  {stats[4]}/{stats[0]} ({100*stats[4]//stats[0] if stats[0] > 0 else 0}%)")
    
    # Check for G1 contamination
    print("\nChecking for G1 contamination...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM codes c
        JOIN vfahead v ON c.vb_vfahead_inr = v.vfahead_inr
        WHERE v.vfahead_g1aktiv = 'T'
    """)
    g1_vb = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM codes c
        JOIN vfahead v ON c.hb_vfahead_inr = v.vfahead_inr
        WHERE v.vfahead_g1aktiv = 'T'
    """)
    g1_hb = cursor.fetchone()[0]
    
    if g1_vb > 0 or g1_hb > 0:
        print(f"  WARNING: Found G1 entries in mapping!")
        print(f"    VB with G1: {g1_vb}")
        print(f"    HB with G1: {g1_hb}")
    else:
        print("  ✓ No G1 entries in mapping")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()