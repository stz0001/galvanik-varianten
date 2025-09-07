-- Update CODES Tabelle mit Kurzzeichen aus VFAHEAD
-- Format: G2Vor10: Beschreibung

-- Update VB-Beschreibungen mit Kurzzeichen
UPDATE codes c
SET vb_beschreibung = (
    SELECT STRING_AGG(
        v.vfahead_kurzzeichen || ': ' || v.vfahead_beschreibung, 
        ' | ' 
        ORDER BY v.vfahead_kurzzeichen
    )
    FROM vfahead v
    WHERE TRIM(v.vfahead_type) = 'VOR'
      AND TRIM(v.vfahead_bmdvariante) = TRIM(c.vb)
      AND v.vfahead_status = 'A'
      AND (
          (c.anlage = 'G2' AND v.vfahead_g2aktiv IN ('A', 'T')) OR
          (c.anlage = 'G3' AND v.vfahead_g3aktiv IN ('A', 'T')) OR
          (c.anlage = 'G4' AND v.vfahead_g4aktiv IN ('A', 'T')) OR
          (c.anlage = 'G5' AND v.vfahead_g5aktiv IN ('A', 'T')) OR
          (c.anlage = 'A6' AND v.source_db = 'MV_Prod')
      )
)
WHERE c.vb IS NOT NULL AND c.vb != '';

-- Update HB-Beschreibungen mit Kurzzeichen
UPDATE codes c
SET hb_beschreibung = (
    SELECT STRING_AGG(
        v.vfahead_kurzzeichen || ': ' || v.vfahead_beschreibung, 
        ' | ' 
        ORDER BY v.vfahead_kurzzeichen
    )
    FROM vfahead v
    WHERE TRIM(v.vfahead_type) = 'HAUPT'
      AND TRIM(v.vfahead_bmdvariante) = TRIM(c.hb)
      AND v.vfahead_status = 'A'
      AND (
          (c.anlage = 'G2' AND v.vfahead_g2aktiv IN ('A', 'T')) OR
          (c.anlage = 'G3' AND v.vfahead_g3aktiv IN ('A', 'T')) OR
          (c.anlage = 'G4' AND v.vfahead_g4aktiv IN ('A', 'T')) OR
          (c.anlage = 'G5' AND v.vfahead_g5aktiv IN ('A', 'T')) OR
          (c.anlage = 'A6' AND v.source_db = 'MV_Prod')
      )
)
WHERE c.hb IS NOT NULL AND c.hb != '';

-- Update PAS-Beschreibungen mit Kurzzeichen
UPDATE codes c
SET pas_beschreibung = (
    SELECT STRING_AGG(
        v.vfahead_kurzzeichen || ': ' || v.vfahead_beschreibung, 
        ' | ' 
        ORDER BY v.vfahead_kurzzeichen
    )
    FROM vfahead v
    WHERE TRIM(v.vfahead_type) = 'PASSIV'
      AND TRIM(v.vfahead_bmdvariante) = TRIM(c.pas)
      AND v.vfahead_status = 'A'
      AND (
          (c.anlage = 'G2' AND v.vfahead_g2aktiv IN ('A', 'T')) OR
          (c.anlage = 'G3' AND v.vfahead_g3aktiv IN ('A', 'T')) OR
          (c.anlage = 'G4' AND v.vfahead_g4aktiv IN ('A', 'T')) OR
          (c.anlage = 'G5' AND v.vfahead_g5aktiv IN ('A', 'T')) OR
          (c.anlage = 'A6' AND v.source_db = 'MV_Prod')
      )
)
WHERE c.pas IS NOT NULL AND c.pas != '';

-- Update NB-Beschreibungen mit Kurzzeichen
UPDATE codes c
SET nb_beschreibung = (
    SELECT STRING_AGG(
        v.vfahead_kurzzeichen || ': ' || v.vfahead_beschreibung, 
        ' | ' 
        ORDER BY v.vfahead_kurzzeichen
    )
    FROM vfahead v
    WHERE (TRIM(v.vfahead_type) = 'NACHBEHAND' OR TRIM(v.vfahead_type) = 'BESCHPROG')
      AND TRIM(v.vfahead_bmdvariante) = TRIM(c.nb)
      AND v.vfahead_status = 'A'
      AND (
          (c.anlage = 'G2' AND v.vfahead_g2aktiv IN ('A', 'T')) OR
          (c.anlage = 'G3' AND v.vfahead_g3aktiv IN ('A', 'T')) OR
          (c.anlage = 'G4' AND v.vfahead_g4aktiv IN ('A', 'T')) OR
          (c.anlage = 'G5' AND v.vfahead_g5aktiv IN ('A', 'T')) OR
          (c.anlage = 'A6' AND v.source_db = 'MV_Prod')
      )
)
WHERE c.nb IS NOT NULL AND c.nb != '';

-- Zeige Beispiele der Updates
SELECT 
    code,
    anlage,
    vb || ': ' || COALESCE(vb_beschreibung, '-') as "Vorbehandlung",
    hb || ': ' || COALESCE(hb_beschreibung, '-') as "Hauptbehandlung"
FROM codes
WHERE anlage IN ('G2', 'G4', 'A6')
ORDER BY anlage, code
LIMIT 10;