# Projekt Variantenexplorer - KISS Spezifikation

## ZIEL
Alle Stücklisten-Codes (G-/A-Codes) aus `galvanik.artikel` dekodieren und anzeigen was dahinter steckt.

---

## DATENBANK-STRUKTUR

### Neue DB: `varianten`
```sql
CREATE DATABASE varianten;

-- Haupttabelle für alle Codes
CREATE TABLE codes (
    id SERIAL PRIMARY KEY,
    anlage VARCHAR(3),      -- G2/G3/G4/G5/A60
    code VARCHAR(20),       -- G41010602310
    vb VARCHAR(2),          -- 10
    hb VARCHAR(2),          -- 20
    pas VARCHAR(2),         -- 10
    nb VARCHAR(2),          -- 10
    vb_text TEXT,           -- "Standard"
    hb_text TEXT,           -- "Alkalisch"
    pas_text TEXT,          -- "Blau"
    nb_text TEXT,           -- "Standard"
    artikel_count INT,      -- 127
    UNIQUE(code)
);

-- Mapping-Tabelle für Beschreibungen
CREATE TABLE mappings (
    position VARCHAR(3),    -- VB/HB/PAS/NB
    wert VARCHAR(2),        -- 10/20/30/60
    text TEXT              -- "Standard Vorbehandlung"
);
```

---

## CODE-DEKODIERUNG

### G-Code (12 Zeichen)
```
G41010602310
││└┴─VB (10)
││  └┴─HB (10)
││    └┴─PAS (60)
││      └┴─NB (23)
││        └┴─XX (10)
└┴─Anlage (G4)
```

### A-Code (12 Zeichen)
```
A61060102210
││└┴─VB (10)
││  └┴─HB (60)
││    └┴─PAS (10)
││      └┴─NB (22)
││        └┴─XX (10)
└┴─Anlage (A6)
```

---

## MAPPINGS (aus Datenmodell-VFA.md)

```
VB (Vorbehandlung):
10 = Standard
20 = Verstärkt
30 = Spezial

HB (Hauptbehandlung):
10 = Minimal
20 = Standard
30 = Verstärkt
40 = Stark
60 = Dual-Prozess (A60)
62 = Dual-Prozess Alt (A60)

PAS (Passivierung):
10 = Blau
22 = Dickschicht transparent
23 = Dickschicht blau
30 = Schwarz

NB (Nachbehandlung):
10 = Standard
22 = Versiegelung Typ 3
30 = Spezial
```

---

## PYTHON IMPORT-SCRIPT

`import_codes.py`:
```python
# 1. Hole alle Codes aus galvanik.artikel
SELECT DISTINCT stueckliste, anlage, COUNT(*) as count
FROM artikel 
WHERE stueckliste LIKE 'G%' OR stueckliste LIKE 'A6%'
GROUP BY stueckliste, anlage

# 2. Dekodiere jeden Code
code = "G41010602310"
anlage = code[0:2]   # G4
vb = code[2:4]       # 10
hb = code[4:6]       # 10
pas = code[6:8]      # 60
nb = code[8:10]      # 23

# 3. Hole Beschreibungen aus mappings
# 4. INSERT in varianten.codes
```

---

## WEB-INTERFACE

### Dateien:
```
/var/www/varianten/
├── index.php        # Hauptseite
├── config.php       # DB-Connection
└── style.css        # Minimal CSS
```

### index.php Funktionen:
1. **Anlagen-Auswahl:** Dropdown (G2/G3/G4/G5/A60/Alle)
2. **Tabelle:** Code | VB | HB | PAS | NB | Artikel-Anzahl
3. **Suche:** Einfaches Textfeld (filtert Tabelle)
4. **Export:** CSV-Download Button

### Beispiel-Ansicht:
```
Anlage: [G4 ▼]  Suche: [_______]  [CSV Export]

Code         | VB         | HB           | PAS          | NB         | Artikel
-------------|------------|--------------|--------------|------------|--------
G41010602310 | 10-Standard| 60-Dual      | 23-Dicksch.  | 10-Standard| 127
G41020101010 | 20-Verstärkt| 10-Minimal  | 10-Blau      | 10-Standard| 89
```

---

## DEPLOYMENT

```bash
# 1. DB anlegen
PGPASSWORD=postgres psql -U postgres -c "CREATE DATABASE varianten;"

# 2. Tabellen erstellen
PGPASSWORD=postgres psql -U postgres varianten < create_tables.sql

# 3. Mappings einfügen  
PGPASSWORD=postgres psql -U postgres varianten < mappings.sql

# 4. Import ausführen
python3 import_codes.py

# 5. Browser öffnen
http://localhost/varianten/
```

---

## FERTIG! 
Keine Authentifizierung, keine APIs, kein JavaScript-Framework - nur PHP, PostgreSQL und eine simple Tabelle!