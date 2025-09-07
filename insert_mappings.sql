-- Clear existing mappings
DELETE FROM mappings;

-- VB (Vorbehandlung) Mappings
INSERT INTO mappings (position, wert, text) VALUES
('VB', '10', 'Standard'),
('VB', '20', 'Verstärkt'),
('VB', '30', 'Spezial'),
('VB', '40', 'Extra stark'),
('VB', '50', 'Sonder');

-- HB (Hauptbehandlung) Mappings
INSERT INTO mappings (position, wert, text) VALUES
('HB', '10', 'Minimal'),
('HB', '20', 'Standard'),
('HB', '30', 'Verstärkt'),
('HB', '40', 'Stark'),
('HB', '50', 'Extra stark'),
('HB', '60', 'Dual-Prozess Alk/Sauer'),
('HB', '62', 'Dual-Prozess Sauer/Alk');

-- PAS (Passivierung) Mappings
INSERT INTO mappings (position, wert, text) VALUES
('PAS', '10', 'Blau'),
('PAS', '20', 'Gelb'),
('PAS', '22', 'Dickschicht transparent'),
('PAS', '23', 'Dickschicht blau'),
('PAS', '30', 'Schwarz'),
('PAS', '40', 'Olive'),
('PAS', '50', 'Transparent');

-- NB (Nachbehandlung) Mappings
INSERT INTO mappings (position, wert, text) VALUES
('NB', '10', 'Standard'),
('NB', '20', 'Versiegelung Typ 2'),
('NB', '22', 'Versiegelung Typ 3'),
('NB', '30', 'Spezial'),
('NB', '40', 'Ölung'),
('NB', '50', 'Wachs');