# Variantenexplorer - Datenstruktur-Dokumentation

## Übersicht der Datenarchitektur

Das System verwaltet die Prozessvarianten für 5 Galvanisierungsanlagen an 2 Standorten:
- **Hauptwerk:** G2, G3, G4, G5 (G = Galvanik)
- **Plettenberg:** A60 (A = Außenstelle, 60 = Anlagennummer)

## Varianten-Bezeichnungsformat

Seit Version 2.0 (September 2025) werden Varianten im Format **[Anlage][Typ][Nummer]** angezeigt:
- **Format:** G4Vor10, G4Haupt60, A6Pass23, G2Nach10
- **Typ-Bezeichnungen:**
  - **Vor** = Vorbehandlung (VB)
  - **Haupt** = Hauptbehandlung (HB)
  - **Pass** = Passivierung (PAS)
  - **Nach** = Nachbehandlung (NB)

## Code-Struktur (12-stellig)

```
Position:  1-2    3-4    5-6    7-8    9-10   11-12
          [PLANT][VB  ][HB  ][PAS ][NB  ][XX  ]
          
Beispiel G-Anlage:  G4  10  60  23  10  00
                    │   │   │   │   │   └── Zusatz (meist 00)
                    │   │   │   │   └────── Nachbehandlung
                    │   │   │   └────────── Passivierung
                    │   │   └────────────── Hauptbehandlung
                    │   └────────────────── Vorbehandlung
                    └────────────────────── Anlage (G4)

Beispiel A-Anlage:  A6  10  60  10  22  10
                    │   │   │   │   │   └── Zusatz
                    │   │   │   │   └────── Nachbehandlung
                    │   │   │   └────────── Passivierung
                    │   │   └────────────── Hauptbehandlung
                    │   └────────────────── Vorbehandlung
                    └────────────────────── Anlage (A6 = A60)
```

## Datenfluss-Diagramm

```
┌─────────────────────────────────────────────────────────────────┐
│                         QUELLDATENBANKEN                         │
├─────────────────────────────┬───────────────────────────────────┤
│         PB_Prod             │            MV_Prod                │
│    (G2, G3, G4, G5)         │             (A60)                 │
│                             │                                   │
│  - VFAHEAD (Programme)      │  - VFAHEAD (Programme)           │
│  - VFALINE (Parameter)      │  - VFALINE (Parameter)           │
└──────────┬──────────────────┴────────────┬──────────────────────┘
           │                               │
           │    import_vfa_all.py          │
           ▼                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     PostgreSQL: varianten                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   VFAHEAD    │────▶│   VFALINE    │     │    CODES     │    │
│  │              │ 1:N │              │     │              │    │
│  │ Prozess-     │     │ Parameter    │◀────│ Artikel-     │    │
│  │ programme    │     │ details      │ N:1 │ codes        │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                     ▲            │
│                                                     │            │
└─────────────────────────────────────────────────────┼────────────┘
                                                      │
                              ┌───────────────────────┴────────────┐
                              │    galvanik.artikel                │
                              │    (Artikel mit Codes)             │
                              └────────────────────────────────────┘
```

## Entitäten-Beziehungs-Diagramm

```
┌─────────────────────────────────────────────────────────────────────┐
│                             CODES                                   │
├─────────────────────────────────────────────────────────────────────┤
│ PK: code (VARCHAR)           z.B. "G41060231000"                   │
├─────────────────────────────────────────────────────────────────────┤
│ anlage          VARCHAR(10)  → "G4" oder "A6"                      │
│ anlage_typ      VARCHAR(10)  → "G" oder "A60"                      │
│ vb              VARCHAR(2)   → "10" (Vorbehandlung)                │
│ hb              VARCHAR(2)   → "60" (Hauptbehandlung)              │
│ pas             VARCHAR(2)   → "23" (Passivierung)                 │
│ nb              VARCHAR(2)   → "10" (Nachbehandlung)               │
│ xx              VARCHAR(2)   → "00" (Zusatz)                       │
│                                                                     │
│ FK: vb_vfahead_inr  ─────────┐                                     │
│ FK: hb_vfahead_inr  ─────────┤                                     │
│ FK: pas_vfahead_inr ─────────┼──▶ VFAHEAD.vfahead_inr             │
│ FK: nb_vfahead_inr  ─────────┘                                     │
│                                                                     │
│ vb_beschreibung  TEXT  → "Entfettung alkalisch | Beizen"           │
│ hb_beschreibung  TEXT  → "Verzinkung Dickschicht"                  │
│ pas_beschreibung TEXT  → "Dickschichtpassivierung blau"            │
│ nb_beschreibung  TEXT  → "Trocknung Standard"                      │
│                                                                     │
│ artikel_count    INTEGER → Anzahl Artikel mit diesem Code          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ N:1
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            VFAHEAD                                  │
├─────────────────────────────────────────────────────────────────────┤
│ PK: vfahead_inr        INTEGER  → 12345                            │
├─────────────────────────────────────────────────────────────────────┤
│ vfahead_bmdvariante    VARCHAR  → "10" (padded to 20 chars)        │
│ vfahead_type           VARCHAR  → "VOR", "HAUPT", "PASSIV", etc.   │
│ vfahead_beschreibung   TEXT     → "Entfettung alkalisch"           │
│ vfahead_kurzzeichen    VARCHAR  → "ENTF-ALK"                       │
│ vfahead_status         CHAR(1)  → "A" (Aktiv)                      │
│                                                                     │
│ vfahead_g2aktiv        CHAR(1)  → "T" oder "F"                     │
│ vfahead_g3aktiv        CHAR(1)  → "T" oder "F"                     │
│ vfahead_g4aktiv        CHAR(1)  → "T" oder "F"                     │
│ vfahead_g5aktiv        CHAR(1)  → "T" oder "F"                     │
│                                                                     │
│ source_db              VARCHAR  → "PB_Prod" oder "MV_Prod"         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1:N
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            VFALINE                                  │
├─────────────────────────────────────────────────────────────────────┤
│ PK: vfaline_inr        INTEGER                                     │
│ FK: vfahead_inr        INTEGER ──▶ VFAHEAD.vfahead_inr            │
├─────────────────────────────────────────────────────────────────────┤
│ vfaline_gruppe         VARCHAR  → "CHEMIE", "TEMPERATUR", etc.     │
│ vfaline_parameter      VARCHAR  → "pH-Wert", "Badtemperatur"       │
│ vfaline_daten_char     VARCHAR  → "8.5-9.5" (Text-Werte)          │
│ vfaline_daten_dec      DECIMAL  → 65.5 (Numerische Werte)         │
│ vfaline_beschreibung   TEXT     → "pH-Wert des Entfettungsbads"    │
│ vfaline_einheit        VARCHAR  → "°C", "g/l", "pH"                │
└─────────────────────────────────────────────────────────────────────┘
```

## Prozesstypen nach Anlage

```
┌────────────┬─────────────────────────────────────────────────────────┐
│   ANLAGE   │                    PROZESSTYPEN                         │
├────────────┼─────────────────────────────────────────────────────────┤
│            │  VB          HB          PAS          NB               │
│   G2-G5    │  VOR    →   HAUPT   →   PASSIV  →   TROCKEN           │
│            │                                                         │
│            │  VB          HB          PAS          NB               │
│   A60      │  VOR    →   HAUPT   →   PASSIV  →   BESCHPROG         │
│            │         oder BESCHPROG                                  │
└────────────┴─────────────────────────────────────────────────────────┘

Besonderheiten:
- VOR und PASSIV sind universelle Prozesse (aus PB_Prod)
- HAUPT ist anlagenspezifisch
- A60 kann BESCHPROG für HB und NB verwenden
```

## Mapping-Logik

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CODE-DEKODIERUNG                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Artikel-Code: "G41060231000"                                      │
│       ↓                                                            │
│  Zerlegung in Komponenten:                                         │
│       │                                                            │
│       ├── Anlage: "G4"                                            │
│       ├── VB:     "10" ─────┐                                     │
│       ├── HB:     "60" ─────┤                                     │
│       ├── PAS:    "23" ─────┤ Mapping auf VFAHEAD                │
│       ├── NB:     "10" ─────┤                                     │
│       └── XX:     "00"      │                                     │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────┐            │
│  │            VFAHEAD-SUCHE                         │            │
│  ├──────────────────────────────────────────────────┤            │
│  │                                                  │            │
│  │  WHERE vfahead_bmdvariante = '10                '│            │
│  │    AND vfahead_type = 'VOR                     '│            │
│  │    AND vfahead_g4aktiv = 'T'                    │            │
│  │    AND source_db = 'PB_Prod'                    │            │
│  │                                                  │            │
│  │  Ergebnis: vfahead_inr = 12345                  │            │
│  │           beschreibung = "Entfettung alkalisch"  │            │
│  └──────────────────────────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Subvarianten-Behandlung

```
NB-Code Mapping für Nachbehandlung:
┌──────┬──────┬─────────────────────────────────┐
│ Code │ Maps │ Beschreibung                    │
│      │  To  │                                 │
├──────┼──────┼─────────────────────────────────┤
│  20  │  20  │ Standard-Nachbehandlung         │
│  21  │  20  │ Standard [Subvariante 21]       │
│  22  │  20  │ Standard [Subvariante 22]       │
│  23  │  20  │ Standard [Subvariante 23]       │
└──────┴──────┴─────────────────────────────────┘
```

## Datenquellen-Trennung

```
┌────────────────────────────────────────────────────────────────┐
│                    STRIKTE TRENNUNG                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  PB_Prod Database                 MV_Prod Database            │
│  ┌─────────────────┐             ┌─────────────────┐         │
│  │  G2 Programme   │             │  A60 Programme  │         │
│  │  G3 Programme   │             │  - HAUPT        │         │
│  │  G4 Programme   │             │  - BESCHPROG    │         │
│  │  G5 Programme   │             └─────────────────┘         │
│  │                 │                                          │
│  │  Universelle:   │             Nutzt universelle           │
│  │  - VOR          │◄────────────Prozesse aus                │
│  │  - PASSIV       │             PB_Prod                     │
│  └─────────────────┘                                          │
│                                                                │
│  WICHTIG: Keine Vermischung der Datenquellen!                 │
│  - G-Anlagen nur aus PB_Prod                                  │
│  - A60 HAUPT/BESCHPROG nur aus MV_Prod                        │
│  - A60 VOR/PASSIV aus PB_Prod (universal)                     │
└────────────────────────────────────────────────────────────────┘
```

## Mehrfach-Varianten

```
Beispiel: Mehrere VFAHEAD-Einträge für gleichen Code

VFAHEAD-Tabelle:
┌────────────┬──────────────┬────────┬─────────────────────────┐
│ vfahead_inr│ bmdvariante  │  type  │ beschreibung            │
├────────────┼──────────────┼────────┼─────────────────────────┤
│   12345    │ '10        ' │ 'VOR'  │ 'Entfettung alkalisch'  │
│   12346    │ '10        ' │ 'VOR'  │ 'Entfettung intensiv'   │
│   12347    │ '10        ' │ 'VOR'  │ 'Beizen'                │
└────────────┴──────────────┴────────┴─────────────────────────┘
                      ↓
              Mapping-Ergebnis:
                      ↓
CODES-Tabelle:
┌────────────┬─────────────────┬──────────────────────────────────┐
│    code    │ vb_vfahead_inr  │ vb_beschreibung                  │
├────────────┼─────────────────┼──────────────────────────────────┤
│ G41060... │     12345       │ 'Entfettung alkalisch |          │
│            │                 │  Entfettung intensiv | Beizen'   │
└────────────┴─────────────────┴──────────────────────────────────┘
```

## Datenkonsistenz-Regeln

1. **Code-Format**: Immer 12-stellig (oder länger mit XX-Erweiterung)
2. **Anlagen-Codes**: G2, G3, G4, G5, A6 (A6 wird als A60 angezeigt)
3. **BMD-Varianten**: 2-stellig, rechtsbündig in 20-Zeichen-Feld
4. **Type-Felder**: Rechtsbündig in 20-Zeichen-Feld
5. **Status**: Nur 'A' (Aktiv) wird berücksichtigt
6. **Source_db**: Entweder 'PB_Prod' oder 'MV_Prod'

## Statistiken (Stand: Import)

```
┌─────────────────────────────────────────────────────┐
│                  DATENVOLUMEN                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Artikel (galvanik.artikel):          ~8,400       │
│    - mit G-Codes:                     ~7,000       │
│    - mit A-Codes:                     ~3,500       │
│    - mit beiden:                      ~2,100       │
│                                                     │
│  VFAHEAD Programme:                      234       │
│    - aus PB_Prod:                        180       │
│    - aus MV_Prod:                         54       │
│                                                     │
│  VFALINE Parameter:                    9,908       │
│    - Durchschnitt pro Programm:       40-50        │
│                                                     │
│  Unique Codes (nach Mapping):         ~1,500       │
│    - G2:                                 xxx       │
│    - G3:                                 xxx       │
│    - G4:                                 xxx       │
│    - G5:                                 xxx       │
│    - A60:                                xxx       │
└─────────────────────────────────────────────────────┘
```

## Technische Details

### AS400 CHAR-Felder
- BMD-Varianten und Types sind CHAR(20) in AS400
- Müssen mit Spaces auf 20 Zeichen aufgefüllt werden
- Vergleiche in SQL müssen dies berücksichtigen

### PostgreSQL Optimierungen
```sql
-- Wichtige Indizes
CREATE INDEX idx_vfahead_lookup ON vfahead(
    vfahead_bmdvariante, 
    vfahead_type, 
    source_db
);

CREATE INDEX idx_codes_components ON codes(
    anlage, vb, hb, pas, nb
);

-- Materialized View für häufige Abfragen
CREATE MATERIALIZED VIEW code_overview AS
SELECT 
    c.*,
    vb_vfa.vfahead_beschreibung as vb_desc,
    hb_vfa.vfahead_beschreibung as hb_desc,
    pas_vfa.vfahead_beschreibung as pas_desc,
    nb_vfa.vfahead_beschreibung as nb_desc
FROM codes c
LEFT JOIN vfahead vb_vfa ON c.vb_vfahead_inr = vb_vfa.vfahead_inr
LEFT JOIN vfahead hb_vfa ON c.hb_vfahead_inr = hb_vfa.vfahead_inr
LEFT JOIN vfahead pas_vfa ON c.pas_vfahead_inr = pas_vfa.vfahead_inr
LEFT JOIN vfahead nb_vfa ON c.nb_vfahead_inr = nb_vfa.vfahead_inr;
```