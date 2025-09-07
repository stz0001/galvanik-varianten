# Changelog - Variantenexplorer

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-09-07

### Geändert
- **Varianten-Bezeichnungsformat komplett überarbeitet**
  - Neues Format: `[Anlage][Typ][Nummer]` (z.B. G4Vor10, A6Haupt60)
  - Typ-Bezeichnungen: 
    - `Vor` = Vorbehandlung (vorher VB)
    - `Haupt` = Hauptbehandlung (vorher HB)
    - `Pass` = Passivierung (vorher PAS)
    - `Nach` = Nachbehandlung (vorher NB)
  - Änderungen in `public/index.php` und `public/details.php`
  - Konsistent mit Galvanik-Projekt Dokumentation

### Dokumentation
- CLAUDE.md erweitert um Abschnitt "Variant Display Format"
- DATENSTRUKTUR-DOKUMENTATION.md erweitert um Varianten-Bezeichnungsformat
- PROGRAMM-DOKUMENTATION.md aktualisiert mit neuen Bezeichnungsbeispielen

### Technische Details
- PHP-Anzeige-Logik angepasst (nicht die Datenbank-Struktur)
- Originale Beschreibungen in der Datenbank bleiben unverändert
- Display-Layer zeigt jetzt konsistente Varianten-Codes

## [2.0.0] - 2025-09-06

### Hinzugefügt
- Vollständiges VFAHEAD/VFALINE Mapping-System
- 134 VFAHEAD Programme mit 3.076 Parametern
- Unterstützung für Multi-Varianten pro Code-Position
- Detaillierte Parameter-Anzeige in details.php

### Geändert
- Migration von einfachen Text-Mappings zu VFAHEAD-Referenzen
- Erweiterte codes-Tabelle mit vfahead_inr Foreign Keys

## [1.0.0] - 2025-09-05

### Initial Release
- Grundlegendes System zur Anzeige von Varianten-Codes
- Support für 5 Anlagen (G2, G3, G4, G5, A60)
- Web-Interface mit Filterung und CSV-Export
- 65 eindeutige Varianten-Codes importiert