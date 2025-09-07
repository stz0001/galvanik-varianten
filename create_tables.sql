-- Drop existing tables if they exist
DROP TABLE IF EXISTS codes CASCADE;
DROP TABLE IF EXISTS mappings CASCADE;

-- Create codes table
CREATE TABLE codes (
    id SERIAL PRIMARY KEY,
    anlage VARCHAR(3),      
    code VARCHAR(20),       
    vb VARCHAR(2),          
    hb VARCHAR(2),          
    pas VARCHAR(2),         
    nb VARCHAR(2),          
    vb_text TEXT,           
    hb_text TEXT,           
    pas_text TEXT,          
    nb_text TEXT,           
    artikel_count INT,      
    UNIQUE(code)
);

-- Create mappings table
CREATE TABLE mappings (
    position VARCHAR(3),    
    wert VARCHAR(2),        
    text TEXT,
    PRIMARY KEY(position, wert)              
);

-- Create indexes for performance
CREATE INDEX idx_codes_anlage ON codes(anlage);
CREATE INDEX idx_codes_vb ON codes(vb);
CREATE INDEX idx_codes_hb ON codes(hb);
CREATE INDEX idx_codes_pas ON codes(pas);
CREATE INDEX idx_codes_nb ON codes(nb);