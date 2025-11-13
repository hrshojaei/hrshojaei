# n8n & Notion Integration - Übersicht

## ✅ Implementiert

Die vollständige Integration zwischen dem AI Recruiting Agent, n8n und Notion ist implementiert und einsatzbereit.

## 📁 Dateien

### Neue Dateien
- `src/notion_client.py` - Notion API Integration
- `src/n8n_webhook.py` - n8n Webhook Client
- `N8N_NOTION_GUIDE.md` - Kompletter Setup Guide
- `n8n-workflows/basic-recruiting-workflow.json` - Vorgefertigter Workflow
- `n8n-workflows/README.md` - Workflow Dokumentation
- `scripts/test_integration.py` - Test-Script
- `MAKE_PRIVATE.md` - Anleitung zum Privat-Setzen

### Geänderte Dateien
- `requirements.txt` - notion-client hinzugefügt
- `.env.example` - Notion und n8n Variablen
- `src/config.py` - Neue Konfigurationsoptionen
- `src/candidate_manager.py` - Integration mit Notion/n8n Events

## 🚀 Quick Start

### 1. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 2. Notion einrichten
1. Erstelle eine Notion Integration: https://www.notion.so/my-integrations
2. Erstelle eine Datenbank mit den benötigten Properties (siehe N8N_NOTION_GUIDE.md)
3. Verbinde die Integration mit der Datenbank
4. Kopiere API Key und Database ID

### 3. n8n einrichten
1. Importiere `n8n-workflows/basic-recruiting-workflow.json` in n8n
2. Kopiere die Webhook URL
3. Konfiguriere die Nodes (Slack, Email, etc.)

### 4. .env konfigurieren
```env
# Notion
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=abc123...
NOTION_ENABLED=true

# n8n
N8N_WEBHOOK_URL=https://your-n8n.app/webhook/recruiting-events
N8N_ENABLED=true
```

### 5. Testen
```bash
python scripts/test_integration.py
```

## 📊 Features

### Notion Integration
- ✅ Automatische Kandidaten-Synchronisation
- ✅ Echtzeit Status-Updates
- ✅ Call-Logs als Kommentare
- ✅ Vollständige Datenbank-Properties

### n8n Webhooks
- ✅ `candidate.created` - Neuer Kandidat
- ✅ `candidate.updated` - Kandidat aktualisiert
- ✅ `candidate.interested` - Kandidat interessiert (wichtig!)
- ✅ `call.started` - Anruf gestartet
- ✅ `call.completed` - Anruf beendet
- ✅ `callback.requested` - Rückruf gewünscht

### Workflow-Automatisierung
- ✅ Slack/Email Benachrichtigungen
- ✅ Google Sheets Logging
- ✅ Erweiterbar für CRM, Tasks, etc.

## 📚 Dokumentation

### Hauptdokumentation
- **N8N_NOTION_GUIDE.md** - Vollständiger Setup Guide mit:
  - Notion Workspace Vorbereitung
  - n8n Installation und Konfiguration
  - Event-Beschreibungen
  - Workflow-Ideen
  - Troubleshooting

### Workflow-Dokumentation
- **n8n-workflows/README.md** - Workflow-Templates und Installation

### Repository-Verwaltung
- **MAKE_PRIVATE.md** - Anleitung zum Privat-Setzen des Repos

## 🔧 Technische Details

### Event Flow
```
Recruiting Agent → CandidateManager
                     ↓
                ┌────┴────┐
                ↓         ↓
           Notion API   n8n Webhook
                ↓         ↓
         Datenbank    Workflows
                         ↓
                   Slack/Email/etc.
```

### Async Integration
Alle Notion und n8n Calls werden asynchron ausgeführt:
- Blockiert nicht den Hauptprozess
- Fehler werden geloggt, aber brechen nicht ab
- Kann deaktiviert werden (NOTION_ENABLED=false, N8N_ENABLED=false)

## 🛡️ Sicherheit

- API Keys niemals committen
- .env ist in .gitignore
- Notion API Tokens sind secret_...
- n8n Webhooks sollten HTTPS verwenden
- Optional: Webhook-Authentifizierung möglich

## 🧪 Testen

```bash
# Module testen
python -c "from src.notion_client import notion_client; print(notion_client.is_enabled())"
python -c "from src.n8n_webhook import n8n_webhook; print(n8n_webhook.is_enabled())"

# Integration testen
python scripts/test_integration.py

# Mit echten Kandidaten testen
python -m src.main add  # Kandidat hinzufügen
# Prüfe Notion und n8n Executions
```

## 📝 Repository Privat machen

Um das Repository privat zu setzen, siehe **MAKE_PRIVATE.md**.

**Wichtig:** Dies muss manuell in den GitHub Settings durchgeführt werden:
```
https://github.com/hrshojaei/hrshojaei/settings
→ Danger Zone → Change visibility → Make private
```

## 🆘 Support

Bei Problemen:
1. Prüfe Logs: `tail -f logs/calling_agent_*.log`
2. Teste Module einzeln
3. Siehe Troubleshooting in N8N_NOTION_GUIDE.md

## ✨ Beispiel Workflow

1. Kandidat wird hinzugefügt
   → Erscheint automatisch in Notion
   → n8n erhält `candidate.created` Event

2. Anruf wird getätigt
   → n8n erhält `call.started` Event

3. Kandidat zeigt Interesse
   → Notion Status → "interested"
   → n8n erhält `candidate.interested` Event
   → Slack-Notification an Team
   → Email an Hiring Manager
   → Task in Asana/Trello erstellt

4. Anruf endet
   → Call Log in Notion als Kommentar
   → n8n erhält `call.completed` Event
   → Daten in Google Sheets geloggt

## 🎯 Nächste Schritte

1. Notion Datenbank erstellen und verbinden
2. n8n Workflow importieren und anpassen
3. Testlauf mit Demo-Kandidaten
4. Workflow nach Bedarf erweitern
5. Repository auf privat setzen (optional)

---

**Viel Erfolg mit der Recruiting-Automatisierung!** 🚀
