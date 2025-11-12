# Import-Anleitung: Aktuelle Arbeitgeber (Testdaten)

## Übersicht

Diese Testdaten enthalten 20 realistische Arbeitgeber (Hörgeräte-Geschäfte) in der Region Baden-Baden und Umgebung.

## Datei

**test-arbeitgeber-baden-baden.csv**

### Inhalt:
- 20 Arbeitgeber
- Verteilt über: Gaggenau, Freudenstadt, Karlsruhe, Pfinztal, Malsch, Ettlingen, Offenburg, Achern, Bühl, Rastatt, Baden-Baden
- Kategorien: Hörakustiker, Optiker mit Hörakustik, Hörakustiker Filialen

## Import in Notion

### Schritt 1: CSV-Datei herunterladen

Die Datei befindet sich im Repository: `test-arbeitgeber-baden-baden.csv`

### Schritt 2: Notion-Datenbank öffnen

1. Öffnen Sie Ihre Notion-Datenbank **"Aktuelle Arbeitgeber"**
2. ID: `29a0974bd6228043850bf887c636d116`

### Schritt 3: Import durchführen

1. Klicken Sie oben rechts auf **"···"** (Mehr)
2. Wählen Sie **"Import"**
3. Wählen Sie **"CSV"**
4. Laden Sie die Datei `test-arbeitgeber-baden-baden.csv` hoch

### Schritt 4: Spalten zuordnen

Ordnen Sie die CSV-Spalten den Notion-Properties zu:

| CSV-Spalte | Notion Property |
|------------|----------------|
| Name | Name (Title) |
| Adresse | Adresse |
| Kategorie | Kategorie |
| Stadt | Stadt |

**Falls Properties fehlen:**
- Erstellen Sie sie in Notion (z.B. "Kategorie" als Text, "Stadt" als Text)

### Schritt 5: Import bestätigen

Klicken Sie auf **"Import"**

## Nach dem Import

### Erwartetes Ergebnis

20 Arbeitgeber mit folgenden Eigenschaften:
- **Name**: z.B. "Hörwelt Gaggenau"
- **Adresse**: Vollständige Adresse mit PLZ
- **Kategorie**: Hörakustiker, Optiker mit Hörakustik, etc.
- **Stadt**: Gaggenau, Freudenstadt, Karlsruhe, etc.

### Verwendung im Workflow

Die Arbeitgeber-Daten werden geladen, aber aktuell **nicht für die Zuordnung verwendet**.

Der Workflow nutzt nur:
1. **Kandidaten** → Suchen Fachgeschäfte in der Nähe
2. **Fachgeschäfte** → Werden Kandidaten zugeordnet

**Mögliche Erweiterung:**
- Kandidaten haben einen "Aktuellen Arbeitgeber"
- Workflow schließt diesen Arbeitgeber von Zuordnungen aus
- Oder: Bevorzugt Fachgeschäfte die NICHT der aktuelle Arbeitgeber sind

## Arbeitgeber-Verteilung

| Stadt | Anzahl Arbeitgeber |
|-------|-------------------|
| Baden-Baden | 2 |
| Karlsruhe | 2 |
| Offenburg | 2 |
| Gaggenau | 2 |
| Freudenstadt | 2 |
| Achern | 2 |
| Bühl | 2 |
| Rastatt | 2 |
| Ettlingen | 2 |
| Pfinztal | 1 |
| Malsch | 1 |

## Zusammenspiel mit Kandidaten

Beispiel:
- **Nina Lehmann** wohnt in Gaggenau
- **Aktueller Arbeitgeber**: Hörwelt Gaggenau (auch in Gaggenau)
- **Zuordnung**: Findet andere Fachgeschäfte in der Nähe für Wechsel-Optionen

Dies simuliert realistische Recruiting-Szenarien, wo Kandidaten bei einem Arbeitgeber sind und zu anderen wechseln könnten.
