-- Korrigiere VFAHEAD Kurzzeichen im Format AnlageTypVariante
-- z.B. G2Vor10, G4Hau20, A6Pas30

-- Wiederherstellung aus Backup falls vorhanden
UPDATE vfahead 
SET vfahead_kurzzeichen = kurzzeichen_backup 
WHERE kurzzeichen_backup IS NOT NULL;

-- Erstelle neue Kurzzeichen basierend auf aktiven Anlagen
WITH kurzzeichen_updates AS (
    SELECT 
        vfahead_inr,
        CASE 
            -- G2 aktiv
            WHEN vfahead_g2aktiv IN ('A', 'T') THEN 
                'G2' || 
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
                END || TRIM(vfahead_bmdvariante)
            -- G3 aktiv
            WHEN vfahead_g3aktiv IN ('A', 'T') THEN 
                'G3' || 
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
                END || TRIM(vfahead_bmdvariante)
            -- G4 aktiv
            WHEN vfahead_g4aktiv IN ('A', 'T') THEN 
                'G4' || 
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
                END || TRIM(vfahead_bmdvariante)
            -- G5 aktiv
            WHEN vfahead_g5aktiv IN ('A', 'T') THEN 
                'G5' || 
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
                END || TRIM(vfahead_bmdvariante)
            -- A60 (über source_db)
            WHEN source_db = 'MV_Prod' THEN 
                'A6' || 
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
                END || TRIM(vfahead_bmdvariante)
            ELSE vfahead_kurzzeichen -- Behalte aktuellen Wert
        END as neues_kurzzeichen
    FROM vfahead
    WHERE vfahead_status = 'A'
)
UPDATE vfahead v
SET vfahead_kurzzeichen = ku.neues_kurzzeichen
FROM kurzzeichen_updates ku
WHERE v.vfahead_inr = ku.vfahead_inr
  AND ku.neues_kurzzeichen IS NOT NULL;

-- Zeige Beispiele
SELECT 
    vfahead_type,
    vfahead_bmdvariante,
    vfahead_g2aktiv as G2,
    vfahead_g3aktiv as G3,
    vfahead_g4aktiv as G4,
    vfahead_g5aktiv as G5,
    source_db,
    vfahead_kurzzeichen as kurzzeichen,
    vfahead_beschreibung
FROM vfahead
WHERE vfahead_status = 'A'
ORDER BY vfahead_type, vfahead_bmdvariante
LIMIT 20;