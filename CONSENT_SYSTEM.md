# Datenschutz-Einwilligungssystem

Ein DSGVO-konformes System zur Einholung von Datenschutz-Einwilligungen per E-Mail mit digitaler Signatur.

## Übersicht

Dieses System ermöglicht es dir, Kandidaten per E-Mail um ihre Einwilligung zur Datenverarbeitung zu bitten. Der Kandidat erhält eine E-Mail mit einem eindeutigen Link, über den er die Datenschutzerklärung lesen und digital zustimmen kann.

## Features

✅ **E-Mail-Versand** - Automatischer Versand von Einwilligungsanfragen
✅ **Web-Interface** - Professionelle Einwilligungsseite mit vollständiger Datenschutzerklärung
✅ **Digitale Signatur** - Token-basierte Authentifizierung mit IP/User-Agent-Tracking
✅ **DSGVO-konform** - Speicherung aller relevanten Informationen für Nachweiszwecke
✅ **Status-Tracking** - Überprüfung ob Einwilligung erteilt wurde
✅ **CLI & API** - Einfache Nutzung via Kommandozeile oder REST API

## Ablauf

```
1. Du sendest Einwilligungs-E-Mail
        ↓
2. Kandidat erhält E-Mail mit Link
        ↓
3. Kandidat klickt auf Link
        ↓
4. Webseite zeigt Datenschutzerklärung
        ↓
5. Kandidat stimmt digital zu
        ↓
6. Zustimmung wird mit IP & Timestamp gespeichert
```

## Installation & Konfiguration

### 1. SMTP-Konfiguration in `.env`

Füge folgende Zeilen zu deiner `.env` Datei hinzu:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=deine-email@gmail.com
SMTP_PASSWORD=dein-app-passwort
```

**Wichtig für Gmail:**
- Du benötigst ein **App-Passwort** (nicht dein normales Gmail-Passwort)
- Aktiviere [2-Faktor-Authentifizierung](https://myaccount.google.com/security)
- Erstelle ein [App-Passwort](https://myaccount.google.com/apppasswords)

**Andere E-Mail-Anbieter:**
- **Office 365/Outlook**: `smtp.office365.com`, Port 587
- **SendGrid**: `smtp.sendgrid.net`, Port 587
- **Eigener SMTP**: Passe Host und Port entsprechend an

### 2. Server starten

```bash
python -m src.main server
```

Der Server läuft auf `http://localhost:8000` (oder deinem konfigurierten `PUBLIC_URL`)

## Verwendung

### CLI-Commands

#### Einwilligung versenden

```bash
python -m src.main send-consent
```

Interaktiver Dialog:
```
📧 Send Consent Request
==================================================
Email: max@example.com
Purpose (default: 'Kontaktaufnahme und Datenspeicherung'):

✓ Consent request created with token: abc123...
✓ Email sent successfully!

Consent link: https://your-domain.com/consent/abc123...
```

#### Einwilligungsstatus prüfen

```bash
python -m src.main check-consent
```

Interaktiver Dialog:
```
🔍 Check Consent Status
==================================================
Email: max@example.com

Email: max@example.com
Has valid consent: ✓ Yes
Total requests: 1

Consent Requests:
--------------------------------------------------------------------------------

ID: 1
Purpose: Kontaktaufnahme und Datenspeicherung
Created: 2025-01-15 10:30:00
Status: ✓ Given
Confirmed: 2025-01-15 10:35:22
IP: 192.168.1.100
```

### REST API

#### Einwilligung senden

```bash
POST /consent/api/send
Content-Type: application/json

{
  "email": "max@example.com",
  "purpose": "Kontaktaufnahme und Datenspeicherung"
}
```

Response:
```json
{
  "success": true,
  "email": "max@example.com",
  "token": "abc123...",
  "message": "Einwilligungsanfrage wurde gesendet"
}
```

#### Status prüfen

```bash
GET /consent/api/status/max@example.com
```

Response:
```json
{
  "email": "max@example.com",
  "has_valid_consent": true,
  "total_requests": 1,
  "requests": [
    {
      "id": 1,
      "purpose": "Kontaktaufnahme und Datenspeicherung",
      "created_at": "2025-01-15T10:30:00",
      "consent_given": true,
      "consent_timestamp": "2025-01-15T10:35:22"
    }
  ]
}
```

### Python-Code

```python
from src.consent_manager import ConsentManager
from src.email_service import EmailService

# Einwilligung erstellen und senden
consent_manager = ConsentManager()
email_service = EmailService()

# Erstelle Request
request = consent_manager.create_consent_request(
    email="max@example.com",
    purpose="Kontaktaufnahme und Datenspeicherung"
)

# Sende E-Mail
email_service.send_consent_request(
    to_email="max@example.com",
    token=request.token,
    purpose="Kontaktaufnahme und Datenspeicherung"
)

# Prüfe Status
has_consent = consent_manager.has_valid_consent("max@example.com")
print(f"Einwilligung vorhanden: {has_consent}")
```

## Datenbank

Die Einwilligungen werden in `data/consent.db` (SQLite) gespeichert:

### Tabelle: `consent_requests`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | INTEGER | Eindeutige ID |
| email | TEXT | E-Mail-Adresse |
| token | TEXT | Eindeutiger Token (UUID) |
| purpose | TEXT | Zweck der Einwilligung |
| created_at | TIMESTAMP | Erstellungszeitpunkt |
| consent_given | BOOLEAN | Ob Einwilligung erteilt |
| consent_timestamp | TIMESTAMP | Zeitpunkt der Zustimmung |
| ip_address | TEXT | IP-Adresse (für Nachweis) |
| user_agent | TEXT | Browser User-Agent |

## DSGVO-Konformität

Das System erfüllt folgende DSGVO-Anforderungen:

✅ **Freiwilligkeit**: Klare Opt-in-Mechanik ohne Vorauswahl
✅ **Informiertheit**: Vollständige Datenschutzerklärung vor Zustimmung
✅ **Spezifität**: Zweck der Datenverarbeitung wird klar benannt
✅ **Nachweisbarkeit**: Speicherung von Zeitpunkt, IP-Adresse und User-Agent
✅ **Widerrufbarkeit**: Hinweis auf Widerrufsrecht in der Erklärung
✅ **Transparenz**: Alle Rechte (Auskunft, Löschung, etc.) werden aufgeführt

### Gespeicherte Nachweise

Für jede Einwilligung wird gespeichert:
- **Wann** die Einwilligung erteilt wurde (Timestamp)
- **Von wo** die Einwilligung kam (IP-Adresse)
- **Womit** die Einwilligung erteilt wurde (Browser User-Agent)
- **Wofür** die Einwilligung gilt (Purpose)

Diese Informationen dienen dem **Nachweis der Einwilligung** gemäß Art. 7 Abs. 1 DSGVO.

## Web-Interface

Das Web-Interface ist vollständig responsive und modern gestaltet:

- **Desktop & Mobile** optimiert
- **Professionelles Design** mit Gradient-Header
- **Übersichtliche Darstellung** der Datenschutzrechte
- **Checkbox-Bestätigung** vor Zustimmung erforderlich
- **Erfolgs-/Fehlerseiten** mit klarem Feedback

### Screenshots der Einwilligungsseite:

Die Seite enthält:
1. Firmen-Header mit Namen
2. E-Mail-Adresse des Empfängers
3. Vollständige Datenschutzerklärung mit:
   - Zweck der Datenverarbeitung
   - Welche Daten verarbeitet werden
   - Rechtsgrundlage (Art. 6 Abs. 1 lit. a DSGVO)
   - Alle Betroffenenrechte (Widerruf, Auskunft, Löschung, etc.)
   - Kontaktdaten
   - Speicherdauer
4. Pflicht-Checkbox zur Bestätigung
5. Buttons "Ablehnen" und "Einwilligung erteilen"

## Anpassung

### E-Mail-Template anpassen

Bearbeite `src/email_service.py`:
- `_generate_consent_email_html()` für HTML-Version
- `_generate_consent_email_text()` für Text-Version

### Web-Interface anpassen

Bearbeite `src/consent_routes.py`:
- `_generate_consent_form()` für Einwilligungsformular
- `_generate_success_page()` für Erfolgsseite
- `_generate_error_page()` für Fehlerseite

### Firmeninformationen

Werden automatisch aus `.env` geladen:
- `COMPANY_NAME`
- `CONTACT_EMAIL`
- `CONTACT_PHONE`

## Troubleshooting

### E-Mail wird nicht gesendet

**Problem**: `✗ Fehler beim E-Mail-Versand`

**Lösungen**:
1. Prüfe SMTP-Credentials in `.env`
2. Bei Gmail: Verwende App-Passwort, nicht normales Passwort
3. Prüfe Firewall/Ports: Port 587 muss offen sein
4. Teste mit anderem SMTP-Server

### Link funktioniert nicht

**Problem**: Consent-Link führt zu 404

**Lösungen**:
1. Prüfe `PUBLIC_URL` in `.env`
2. Server muss laufen: `python -m src.main server`
3. In Development: Nutze ngrok für öffentliche URL

### Datenbank-Fehler

**Problem**: `no such table: consent_requests`

**Lösung**: Datenbank wird automatisch erstellt beim ersten Start. Falls nicht:
```python
from src.consent_manager import ConsentManager
cm = ConsentManager()  # Erstellt Datenbank automatisch
```

## Best Practices

1. **Vor Kontaktaufnahme prüfen**: Prüfe immer, ob Einwilligung vorliegt, bevor du Kandidaten kontaktierst
   ```python
   if not consent_manager.has_valid_consent(email):
       print("Keine Einwilligung vorhanden!")
   ```

2. **Zweck spezifizieren**: Gib immer einen klaren Zweck an
   ```python
   purpose = "Kontaktaufnahme bezüglich Stellenangebote im Hörakustik-Bereich"
   ```

3. **Regelmäßige Backups**: Sichere `data/consent.db` regelmäßig (DSGVO-Nachweispflicht!)

4. **Löschfristen beachten**: Implementiere Löschung nach bestimmter Zeit oder auf Anfrage

5. **Widerruf ermöglichen**: Biete einfachen Weg zur Zurücknahme der Einwilligung

## Integration mit Recruiting-System

### Vor Telefonanruf Einwilligung prüfen

```python
from src.consent_manager import ConsentManager
from src.candidate_manager import CandidateManager

consent_manager = ConsentManager()
candidate_manager = CandidateManager()

# Hole Kandidat
candidate = candidate_manager.get_candidate(candidate_id)

# Prüfe Einwilligung
if not consent_manager.has_valid_consent(candidate.email):
    print(f"⚠️  Keine Einwilligung für {candidate.email}")
    # Sende Einwilligung zuerst
    # ...dann erst anrufen
else:
    # Einwilligung vorhanden, Anruf kann durchgeführt werden
    make_call(candidate)
```

### Automatischer Workflow

```python
def contact_candidate(candidate_id):
    """Kontaktiere Kandidaten nur mit Einwilligung"""
    candidate = candidate_manager.get_candidate(candidate_id)

    if not candidate.email:
        print("Keine E-Mail vorhanden!")
        return

    # Prüfe Einwilligung
    if not consent_manager.has_valid_consent(candidate.email):
        # Sende Einwilligung
        request = consent_manager.create_consent_request(
            email=candidate.email,
            purpose="Kontaktaufnahme bezüglich beruflicher Möglichkeiten"
        )
        email_service.send_consent_request(
            to_email=candidate.email,
            token=request.token,
            purpose="Kontaktaufnahme bezüglich beruflicher Möglichkeiten"
        )
        print(f"📧 Einwilligung angefordert von {candidate.email}")
        print("⏳ Warte auf Bestätigung...")
        return

    # Einwilligung vorhanden -> Anrufen
    print(f"✓ Einwilligung vorhanden, rufe {candidate.name} an...")
    make_call(candidate)
```

## Support

Bei Fragen oder Problemen:
- Prüfe Logs in `./logs/calling_agent_*.log`
- Teste mit `python -m src.main send-consent`
- Prüfe SMTP-Verbindung: `telnet smtp.gmail.com 587`

## Lizenz

Siehe Haupt-README
