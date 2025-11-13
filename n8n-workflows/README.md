# n8n und Notion Workflows Beispiele

Dieses Verzeichnis enthält vorgefertigte n8n Workflow-Templates, die du direkt in deine n8n-Instanz importieren kannst.

## Verfügbare Workflows

### 1. basic-recruiting-workflow.json
Basis-Workflow für die wichtigsten Recruiting-Events:
- ✅ Benachrichtigungen bei interessierten Kandidaten (Slack + Email)
- ✅ Call-Log-Dokumentation in Google Sheets
- ✅ Automatische Response an Webhook

**Events:**
- `candidate.interested` → Slack/Email Benachrichtigung
- `call.completed` → Google Sheets Logging

## Installation

### Schritt 1: Workflow importieren

1. Öffne deine n8n-Instanz
2. Klicke auf **"+ New Workflow"**
3. Klicke auf die **drei Punkte** (⋮) oben rechts
4. Wähle **"Import from File"**
5. Wähle die `.json` Datei aus diesem Ordner

### Schritt 2: Webhook URL kopieren

1. Klicke im importierten Workflow auf den **"Webhook"** Node
2. Kopiere die **Webhook URL** (z.B. `https://your-n8n.app/webhook/recruiting-events`)
3. Speichere diese URL für die Konfiguration

### Schritt 3: Recruiting Agent konfigurieren

Füge in deiner `.env` Datei hinzu:

```env
N8N_WEBHOOK_URL=https://your-n8n.app/webhook/recruiting-events
N8N_ENABLED=true
```

### Schritt 4: Services verbinden

Konfiguriere die einzelnen Nodes im Workflow:

#### Slack Node
- Verbinde deinen Slack Workspace
- Wähle den Ziel-Channel
- Passe die Nachricht nach Bedarf an

#### Email Node
- Konfiguriere SMTP oder nutze einen Service (SendGrid, Mailgun)
- Setze Absender und Empfänger
- Passe Betreff und Text an

#### Google Sheets Node (optional)
- Verbinde deinen Google Account
- Erstelle ein neues Google Sheet für "Call Logs"
- Kopiere die Sheet ID in den Node
- Stelle sicher, dass die Spalten übereinstimmen:
  - Timestamp
  - Candidate ID
  - Name
  - Outcome
  - Duration
  - Summary
  - Next Action

### Schritt 5: Workflow aktivieren

1. Klicke oben rechts auf **"Active"** (Toggle)
2. Der Workflow ist nun live!

## Events Testen

Du kannst Events manuell testen:

```bash
# Test mit curl
curl -X POST https://your-n8n.app/webhook/recruiting-events \
  -H "Content-Type: application/json" \
  -d '{
    "event": "candidate.interested",
    "timestamp": "2024-11-13T21:00:00",
    "data": {
      "candidate_id": 1,
      "candidate_name": "Test Kandidat",
      "phone": "+4915112345678",
      "email": "test@example.com",
      "notes": "Test Notiz",
      "priority": "high"
    }
  }'
```

## Workflow erweitern

### Weitere Services hinzufügen

Du kannst den Workflow einfach erweitern:

1. **Notion**: Direkt Kandidaten in Notion erstellen/aktualisieren
2. **Trello/Asana**: Tasks für Follow-ups erstellen
3. **CRM**: HubSpot, Salesforce, Pipedrive synchronisieren
4. **SMS**: Twilio SMS für dringende Kandidaten
5. **Calendar**: Google Calendar Events für Termine

### Beispiel: Notion Node hinzufügen

1. Füge nach "Is Candidate Interested?" einen **Notion Node** hinzu
2. Wähle "Create Database Item"
3. Verbinde mit deiner Notion-Datenbank
4. Mappe die Felder:
   ```
   Name → {{$json.data.candidate_name}}
   Phone → {{$json.data.phone}}
   Status → interested
   ```

### Beispiel: SMS bei sehr interessierten Kandidaten

```javascript
// Function Node
if (items[0].json.data.priority === 'high') {
  return items;
}
return [];

// Dann verbinden mit Twilio SMS Node
```

## Best Practices

### 1. Error Handling
- Füge Error Trigger Nodes hinzu
- Logge fehlgeschlagene Events
- Sende Error-Notifications an Admin

### 2. Filtering
- Nutze IF Nodes um Events zu filtern
- Verhindere redundante Benachrichtigungen
- Priorisiere wichtige Events

### 3. Rate Limiting
- Beachte API Limits von Services
- Nutze Queue/Batch Nodes bei hoher Last
- Implementiere Retry-Logic

### 4. Monitoring
- Überwache Workflow-Executions
- Prüfe regelmäßig Failed Runs
- Setze Alerts für kritische Fehler

## Verfügbare Events

Alle Events die der Recruiting Agent sendet:

| Event | Beschreibung | Wichtigkeit |
|-------|--------------|-------------|
| `candidate.created` | Neuer Kandidat erstellt | Normal |
| `candidate.updated` | Kandidat aktualisiert | Normal |
| `call.started` | Anruf gestartet | Normal |
| `call.completed` | Anruf beendet | Normal |
| `candidate.interested` | Kandidat ist interessiert | **Hoch** |
| `callback.requested` | Rückruf angefordert | Mittel |

## Troubleshooting

### Webhook empfängt keine Events
```bash
# Prüfe ob n8n erreichbar ist
curl https://your-n8n.app/webhook/recruiting-events

# Prüfe Recruiting Agent Logs
tail -f logs/calling_agent_*.log | grep n8n
```

### Workflow führt nicht aus
- Stelle sicher, dass Workflow **Active** ist
- Prüfe ob Webhook Node korrekt konfiguriert ist
- Teste mit Manual Trigger

### Services nicht verbunden
- Reconnect die OAuth-Verbindungen
- Prüfe API Keys und Credentials
- Teste Nodes einzeln mit "Execute Node"

## Support

Bei Fragen:
- Siehe [N8N_NOTION_GUIDE.md](../N8N_NOTION_GUIDE.md) für Details
- n8n Docs: https://docs.n8n.io
- Notion API: https://developers.notion.com

## Weitere Workflow-Ideen

1. **Daily Summary**: Täglicher Report mit allen Anrufen
2. **Lead Scoring**: Automatisches Scoring basierend auf Responses
3. **Follow-up Automation**: Automatische Reminder für Callbacks
4. **Team Dashboard**: Live-Dashboard mit Airtable/Notion
5. **Analytics**: Daten-Aggregation für Reports
