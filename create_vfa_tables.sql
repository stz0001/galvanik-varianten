-- Drop existing tables if they exist
DROP TABLE IF EXISTS vfaline CASCADE;
DROP TABLE IF EXISTS vfahead CASCADE;

-- Create VFAHEAD table
CREATE TABLE vfahead (
    vfahead_inr SERIAL PRIMARY KEY,
    type VARCHAR(20),              -- VOR, HAUPT, PASSIV, NACHBEHAND, BESCHPROG
    bmdvariante VARCHAR(10),       -- 10, 20, 30, 40, 50, 60, etc.
    anlage_codes TEXT[],           -- Array: ['G2','G3','G4'] etc.
    beschreibung TEXT,
    kurzzeichen VARCHAR(20),
    status CHAR(1) DEFAULT 'A',    -- A=Aktiv, I=Inaktiv
    erstellung_dat DATE DEFAULT CURRENT_DATE,
    aenderung_dat DATE DEFAULT CURRENT_DATE
);

-- Create VFALINE table
CREATE TABLE vfaline (
    id SERIAL PRIMARY KEY,
    vfahead_inr INTEGER REFERENCES vfahead(vfahead_inr) ON DELETE CASCADE,
    gruppe VARCHAR(20),            -- ALKZN, SZN, PASSIV, STANDARD, etc.
    parameter VARCHAR(30),         -- ABSFAK, WIRKGRAD, TEMP_1, etc.
    daten_char VARCHAR(50),        -- Text value
    daten_dec DECIMAL(10,2),       -- Numeric value
    beschreibung TEXT
);

-- Create indexes for performance
CREATE INDEX idx_vfahead_type ON vfahead(type);
CREATE INDEX idx_vfahead_bmdvariante ON vfahead(bmdvariante);
CREATE INDEX idx_vfahead_status ON vfahead(status);
CREATE INDEX idx_vfaline_vfahead_inr ON vfaline(vfahead_inr);
CREATE INDEX idx_vfaline_gruppe ON vfaline(gruppe);
CREATE INDEX idx_vfaline_parameter ON vfaline(parameter);

-- Add GIN index for array search
CREATE INDEX idx_vfahead_anlage_codes ON vfahead USING GIN(anlage_codes);