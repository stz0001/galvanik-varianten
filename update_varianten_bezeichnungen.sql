-- Update Variantenbezeichnungen auf korrektes Format: AnlageTypNummer
-- Format: G2Vor10, G3Hau20, A6Pas30 etc.

-- Backup der aktuellen Bezeichnungen
ALTER TABLE vfahead ADD COLUMN IF NOT EXISTS beschreibung_backup TEXT;
UPDATE vfahead SET beschreibung_backup = vfahead_beschreibung WHERE beschreibung_backup IS NULL;

-- Update für G-Anlagen (G2, G3, G4, G5)
UPDATE vfahead SET vfahead_beschreibung = 
    CASE 
        -- Vorbehandlung
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '10' AND vfahead_g2aktiv = 'A' THEN 'G2Vor10'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '10' AND vfahead_g3aktiv = 'A' THEN 'G3Vor10'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '10' AND vfahead_g4aktiv = 'A' THEN 'G4Vor10'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '10' AND vfahead_g5aktiv = 'A' THEN 'G5Vor10'
        
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '20' AND vfahead_g2aktiv = 'A' THEN 'G2Vor20'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '20' AND vfahead_g3aktiv = 'A' THEN 'G3Vor20'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '20' AND vfahead_g4aktiv = 'A' THEN 'G4Vor20'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '20' AND vfahead_g5aktiv = 'A' THEN 'G5Vor20'
        
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '30' AND vfahead_g2aktiv = 'A' THEN 'G2Vor30'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '30' AND vfahead_g3aktiv = 'A' THEN 'G3Vor30'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '30' AND vfahead_g4aktiv = 'A' THEN 'G4Vor30'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '30' AND vfahead_g5aktiv = 'A' THEN 'G5Vor30'
        
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '50' AND vfahead_g2aktiv = 'A' THEN 'G2Vor50'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '50' AND vfahead_g3aktiv = 'A' THEN 'G3Vor50'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '50' AND vfahead_g4aktiv = 'A' THEN 'G4Vor50'
        WHEN vfahead_type = 'VOR' AND vfahead_bmdvariante = '50' AND vfahead_g5aktiv = 'A' THEN 'G5Vor50'
        
        -- Hauptbehandlung  
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '10' AND vfahead_g2aktiv = 'A' THEN 'G2Hau10'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '10' AND vfahead_g3aktiv = 'A' THEN 'G3Hau10'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '10' AND vfahead_g4aktiv = 'A' THEN 'G4Hau10'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '10' AND vfahead_g5aktiv = 'A' THEN 'G5Hau10'
        
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '20' AND vfahead_g2aktiv = 'A' THEN 'G2Hau20'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '20' AND vfahead_g3aktiv = 'A' THEN 'G3Hau20'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '20' AND vfahead_g4aktiv = 'A' THEN 'G4Hau20'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '20' AND vfahead_g5aktiv = 'A' THEN 'G5Hau20'
        
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '30' AND vfahead_g2aktiv = 'A' THEN 'G2Hau30'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '30' AND vfahead_g3aktiv = 'A' THEN 'G3Hau30'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '30' AND vfahead_g4aktiv = 'A' THEN 'G4Hau30'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '30' AND vfahead_g5aktiv = 'A' THEN 'G5Hau30'
        
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '60' AND vfahead_g2aktiv = 'A' THEN 'G2Hau60'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '60' AND vfahead_g3aktiv = 'A' THEN 'G3Hau60'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '60' AND vfahead_g4aktiv = 'A' THEN 'G4Hau60'
        WHEN vfahead_type = 'HAUPT' AND vfahead_bmdvariante = '60' AND vfahead_g5aktiv = 'A' THEN 'G5Hau60'
        
        -- Passivierung
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '10' AND vfahead_g2aktiv = 'A' THEN 'G2Pas10'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '10' AND vfahead_g3aktiv = 'A' THEN 'G3Pas10'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '10' AND vfahead_g4aktiv = 'A' THEN 'G4Pas10'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '10' AND vfahead_g5aktiv = 'A' THEN 'G5Pas10'
        
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '22' AND vfahead_g2aktiv = 'A' THEN 'G2Pas22'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '22' AND vfahead_g3aktiv = 'A' THEN 'G3Pas22'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '22' AND vfahead_g4aktiv = 'A' THEN 'G4Pas22'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '22' AND vfahead_g5aktiv = 'A' THEN 'G5Pas22'
        
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '23' AND vfahead_g2aktiv = 'A' THEN 'G2Pas23'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '23' AND vfahead_g3aktiv = 'A' THEN 'G3Pas23'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '23' AND vfahead_g4aktiv = 'A' THEN 'G4Pas23'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '23' AND vfahead_g5aktiv = 'A' THEN 'G5Pas23'
        
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '30' AND vfahead_g2aktiv = 'A' THEN 'G2Pas30'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '30' AND vfahead_g3aktiv = 'A' THEN 'G3Pas30'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '30' AND vfahead_g4aktiv = 'A' THEN 'G4Pas30'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '30' AND vfahead_g5aktiv = 'A' THEN 'G5Pas30'
        
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '50' AND vfahead_g2aktiv = 'A' THEN 'G2Pas50'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '50' AND vfahead_g3aktiv = 'A' THEN 'G3Pas50'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '50' AND vfahead_g4aktiv = 'A' THEN 'G4Pas50'
        WHEN vfahead_type = 'PASSIV' AND vfahead_bmdvariante = '50' AND vfahead_g5aktiv = 'A' THEN 'G5Pas50'
        
        -- Nachbehandlung
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '10' AND vfahead_g2aktiv = 'A' THEN 'G2Nac10'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '10' AND vfahead_g3aktiv = 'A' THEN 'G3Nac10'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '10' AND vfahead_g4aktiv = 'A' THEN 'G4Nac10'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '10' AND vfahead_g5aktiv = 'A' THEN 'G5Nac10'
        
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '22' AND vfahead_g2aktiv = 'A' THEN 'G2Nac22'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '22' AND vfahead_g3aktiv = 'A' THEN 'G3Nac22'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '22' AND vfahead_g4aktiv = 'A' THEN 'G4Nac22'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '22' AND vfahead_g5aktiv = 'A' THEN 'G5Nac22'
        
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '30' AND vfahead_g2aktiv = 'A' THEN 'G2Nac30'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '30' AND vfahead_g3aktiv = 'A' THEN 'G3Nac30'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '30' AND vfahead_g4aktiv = 'A' THEN 'G4Nac30'
        WHEN vfahead_type = 'NACHBEHAND' AND vfahead_bmdvariante = '30' AND vfahead_g5aktiv = 'A' THEN 'G5Nac30'
        
        ELSE vfahead_beschreibung -- Behalte Original bei anderen
    END
WHERE vfahead_status = 'A' 
  AND source_db = 'PB_Prod';

-- Generische Update-Funktion für A60 (noch zu implementieren basierend auf tatsächlichen Daten)
-- Format sollte sein: A6Vor10, A6Hau20, A6Pas30, A6Nac10

-- Zeige Änderungen
SELECT 
    vfahead_type,
    vfahead_bmdvariante,
    beschreibung_backup as alt,
    vfahead_beschreibung as neu
FROM vfahead
WHERE vfahead_beschreibung != beschreibung_backup
ORDER BY vfahead_type, vfahead_bmdvariante
LIMIT 20;
