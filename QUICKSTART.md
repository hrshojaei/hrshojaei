# Quickstart Guide - AI Recruiting Call Agent

Dieses Tutorial führt dich Schritt für Schritt durch die Einrichtung und den ersten Test-Anruf.

## 1. Voraussetzungen

### Python Installation
```bash
python --version  # Sollte 3.10 oder höher sein
```

Falls Python nicht installiert ist, lade es von [python.org](https://python.org) herunter.

### Twilio Account erstellen

1. Gehe zu [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Registriere dich für einen kostenlosen Trial Account
3. Verifiziere deine Email und Telefonnummer
4. Du erhältst $15 Trial Credit (ausreichend für ~100 Minuten Anrufe)

### Twilio Credentials holen

Nach der Registrierung findest du auf dem Twilio Dashboard:

1. **Account SID**: Unter "Account Info"
2. **Auth Token**: Unter "Account Info" (klicke auf "Show" um ihn anzuzeigen)
3. **Phone Number**: Gehe zu "Phone Numbers" → "Manage" → "Buy a number"
   - Wähle ein deutsches Nummer (+49) für lokale Anrufe
   - Kosten: ~€1/Monat
   - Stelle sicher, dass "Voice" aktiviert ist

### Anthropic oder OpenAI API Key

**Option A - Anthropic Claude (empfohlen):**
1. Gehe zu [console.anthropic.com](https://console.anthropic.com)
2. Erstelle einen Account
3. Gehe zu "API Keys" und erstelle einen neuen Key
4. Kosten: ~$0.003 pro 1K Tokens (sehr günstig)

**Option B - OpenAI:**
1. Gehe zu [platform.openai.com](https://platform.openai.com)
2. Erstelle einen Account und lade Guthaben auf
3. Erstelle einen API Key unter "API Keys"

## 2. Installation

### Projekt Setup

```bash
# 1. In das Projekt-Verzeichnis wechseln
cd /home/user/hrshojaei

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. .env Datei erstellen
cp .env.example .env
```

### .env konfigurieren

Öffne die `.env` Datei und trage deine Credentials ein:

```env
# Twilio (PFLICHT)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+491234567890

# AI Provider (wähle einen)
AI_PROVIDER=anthropic

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx

# ODER OpenAI
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx

# Public URL (zunächst ngrok, später deine Domain)
PUBLIC_URL=https://your-ngrok-url.ngrok.io
```

**Wichtig**: Die `PUBLIC_URL` konfigurieren wir im nächsten Schritt!

## 3. Ngrok einrichten (für lokale Entwicklung)

Twilio braucht eine öffentliche URL, um deine Webhooks zu erreichen. Ngrok erstellt einen Tunnel von deinem lokalen Server ins Internet.

### Ngrok installieren

**macOS:**
```bash
brew install ngrok
```

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

**Windows:**
Download von [ngrok.com/download](https://ngrok.com/download)

### Ngrok Account erstellen

1. Gehe zu [ngrok.com](https://ngrok.com)
2. Registriere einen kostenlosen Account
3. Kopiere deinen Authtoken vom Dashboard
4. Authentifiziere ngrok:

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

## 4. Datenbank initialisieren

```bash
python -m src.candidate_manager init
```

Du solltest sehen: `✓ Database initialized`

## 5. Test-Kandidat hinzufügen

```bash
python -m src.main add
```

Trage ein (nutze deine eigene Nummer für den ersten Test!):
```
Name: Test Kandidat
Phone: +4915112345678  # DEINE NUMMER!
Email: test@example.com
Current Company: Test Firma
Current Position: Hörakustiker
Years of Experience: 5
Notes: Erster Test
```

## 6. Server und Ngrok starten

**Terminal 1 - Server starten:**
```bash
python -m src.main server
```

Du solltest sehen:
```
INFO: Starting server on 0.0.0.0:8000
INFO: Application startup complete
```

**Terminal 2 - Ngrok Tunnel starten:**
```bash
ngrok http 8000
```

Du erhältst eine URL wie:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

### Public URL in .env eintragen

1. Kopiere die ngrok URL (z.B. `https://abc123.ngrok.io`)
2. Öffne `.env` und setze:
   ```env
   PUBLIC_URL=https://abc123.ngrok.io
   ```
3. **Wichtig**: Starte den Server neu (Strg+C und dann wieder `python -m src.main server`)

## 7. Ersten Test-Anruf machen

**In einem neuen Terminal (Terminal 3):**

```bash
python -m src.main call +4915112345678  # Deine eigene Nummer
```

Du solltest sehen:
```
✓ Call initiated successfully!
Call SID: CAxxxxxxxxxxxxxxxxxxxx
Candidate ID: 1
```

**Innerhalb weniger Sekunden klingelt dein Telefon!** 📞

### Was passiert:

1. Dein Telefon klingelt
2. Du nimmst ab
3. Der AI-Agent begrüßt dich: "Guten Tag, mein Name ist Sarah von..."
4. Du kannst mit dem Agent sprechen
5. Der Agent antwortet intelligent auf deine Fragen

## 8. Test-Gespräch führen

**Beispiel-Dialog:**

**Agent**: "Guten Tag, mein Name ist Sarah von Hörakustik Excellence GmbH. Ich rufe Sie an, weil wir aktuell nach erfahrenen Hörakustikern suchen. Haben Sie gerade 2-3 Minuten Zeit?"

**Du**: "Ja, habe ich."

**Agent**: "Perfekt! Wie lange sind Sie schon in der Hörakustik-Branche tätig?"

**Du**: "Etwa 5 Jahre."

**Agent**: "Das ist eine gute Erfahrung! Sind Sie grundsätzlich offen für neue berufliche Möglichkeiten?"

**Du**: "Ja, durchaus."

**Agent**: "Sehr gut! Lassen Sie mich Ihnen kurz erzählen, was wir bieten..."

### Gespräch beenden

Sage einfach "Tschüss" oder "Auf Wiederhören" und der Agent beendet höflich das Gespräch.

## 9. Ergebnisse prüfen

### Statistiken anzeigen

```bash
python -m src.main stats
```

Ausgabe:
```
📊 Calling Agent Statistics
==================================================

Total Candidates: 1
Total Calls: 1
Average Call Duration: 120 seconds

Candidates by Status:
  contacted: 1
```

### Datenbank direkt prüfen

```bash
sqlite3 data/candidates.db
```

```sql
-- Alle Kandidaten anzeigen
SELECT * FROM candidates;

-- Alle Anrufe anzeigen
SELECT * FROM call_logs;

-- Gesprächsverlauf anzeigen
SELECT * FROM conversation_history WHERE call_log_id = 1;

-- Beenden
.quit
```

## 10. Mehrere Kandidaten hinzufügen und Kampagne starten

### Kandidaten-CSV importieren (optional)

Erstelle `candidates.csv`:
```csv
name,phone,email,current_company,experience_years
Max Mustermann,+4915112345671,max@example.com,Hörakustik A,5
Anna Schmidt,+4915112345672,anna@example.com,Hörakustik B,7
Peter Weber,+4915112345673,peter@example.com,Hörakustik C,3
```

Importiere mit Python:
```python
import csv
from src.candidate_manager import CandidateManager

manager = CandidateManager()

with open('candidates.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        manager.add_candidate(
            name=row['name'],
            phone=row['phone'],
            email=row.get('email'),
            current_company=row.get('current_company'),
            experience_years=int(row['experience_years']) if row.get('experience_years') else None
        )
        print(f"Added: {row['name']}")
```

### Kampagne starten

```bash
python -m src.main campaign 5
```

Der Agent wird nacheinander bis zu 5 Kandidaten anrufen.

## 11. Monitoring & Logs

### Live-Logs ansehen

Die Logs werden in Echtzeit ausgegeben und auch gespeichert:

```bash
# Live-Logs (im Server-Terminal sichtbar)
# Oder:
tail -f logs/calling_agent_*.log
```

### Twilio Console

Besuche [console.twilio.com](https://console.twilio.com) um:
- Anrufe zu überwachen
- Kosten zu sehen
- Probleme zu debuggen
- Call Recordings anzuhören (falls aktiviert)

## 12. Gesprächs-Script anpassen

Bearbeite `src/prompts.py` um das Verhalten des Agents anzupassen:

```python
# Firmenname ändern
COMPANY_NAME = "Deine Firma GmbH"

# Gesprächsstil anpassen
SYSTEM_PROMPT = """
Du bist ein professioneller Recruiter...
[Passe hier den Stil an]
"""

# Begrüßung ändern
def get_greeting_template(candidate_name: str) -> str:
    return f"""
    Guten Tag {candidate_name},
    hier spricht [DEIN NAME] von [DEINE FIRMA]...
    """
```

Starte den Server neu, damit die Änderungen wirksam werden.

## 13. Produktiv-Deployment (Optional)

Für den Produktiv-Einsatz:

### Server auf VPS hosten

1. **VPS mieten** (z.B. bei Hetzner, DigitalOcean, AWS)
2. **Domain registrieren** (z.B. calling-agent.deine-firma.de)
3. **SSL-Zertifikat** einrichten (Let's Encrypt)
4. **Systemd Service** erstellen für automatischen Start

### Beispiel Systemd Service

`/etc/systemd/system/calling-agent.service`:
```ini
[Unit]
Description=AI Calling Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/calling-agent
Environment="PATH=/opt/calling-agent/venv/bin"
ExecStart=/opt/calling-agent/venv/bin/python -m src.main server
Restart=always

[Install]
WantedBy=multi-user.target
```

Aktivieren:
```bash
sudo systemctl enable calling-agent
sudo systemctl start calling-agent
```

### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name calling-agent.deine-firma.de;

    ssl_certificate /etc/letsencrypt/live/calling-agent.deine-firma.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/calling-agent.deine-firma.de/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### "Failed to make call: Authentication Error"
→ Überprüfe TWILIO_ACCOUNT_SID und TWILIO_AUTH_TOKEN in .env

### "Webhook not found" / "Connection refused"
→ Stelle sicher, dass:
  - Server läuft (`python -m src.main server`)
  - Ngrok läuft (`ngrok http 8000`)
  - PUBLIC_URL in .env korrekt gesetzt ist
  - Server nach Änderung von .env neu gestartet wurde

### "No answer" / Anruf kommt nicht an
→ Überprüfe:
  - Telefonnummer ist korrekt formatiert (+49...)
  - Nummer ist nicht blockiert
  - Du hast Twilio Trial Nummer verifiziert (bei Trial Account)

### AI antwortet nicht richtig / Fehler
→ Überprüfe:
  - ANTHROPIC_API_KEY oder OPENAI_API_KEY in .env
  - API Key hat genügend Credits
  - Check logs für detaillierte Fehlermeldungen

### Gesprächsqualität schlecht
→ Optimiere:
  - Verwende bessere TTS (ElevenLabs statt Twilio)
  - Passe Prompts in `src/prompts.py` an
  - Reduziere max_tokens für kürzere Antworten

## Nächste Schritte

1. ✅ **Test-Anruf erfolgreich** - Gratulation!
2. 📝 Passe Gesprächs-Script an deine Bedürfnisse an
3. 📊 Importiere echte Kandidaten-Daten
4. 🚀 Starte erste kleine Kampagne (5-10 Anrufe)
5. 📈 Analysiere Ergebnisse und optimiere
6. 🏭 Produktiv-Deployment auf VPS

## Support

Bei Fragen oder Problemen:
- Prüfe Logs: `logs/calling_agent_*.log`
- Twilio Console: [console.twilio.com](https://console.twilio.com)
- Anthropic Docs: [docs.anthropic.com](https://docs.anthropic.com)

Viel Erfolg beim Recruiting! 🎉
