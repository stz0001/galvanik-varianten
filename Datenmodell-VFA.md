# Datenmodell VFA - Detaillierte Beschreibung
## Galvanik Varianten-System Datenarchitektur

---

## 1. GESAMTÜBERSICHT DATENMODELL

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        GALVANIK VARIANTEN-SYSTEM DATENMODELL                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐       ┌──────────────────┐  │
│  │     ARTIKEL      │         │     VFAHEAD      │       │     VFALINE      │  │
│  ├──────────────────┤         ├──────────────────┤       ├──────────────────┤  │
│  │ artikel_inr  (PK)│         │ vfahead_inr  (PK)│◄──────│ vfahead_inr  (FK)│  │
│  │ artikel_nr       │         │ type             │       │ gruppe           │  │
│  │ bezeichnung      │         │ bmdvariante      │       │ parameter        │  │
│  │ g_code     ──────┼────────►│ anlage_codes[]   │       │ daten_char       │  │
│  │ a_code     ──────┼────────►│ beschreibung     │       │ daten_dec        │  │
│  │ stueckliste      │         │ kurzzeichen      │       │ beschreibung     │  │
│  │ anlage           │         │ status           │       └──────────────────┘  │
│  └──────────────────┘         │ erstellung_dat   │        9.908 Parameter       │
│   8.386 Artikel               │ aenderung_dat    │                              │
│                               └──────────────────┘                              │
│                                234 Programme                                     │
│                                                                                   │
│  BEZIEHUNGEN:                                                                    │
│  ════════════                                                                    │
│  • ARTIKEL.g_code/a_code ──(DECODE)──► VFAHEAD via BMDVARIANTE + TYPE          │
│  • VFAHEAD ◄──(1:N)──► VFALINE via vfahead_inr                                 │
│  • VFAHEAD.anlage_codes[] ◄──(FILTER)── WHERE anlage = ANY(anlage_codes)       │
│                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. TABELLEN-DETAILS

### 2.1 ARTIKEL Tabelle
```
┌───────────────────────────────────────────────────────────────────────────┐
│                            ARTIKEL TABELLE                                │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ PRIMÄRSCHLÜSSEL:                                                         │
│ ► artikel_inr (INTEGER) - Eindeutige Artikel-ID                         │
│                                                                           │
│ STAMMDATEN:                                                              │
│ ► artikel_nr (VARCHAR 50) - Artikelnummer                               │
│ ► bezeichnung (TEXT) - Artikelbezeichnung                               │
│                                                                           │
│ STÜCKLISTEN-CODES (KRITISCH!):                                          │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │ g_code (VARCHAR 20) - Code für G-Anlagen (G2/G3/G4/G5)      │        │
│ │   Format: G[Anlage][VB][HB][PAS][NB][XX]                    │        │
│ │   Beispiel: "G21020101010"                                  │        │
│ │             G2 = Anlage G2                                   │        │
│ │             10 = VB (Vorbehandlung)                          │        │
│ │             20 = HB (Hauptbehandlung)                        │        │
│ │             10 = PAS (Passivierung)                          │        │
│ │             10 = NB (Nachbehandlung)                         │        │
│ │             10 = XX (Zusatz)                                 │        │
│ └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │ a_code (VARCHAR 20) - Code für A60-Anlage                   │        │
│ │   Format: A6[VB][HB][PAS][NB][XX]                           │        │
│ │   Beispiel: "A61060102210"                                  │        │
│ │             A6 = Anlage A60                                  │        │
│ │             10 = VB                                          │        │
│ │             60 = HB (⚡ DUAL-PROZESS!)                       │        │
│ │             10 = PAS                                         │        │
│ │             22 = NB                                          │        │
│ │             10 = XX                                          │        │
│ └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│ WEITERE FELDER:                                                          │
│ ► stueckliste (TEXT) - Vollständiger Stücklistencode                    │
│ ► anlage (VARCHAR) - Anlagenbezeichnung                                 │
│                                                                           │
│ STATISTIK:                                                               │
│ • 8.386 Artikel gesamt                                                   │
│ • ~7.000 mit G-Code                                                      │
│ • ~3.500 mit A-Code                                                      │
│ • ~2.100 mit beiden Codes (Dual)                                        │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 VFAHEAD Tabelle
```
┌───────────────────────────────────────────────────────────────────────────┐
│                            VFAHEAD TABELLE                                │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ PRIMÄRSCHLÜSSEL:                                                         │
│ ► vfahead_inr (INTEGER) - Eindeutige Programm-ID                        │
│                                                                           │
│ PROZESS-ZUORDNUNG:                                                       │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │ type (VARCHAR 20) - Prozessschritt-Typ                      │        │
│ │   Werte und Mapping:                                        │        │
│ │   • "VOR"       → VB  (Vorbehandlung)                       │        │
│ │   • "HAUPT"     → HB  (Hauptbehandlung/Verzinkung)          │        │
│ │   • "PASSIV"    → PAS (Passivierung)                        │        │
│ │   • "NACHBEHAND"→ NB  (Nachbehandlung)                      │        │
│ │   • "BESCHPROG" → NB  (auch Nachbehandlung)                 │        │
│ └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │ bmdvariante (VARCHAR 10) - Varianten-Code                  │        │
│ │   Werte: "10", "20", "30", "40", "50", "60", ...           │        │
│ │   Bedeutung:                                                │        │
│ │   • 10 = Standard/Minimal                                   │        │
│ │   • 20 = Alternative/Normal                                 │        │
│ │   • 30 = Verstärkt/Spezial                                  │        │
│ │   • 60 = DUAL-PROZESS (bei HB in A60!)                     │        │
│ └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│ ANLAGEN-ZUORDNUNG (KRITISCH!):                                          │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │ anlage_codes (TEXT[]) - PostgreSQL Array!                   │        │
│ │   Beispiel: ['G2','G3','G4']                                │        │
│ │   Filterung: WHERE 'G2' = ANY(anlage_codes)                │        │
│ │   NICHT: WHERE anlage_codes = 'G2' (FALSCH!)                │        │
│ └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│ BESCHREIBUNGEN:                                                          │
│ ► beschreibung (TEXT) - Ausführliche Programmbeschreibung               │
│ ► kurzzeichen (VARCHAR 20) - Kurzbeschreibung                           │
│                                                                           │
│ STATUS & ZEITEN:                                                         │
│ ► status (CHAR 1) - 'A'=Aktiv, 'I'=Inaktiv                             │
│ ► erstellung_dat (DATE) - Erstellungsdatum                              │
│ ► aenderung_dat (DATE) - Änderungsdatum                                 │
│                                                                           │
│ STATISTIK:                                                               │
│ • 234 Programme gesamt                                                   │
│ • 45 Type=VOR, 78 Type=HAUPT, 56 Type=PASSIV                           │
│ • 38 Type=NACHBEHAND, 17 Type=BESCHPROG                                │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.3 VFALINE Tabelle
```
┌───────────────────────────────────────────────────────────────────────────┐
│                            VFALINE TABELLE                                │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ FREMDSCHLÜSSEL:                                                          │
│ ► vfahead_inr (INTEGER) - Verweis auf VFAHEAD.vfahead_inr              │
│                                                                           │
│ PARAMETER-GRUPPIERUNG:                                                   │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │ gruppe (VARCHAR 20) - Parameter-Gruppe                      │        │
│ │   Wichtige Gruppen:                                         │        │
│ │   • "ALKZN"    - Alkalische Verzinkung                      │        │
│ │   • "SZN"      - Saure Verzinkung                           │        │
│ │   • "PASSIV"   - Passivierung                               │        │
│ │   • "STANDARD" - Standardparameter                          │        │
│ │   • "ABTROPFEN"- Abtropfparameter                           │        │
│ │   • NULL       - Ohne Gruppe (viele Einträge!)              │        │
│ └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│ PARAMETER-DEFINITION:                                                    │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │ parameter (VARCHAR 30) - Parameter-Name                     │        │
│ │   Kritische Parameter:                                       │        │
│ │   • "ABSFAK"    - Abscheidefaktor                           │        │
│ │   • "WIRKGRAD"  - Wirkungsgrad in %                         │        │
│ │   • "TAKTE"     - Anzahl Prozess-Takte                      │        │
│ │   • "TEMP_1"    - Temperatur Station 1                      │        │
│ │   • "DREHZAHL_1"- Drehzahl Station 1                        │        │
│ │   • "SCHALTER"  - Schalter Ein/Aus (0/1)                    │        │
│ └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
│ PARAMETER-WERTE:                                                         │
│ ► daten_char (VARCHAR 50) - Textwert des Parameters                     │
│ ► daten_dec (DECIMAL 10,2) - Zahlenwert des Parameters                  │
│   Hinweis: Meist ist nur eines der beiden Felder gefüllt!               │
│                                                                           │
│ BESCHREIBUNG:                                                            │
│ ► beschreibung (TEXT) - Erklärung des Parameters                        │
│                                                                           │
│ STATISTIK:                                                               │
│ • 9.908 Parameter-Einträge gesamt                                       │
│ • 4.234 mit Gruppe                                                       │
│ • 5.674 ohne Gruppe (NULL)                                              │
│                                                                           │
│ DUAL-PROZESS SPEZIALITÄT:                                               │
│ Bei HB=60 (A60) sind BEIDE Wirkungsgrade definiert:                     │
│ • ALKZN/WIRKGRAD = 65.00 (Alkalisch)                                    │
│ • SZN/WIRKGRAD = 95.00 (Sauer)                                          │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CODE-DEKODIERUNG UND MATCHING-LOGIK

### 3.1 Code-Struktur Dekodierung
```
┌───────────────────────────────────────────────────────────────────────────┐
│                        CODE-DEKODIERUNG PROZESS                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ SCHRITT 1: CODE PARSEN                                                   │
│ ═══════════════════════                                                  │
│                                                                           │
│ G-Code Beispiel: "G21020101010"                                         │
│ ┌─────┬─────┬─────┬─────┬─────┬─────┐                                  │
│ │ G2  │ 10  │ 20  │ 10  │ 10  │ 10  │                                  │
│ └──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┘                                  │
│    │     │     │     │     │     │                                      │
│    │     │     │     │     │     └─► Position 11-12: XX (Zusatz)        │
│    │     │     │     │     └───────► Position 9-10:  NB                 │
│    │     │     │     └─────────────► Position 7-8:   PAS                │
│    │     │     └───────────────────► Position 5-6:   HB                 │
│    │     └─────────────────────────► Position 3-4:   VB                 │
│    └───────────────────────────────► Position 1-2:   Anlage (G2)        │
│                                                                           │
│ A-Code Beispiel: "A61060102210"                                         │
│ ┌─────┬─────┬─────┬─────┬─────┬─────┐                                  │
│ │ A6  │ 10  │ 60  │ 10  │ 22  │ 10  │                                  │
│ └──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┘                                  │
│    │     │     │     │     │     │                                      │
│    │     │     │     │     │     └─► XX = 10                            │
│    │     │     │     │     └───────► NB = 22 (Versiegelung Typ 3)      │
│    │     │     │     └─────────────► PAS = 10 (Bläupassivierung)       │
│    │     │     └───────────────────► HB = 60 (⚡ DUAL-PROZESS!)        │
│    │     └─────────────────────────► VB = 10 (Standard)                 │
│    └───────────────────────────────► Anlage = A60                       │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### 3.2 VFAHEAD Matching-Logik
```
┌───────────────────────────────────────────────────────────────────────────┐
│                      VFAHEAD MATCHING-ALGORITHMUS                         │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ FÜR JEDE CODE-POSITION (VB, HB, PAS, NB):                               │
│ ══════════════════════════════════════════                              │
│                                                                           │
│ EINGABE:                                                                  │
│ • position_value (z.B. "10", "20", "60")                                │
│ • position_type (VB→VOR, HB→HAUPT, PAS→PASSIV, NB→NACHBEHAND)          │
│ • anlage (z.B. "G2", "A60")                                             │
│                                                                           │
│ MATCHING-PROZESS:                                                        │
│                                                                           │
│ ┌─────────────────────────────────────────────────────┐                │
│ │ 1. Type-Mapping bestimmen:                          │                │
│ │    VB  → type IN ('VOR')                            │                │
│ │    HB  → type IN ('HAUPT')                          │                │
│ │    PAS → type IN ('PASSIV')                         │                │
│ │    NB  → type IN ('NACHBEHAND', 'BESCHPROG')        │                │
│ └─────────────────────────────────────────────────────┘                │
│                                                                           │
│ ┌─────────────────────────────────────────────────────┐                │
│ │ 2. SQL-Query ausführen:                             │                │
│ │                                                      │                │
│ │ SELECT * FROM vfahead                               │                │
│ │ WHERE bmdvariante = :position_value                 │                │
│ │   AND type IN (:mapped_types)                       │                │
│ │   AND :anlage = ANY(anlage_codes)  -- KRITISCH!    │                │
│ │   AND status = 'A'                                  │                │
│ └─────────────────────────────────────────────────────┘                │
│                                                                           │
│ ┌─────────────────────────────────────────────────────┐                │
│ │ 3. Ergebnis:                                        │                │
│ │    → Ein oder mehrere VFAHEAD-Programme            │                │
│ │    → Jedes mit vfahead_inr für VFALINE-Lookup      │                │
│ └─────────────────────────────────────────────────────┘                │
│                                                                           │
│ BEISPIEL-MATCHING:                                                       │
│ ═════════════════                                                        │
│ Code: G21020101010                                                       │
│                                                                           │
│ Position VB=10:                                                          │
│ • type = 'VOR'                                                           │
│ • bmdvariante = '10'                                                     │
│ • 'G2' = ANY(anlage_codes) ✓                                            │
│ → Findet: VFAHEAD #123 "Standard-Vorbehandlung"                         │
│                                                                           │
│ Position HB=20:                                                          │
│ • type = 'HAUPT'                                                         │
│ • bmdvariante = '20'                                                     │
│ • 'G2' = ANY(anlage_codes) ✓                                            │
│ → Findet: VFAHEAD #456 "Zink alkalisch"                                 │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### 3.3 VFALINE Parameter-Abruf
```
┌───────────────────────────────────────────────────────────────────────────┐
│                        VFALINE PARAMETER-ABRUF                            │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ NACHDEM VFAHEAD GEFUNDEN:                                                │
│ ═════════════════════════                                                │
│                                                                           │
│ ┌──────────────────────┐        ┌──────────────────────┐               │
│ │    VFAHEAD #123      │        │    VFALINE Params    │               │
│ │  vfahead_inr = 123   │───────►│  WHERE vfahead_inr   │               │
│ │  type = 'VOR'        │        │     = 123            │               │
│ │  bmdvariante = '10'  │        │                      │               │
│ └──────────────────────┘        │  Ergebnis:          │               │
│                                  │  ┌────────────────┐ │               │
│                                  │  │STANDARD/SCHALTER│ │               │
│                                  │  │  = 1            │ │               │
│                                  │  ├────────────────┤ │               │
│                                  │  │STANDARD/TEMP_1  │ │               │
│                                  │  │  = 60.00        │ │               │
│                                  │  ├────────────────┤ │               │
│                                  │  │STANDARD/DREHZAHL│ │               │
│                                  │  │  = 25.00        │ │               │
│                                  │  └────────────────┘ │               │
│                                  └──────────────────────┘               │
│                                                                           │
│ SQL-QUERY:                                                               │
│ ══════════                                                               │
│ SELECT gruppe, parameter, daten_char, daten_dec, beschreibung           │
│ FROM vfaline                                                             │
│ WHERE vfahead_inr = :vfahead_inr                                        │
│ ORDER BY gruppe, parameter;                                             │
│                                                                           │
│ PARAMETER-GRUPPIERUNG:                                                   │
│ ═════════════════════                                                   │
│ Die Parameter werden nach gruppe/parameter gruppiert:                    │
│                                                                           │
│ • ALKZN/ABSFAK     = 0.23                                               │
│ • ALKZN/WIRKGRAD   = 65.00                                              │
│ • ALKZN/TAKTE      = 3                                                  │
│ • PASSIV/TEMP_1    = 35.00                                              │
│ • STANDARD/SCHALTER = 1                                                 │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 4. FILTERLOGIK UND SPEZIALFÄLLE

### 4.1 Anlage-Filterung mit PostgreSQL Array
```
┌───────────────────────────────────────────────────────────────────────────┐
│                    ANLAGE-FILTERUNG MIT POSTGRESQL ARRAY                  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ PROBLEM:                                                                  │
│ ════════                                                                  │
│ VFAHEAD.anlage_codes ist ein PostgreSQL TEXT[] Array                     │
│ Beispiel: ['G2','G3','G4']                                              │
│                                                                           │
│ FALSCHE ANSÄTZE (FUNKTIONIEREN NICHT!):                                 │
│ ═══════════════════════════════════════                                 │
│                                                                           │
│ ❌ WHERE anlage_codes = 'G2'                                            │
│    → Fehler: Kann Array nicht mit String vergleichen                    │
│                                                                           │
│ ❌ WHERE anlage_codes LIKE '%G2%'                                       │
│    → Fehler: LIKE funktioniert nicht mit Arrays                         │
│                                                                           │
│ ❌ WHERE 'G2' IN anlage_codes                                           │
│    → Fehler: IN erwartet Liste, nicht Array                             │
│                                                                           │
│ KORREKTE LÖSUNG:                                                         │
│ ════════════════                                                         │
│                                                                           │
│ ✅ WHERE 'G2' = ANY(anlage_codes)                                       │
│    → Prüft ob 'G2' in irgendeinem Element des Arrays ist               │
│                                                                           │
│ ✅ WHERE :anlage = ANY(anlage_codes)                                    │
│    → Mit Parameter-Binding                                              │
│                                                                           │
│ WEITERE ARRAY-OPERATOREN:                                               │
│ ═════════════════════════                                               │
│                                                                           │
│ • ANY() - Mindestens ein Element erfüllt Bedingung                      │
│ • ALL() - Alle Elemente erfüllen Bedingung                              │
│ • @>    - Array enthält andere Array                                    │
│ • <@    - Array ist enthalten in                                        │
│ • &&    - Arrays überlappen sich                                        │
│                                                                           │
│ PHP-BEISPIEL:                                                            │
│ ═════════════                                                            │
│ $stmt = $pdo->prepare("                                                 │
│     SELECT * FROM vfahead                                               │
│     WHERE :anlage = ANY(anlage_codes)                                   │
│     AND status = 'A'                                                    │
│ ");                                                                      │
│ $stmt->execute(['anlage' => 'G2']);                                     │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Dual-Prozess Spezialfall
```
┌───────────────────────────────────────────────────────────────────────────┐
│                        DUAL-PROZESS (HB=60) SPEZIALFALL                   │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ ⚡ NUR BEI A60-ANLAGE!                                                   │
│ ═══════════════════════                                                  │
│                                                                           │
│ ERKENNUNG:                                                               │
│ • Code beginnt mit "A6"                                                  │
│ • Position 5-6 (HB) = "60"                                              │
│ • Beispiel: A61060102210                                                │
│                                                                           │
│ BEDEUTUNG:                                                               │
│ ═══════════                                                              │
│ Dual-Prozess = BEIDE Verzinkungsarten nacheinander!                     │
│                                                                           │
│ ┌─────────────────────┐      ┌─────────────────────┐                   │
│ │  1. ALKALISCH (65%) │ ───► │  2. SAUER (95%)     │                   │
│ │  ALKZN/WIRKGRAD=65  │      │  SZN/WIRKGRAD=95    │                   │
│ └─────────────────────┘      └─────────────────────┘                   │
│                                                                           │
│ VFALINE PARAMETER BEI HB=60:                                            │
│ ════════════════════════════                                            │
│                                                                           │
│ SELECT * FROM vfaline v                                                 │
│ JOIN vfahead h ON v.vfahead_inr = h.vfahead_inr                        │
│ WHERE h.bmdvariante = '60'                                              │
│   AND h.type = 'HAUPT'                                                  │
│   AND 'A60' = ANY(h.anlage_codes);                                      │
│                                                                           │
│ Typische Parameter:                                                      │
│ ┌──────────────────────────────┐                                       │
│ │ ALKZN/ABSFAK    = 0.23       │                                       │
│ │ ALKZN/WIRKGRAD  = 65.00      │ ← Alkalisch 65%                       │
│ │ ALKZN/TAKTE     = 3          │                                       │
│ │ SZN/ABSFAK      = 0.31       │                                       │
│ │ SZN/WIRKGRAD    = 95.00      │ ← Sauer 95%                           │
│ │ SZN/TAKTE       = 2          │                                       │
│ └──────────────────────────────┘                                       │
│                                                                           │
│ STATISTIK:                                                               │
│ • 2.588 Artikel nutzen Dual-Prozess (31% aller Artikel)                 │
│ • NUR bei A60-Anlage möglich                                            │
│ • Kombination für höchste Qualität                                      │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 5. KOMPLETTER DATENFLUSS

### 5.1 Von Artikel-Code zu Parametern
```
┌───────────────────────────────────────────────────────────────────────────┐
│                    KOMPLETTER DATENFLUSS-PROZESS                          │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ START: ARTIKEL MIT CODE                                                  │
│ ════════════════════════                                                │
│                                                                           │
│ ┌─────────────────────────┐                                             │
│ │  ARTIKEL #12345          │                                             │
│ │  artikel_nr: "ART-4711"  │                                             │
│ │  g_code: "G21020101010"  │                                             │
│ │  a_code: "A61060102210"  │                                             │
│ └───────────┬───────────┘                                               │
│             │                                                            │
│             ▼                                                            │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │  SCHRITT 1: CODE DEKODIEREN                                 │        │
│ │  G21020101010 → G2|10|20|10|10|10                          │        │
│ │  A61060102210 → A6|10|60|10|22|10                          │        │
│ └───────────┬─────────────────────────────────────────────────┘        │
│             │                                                            │
│             ▼                                                            │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │  SCHRITT 2: VFAHEAD PROGRAMME FINDEN                        │        │
│ │                                                              │        │
│ │  Für G2-Anlage:                                             │        │
│ │  • VB=10  → VFAHEAD WHERE type='VOR' AND bmdvariante='10'  │        │
│ │             AND 'G2'=ANY(anlage_codes) → ID #123           │        │
│ │  • HB=20  → VFAHEAD WHERE type='HAUPT' AND bmdvariante='20'│        │
│ │             AND 'G2'=ANY(anlage_codes) → ID #456           │        │
│ │  • PAS=10 → VFAHEAD WHERE type='PASSIV' AND bmdvariante='10'│       │
│ │             AND 'G2'=ANY(anlage_codes) → ID #789           │        │
│ │  • NB=10  → VFAHEAD WHERE type IN ('NACHBEHAND','BESCHPROG')│       │
│ │             AND bmdvariante='10' → ID #012                 │        │
│ └───────────┬─────────────────────────────────────────────────┘        │
│             │                                                            │
│             ▼                                                            │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │  SCHRITT 3: VFALINE PARAMETER LADEN                         │        │
│ │                                                              │        │
│ │  Für jedes gefundene VFAHEAD:                               │        │
│ │  • SELECT * FROM vfaline WHERE vfahead_inr = #123           │        │
│ │    → STANDARD/SCHALTER=1, STANDARD/TEMP_1=60               │        │
│ │  • SELECT * FROM vfaline WHERE vfahead_inr = #456           │        │
│ │    → ALKZN/ABSFAK=0.23, ALKZN/WIRKGRAD=65                  │        │
│ │  • SELECT * FROM vfaline WHERE vfahead_inr = #789           │        │
│ │    → PASSIV/TEMP_1=35, PASSIV/ZEIT=120                     │        │
│ │  • SELECT * FROM vfaline WHERE vfahead_inr = #012           │        │
│ │    → VERSIEG/TYPE=3, VERSIEG/TEMP=80                       │        │
│ └───────────┬─────────────────────────────────────────────────┘        │
│             │                                                            │
│             ▼                                                            │
│ ┌─────────────────────────────────────────────────────────────┐        │
│ │  ERGEBNIS: KOMPLETTER PROZESS                               │        │
│ │                                                              │        │
│ │  Artikel ART-4711 durchläuft:                               │        │
│ │  1. Standard-Vorbehandlung (60°C, Drehzahl 25)              │        │
│ │  2. Alkalische Verzinkung (65% Wirkungsgrad)                │        │
│ │  3. Bläupassivierung (35°C, 120 Sekunden)                   │        │
│ │  4. Standard-Nachbehandlung mit Versiegelung Typ 3          │        │
│ └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 6. WICHTIGE SQL-QUERIES

### 6.1 Programme für Artikel-Code finden
```sql
-- Für G-Anlage (Beispiel G2, VB=10)
SELECT h.*, array_to_string(h.anlage_codes, ',') as anlagen
FROM vfahead h
WHERE h.bmdvariante = '10'
  AND h.type = 'VOR'
  AND 'G2' = ANY(h.anlage_codes)
  AND h.status = 'A';

-- Für A60-Anlage (Beispiel HB=60 Dual-Prozess)
SELECT h.*, array_to_string(h.anlage_codes, ',') as anlagen
FROM vfahead h
WHERE h.bmdvariante = '60'
  AND h.type = 'HAUPT'
  AND 'A60' = ANY(h.anlage_codes)
  AND h.status = 'A';
```

### 6.2 Parameter mit Programm-Info abrufen
```sql
-- Alle Parameter für einen kompletten Code
WITH code_parts AS (
  SELECT 
    'G2' as anlage,
    '10' as vb,
    '20' as hb,
    '10' as pas,
    '10' as nb
)
SELECT 
  CASE 
    WHEN h.type = 'VOR' THEN 'VB'
    WHEN h.type = 'HAUPT' THEN 'HB'
    WHEN h.type = 'PASSIV' THEN 'PAS'
    WHEN h.type IN ('NACHBEHAND','BESCHPROG') THEN 'NB'
  END as position,
  h.bmdvariante,
  h.beschreibung as programm,
  v.gruppe,
  v.parameter,
  COALESCE(v.daten_char, v.daten_dec::text) as wert
FROM code_parts cp
CROSS JOIN LATERAL (
  SELECT * FROM vfahead
  WHERE status = 'A'
    AND cp.anlage = ANY(anlage_codes)
    AND (
      (type = 'VOR' AND bmdvariante = cp.vb) OR
      (type = 'HAUPT' AND bmdvariante = cp.hb) OR
      (type = 'PASSIV' AND bmdvariante = cp.pas) OR
      (type IN ('NACHBEHAND','BESCHPROG') AND bmdvariante = cp.nb)
    )
) h
LEFT JOIN vfaline v ON h.vfahead_inr = v.vfahead_inr
ORDER BY 
  CASE position
    WHEN 'VB' THEN 1
    WHEN 'HB' THEN 2
    WHEN 'PAS' THEN 3
    WHEN 'NB' THEN 4
  END,
  v.gruppe, v.parameter;
```

### 6.3 Deduplizierte Parameter-Liste
```sql
-- Eindeutige Parameter ohne Duplikate
SELECT DISTINCT ON (v.gruppe, v.parameter)
  v.gruppe,
  v.parameter,
  v.daten_char,
  v.daten_dec,
  v.beschreibung
FROM vfahead h
JOIN vfaline v ON h.vfahead_inr = v.vfahead_inr
WHERE h.status = 'A'
  AND 'G2' = ANY(h.anlage_codes)
  AND h.type = 'HAUPT'
  AND h.bmdvariante = '20'
ORDER BY v.gruppe, v.parameter, h.erstellung_dat DESC;
```

---

## 7. ZUSAMMENFASSUNG DER KRITISCHEN PUNKTE

### ⚠️ WICHTIGSTE REGELN:

1. **ARRAY-FILTERUNG:** 
   - IMMER `WHERE anlage = ANY(anlage_codes)` verwenden
   - NIEMALS direkte Vergleiche mit Arrays

2. **TYPE-MAPPING:**
   - VB → 'VOR'
   - HB → 'HAUPT'
   - PAS → 'PASSIV'
   - NB → 'NACHBEHAND' ODER 'BESCHPROG'

3. **DUAL-PROZESS:**
   - NUR bei A60-Anlage
   - HB=60 bedeutet alkalisch UND sauer
   - Zwei Wirkungsgrade: 65% und 95%

4. **NULL-HANDLING:**
   - Viele VFALINE haben gruppe=NULL
   - Nutze COALESCE(gruppe, 'STANDARD')

5. **DEDUPLIZIERUNG:**
   - Nutze DISTINCT ON für eindeutige Parameter
   - Sortiere nach Erstellungsdatum für neueste Version

---

Dokumentation erstellt: 2025-09-06
Version: 1.0
Fokus: Datenmodell-Verständnis ohne SQL-CREATE Statements