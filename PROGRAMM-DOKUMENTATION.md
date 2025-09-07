# Variantenexplorer - Programm-Dokumentation

## Übersicht
Der Variantenexplorer ist eine Web-Anwendung zur Verwaltung und Anzeige von Galvanik-Varianten (Oberflächenbehandlungsprozessen) für verschiedene Produktionsanlagen.

## Systemarchitektur

### Technologie-Stack
- **Backend**: PHP 8.x
- **Datenbank**: PostgreSQL 15
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Datenimport**: Python 3.x mit psycopg2

### Verzeichnisstruktur
```
/var/www/varianten/
├── public/                 # Web-Root (öffentlich zugänglich)
│   ├── index.php          # Hauptseite mit Variantenübersicht
│   ├── details.php        # Detailansicht einzelner Varianten
│   └── style.css          # Stylesheet
├── config.php             # Datenbankverbindung
├── map_codes_complete.py  # Hauptskript für Code-Mapping
└── import_vfa_*.py        # Import-Skripte für VFAHEAD/VFALINE
```

## Web-Interface

### index.php - Hauptübersicht
**Funktionen:**
- Anzeige aller Varianten-Codes in tabellarischer Form
- Filterung nach Anlage (G2, G3, G4, G5, A60)
- Volltextsuche in Codes und Beschreibungen
- CSV-Export der gefilterten Daten
- Statistik-Karten mit Code- und Artikel-Anzahl pro Anlage

**Besonderheiten:**
- A6 wird in der Oberfläche als "A60" angezeigt (User-Präferenz)
- Varianten werden im Format **[Anlage][Typ][Nummer]** angezeigt (z.B. G4Vor10, G4Haupt60)
- Typ-Kürzel: Vor (Vorbehandlung), Haupt (Hauptbehandlung), Pass (Passivierung), Nach (Nachbehandlung)
- Verwendet beschreibung-Felder aus codes-Tabelle (enthält alle Varianten mit "|" getrennt)
- Responsive Design für verschiedene Bildschirmgrößen

### details.php - Detailansicht
**Funktionen:**
- Anzeige aller 4 Prozessschritte einer Variante im Format [Anlage][Typ][Nummer]:
  - G4Vor10 (Vorbehandlung)
  - G4Haupt60 (Hauptbehandlung)
  - G4Pass23 (Passivierung)
  - G4Nach10 (Nachbehandlung)
- Darstellung aller VFAHEAD-Parameter aus VFALINE
- Bei mehreren VFAHEAD-Varianten: Auflistung als Bullet-Liste

**Datenfluss:**
1. Lädt Code aus `codes`-Tabelle
2. Verwendet vb/hb/pas/nb_vfahead_inr für Parameter-Abfrage
3. Zeigt beschreibung-Felder (enthält alle Varianten)
4. Lädt VFALINE-Parameter für jeden Prozessschritt

### config.php - Datenbankverbindung
```php
function getDB() {
    $host = 'localhost';
    $db = 'varianten';
    $user = 'postgres';
    $pass = 'postgres';
    
    $dsn = "pgsql:host=$host;dbname=$db";
    $pdo = new PDO($dsn, $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    return $pdo;
}
```

## Python-Skripte

### map_codes_complete.py - Hauptmapping
**Zweck:** Importiert Artikel-Codes und mappt sie auf VFAHEAD-Programme

**Ablauf:**
1. **Import der Artikel-Codes** (aus galvanik.artikel)
   - Extrahiert 12-stellige Codes aus stueckliste-Feld
   - Decodiert Positionen (1-2: Anlage, 3-4: VB, 5-6: HB, 7-8: PAS, 9-10: NB, 11-12: XX)

2. **Code-Dekodierung**
   - G-Codes: G2, G3, G4, G5 (Hauptwerk)
   - A-Codes: A6 (Plettenberg, wird als A60 bezeichnet)

3. **VFAHEAD-Mapping**
   - G-Anlagen nutzen Typen: VOR, HAUPT, PASSIV, TROCKEN
   - A60 nutzt: VOR (universal), HAUPT/BESCHPROG, PASSIV (universal), BESCHPROG
   - Strikte Trennung: PB_Prod (G-Anlagen) und MV_Prod (A60)

4. **Spezialbehandlungen**
   - NB-Subvarianten: 21→20, 22→20, 23→20 (mit Kennzeichnung)
   - Universal-Prozesse: VOR und PASSIV aus PB_Prod für alle Anlagen
   - Mehrfach-Varianten: Alle VFAHEAD mit gleichem Code werden verknüpft

### import_vfa_all.py - VFAHEAD/VFALINE Import
**Zweck:** Importiert Stammdaten aus AS400/DB2

**Datenquellen:**
- PB_Prod: G-Anlagen (G2, G3, G4, G5)
- MV_Prod: A60-Anlage

**Import-Strategie:**
- 1:1 Import ohne Manipulation
- Beibehaltung aller Original-Felder
- source_db-Feld zur Quellentrennung

## Datenbank-Schema

### Tabelle: codes
```sql
CREATE TABLE codes (
    code VARCHAR(20) PRIMARY KEY,
    anlage VARCHAR(10),
    anlage_typ VARCHAR(10),
    vb VARCHAR(2),
    hb VARCHAR(2),
    pas VARCHAR(2),
    nb VARCHAR(2),
    xx VARCHAR(2),
    vb_vfahead_inr INTEGER,
    hb_vfahead_inr INTEGER,
    pas_vfahead_inr INTEGER,
    nb_vfahead_inr INTEGER,
    vb_beschreibung TEXT,    -- Alle Varianten mit "|" getrennt
    hb_beschreibung TEXT,
    pas_beschreibung TEXT,
    nb_beschreibung TEXT,
    artikel_count INTEGER
);
```

### Tabelle: vfahead
```sql
CREATE TABLE vfahead (
    vfahead_inr INTEGER PRIMARY KEY,
    vfahead_bmdvariante VARCHAR(20),
    vfahead_type VARCHAR(20),
    vfahead_beschreibung TEXT,
    vfahead_kurzzeichen VARCHAR(50),
    vfahead_g2aktiv CHAR(1),
    vfahead_g3aktiv CHAR(1),
    vfahead_g4aktiv CHAR(1),
    vfahead_g5aktiv CHAR(1),
    source_db VARCHAR(20)     -- PB_Prod oder MV_Prod
);
```

### Tabelle: vfaline
```sql
CREATE TABLE vfaline (
    vfaline_inr INTEGER PRIMARY KEY,
    vfahead_inr INTEGER REFERENCES vfahead,
    vfaline_gruppe VARCHAR(50),
    vfaline_parameter VARCHAR(100),
    vfaline_daten_char VARCHAR(255),
    vfaline_daten_dec DECIMAL(15,6),
    vfaline_beschreibung TEXT
);
```

## Wartung und Betrieb

### Daten-Aktualisierung
```bash
# 1. VFAHEAD/VFALINE importieren
python3 import_vfa_all.py

# 2. Artikel-Codes mappen
python3 map_codes_complete.py
```

### Troubleshooting

**Problem:** A60-Filter zeigt keine Daten
- **Lösung:** Datenbank speichert "A6", Interface zeigt "A60"

**Problem:** Fehlende Beschreibungen bei VOR/PASSIV für A60
- **Lösung:** Universal-Prozesse aus PB_Prod verwenden

**Problem:** Falsche Anlagen-Zuordnung
- **Lösung:** source_db-Feld prüfen, strikte Trennung PB_Prod/MV_Prod

## Performance-Optimierung

### Indizes
```sql
CREATE INDEX idx_codes_anlage ON codes(anlage);
CREATE INDEX idx_vfahead_type ON vfahead(vfahead_type);
CREATE INDEX idx_vfahead_bmd ON vfahead(vfahead_bmdvariante);
CREATE INDEX idx_vfaline_vfahead ON vfaline(vfahead_inr);
```

### Caching
- Browser-Caching für CSS aktiviert
- PostgreSQL Query-Cache nutzen
- PHP OPcache aktivieren

## Sicherheit

### Best Practices
- Prepared Statements gegen SQL-Injection
- htmlspecialchars() für XSS-Schutz
- Keine Passwörter im Code (config.php auslagern)
- Web-Root nur auf public/ Verzeichnis

### Backup
```bash
# Datenbank-Backup
pg_dump -U postgres varianten > backup_$(date +%Y%m%d).sql

# Restore
psql -U postgres varianten < backup_20240907.sql
```