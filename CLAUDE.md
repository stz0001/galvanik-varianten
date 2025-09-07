# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Galvanik Varianten-System (Galvanization Variants System) that manages process parameters for surface treatment in galvanization facilities. The system handles 12-digit article codes and detailed parameter configurations for plants G2, G3, G4, G5 (main facility) and A60 (Plettenberg).

## Database Architecture

The system uses PostgreSQL with three core tables:

### 1. **CODES** Table (65 variants)
Primary storage for decoded article codes with process mappings.

**Key Fields:**
- `id` (SERIAL PRIMARY KEY)
- `code` (VARCHAR(20), UNIQUE) - 12-digit process code
- `anlage` (VARCHAR(3)) - Plant identifier: G2, G3, G4, G5, or A6
- `anlage_typ` (VARCHAR(10)) - Plant type: "G" or "A60"
- Process steps: `vb`, `hb`, `pas`, `nb`, `xx` (all VARCHAR(2))
- Process descriptions: `vb_beschreibung`, `hb_beschreibung`, `pas_beschreibung`, `nb_beschreibung` (TEXT)
- VFAHEAD references: `vb_vfahead_inr`, `hb_vfahead_inr`, `pas_vfahead_inr`, `nb_vfahead_inr` (BIGINT)
- Additional references: `beschprog_vfahead_inr`, `trocken_vfahead_inr`, `vtrock_vfahead_inr`, `belade_vfahead_inr`, `entlade_vfahead_inr`, `umlade_vfahead_inr`
- `artikel_count` (INTEGER) - Number of articles using this code

### 2. **VFAHEAD** Table (134 programs)
Process program definitions with plant-specific activation flags.

**Key Fields:**
- `vfahead_inr` (BIGINT PRIMARY KEY)
- `vfahead_status` (CHAR(1)) - 'A' for active
- `vfahead_type` (VARCHAR(20)) - Process type: VOR, HAUPT, PASSIV, NACHBEHAND, BESCHPROG, TROCKEN
- `vfahead_bmdvariante` (VARCHAR(20)) - Variant code (10, 20, 30, etc.)
- `vfahead_beschreibung` (VARCHAR(50)) - Process description
- Plant activation: `vfahead_g2aktiv`, `vfahead_g3aktiv`, `vfahead_g4aktiv`, `vfahead_g5aktiv` (CHAR(1))
- `source_db` (VARCHAR(20)) - Source database: 'PB_Prod' or 'MV_Prod'

### 3. **VFALINE** Table (3,076 parameters)
Detailed parameter values for each VFAHEAD program.

**Key Fields:**
- `vfaline_inr` (BIGINT PRIMARY KEY)
- `vfaline_vfahead_inr` (BIGINT FOREIGN KEY → VFAHEAD)
- `vfaline_gruppe` (VARCHAR(20)) - Parameter group
- `vfaline_parameter` (VARCHAR(20)) - Parameter name
- `vfaline_daten_char` (VARCHAR(50)) - Text value
- `vfaline_daten_dec` (NUMERIC(18,6)) - Numeric value

## Code Structure (12-digit)

```
Position:  1-2    3-4    5-6    7-8    9-10   11-12
          [PLANT][VB  ][HB  ][PAS ][NB  ][XX  ]
          
Example:   G4    10    60    23    10    00
           │     │     │     │     │     └── Additional (usually 00)
           │     │     │     │     └──────── Post-treatment
           │     │     │     └────────────── Passivation
           │     │     └──────────────────── Main treatment
           │     └────────────────────────── Pre-treatment
           └──────────────────────────────── Plant (G4)
```

## Important Relationships

1. **Code Decoding Process:**
   - Extract 12-digit codes from source articles
   - Decode into segments (plant, VB, HB, PAS, NB, XX)
   - Map each segment to VFAHEAD programs based on type and variant

2. **Data Sources:**
   - **PB_Prod**: Programs for G-plants (G2, G3, G4, G5)
   - **MV_Prod**: Programs for A60 plant
   - Universal processes (VOR, PASSIV) from PB_Prod apply to all plants

3. **Special Mappings:**
   - A60 dual process support: HB=60 or HB=62 can have two programs
   - Subvariant fallbacks: NB 21→20, 22→20, 23→20 (with notation)
   - Multiple VFAHEAD entries per code segment are combined with "|" separator

## Common Query Patterns

### Get all parameters for a code:
```sql
SELECT c.*, v.*, l.*
FROM codes c
LEFT JOIN vfahead v ON v.vfahead_inr IN (
    c.vb_vfahead_inr, c.hb_vfahead_inr, 
    c.pas_vfahead_inr, c.nb_vfahead_inr
)
LEFT JOIN vfaline l ON l.vfaline_vfahead_inr = v.vfahead_inr
WHERE c.code = 'G41060231000'
ORDER BY v.vfahead_type, l.vfaline_gruppe, l.vfaline_parameter;
```

### Find active programs for a plant:
```sql
SELECT * FROM vfahead 
WHERE vfahead_status = 'A' 
AND vfahead_g4aktiv = 'A'
AND vfahead_type = 'HAUPT';
```

## File Structure

```
/var/www/varianten/
├── public/                   # Web interface
│   ├── index.php            # Main overview
│   └── details.php          # Variant details
├── import_vfa_all.py        # Import VFAHEAD/VFALINE from AS400
├── map_codes_complete.py    # Map codes to VFAHEAD programs
└── DATENSTRUKTUR-DOKUMENTATION.md  # Detailed data structure docs
```

## Notes

- Plant "A6" is displayed as "A60" in the UI for user preference
- The system maintains strict separation between PB_Prod and MV_Prod sources
- All field names in VFAHEAD/VFALINE tables have prefixes (vfahead_, vfaline_)
- Description fields can contain multiple variants separated by "|"