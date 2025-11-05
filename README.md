# AI Recruiting Agent für Hörakustik-Branche

Ein intelligenter Telefon-Agent, der automatisch potenzielle Kandidaten in der Hörakustik-Branche kontaktiert und für neue Arbeitsmöglichkeiten gewinnt.

## Features

- 🤖 **AI-gesteuerte Gespräche**: Nutzt Claude/GPT für natürliche, überzeugende Dialoge
- 📞 **Automatische Anrufe**: Integriert mit Twilio für zuverlässige Telefonie
- 🎯 **Recruiting-Fokus**: Speziell für Hörakustik-Branche optimiert
- 📊 **Kandidaten-Tracking**: Verwaltet Kandidaten und Gesprächsverläufe
- 🗣️ **Echtzeit-Konversation**: Speech-to-Text und Text-to-Speech Integration
- 📝 **Gesprächsprotokoll**: Automatische Dokumentation aller Gespräche

## Technologie-Stack

- **Backend**: Python 3.10+ mit FastAPI
- **Telefonie**: Twilio Voice API
- **AI**: Anthropic Claude / OpenAI GPT
- **Speech-to-Text**: Deepgram / AssemblyAI
- **Text-to-Speech**: ElevenLabs / Twilio
- **Datenbank**: SQLite (upgradebar zu PostgreSQL)

## Installation

### Voraussetzungen

- Python 3.10 oder höher
- Twilio Account (https://www.twilio.com/try-twilio)
- Anthropic API Key oder OpenAI API Key
- Deepgram API Key (optional, für bessere STT)
- ElevenLabs API Key (optional, für bessere Stimmen)

### Setup

1. Repository klonen und Dependencies installieren:
```bash
pip install -r requirements.txt
```

2. Umgebungsvariablen konfigurieren:
```bash
cp .env.example .env
# Dann .env mit deinen API-Keys bearbeiten
```

3. Datenbank initialisieren:
```bash
python -m src.candidate_manager init
```

4. Server starten:
```bash
python -m src.main
```

## Konfiguration

Bearbeite die `.env` Datei mit deinen Credentials:

```env
# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+49xxx

# AI Provider (wähle einen)
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
AI_PROVIDER=anthropic  # oder "openai"

# Speech Services (optional)
DEEPGRAM_API_KEY=your_deepgram_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
PUBLIC_URL=https://your-domain.com  # Für Twilio Webhooks
```

## Verwendung

### Kandidaten hinzufügen

```python
from src.candidate_manager import CandidateManager

manager = CandidateManager()
manager.add_candidate(
    name="Max Mustermann",
    phone="+4915112345678",
    current_company="Hörakustik XY",
    experience_years=5,
    notes="Filialleiter, interessiert an Weiterentwicklung"
)
```

### Anruf-Kampagne starten

```bash
python -m src.main start-campaign --max-calls 10
```

### Einzelnen Kandidaten anrufen

```bash
python -m src.main call-candidate --phone "+4915112345678"
```

## Gesprächsablauf

Der Agent folgt diesem Ablauf:

1. **Begrüßung**: Stellt sich vor und erklärt den Grund des Anrufs
2. **Qualifikation**: Prüft Interesse und aktuelle Situation
3. **Präsentation**: Stellt die Arbeitsmöglichkeit vor
4. **Einwandbehandlung**: Geht auf Bedenken ein
5. **Call-to-Action**: Vereinbart nächste Schritte (Termin, Bewerbung, etc.)

## Kosten-Übersicht

### Twilio (Telefonie)
- Eingehend/Ausgehend DE: ~€0.012 pro Minute
- Telefonnummer: ~€1.00 pro Monat

### AI Services
- Anthropic Claude: ~$0.003 pro 1K Tokens (input), $0.015 (output)
- OpenAI GPT-4: ~$0.03 pro 1K Tokens

### Speech Services
- Deepgram STT: $0.0043 pro Minute
- ElevenLabs TTS: ~$0.18 pro 1K Zeichen (oder kostenloser Tier)

**Geschätzte Kosten pro 10-minütigem Gespräch: ca. €0.30-0.50**

## Entwicklung

### Projekt-Struktur

```
calling-agent/
├── src/
│   ├── main.py                 # FastAPI Server & CLI
│   ├── twilio_client.py        # Twilio Integration
│   ├── ai_engine.py            # AI Konversations-Engine
│   ├── candidate_manager.py    # Kandidaten-Verwaltung
│   ├── call_handler.py         # Anruf-Logik & Flow
│   ├── prompts.py              # Gesprächs-Templates
│   └── config.py               # Konfiguration
├── data/
│   └── candidates.db           # SQLite Datenbank
├── logs/                       # Gesprächsprotokolle
├── requirements.txt
├── .env.example
└── README.md
```

### Anpassen der Gesprächs-Scripts

Bearbeite `src/prompts.py` um den Gesprächsablauf anzupassen:

```python
SYSTEM_PROMPT = """
Du bist ein professioneller Recruiter für [DEIN UNTERNEHMEN]...
"""
```

## Rechtliche Hinweise

⚠️ **WICHTIG**: Beachte folgende rechtliche Anforderungen:

1. **DSGVO-Konformität**: Hole Einwilligung für Aufzeichnungen ein
2. **Telefonmarketing-Gesetze**: Prüfe UWG-Vorgaben für B2B Cold Calling
3. **Aufzeichnungen**: Informiere über mögliche Gesprächsaufzeichnungen
4. **Datenspeicherung**: Implementiere Löschfristen und Auskunftsrechte

## Support & Beitragen

Bei Fragen oder Problemen, erstelle bitte ein Issue im Repository.

## Lizenz

[Deine gewählte Lizenz]
