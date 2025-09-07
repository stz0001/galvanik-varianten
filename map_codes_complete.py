#!/usr/bin/env python3
"""
Map article codes to VFAHEAD programs
Handles both G-plants and A60 with their different structures
"""

import psycopg2
from datetime import datetime

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host='localhost',
    database='varianten',
    user='postgres',
    password='postgres'
)
pg_cursor = pg_conn.cursor()

print(f"\n=== Mapping Codes to VFAHEAD ===")
print(f"Start: {datetime.now()}")

# First, import all artikel codes
print("\n1. Importing artikel codes...")
galvanik_conn = psycopg2.connect(
    host='localhost',
    database='galvanik',
    user='postgres',
    password='postgres'
)
galvanik_cursor = galvanik_conn.cursor()

# Get all articles with codes (codes are in stueckliste column)
galvanik_cursor.execute("""
    SELECT id, stueckliste, anlage 
    FROM artikel 
    WHERE stueckliste IS NOT NULL AND stueckliste != ''
    LIMIT 10000
""")

articles = galvanik_cursor.fetchall()
print(f"Found {len(articles)} articles with codes")

# Process each article
codes_data = []
for artikel_id, stueckliste, anlage in articles:
    # stueckliste contains the full code (e.g., "G41010602310" or "A61060102210")
    code = stueckliste.strip()
    
    # Determine if it's a G-code or A-code based on first character
    g_code = code if code.startswith('G') else None
    a_code = code if code.startswith('A') else None
    # Process G-code
    if g_code and len(g_code) >= 12:
        anlage = g_code[0:2]  # G2, G3, G4, G5
        if anlage in ['G2', 'G3', 'G4', 'G5']:
            vb = g_code[2:4]
            hb = g_code[4:6]
            pas = g_code[6:8]
            nb = g_code[8:10]
            xx = g_code[10:12] if len(g_code) >= 12 else '00'
            
            codes_data.append({
                'code': g_code,
                'anlage': anlage,
                'anlage_typ': 'G',
                'vb': vb,
                'hb': hb,
                'pas': pas,
                'nb': nb,
                'xx': xx,
                'artikel_inr': artikel_id
            })
    
    # Process A-code
    if a_code and len(a_code) >= 12:
        anlage = a_code[0:2]  # A6 (nur 2 Zeichen!)
        if anlage == 'A6':
            vb = a_code[2:4]   # Position 3-4
            hb = a_code[4:6]   # Position 5-6
            pas = a_code[6:8]  # Position 7-8
            nb = a_code[8:10]  # Position 9-10
            xx = a_code[10:12] # Position 11-12
            
            codes_data.append({
                'code': a_code,
                'anlage': 'A6',  # Verwende A6 (nicht A60)
                'anlage_typ': 'A60',
                'vb': vb,
                'hb': hb,
                'pas': pas,
                'nb': nb,
                'xx': xx,
                'artikel_inr': artikel_id
            })

print(f"Processed {len(codes_data)} codes")

# Group by unique codes and count articles
from collections import defaultdict
code_groups = defaultdict(list)
for data in codes_data:
    code_groups[data['code']].append(data['artikel_inr'])

print(f"Found {len(code_groups)} unique codes")

# Insert unique codes into database
print("\n2. Inserting codes into database...")
inserted = 0
for code, artikel_list in code_groups.items():
    # Get first occurrence for structure
    code_data = next(d for d in codes_data if d['code'] == code)
    
    pg_cursor.execute("""
        INSERT INTO codes (code, anlage, anlage_typ, vb, hb, pas, nb, xx, artikel_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (code) DO UPDATE 
        SET artikel_count = EXCLUDED.artikel_count
    """, (
        code,
        code_data['anlage'],
        code_data['anlage_typ'],
        code_data['vb'],
        code_data['hb'],
        code_data['pas'],
        code_data['nb'],
        code_data['xx'],
        len(artikel_list)
    ))
    inserted += 1

pg_conn.commit()
print(f"✓ Inserted/updated {inserted} codes")

# Now map to VFAHEAD
print("\n3. Mapping codes to VFAHEAD programs...")

def find_vfahead_universal(bmdvariante, type_name, source_db='PB_Prod'):
    """Find ALL matching VFAHEAD entries for VOR/PASSIV - but ONLY within same data source!"""
    
    # Pad bmdvariante to 20 characters (AS400 CHAR field)
    bmdvariante = str(bmdvariante).ljust(20)
    # Pad type_name to 20 characters (AS400 CHAR field)
    type_name = str(type_name).ljust(20)
    
    # Query for ALL matching VFAHEAD - but ONLY from the correct data source!
    query = """
        SELECT vfahead_inr, vfahead_beschreibung
        FROM vfahead 
        WHERE vfahead_bmdvariante = %s 
        AND vfahead_type = %s
        AND source_db = %s
        ORDER BY vfahead_inr DESC
    """
    
    try:
        pg_cursor.execute(query, (bmdvariante, type_name, source_db))
        results = pg_cursor.fetchall()
        
        if results:
            # Return first INR (for DB storage) but all descriptions
            first_inr = results[0][0]
            descs = [r[1].strip() for r in results]
            return first_inr, ' | '.join(descs)
    except Exception as e:
        # Silent fail - no matching VFAHEAD found
        pass
    
    return None, None

def find_vfahead(bmdvariante, type_name, anlage):
    """Find matching VFAHEAD entry"""
    
    # Pad bmdvariante to 20 characters (AS400 CHAR field)
    bmdvariante = str(bmdvariante).ljust(20)
    # Pad type_name to 20 characters (AS400 CHAR field)
    type_name = str(type_name).ljust(20)
    
    # Build anlage condition based on plant
    # CRITICAL: G-Anlagen (PB_Prod) and A60 (MV_Prod) data must NEVER mix!
    if anlage == 'G2':
        anlage_condition = "vfahead_g2aktiv = 'T' AND source_db = 'PB_Prod'"
    elif anlage == 'G3':
        anlage_condition = "vfahead_g3aktiv = 'T' AND source_db = 'PB_Prod'"
    elif anlage == 'G4':
        anlage_condition = "vfahead_g4aktiv = 'T' AND source_db = 'PB_Prod'"
    elif anlage == 'G5':
        anlage_condition = "vfahead_g5aktiv = 'T' AND source_db = 'PB_Prod'"
    elif anlage == 'A6' or anlage == 'A60':
        # A60 uses MV_Prod database - completely separate from G-plants!
        anlage_condition = "source_db = 'MV_Prod'"
    else:
        return None, None
    
    # Query for matching VFAHEAD
    if anlage in ['A6', 'A60']:
        # Special query for A60 - use source_db to ensure complete separation
        query = """
            SELECT vfahead_inr, vfahead_beschreibung
            FROM vfahead 
            WHERE vfahead_bmdvariante = %s 
            AND vfahead_type = %s
            AND source_db = 'MV_Prod'
            ORDER BY vfahead_inr DESC
        """
    else:
        # Query for G-plants with plant-specific aktiv columns
        query = f"""
            SELECT vfahead_inr, vfahead_beschreibung
            FROM vfahead 
            WHERE vfahead_bmdvariante = %s 
            AND vfahead_type = %s
            AND {anlage_condition}
            ORDER BY vfahead_inr DESC
        """
    
    try:
        pg_cursor.execute(query, (bmdvariante, type_name))
        
        if anlage in ['A6', 'A60']:
            # For A60, return all matching entries
            results = pg_cursor.fetchall()
            if results:
                first_inr = results[0][0]
                descs = [r[1].strip() for r in results]
                return first_inr, ' | '.join(descs)
        else:
            # For G-plants, also return all matches for VOR/PASSIV
            if type_name.strip() in ['VOR', 'PASSIV']:
                results = pg_cursor.fetchall()
                if results:
                    first_inr = results[0][0]
                    descs = [r[1].strip() for r in results]
                    return first_inr, ' | '.join(descs)
            else:
                # For other types, return first match
                result = pg_cursor.fetchone()
                if result and len(result) >= 2:
                    return result[0], result[1]  # Return INR and description
    except Exception as e:
        # Silent fail - no matching VFAHEAD found
        pass
    
    return None, None

# Process each code
pg_cursor.execute("SELECT * FROM codes")
codes = pg_cursor.fetchall()
col_names = [desc[0] for desc in pg_cursor.description]

total_mapped = 0
for row in codes:
    code_dict = dict(zip(col_names, row))
    code = code_dict['code']
    anlage = code_dict['anlage']
    anlage_typ = code_dict['anlage_typ']
    
    updates = {}
    
    if anlage_typ == 'G':
        # G-Anlagen use VOR/HAUPT/PASSIV/TROCKEN
        
        # VB -> VOR
        if code_dict['vb'] != '00':
            inr, desc = find_vfahead(code_dict['vb'], 'VOR', anlage)
            if inr:
                updates['vb_vfahead_inr'] = inr
                updates['vb_beschreibung'] = desc
        
        # HB -> HAUPT
        if code_dict['hb'] != '00':
            inr, desc = find_vfahead(code_dict['hb'], 'HAUPT', anlage)
            if inr:
                updates['hb_vfahead_inr'] = inr
                updates['hb_beschreibung'] = desc
        
        # PAS -> PASSIV
        if code_dict['pas'] != '00':
            inr, desc = find_vfahead(code_dict['pas'], 'PASSIV', anlage)
            if inr:
                updates['pas_vfahead_inr'] = inr
                updates['pas_beschreibung'] = desc
        
        # NB -> TROCKEN (not NACHBEHAND)
        # For NB, treat second digit as 0 for mapping (21->20, 22->20, 23->20)
        if code_dict['nb'] != '00':
            nb_code = code_dict['nb']
            # Map subvariants to base variant (e.g., 21->20, 22->20, 23->20)
            nb_base = nb_code[0] + '0'  # Take first digit and add '0'
            
            inr, desc = find_vfahead(nb_base, 'TROCKEN', anlage)
            if inr:
                updates['nb_vfahead_inr'] = inr
                # Keep original code in description for clarity
                if nb_code != nb_base:
                    updates['nb_beschreibung'] = f"{desc} [Subvariante {nb_code}]"
                else:
                    updates['nb_beschreibung'] = desc
    
    elif anlage_typ == 'A60':
        # A60 uses HAUPT/BESCHPROG from MV_Prod
        # BUT: VOR and PASSIV are universal and come from PB_Prod!
        # These basic processes are shared across ALL plants
        
        # VB -> VOR (Vorbehandlung) - Universal process from PB_Prod
        if code_dict['vb'] != '00':
            # VOR is universal - use from PB_Prod (no plant-specific filtering needed)
            inr, desc = find_vfahead_universal(code_dict['vb'], 'VOR', 'PB_Prod')
            if inr:
                updates['vb_vfahead_inr'] = inr
                updates['vb_beschreibung'] = desc
        
        # HB -> HAUPT or BESCHPROG (Hauptbehandlung) - From MV_Prod ONLY
        if code_dict['hb'] != '00':
            # Try HAUPT first (for codes 20, 60)
            inr, desc = find_vfahead(code_dict['hb'], 'HAUPT', anlage)
            if not inr:
                # Fallback to BESCHPROG
                inr, desc = find_vfahead(code_dict['hb'], 'BESCHPROG', anlage)
            if inr:
                updates['hb_vfahead_inr'] = inr
                updates['hb_beschreibung'] = desc
        
        # PAS -> PASSIV (Passivierung) - Universal process from PB_Prod
        if code_dict['pas'] != '00':
            # PASSIV is universal - use from PB_Prod
            inr, desc = find_vfahead_universal(code_dict['pas'], 'PASSIV', 'PB_Prod')
            if inr:
                updates['pas_vfahead_inr'] = inr
                updates['pas_beschreibung'] = desc
        
        # NB -> BESCHPROG (Nachbehandlung/Beschichtungsprogramm)
        # For NB, treat second digit as 0 for mapping (21->20, 22->20, 23->20)
        if code_dict['nb'] != '00':
            nb_code = code_dict['nb']
            # Map subvariants to base variant (e.g., 21->20, 22->20, 23->20)
            nb_base = nb_code[0] + '0'  # Take first digit and add '0'
            
            inr, desc = find_vfahead(nb_base, 'BESCHPROG', anlage)
            if inr:
                updates['nb_vfahead_inr'] = inr
                # Keep original code in description for clarity
                if nb_code != nb_base:
                    updates['nb_beschreibung'] = f"{desc} [Subvariante {nb_code}]"
                else:
                    updates['nb_beschreibung'] = desc
    
    # Update database if we found mappings
    if updates:
        set_clause = ', '.join(["{} = %s".format(k) for k in updates.keys()])
        values = list(updates.values()) + [code]
        
        query = """
            UPDATE codes 
            SET {}
            WHERE code = %s
        """.format(set_clause)
        
        pg_cursor.execute(query, values)
        total_mapped += 1

pg_conn.commit()
print(f"✓ Mapped {total_mapped} codes to VFAHEAD programs")

# Statistics
print("\n4. Mapping Statistics...")

# G-Anlagen mapping success
pg_cursor.execute("""
    SELECT anlage,
           COUNT(*) as total,
           COUNT(vb_vfahead_inr) as vb_mapped,
           COUNT(hb_vfahead_inr) as hb_mapped,
           COUNT(pas_vfahead_inr) as pas_mapped,
           COUNT(nb_vfahead_inr) as nb_mapped
    FROM codes
    WHERE anlage_typ = 'G'
    GROUP BY anlage
    ORDER BY anlage
""")

print("\nG-Anlagen Mapping:")
for row in pg_cursor.fetchall():
    print(f"  {row[0]}: Total={row[1]}, VB={row[2]}, HB={row[3]}, PAS={row[4]}, NB={row[5]}")

# A60 mapping success
pg_cursor.execute("""
    SELECT COUNT(*) as total,
           COUNT(vb_vfahead_inr) as vb_mapped,
           COUNT(hb_vfahead_inr) as hb_mapped,
           COUNT(pas_vfahead_inr) as pas_mapped,
           COUNT(nb_vfahead_inr) as nb_mapped
    FROM codes
    WHERE anlage_typ = 'A60'
""")

row = pg_cursor.fetchone()
if row[0] > 0:
    print(f"\nA60 Mapping:")
    print(f"  Total={row[0]}, VB={row[1]}, HB={row[2]}, PAS={row[3]}, NB={row[4]}")

# Cleanup
galvanik_cursor.close()
galvanik_conn.close()
pg_cursor.close()
pg_conn.close()

print(f"\n✓ Mapping completed: {datetime.now()}")