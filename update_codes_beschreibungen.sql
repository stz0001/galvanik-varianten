-- Update CODES Tabelle mit neuen Kurzzeichen-basierten Beschreibungen
-- Format: AnlageTypVariante (z.B. G2Vor10, A6Hau20)

-- Backup der aktuellen Beschreibungen
ALTER TABLE codes ADD COLUMN IF NOT EXISTS vb_beschreibung_backup TEXT;
ALTER TABLE codes ADD COLUMN IF NOT EXISTS hb_beschreibung_backup TEXT;
ALTER TABLE codes ADD COLUMN IF NOT EXISTS pas_beschreibung_backup TEXT;
ALTER TABLE codes ADD COLUMN IF NOT EXISTS nb_beschreibung_backup TEXT;

UPDATE codes SET 
    vb_beschreibung_backup = vb_beschreibung,
    hb_beschreibung_backup = hb_beschreibung,
    pas_beschreibung_backup = pas_beschreibung,
    nb_beschreibung_backup = nb_beschreibung
WHERE vb_beschreibung_backup IS NULL;

-- Erstelle temporäre Funktion für Type-Mapping
CREATE OR REPLACE FUNCTION get_type_from_position(pos VARCHAR) RETURNS VARCHAR AS $$
BEGIN
    RETURN CASE 
        WHEN pos = 'vb' THEN 'VOR'
        WHEN pos = 'hb' THEN 'HAUPT'
        WHEN pos = 'pas' THEN 'PASSIV'
        WHEN pos = 'nb' THEN 'NACHBEHAND'
        ELSE NULL
    END;
END;
$$ LANGUAGE plpgsql;

-- Update VB-Beschreibungen
UPDATE codes c
SET vb_beschreibung = COALESCE(
    (SELECT STRING_AGG(DISTINCT 
        CASE 
            WHEN c.anlage_typ = 'G' THEN c.anlage || 'Vor' || TRIM(c.vb)
            ELSE 'A6Vor' || TRIM(c.vb)
        END || ': ' || v.vfahead_beschreibung, ' | ' ORDER BY 1)
     FROM vfahead v
     WHERE TRIM(v.vfahead_type) = 'VOR'
       AND TRIM(v.vfahead_bmdvariante) = TRIM(c.vb)
       AND v.vfahead_status = 'A'
       AND (
           (c.anlage = 'G2' AND v.vfahead_g2aktiv = 'A') OR
           (c.anlage = 'G3' AND v.vfahead_g3aktiv = 'A') OR
           (c.anlage = 'G4' AND v.vfahead_g4aktiv = 'A') OR
           (c.anlage = 'G5' AND v.vfahead_g5aktiv = 'A') OR
           (c.anlage = 'A6' AND v.source_db = 'MV_Prod')
       )
    ),
    c.anlage || 'Vor' || c.vb
)
WHERE c.vb IS NOT NULL AND c.vb != '';

-- Update HB-Beschreibungen
UPDATE codes c
SET hb_beschreibung = COALESCE(
    (SELECT STRING_AGG(DISTINCT 
        CASE 
            WHEN c.anlage_typ = 'G' THEN c.anlage || 'Hau' || TRIM(c.hb)
            ELSE 'A6Hau' || TRIM(c.hb)
        END || ': ' || v.vfahead_beschreibung, ' | ' ORDER BY 1)
     FROM vfahead v
     WHERE TRIM(v.vfahead_type) = 'HAUPT'
       AND TRIM(v.vfahead_bmdvariante) = TRIM(c.hb)
       AND v.vfahead_status = 'A'
       AND (
           (c.anlage = 'G2' AND v.vfahead_g2aktiv = 'A') OR
           (c.anlage = 'G3' AND v.vfahead_g3aktiv = 'A') OR
           (c.anlage = 'G4' AND v.vfahead_g4aktiv = 'A') OR
           (c.anlage = 'G5' AND v.vfahead_g5aktiv = 'A') OR
           (c.anlage = 'A6' AND v.source_db = 'MV_Prod')
       )
    ),
    c.anlage || 'Hau' || c.hb
)
WHERE c.hb IS NOT NULL AND c.hb != '';

-- Update PAS-Beschreibungen
UPDATE codes c
SET pas_beschreibung = COALESCE(
    (SELECT STRING_AGG(DISTINCT 
        CASE 
            WHEN c.anlage_typ = 'G' THEN c.anlage || 'Pas' || TRIM(c.pas)
            ELSE 'A6Pas' || TRIM(c.pas)
        END || ': ' || v.vfahead_beschreibung, ' | ' ORDER BY 1)
     FROM vfahead v
     WHERE TRIM(v.vfahead_type) = 'PASSIV'
       AND TRIM(v.vfahead_bmdvariante) = TRIM(c.pas)
       AND v.vfahead_status = 'A'
       AND (
           (c.anlage = 'G2' AND v.vfahead_g2aktiv = 'A') OR
           (c.anlage = 'G3' AND v.vfahead_g3aktiv = 'A') OR
           (c.anlage = 'G4' AND v.vfahead_g4aktiv = 'A') OR
           (c.anlage = 'G5' AND v.vfahead_g5aktiv = 'A') OR
           (c.anlage = 'A6' AND v.source_db = 'MV_Prod')
       )
    ),
    c.anlage || 'Pas' || c.pas
)
WHERE c.pas IS NOT NULL AND c.pas != '';

-- Update NB-Beschreibungen
UPDATE codes c
SET nb_beschreibung = COALESCE(
    (SELECT STRING_AGG(DISTINCT 
        CASE 
            WHEN c.anlage_typ = 'G' THEN c.anlage || 'Nac' || TRIM(c.nb)
            ELSE 'A6Nac' || TRIM(c.nb)
        END || ': ' || v.vfahead_beschreibung, ' | ' ORDER BY 1)
     FROM vfahead v
     WHERE (TRIM(v.vfahead_type) = 'NACHBEHAND' OR TRIM(v.vfahead_type) = 'BESCHPROG')
       AND TRIM(v.vfahead_bmdvariante) = TRIM(c.nb)
       AND v.vfahead_status = 'A'
       AND (
           (c.anlage = 'G2' AND v.vfahead_g2aktiv = 'A') OR
           (c.anlage = 'G3' AND v.vfahead_g3aktiv = 'A') OR
           (c.anlage = 'G4' AND v.vfahead_g4aktiv = 'A') OR
           (c.anlage = 'G5' AND v.vfahead_g5aktiv = 'A') OR
           (c.anlage = 'A6' AND v.source_db = 'MV_Prod')
       )
    ),
    c.anlage || 'Nac' || c.nb
)
WHERE c.nb IS NOT NULL AND c.nb != '';

-- Zeige Beispiel-Änderungen
SELECT 
    code,
    anlage,
    vb || ' → ' || vb_beschreibung as "VB",
    hb || ' → ' || hb_beschreibung as "HB"
FROM codes
WHERE code IN ('G41060231000', 'G21020101010', 'A61060102210')
LIMIT 10;

-- Cleanup
DROP FUNCTION IF EXISTS get_type_from_position(VARCHAR);