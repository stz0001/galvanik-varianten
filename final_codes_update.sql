-- Finale Update für CODES Tabelle
-- Verwende anlagenspezifische Kurzzeichen im Format AnlageTypVariante

-- Update VB-Beschreibungen
UPDATE codes c
SET vb_beschreibung = 
    c.anlage || 
    CASE 
        WHEN c.anlage = 'A6' THEN ''
        ELSE ''
    END ||
    'Vor' || c.vb || ': ' ||
    COALESCE(
        (SELECT vfahead_beschreibung 
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
         LIMIT 1),
        'Vorbehandlung ' || c.vb
    )
WHERE c.vb IS NOT NULL AND c.vb != '';

-- Update HB-Beschreibungen
UPDATE codes c
SET hb_beschreibung = 
    c.anlage || 
    CASE 
        WHEN c.anlage = 'A6' THEN ''
        ELSE ''
    END ||
    'Hau' || c.hb || ': ' ||
    COALESCE(
        (SELECT vfahead_beschreibung 
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
         LIMIT 1),
        'Hauptbehandlung ' || c.hb
    )
WHERE c.hb IS NOT NULL AND c.hb != '';

-- Update PAS-Beschreibungen
UPDATE codes c
SET pas_beschreibung = 
    c.anlage || 
    CASE 
        WHEN c.anlage = 'A6' THEN ''
        ELSE ''
    END ||
    'Pas' || c.pas || ': ' ||
    COALESCE(
        (SELECT vfahead_beschreibung 
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
         LIMIT 1),
        'Passivierung ' || c.pas
    )
WHERE c.pas IS NOT NULL AND c.pas != '';

-- Update NB-Beschreibungen
UPDATE codes c
SET nb_beschreibung = 
    c.anlage || 
    CASE 
        WHEN c.anlage = 'A6' THEN ''
        ELSE ''
    END ||
    'Nac' || c.nb || ': ' ||
    COALESCE(
        (SELECT vfahead_beschreibung 
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
         LIMIT 1),
        'Nachbehandlung ' || c.nb
    )
WHERE c.nb IS NOT NULL AND c.nb != '';

-- Zeige Beispiele
SELECT 
    code,
    anlage,
    vb_beschreibung,
    hb_beschreibung
FROM codes
WHERE anlage IN ('G2', 'G4', 'A6')
ORDER BY anlage, code
LIMIT 10;