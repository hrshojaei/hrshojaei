# n8n Workflow Integration

Dieser Workflow automatisiert die Kandidaten-Zuordnung und Call-Trigger-Funktionalität.

## 🎯 Was macht der Workflow?

1. **Kandidaten & Fachgeschäfte aus Notion laden**
   - Notion Database: Kandidaten (mit Wohnadresse & Telefonnummer)
   - Notion Database: Fachgeschäfte (mit Adresse)
   - Notion Database: Aktuelle Arbeitgeber

2. **Adressen geocodieren**
   - Google Geocoding API → Lat/Lng Koordinaten

3. **Distanz-basierte Zuordnung**
   - Berechnet Entfernung zwischen Kandidaten und Fachgeschäften
   - **Dynamischer Distanz-Bereich: 10-100 km** (anpassbar)
   - Sortiert nach nächstem Fachgeschäft

4. **Automatischer Call-Trigger**
   - Sendet Daten an deine Calling-API
   - Triggert automatisch Anrufe für passende Kandidaten

## 📋 Setup-Anleitung

### 1. Workflow in n8n importieren

```bash
# Workflow-Datei liegt in:
n8n-workflows/kandidaten-zuordnung-mit-calls.json
```

In n8n:
1. **Workflows** → **Import from File**
2. Wähle: `kandidaten-zuordnung-mit-calls.json`
3. Klicke **Import**

### 2. Environment Variable setzen

In n8n unter **Settings → Environment Variables**:

```
CALLING_API_URL=https://deine-domain.com
```

**Oder** direkt im HTTP Request Node eintragen:
- Node `📞 Call triggern` öffnen
- URL ändern: `https://deine-domain.com/api/n8n/trigger-call`

### 3. Notion Credentials konfigurieren

Die drei Notion-Nodes benötigen:
- **Credential Name**: `Notion Kandidaten`
- Notion Integration Token

Falls noch nicht vorhanden:
1. [Notion Integration erstellen](https://www.notion.so/my-integrations)
2. Token kopieren
3. In n8n unter **Credentials** → **Notion API** hinzufügen
4. Datenbanken freigeben für die Integration

### 4. Google Maps API Key

Der Node `🌍 Google Geocoding API` nutzt bereits einen API Key.

**Optional**: Eigenen Key verwenden:
1. [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **Credentials**
3. API Key erstellen
4. Geocoding API aktivieren
5. Key im Node ersetzen

## ⚙️ Distanz anpassen

Im Node **⚙️ Distanz einstellen (10-100 km)**:

```javascript
{
  "min_distanz_km": 10,   // Minimum Distanz
  "max_distanz_km": 100   // Maximum Distanz
}
```

**Beispiele:**
- `10-50 km` → Lokale Kandidaten
- `20-100 km` → Regionale Kandidaten
- `5-25 km` → Sehr nah

## 🚀 Workflow starten

1. Workflow öffnen in n8n
2. Oben rechts: **Execute Workflow**
3. Workflow läuft automatisch durch

**Output:**
```json
{
  "kandidat_id": "notion-id",
  "kandidat_name": "Max Mustermann",
  "kandidat_phone": "+4915112345678",
  "fachgeschaefte_namen": ["Geschäft A", "Geschäft B"],
  "distanzen_km": [15.3, 42.7],
  "naechstes_geschaeft": "Geschäft A",
  "naechste_distanz_km": 15.3
}
```

Für jeden Kandidaten wird automatisch ein Call getriggert via:
```
POST /api/n8n/trigger-call
```

## 🔧 API-Endpoint Details

### POST `/api/n8n/trigger-call`

**Request Body:**
```json
{
  "kandidat_id": "notion-id",
  "kandidat_name": "Max Mustermann",
  "phone": "+4915112345678",
  "fachgeschaefte": ["Geschäft A", "Geschäft B"],
  "distanzen": [15.3, 42.7],
  "naechstes_geschaeft": "Geschäft A"
}
```

**Response:**
```json
{
  "success": true,
  "kandidat_id": "notion-id",
  "candidate_id_db": 123,
  "call_sid": "CAxxxx" // oder "session_id" für Sipgate,
  "message": "Call zu Max Mustermann getriggert"
}
```

### Was passiert im Backend?

1. **Kandidat-Check**: Prüft ob Kandidat bereits in DB existiert
2. **Anlegen**: Falls neu → Kandidat in DB anlegen mit Notizen:
   ```
   Nächstes Fachgeschäft: Geschäft A (15.3 km)
   Weitere Geschäfte in der Nähe: Geschäft B, Geschäft C
   ```
3. **Call-Trigger**: Startet automatischen Anruf via Twilio/Sipgate

## 🎨 Workflow-Visualisierung

```
Manueller Start
    ↓
⚙️ Distanz einstellen (10-100 km)
    ↓ ↓ ↓
📋 Kandidaten laden    🏪 Fachgeschäfte laden    👔 Arbeitgeber laden
    ↓ ↓ ↓
🔀 Kombination (Merge)
    ↓
📍 Adressen extrahieren
    ↓
🌍 Google Geocoding API (parallel für alle Adressen)
    ↓
📊 Koordinaten verarbeiten
    ↓
🔗 Alle Koordinaten sammeln (Aggregate)
    ↓
🎯 Zuordnung berechnen (Haversine-Formel)
    ↓
📞 Call triggern (HTTP Request → deine API)
```

## 🐛 Troubleshooting

### Keine Ergebnisse?

**Console-Log prüfen:**
Der Node `🎯 Zuordnung berechnen` gibt Debug-Output:
```
=== DISTANZ-BEREICH ===
Min: 10 km, Max: 100 km

Kandidaten: 25
Fachgeschäfte: 8

Max Mustermann (lat, lng):
  → Geschäft A: 15.3 km
    ✓ INNERHALB 10-100 km!
  → Geschäft B: 142.7 km
```

### API Call schlägt fehl?

1. **Server läuft?**
   ```bash
   python -m src.main server
   ```

2. **URL korrekt?**
   - Environment Variable `CALLING_API_URL` gesetzt?
   - Node `📞 Call triggern` → URL prüfen

3. **Telefonnummer fehlt?**
   - Notion: Feld `property_telefonnummer` muss gefüllt sein

### Geocoding-Fehler?

- Google Maps API Quota überschritten?
- API Key gültig?
- Adressformat korrekt? (Straße, PLZ Ort, Land)

## 📊 Kosten

**Google Geocoding API:**
- Erste 40.000 Requests/Monat: **kostenlos**
- Danach: $5 pro 1.000 Requests
- [Pricing Details](https://mapsplatform.google.com/pricing/)

**n8n:**
- Self-hosted: **kostenlos**
- Cloud: Ab $20/Monat

**Calling-App:**
- Siehe Hauptprojekt `README.md`

## 🔐 Sicherheit

**WICHTIG:**
- Google API Key nicht im Code committen (wenn eigenen verwendest)
- n8n Webhook mit Authentication schützen
- Environment Variables nutzen für URLs/Keys

## 📝 Anpassungen

### Nur bestimmte Kandidaten anrufen

Im Node `🎯 Zuordnung berechnen` am Ende hinzufügen:

```javascript
// Nur Top 10 Kandidaten mit nächster Distanz
ergebnisse.sort((a, b) => a.naechste_distanz_km - b.naechste_distanz_km);
return ergebnisse.slice(0, 10);
```

### Rate Limiting (nicht alle auf einmal anrufen)

Nach Node `📞 Call triggern` einen **Wait Node** einfügen:
- **Wait**: 5 Sekunden zwischen Calls
- Verhindert API Rate Limits

### Ergebnisse zurück nach Notion schreiben

Nach Node `🎯 Zuordnung berechnen`:
- **Notion Node** hinzufügen
- **Operation**: Update Database Page
- **Update**: Feld `zugeordnete_geschaefte` mit `fachgeschaefte_namen`

## 💡 Weitere Ideen

- **Scheduling**: Workflow täglich automatisch laufen lassen
- **Filter**: Nur Kandidaten mit Status "Neu" anrufen
- **Notifications**: Slack/Email bei erfolgreichen Calls
- **Analytics**: Call-Erfolgsquote nach Distanz auswerten

## 🆘 Support

Bei Fragen:
1. n8n Community Forum: https://community.n8n.io/
2. GitHub Issues im Hauptprojekt
