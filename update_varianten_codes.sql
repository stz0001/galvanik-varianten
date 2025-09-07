-- Update Varianten-Codes in VFAHEAD Tabelle
-- Format: AnlageTypVariante (z.B. G2Vor10, A6Hau20)
-- basierend auf aktiven Anlagen-Flags

-- Backup der aktuellen Beschreibungen
ALTER TABLE vfahead ADD COLUMN IF NOT EXISTS kurzzeichen_backup VARCHAR(50);
UPDATE vfahead SET kurzzeichen_backup = vfahead_kurzzeichen WHERE kurzzeichen_backup IS NULL;

-- Erstelle temporäre Funktion für Type-Kürzel
CREATE OR REPLACE FUNCTION get_type_kuerzel(type_name VARCHAR) RETURNS VARCHAR AS $$
BEGIN
    RETURN CASE 
        WHEN type_name = 'VOR' THEN 'Vor'
        WHEN type_name = 'HAUPT' THEN 'Hau'
        WHEN type_name = 'PASSIV' THEN 'Pas'
        WHEN type_name = 'NACHBEHAND' THEN 'Nac'
        WHEN type_name = 'BESCHPROG' THEN 'Bes'
        WHEN type_name = 'TROCKEN' THEN 'Tro'
        WHEN type_name = 'TEMPERN' THEN 'Tem'
        WHEN type_name = 'VTROCK' THEN 'VTr'
        ELSE SUBSTRING(type_name, 1, 3)
    END;
END;
$$ LANGUAGE plpgsql;

-- Update für alle aktiven VFAHEAD-Einträge
-- Generiere Kurzzeichen basierend auf Anlage + Type + Variante

-- Für G2
UPDATE vfahead 
SET vfahead_kurzzeichen = 'G2' || get_type_kuerzel(TRIM(vfahead_type)) || TRIM(vfahead_bmdvariante)
WHERE vfahead_g2aktiv = 'A' 
  AND vfahead_status = 'A'
  AND source_db = 'PB_Prod';

-- Für G3  
UPDATE vfahead 
SET vfahead_kurzzeichen = 'G3' || get_type_kuerzel(TRIM(vfahead_type)) || TRIM(vfahead_bmdvariante)
WHERE vfahead_g3aktiv = 'A' 
  AND vfahead_status = 'A'
  AND source_db = 'PB_Prod';

-- Für G4
UPDATE vfahead 
SET vfahead_kurzzeichen = 'G4' || get_type_kuerzel(TRIM(vfahead_type)) || TRIM(vfahead_bmdvariante)
WHERE vfahead_g4aktiv = 'A' 
  AND vfahead_status = 'A'
  AND source_db = 'PB_Prod';

-- Für G5
UPDATE vfahead 
SET vfahead_kurzzeichen = 'G5' || get_type_kuerzel(TRIM(vfahead_type)) || TRIM(vfahead_bmdvariante)
WHERE vfahead_g5aktiv = 'A' 
  AND vfahead_status = 'A'
  AND source_db = 'PB_Prod';

-- Für A60 (MV_Prod)
UPDATE vfahead 
SET vfahead_kurzzeichen = 'A6' || get_type_kuerzel(TRIM(vfahead_type)) || TRIM(vfahead_bmdvariante)
WHERE vfahead_status = 'A'
  AND source_db = 'MV_Prod';

-- Update CODES Tabelle mit neuen Kurzzeichen-basierten Beschreibungen
-- Dies nutzt die neue Struktur, um konsistente Bezeichnungen zu erstellen

-- Zeige Änderungen
SELECT 
    vfahead_type,
    vfahead_bmdvariante,
    vfahead_g2aktiv as G2,
    vfahead_g3aktiv as G3,
    vfahead_g4aktiv as G4,
    vfahead_g5aktiv as G5,
    kurzzeichen_backup as alt,
    vfahead_kurzzeichen as neu,
    vfahead_beschreibung
FROM vfahead
WHERE vfahead_kurzzeichen != kurzzeichen_backup
  OR kurzzeichen_backup IS NULL
ORDER BY vfahead_type, vfahead_bmdvariante
LIMIT 30;

-- Cleanup
DROP FUNCTION IF EXISTS get_type_kuerzel(VARCHAR);