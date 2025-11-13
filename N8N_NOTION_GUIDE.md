# n8n und Notion Integration

Dieses Dokument beschreibt, wie du den AI Recruiting Agent mit n8n (Workflow-Automatisierung) und Notion (Kandidaten-Datenbank) integrierst.

## Übersicht

Die Integration ermöglicht:
- 📊 **Notion**: Automatische Synchronisation von Kandidaten und Call-Logs in eine Notion-Datenbank
- 🔄 **n8n**: Event-basierte Workflow-Automatisierung für Benachrichtigungen, Follow-ups und Team-Koordination
- 🚀 **Automatisierung**: Echtzeit-Benachrichtigungen bei interessierten Kandidaten, automatische Dokumentation

## Teil 1: Notion Integration

### 1.1 Notion Workspace vorbereiten

#### Schritt 1: Notion Integration erstellen

1. Gehe zu [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Klicke auf "+ New Integration"
3. Gib einen Namen ein: "AI Recruiting Agent"
4. Wähle den Workspace aus
5. Klicke auf "Submit"
6. **Kopiere den "Internal Integration Token"** (beginnt mit `secret_...`)

#### Schritt 2: Notion Datenbank erstellen

1. Öffne Notion und erstelle eine neue Page
2. Füge eine neue Database (Table) hinzu
3. Benenne sie: "Recruiting Kandidaten"
4. Füge folgende Properties hinzu:

| Property Name | Type | Beschreibung |
|---------------|------|--------------|
| Name | Title | Kandidatenname |
| Candidate ID | Number | Eindeutige ID aus der SQLite DB |
| Telefon | Phone | Telefonnummer |
| Email | Email | E-Mail-Adresse |
| Status | Select | new, contacted, interested, not_interested, callback |
| Aktueller Arbeitgeber | Text | Aktueller Arbeitgeber |
| Position | Text | Aktuelle Position |
| Berufserfahrung (Jahre) | Number | Jahre Berufserfahrung |
| Notizen | Text | Zusätzliche Notizen |
| Letzter Anruf | Date | Datum des letzten Anrufs |
| Anruf-Ergebnis | Select | interested, not_interested, callback_requested, info_sent |

**Select Options für "Status":**
- new (Grau)
- contacted (Blau)
- interested (Grün)
- not_interested (Rot)
- callback (Orange)

**Select Options für "Anruf-Ergebnis":**
- interested (Grün)
- not_interested (Rot)
- callback_requested (Orange)
- info_sent (Blau)
- appointment_scheduled (Lila)

#### Schritt 3: Integration mit Datenbank verbinden

1. Öffne die erstellte Datenbank in Notion
2. Klicke oben rechts auf "..." (drei Punkte)
3. Scrolle zu "Connections" → "+ Add connections"
4. Wähle deine erstellte Integration ("AI Recruiting Agent")

#### Schritt 4: Database ID kopieren

Die Database ID findest du in der URL:
```
https://www.notion.so/[workspace]/[DATABASE_ID]?v=[view_id]
```

Beispiel:
```
https://www.notion.so/myworkspace/abc123def456?v=...
                                  ^^^^^^^^^^^ 
                                  Dies ist die Database ID
```

### 1.2 Recruiting Agent konfigurieren

Bearbeite deine `.env` Datei:

```env
# Notion Integration
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=abc123def456
NOTION_ENABLED=true
```

### 1.3 Notion Integration testen

```bash
# Server starten
python -m src.main server

# In einem neuen Terminal: Test-Kandidat erstellen
python -m src.main add
```

Nach dem Hinzufügen eines Kandidaten sollte dieser automatisch in Notion erscheinen!

### 1.4 Funktionen

Die Notion-Integration synchronisiert automatisch:

1. **Neue Kandidaten**: Werden sofort in Notion erstellt
2. **Kandidaten-Updates**: Status-Änderungen werden synchronisiert
3. **Call-Logs**: Jeder Anruf wird als Kommentar auf der Kandidaten-Page hinzugefügt
4. **Gesprächsverläufe**: Details wie Dauer, Ergebnis, Zusammenfassung

## Teil 2: n8n Workflow Integration

### 2.1 n8n installieren

#### Option A: n8n Cloud (empfohlen für Anfänger)

1. Gehe zu [https://n8n.io](https://n8n.io)
2. Erstelle einen Account
3. Starte eine n8n Cloud-Instanz

#### Option B: Self-hosted n8n

```bash
# Mit Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Oder mit npm
npm install -g n8n
n8n start
```

### 2.2 n8n Workflow importieren

1. Öffne n8n (http://localhost:5678)
2. Klicke auf "+ New Workflow"
3. Klicke auf "..." (drei Punkte) → "Import from File"
4. Wähle: `n8n-workflows/basic-recruiting-workflow.json`

### 2.3 Workflow konfigurieren

#### Schritt 1: Webhook URL erhalten

1. Öffne den importierten Workflow
2. Klicke auf den "Webhook" Node
3. Kopiere die Webhook URL (z.B. `https://your-n8n.app/webhook/recruiting-events`)

#### Schritt 2: Recruiting Agent konfigurieren

Füge in deiner `.env` hinzu:

```env
# n8n Webhook
N8N_WEBHOOK_URL=https://your-n8n.app/webhook/recruiting-events
N8N_ENABLED=true
```

#### Schritt 3: Workflow-Nodes anpassen

**Slack Notification Node:**
- Verbinde deinen Slack Account
- Wähle den gewünschten Channel
- Format kann angepasst werden

**Email Node:**
- Konfiguriere SMTP-Einstellungen oder nutze einen Service
- Passe Absender und Empfänger an

**Google Sheets Node (optional):**
- Verbinde Google Account
- Erstelle ein Google Sheet für Call Logs
- Kopiere die Sheet ID in den Node

### 2.4 Workflow aktivieren

1. Klicke in n8n oben rechts auf "Active"
2. Der Workflow ist nun aktiv und empfängt Events!

## Teil 3: Events und Automatisierungen

### 3.1 Verfügbare Events

Der Recruiting Agent sendet folgende Events an n8n:

#### candidate.created
```json
{
  "event": "candidate.created",
  "timestamp": "2024-11-13T21:00:00",
  "data": {
    "candidate_id": 123,
    "name": "Max Mustermann",
    "phone": "+4915112345678",
    "email": "max@example.com",
    "company": "Hörakustik XY"
  }
}
```

#### candidate.updated
```json
{
  "event": "candidate.updated",
  "timestamp": "2024-11-13T21:00:00",
  "data": {
    "candidate_id": 123,
    "name": "Max Mustermann",
    "status": "interested",
    "changes": {...}
  }
}
```

#### call.started
```json
{
  "event": "call.started",
  "timestamp": "2024-11-13T21:00:00",
  "data": {
    "call_sid": "CA123...",
    "candidate_id": 123,
    "candidate_name": "Max Mustermann",
    "phone": "+4915112345678"
  }
}
```

#### call.completed
```json
{
  "event": "call.completed",
  "timestamp": "2024-11-13T21:05:00",
  "data": {
    "call_sid": "CA123...",
    "candidate_id": 123,
    "candidate_name": "Max Mustermann",
    "duration_seconds": 300,
    "outcome": "interested",
    "summary": "Kandidat sehr interessiert...",
    "next_action": "Termin vereinbaren"
  }
}
```

#### candidate.interested ⭐ (Wichtig!)
```json
{
  "event": "candidate.interested",
  "timestamp": "2024-11-13T21:05:00",
  "data": {
    "candidate_id": 123,
    "candidate_name": "Max Mustermann",
    "phone": "+4915112345678",
    "email": "max@example.com",
    "notes": "Sehr interessiert, sofort kontaktieren!",
    "priority": "high"
  }
}
```

#### callback.requested
```json
{
  "event": "callback.requested",
  "timestamp": "2024-11-13T21:05:00",
  "data": {
    "candidate_id": 123,
    "candidate_name": "Max Mustermann",
    "phone": "+4915112345678",
    "requested_time": "Morgen zwischen 10-12 Uhr"
  }
}
```

### 3.2 Workflow-Ideen

#### 1. Sofortige Benachrichtigung bei Interesse

```
Webhook → Filter (candidate.interested) → Slack/Email → Notion Update
```

#### 2. Follow-up Tasks erstellen

```
Webhook → Filter (callback.requested) → Create Task (Todoist/Asana) → Email
```

#### 3. Call Logs dokumentieren

```
Webhook → Filter (call.completed) → Google Sheets Append → Notion Comment
```

#### 4. Team-Dashboard aktualisieren

```
Webhook → Filter (alle events) → Update Dashboard (Airtable/Notion/Sheets)
```

#### 5. CRM Integration

```
Webhook → Filter → HubSpot/Salesforce/Pipedrive Update
```

## Teil 4: Erweiterte Konfiguration

### 4.1 Notion: Separate Call Logs Datenbank

Für detailliertere Auswertungen kannst du eine separate Call Logs Datenbank erstellen:

**Properties:**
- Call ID (Title)
- Candidate (Relation → Recruiting Kandidaten)
- Datum (Date)
- Dauer (Number)
- Ergebnis (Select)
- Zusammenfassung (Text)
- Nächster Schritt (Text)

### 4.2 n8n: Mehrere Workflows

Erstelle separate Workflows für verschiedene Zwecke:

1. **Notifications Workflow**: Slack/Email Benachrichtigungen
2. **Documentation Workflow**: Logs in verschiedene Tools
3. **Follow-up Workflow**: Automatische Task-Erstellung
4. **Analytics Workflow**: Daten-Aggregation und Reports

### 4.3 Error Handling

In n8n:
- Füge "Error Trigger" Nodes hinzu
- Sende Fehler-Benachrichtigungen
- Logge Failed Events für Retry

## Teil 5: Best Practices

### 5.1 Sicherheit

- ✅ Notion API Keys niemals committen
- ✅ n8n Webhooks sollten HTTPS verwenden
- ✅ Verwende Webhook Authentifizierung (optional)
- ✅ Limitiere Zugriff auf sensible Daten

### 5.2 Performance

- ⚡ Notion API hat Rate Limits (3 requests/second)
- ⚡ n8n Webhooks: Nutze Queues für hohe Last
- ⚡ Batching für Bulk-Operations

### 5.3 Monitoring

- 📊 Überwache n8n Workflow Executions
- 📊 Prüfe Notion Sync-Fehler in Logs
- 📊 Setze Alerts für Failed Executions

## Teil 6: Troubleshooting

### Notion Sync funktioniert nicht

```bash
# Prüfe Logs
tail -f logs/calling_agent_*.log | grep -i notion

# Test Notion Connection
python -c "from src.notion_client import notion_client; print(notion_client.is_enabled())"
```

**Häufige Probleme:**
- ❌ Integration nicht mit Datenbank verbunden
- ❌ Falsche Database ID
- ❌ API Key ungültig
- ❌ Properties haben andere Namen

### n8n Webhook empfängt keine Events

```bash
# Prüfe Logs
tail -f logs/calling_agent_*.log | grep -i n8n

# Test Webhook manuell
curl -X POST https://your-n8n.app/webhook/recruiting-events \
  -H "Content-Type: application/json" \
  -d '{"event":"test","data":{}}'
```

**Häufige Probleme:**
- ❌ N8N_ENABLED=false in .env
- ❌ Falsche Webhook URL
- ❌ n8n Workflow nicht aktiviert
- ❌ Firewall blockiert Requests

## Teil 7: Beispiel Setup

### Komplettes Setup-Script

```bash
# 1. Notion konfigurieren
export NOTION_API_KEY="secret_..."
export NOTION_DATABASE_ID="abc123..."
export NOTION_ENABLED=true

# 2. n8n konfigurieren
export N8N_WEBHOOK_URL="https://your-n8n.app/webhook/recruiting-events"
export N8N_ENABLED=true

# 3. .env aktualisieren
echo "NOTION_API_KEY=$NOTION_API_KEY" >> .env
echo "NOTION_DATABASE_ID=$NOTION_DATABASE_ID" >> .env
echo "NOTION_ENABLED=$NOTION_ENABLED" >> .env
echo "N8N_WEBHOOK_URL=$N8N_WEBHOOK_URL" >> .env
echo "N8N_ENABLED=$N8N_ENABLED" >> .env

# 4. Server neustarten
pkill -f "python -m src.main"
python -m src.main server
```

## Zusammenfassung

Mit dieser Integration hast du:
- ✅ Automatische Kandidaten-Dokumentation in Notion
- ✅ Echtzeit-Benachrichtigungen via n8n
- ✅ Flexible Workflow-Automatisierung
- ✅ Zentrale Datenverwaltung
- ✅ Team-Kollaboration in Notion

Bei Fragen oder Problemen, siehe die Logs oder erstelle ein Issue im Repository!
