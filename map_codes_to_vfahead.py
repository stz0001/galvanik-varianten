#!/usr/bin/env python3
"""
Mappt die Artikel-Codes zu den echten VFAHEAD Einträgen basierend auf:
- Type (VOR, HAUPT, PASSIV, NACH/BESCHPROG)
- BMDVariante (10, 20, 30, etc.)
- Anlage (G2, G3, G4, G5, A60)
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'database': 'varianten',
    'user': 'postgres',
    'password': 'postgres'
}

def get_vfahead_for_position(cursor, anlage, position_type, bmdvariante):
    """Find VFAHEAD entry for a specific position"""
    
    # Map position to type
    type_mapping = {
        'VB': ['VOR'],
        'HB': ['HAUPT'],
        'PAS': ['PASSIV'],
        'NB': ['NACH', 'BESCHPROG', 'NACHBEHAND']
    }
    
    types = type_mapping.get(position_type, [])
    if not types or not bmdvariante:
        return (None, None)
    
    # Build query based on anlage
    if anlage in ['G2', 'G3', 'G4', 'G5']:
        # For G anlagen, use the specific flags
        anlage_field = f"vfahead_{anlage.lower()}aktiv"
        type_conditions = " OR ".join(["TRIM(vfahead_type) = %s" for _ in types])
        
        query_template = """
            SELECT vfahead_inr, vfahead_beschreibung
            FROM vfahead
            WHERE ({})
            AND TRIM(vfahead_bmdvariante) = %s
            AND {} = 'T'
            AND vfahead_status IN ('A', 'P')
            ORDER BY vfahead_inr
            LIMIT 1
        """
        query = query_template.format(type_conditions, anlage_field)
        params = types + [bmdvariante]
        cursor.execute(query, params)
    else:
        # For A60, look in description or use different logic
        type_conditions = " OR ".join(["TRIM(vfahead_type) = %s" for _ in types])
        query_template = """
            SELECT vfahead_inr, vfahead_beschreibung
            FROM vfahead
            WHERE ({})
            AND TRIM(vfahead_bmdvariante) = %s
            AND vfahead_status IN ('A', 'P')
            AND (vfahead_beschreibung LIKE '%%A60%%' OR vfahead_beschreibung LIKE '%%A6%%')
            ORDER BY vfahead_inr
            LIMIT 1
        """
        query = query_template.format(type_conditions)
        params = types + [bmdvariante]
        cursor.execute(query, params)
    
    result = cursor.fetchone()
    if result:
        return result[0], result[1]  # vfahead_inr, vfahead_beschreibung
    
    # If not found with specific anlage, try without
    type_conditions = " OR ".join(["TRIM(vfahead_type) = %s" for _ in types])
    query_template = """
        SELECT vfahead_inr, vfahead_beschreibung
        FROM vfahead
        WHERE ({})
        AND TRIM(vfahead_bmdvariante) = %s
        AND vfahead_status IN ('A', 'P')
        ORDER BY vfahead_inr
        LIMIT 1
    """
    query = query_template.format(type_conditions)
    params = types + [bmdvariante]
    cursor.execute(query, params)
    result = cursor.fetchone()
    
    return (result[0], result[1]) if result else (None, None)  # vfahead_inr, vfahead_beschreibung

def main():
    print("Mapping Codes to VFAHEAD...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()  # Use regular cursor to avoid psycopg2 RealDictCursor bug
    
    # Get all codes
    cursor.execute("SELECT * FROM codes ORDER BY anlage, code")
    codes = cursor.fetchall()
    
    updated = 0
    not_found = []
    
    for code in codes:
        # code columns: 0=id, 1=anlage, 2=code, 3=vb, 4=hb, 5=pas, 6=nb
        # Find VFAHEAD for each position
        vb_inr, vb_desc = get_vfahead_for_position(cursor, code[1], 'VB', code[3])
        hb_inr, hb_desc = get_vfahead_for_position(cursor, code[1], 'HB', code[4])
        pas_inr, pas_desc = get_vfahead_for_position(cursor, code[1], 'PAS', code[5])
        nb_inr, nb_desc = get_vfahead_for_position(cursor, code[1], 'NB', code[6])
        
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
            vb_desc, hb_desc, pas_desc, nb_desc,
            code[0]  # id
        ))
        
        # Track missing mappings
        missing = []
        if not vb_inr and code[3]:  # vb
            missing.append(f"VB={code[3]}")
        if not hb_inr and code[4]:  # hb
            missing.append(f"HB={code[4]}")
        if not pas_inr and code[5]:  # pas
            missing.append(f"PAS={code[5]}")
        if not nb_inr and code[6]:  # nb
            missing.append(f"NB={code[6]}")
        
        if missing:
            not_found.append(f"{code[2]} ({code[1]}): {', '.join(missing)}")  # code, anlage
        else:
            updated += 1
        
        if len(codes) > 10 and updated % 10 == 0:
            print(f"  Processed {updated}/{len(codes)}...")
    
    conn.commit()
    
    print(f"\n✓ Mapped {updated}/{len(codes)} codes successfully")
    
    if not_found:
        print(f"\n⚠ Could not find VFAHEAD for {len(not_found)} positions:")
        for item in not_found[:10]:
            print(f"  - {item}")
        if len(not_found) > 10:
            print(f"  ... and {len(not_found) - 10} more")
    
    # Show statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(vb_vfahead_inr) as vb_mapped,
            COUNT(hb_vfahead_inr) as hb_mapped,
            COUNT(pas_vfahead_inr) as pas_mapped,
            COUNT(nb_vfahead_inr) as nb_mapped
        FROM codes
    """)
    
    stats = cursor.fetchone()
    # stats columns: 0=total, 1=vb_mapped, 2=hb_mapped, 3=pas_mapped, 4=nb_mapped
    print(f"\nMapping Statistics:")
    print(f"  VB:  {stats[1]}/{stats[0]} mapped")
    print(f"  HB:  {stats[2]}/{stats[0]} mapped")
    print(f"  PAS: {stats[3]}/{stats[0]} mapped")
    print(f"  NB:  {stats[4]}/{stats[0]} mapped")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()