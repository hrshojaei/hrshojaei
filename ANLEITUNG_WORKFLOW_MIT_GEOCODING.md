# Workflow mit Geocoding - Import-Anleitung

## Übersicht

Dieser Workflow verwendet **HTTP Request Nodes** statt `fetch()` im Code, damit das Geocoding funktioniert.

## Workflow-Struktur

```
Manueller Start
    ↓
⚙️ Distanz einstellen (25 km)
    ↓
📋 Kandidaten laden  +  🏪 Fachgeschäfte laden
    ↓
🔀 Kombination (Merge)
    ↓
📍 Adressen extrahieren (Code)
    ↓
🌍 Google Geocoding API (HTTP Request) ← Hier passiert das Geocoding!
    ↓
📊 Koordinaten verarbeiten (Code)
    ↓
🎯 Zuordnung berechnen (Code mit Haversine-Formel)
```

## Import-Schritte

### 1. Workflow importieren

1. Gehen Sie zu **https://8n8ai.de/**
2. Klicken Sie oben rechts auf **"+  Add workflow"**
3. Klicken Sie auf **"Import from file"** oder fügen Sie die URL ein:
   ```
   https://raw.githubusercontent.com/hrshojaei/hrshojaei/claude/debug-code-execution-011CV28knBYFZ6rA66497Siu/n8n-workflow-mit-geocoding.json
   ```

### 2. Notion Credentials konfigurieren

Für die Nodes **"📋 Kandidaten laden"** und **"🏪 Fachgeschäfte laden"**:

1. Klicken Sie auf den Node
2. Wählen Sie Ihre **Notion Credentials**
3. Prüfen Sie die **Database ID**:
   - Kandidaten: `b3f1eeab2d1a42f2a9ba9792568bc217`
   - Fachgeschäfte: `c6d33fd30f924e6d87fe4cb9fdb2c2aa`

### 3. Distanz anpassen (optional)

Im Node **"⚙️ Distanz einstellen"**:
- Ändern Sie den Wert von `25` auf die gewünschte Distanz (10-100 km)

## Wie es funktioniert

### Schritt 1: Adressen extrahieren
Der Code sammelt alle Adressen aus Kandidaten und Fachgeschäften.

### Schritt 2: Geocoding via HTTP Request
**WICHTIG:** Der Node **"🌍 Google Geocoding API"** macht für **JEDE** Adresse einen separaten API-Aufruf.

- Bei 20 Kandidaten + 10 Fachgeschäften = **30 API-Aufrufe**
- Das dauert ca. 5-10 Sekunden
- Google Maps API Limit: 40.000 Aufrufe/Monat (kostenlos)

### Schritt 3: Distanzberechnung
Der Code berechnet mit der **Haversine-Formel** die Distanz zwischen Kandidaten und Fachgeschäften.

### Schritt 4: Zuordnung
Nur Fachgeschäfte innerhalb der gewählten Distanz werden zugeordnet.

## Ergebnis

Der Workflow gibt aus:

```json
{
  "kandidat_id": "xxx",
  "kandidat_name": "Max Mustermann",
  "fachgeschaefte_ids": ["id1", "id2"],
  "fachgeschaefte_namen": ["Geschäft A", "Geschäft B"],
  "distanzen_km": [5.3, 12.7],
  "anzahl": 2
}
```

## Notion-Zuordnung schreiben

**NÄCHSTER SCHRITT:** Fügen Sie einen weiteren Node hinzu, der die Zuordnungen zurück nach Notion schreibt:

1. Node: **"Notion - Update Page"**
2. Für jeden Kandidaten: Aktualisiere das Feld `property_kandidaten` mit den `fachgeschaefte_ids`

## Troubleshooting

### Problem: "Too many requests"
- Google Maps API Limit erreicht
- Lösung: Warten Sie 1 Minute oder nutzen Sie weniger Test-Daten

### Problem: "Keine Koordinaten gefunden"
- Adresse ist ungültig oder unvollständig
- Lösung: Prüfen Sie die Adressen in Notion

### Problem: Workflow ist langsam
- Normal bei vielen Adressen (1-2 Sekunden pro Adresse)
- Lösung: Akzeptieren oder Koordinaten vorab speichern

## Optimierung für Produktion

### Idee: Koordinaten in Notion speichern

1. Fügen Sie Spalten hinzu:
   - `Koordinaten_Lat` (Number)
   - `Koordinaten_Lng` (Number)
2. Geocodieren Sie Adressen nur 1x beim Erstellen
3. Verwenden Sie die gespeicherten Koordinaten für Zuordnungen

Das spart API-Aufrufe und macht den Workflow schneller!
