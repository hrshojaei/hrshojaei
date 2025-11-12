# Import-Anleitung: Fachgeschäfte (Testdaten)

## Übersicht

Diese Testdaten enthalten 11 "Excellence Hörakustik" Fachgeschäfte in den gleichen Städten wie die Arbeitgeber.

## Datei

**test-fachgeschaefte-baden-baden.csv**

### Inhalt:
- 11 Fachgeschäfte
- Alle heißen "Excellence Hörakustik [Stadt]"
- Verteilt über: Gaggenau, Freudenstadt, Karlsruhe, Pfinztal, Malsch, Ettlingen, Offenburg, Achern, Bühl, Rastatt, Baden-Baden
- Kategorie: Hörakustiker

## Import in Notion

### Schritt 1: CSV-Datei herunterladen

Die Datei befindet sich im Repository: `test-fachgeschaefte-baden-baden.csv`

### Schritt 2: Notion-Datenbank öffnen

1. Öffnen Sie Ihre Notion-Datenbank **"Fachgeschäfte"**
2. ID: `c6d33fd30f924e6d87fe4cb9fdb2c2aa`

### Schritt 3: Import durchführen

1. Klicken Sie oben rechts auf **"···"** (Mehr)
2. Wählen Sie **"Import"**
3. Wählen Sie **"CSV"**
4. Laden Sie die Datei `test-fachgeschaefte-baden-baden.csv` hoch

### Schritt 4: Spalten zuordnen

Ordnen Sie die CSV-Spalten den Notion-Properties zu:

| CSV-Spalte | Notion Property |
|------------|----------------|
| Name | Name (Title) |
| Adresse | Adresse |
| Kategorie | Kategorie |

### Schritt 5: Import bestätigen

Klicken Sie auf **"Import"**

## Nach dem Import

### Erwartetes Ergebnis

11 Fachgeschäfte mit vollständigen Adressen:
- Excellence Hörakustik Gaggenau
- Excellence Hörakustik Freudenstadt
- Excellence Hörakustik Karlsruhe
- Excellence Hörakustik Pfinztal
- Excellence Hörakustik Malsch
- Excellence Hörakustik Ettlingen
- Excellence Hörakustik Offenburg
- Excellence Hörakustik Achern
- Excellence Hörakustik Bühl
- Excellence Hörakustik Rastatt
- Excellence Hörakustik Baden-Baden

### Verwendung im Workflow

Diese Fachgeschäfte werden:
1. Von n8n geladen
2. Mit Google Maps geocodiert
3. Kandidaten in der Nähe zugeordnet (innerhalb 25 km)

## Zusammenspiel mit Kandidaten und Arbeitgebern

**Beispiel-Szenario:**
- **Kandidat:** Nina Lehmann wohnt in Gaggenau
- **Aktueller Arbeitgeber:** Hörwelt Gaggenau
- **Fachgeschäft in der Nähe:** Excellence Hörakustik Gaggenau

Der Workflow findet, dass Nina bei "Excellence Hörakustik Gaggenau" arbeiten könnte (gleiche Stadt = kurze Distanz).

## Erwartete Zuordnungen (bei 25 km Radius)

Die meisten Kandidaten sollten mindestens 1-3 Fachgeschäfte zugeordnet bekommen, da:
- Jede Stadt hat mindestens 1 Fachgeschäft
- Nachbarstädte sind oft < 25 km entfernt

**Beispiel Baden-Baden:**
- Kandidaten aus Baden-Baden finden:
  - Excellence Hörakustik Baden-Baden (0 km)
  - Excellence Hörakustik Rastatt (~15 km)
  - Excellence Hörakustik Bühl (~20 km)

## Nächste Schritte

Nach dem Import aller 3 Datenbanken:
1. **Kandidaten** (20 Testdaten)
2. **Arbeitgeber** (20 Testdaten)
3. **Fachgeschäfte** (11 Testdaten)

Führen Sie den n8n Workflow aus und Sie sollten erfolgreiche Zuordnungen sehen!
