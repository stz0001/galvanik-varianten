-- Korrektur für mehrfach-aktive VFAHEAD Einträge
-- Erstelle für jede aktive Anlage einen separaten Kurzzeichen-Eintrag

-- Zunächst alle Kurzzeichen löschen und neu aufbauen
UPDATE vfahead SET vfahead_kurzzeichen = NULL;

-- Für Programme die in mehreren Anlagen aktiv sind, 
-- verwende die erste verfügbare Anlage als primäres Kurzzeichen
UPDATE vfahead 
SET vfahead_kurzzeichen = 
    CASE 
        WHEN vfahead_g2aktiv IN ('A', 'T') THEN 'G2'
        WHEN vfahead_g3aktiv IN ('A', 'T') THEN 'G3'
        WHEN vfahead_g4aktiv IN ('A', 'T') THEN 'G4'
        WHEN vfahead_g5aktiv IN ('A', 'T') THEN 'G5'
        WHEN source_db = 'MV_Prod' THEN 'A6'
        ELSE 'XX'
    END ||
    CASE TRIM(vfahead_type)
        WHEN 'VOR' THEN 'Vor'
        WHEN 'HAUPT' THEN 'Hau'
        WHEN 'PASSIV' THEN 'Pas'
        WHEN 'NACHBEHAND' THEN 'Nac'
        WHEN 'BESCHPROG' THEN 'Bes'
        WHEN 'TROCKEN' THEN 'Tro'
        WHEN 'TEMPERN' THEN 'Tem'
        WHEN 'VTROCK' THEN 'VTr'
        ELSE LEFT(TRIM(vfahead_type), 3)
    END || 
    TRIM(vfahead_bmdvariante)
WHERE vfahead_status = 'A';

-- Erstelle zusätzliche Spalte für alle aktiven Anlagen
ALTER TABLE vfahead ADD COLUMN IF NOT EXISTS alle_kurzzeichen TEXT;

UPDATE vfahead 
SET alle_kurzzeichen = 
    STRING_AGG(
        anlage || 
        CASE TRIM(vfahead_type)
            WHEN 'VOR' THEN 'Vor'
            WHEN 'HAUPT' THEN 'Hau'
            WHEN 'PASSIV' THEN 'Pas'
            WHEN 'NACHBEHAND' THEN 'Nac'
            WHEN 'BESCHPROG' THEN 'Bes'
            WHEN 'TROCKEN' THEN 'Tro'
            WHEN 'TEMPERN' THEN 'Tem'
            WHEN 'VTROCK' THEN 'VTr'
            ELSE LEFT(TRIM(vfahead_type), 3)
        END || 
        TRIM(vfahead_bmdvariante),
        ', '
        ORDER BY anlage
    )
FROM (
    SELECT 
        vfahead_inr,
        UNNEST(ARRAY[
            CASE WHEN vfahead_g2aktiv IN ('A', 'T') THEN 'G2' END,
            CASE WHEN vfahead_g3aktiv IN ('A', 'T') THEN 'G3' END,
            CASE WHEN vfahead_g4aktiv IN ('A', 'T') THEN 'G4' END,
            CASE WHEN vfahead_g5aktiv IN ('A', 'T') THEN 'G5' END,
            CASE WHEN source_db = 'MV_Prod' THEN 'A6' END
        ]) AS anlage
    FROM vfahead
    WHERE vfahead_status = 'A'
) AS anlagen
WHERE anlagen.vfahead_inr = vfahead.vfahead_inr
  AND anlagen.anlage IS NOT NULL
GROUP BY vfahead.vfahead_inr;