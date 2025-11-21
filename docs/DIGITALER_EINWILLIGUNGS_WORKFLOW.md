# Digitaler Einwilligungs-Workflow

**Version:** 2.0 (Vollständig digital)
**Stand:** November 2025

---

## 📋 Überblick

Dieser Workflow ermöglicht die **vollständig digitale Einholung** der Datenschutz-Einwilligung von Kandidaten **VOR dem ersten Telefonat**.

### Ablauf im Überblick

```
1. Kandidat findenonline gefunden (LinkedIn, XING, etc.)
         ↓
2. Email mit Consent-Link senden
         ↓
3. Kandidat öffnet Link → Web-Formular
         ↓
4. Kandidat liest Datenschutzerklärung
         ↓
5. Kandidat unterschreibt digital (Name eingeben)
         ↓
6. Einwilligung wird gespeichert
         ↓
7. ERST JETZT: Telefonischer Kontakt erlaubt
```

---

## 🔧 Technische Implementierung

### Schritt 1: Kandidat zur Datenbank hinzufügen

```python
from src.candidate_manager import CandidateManager

manager = CandidateManager()

candidate_id = manager.add_candidate(
    name="Max Mustermann",
    phone="+4915112345678",
    email="max.mustermann@example.com",
    current_company="Hörakustik GmbH",
    current_position="Hörakustiker",
    experience_years=5,
    notes="Gefunden auf LinkedIn - interessantes Profil"
)

print(f"Kandidat hinzugefügt: ID {candidate_id}")
```

### Schritt 2: Consent-Link generieren

**Via API:**

```bash
curl -X POST "http://localhost:8000/gdpr/consent/send-link" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 123,
    "email": "max.mustermann@example.com",
    "validity_days": 7
  }'
```

**Antwort:**

```json
{
  "success": true,
  "message": "Consent link generated successfully",
  "candidate_id": 123,
  "token": "abc123...xyz789",
  "consent_url": "https://ihrefirma.de/gdpr/consent/form?token=abc123...xyz789",
  "expires_in_days": 7,
  "email": "max.mustermann@example.com"
}
```

**Via Python:**

```python
import requests

response = requests.post(
    "http://localhost:8000/gdpr/consent/send-link",
    json={
        "candidate_id": 123,
        "email": "max.mustermann@example.com",
        "validity_days": 7
    }
)

data = response.json()
consent_url = data["consent_url"]
print(f"Consent-Link: {consent_url}")
```

### Schritt 3: Email an Kandidaten senden

**Template verwenden:**

```python
from jinja2 import Template

# Email-Template laden
with open('docs/templates/email_initial_consent_request.md') as f:
    template = Template(f.read())

# Template ausfüllen
email_body = template.render(
    CANDIDATE_NAME="Max Mustermann",
    COMPANY_NAME="Ihre Firma GmbH",
    CONSENT_LINK=consent_url,
    JOB_BENEFITS="Attraktives Gehalt, Firmenwagen, Weiterbildung",
    PRIVACY_POLICY_URL="https://ihrefirma.de/datenschutz",
    CONTACT_EMAIL="datenschutz@ihrefirma.de",
    CONTACT_PHONE="+49 123 456789",
    RECRUITER_NAME="Sarah Schmidt",
    COMPANY_WEBSITE="https://ihrefirma.de",
    COMPANY_ADDRESS="Musterstraße 123",
    COMPANY_CITY="12345 Musterstadt",
    CURRENT_DATE="21.11.2025"
)

# Email versenden (SMTP-Beispiel)
import smtplib
from email.mime.text import MIMEText

msg = MIMEText(email_body, 'plain', 'utf-8')
msg['Subject'] = 'Einwilligung erforderlich: Karrieremöglichkeiten | Ihre Firma GmbH'
msg['From'] = 'recruiting@ihrefirma.de'
msg['To'] = 'max.mustermann@example.com'

with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()
    server.login('your-email@gmail.com', 'your-password')
    server.send_message(msg)

print("✅ Consent-Email versendet!")
```

### Schritt 4: Kandidat öffnet Link und sieht Formular

Der Kandidat klickt auf den Link in der Email:
```
https://ihrefirma.de/gdpr/consent/form?token=abc123...xyz789
```

Das System:
1. ✅ Validiert den Token (gültig/abgelaufen/bereits verwendet)
2. ✅ Lädt Kandidaten-Daten aus Datenbank
3. ✅ Zeigt professionelles Web-Formular mit:
   - Pre-filled Kandidaten-Informationen
   - Vollständige Datenschutz-Informationen
   - Checkboxen für verschiedene Einwilligungen
   - Digitale Signatur-Feld (Name eingeben)

### Schritt 5: Kandidat unterschreibt digital

**Was passiert beim Submit:**

1. JavaScript validiert Eingaben (Frontend)
2. POST-Request an `/gdpr/consent/submit-signature`
3. Backend validiert Token erneut
4. Signatur wird geprüft (min. 3 Zeichen)
5. Einwilligung wird in Datenbank gespeichert:
   ```sql
   consent_given = 1
   consent_timestamp = '2025-11-21 10:30:00'
   consent_method = 'web'
   consent_version = 'v1.0'
   recording_consent = 1 (falls aktiviert)
   marketing_consent = 0 (falls nicht aktiviert)
   data_retention_until = '2027-11-21' (2 Jahre)
   ```
6. Token wird als "verwendet" markiert
7. IP-Adresse & User-Agent werden protokolliert (Audit-Trail)
8. Erfolgs-Meldung wird angezeigt

**Audit-Trail (für DSGVO-Nachweis):**

```
Kandidat: Max Mustermann (ID: 123)
Signatur: "Max Mustermann"
Zeitstempel: 2025-11-21 10:30:45
IP-Adresse: 192.168.1.100
Browser: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
Methode: web
Token: abc123...xyz789 (gültig bis 2025-11-28)
```

### Schritt 6: Einwilligung prüfen vor Anruf

**Vor jedem Anruf MUSS geprüft werden:**

```python
from src.candidate_manager import CandidateManager

manager = CandidateManager()

# Kandidat laden
candidate = manager.get_candidate(candidate_id=123)

# Einwilligung prüfen
if manager.has_valid_consent(candidate.id):
    print("✅ Einwilligung vorhanden - Anruf erlaubt!")
    # Anruf durchführen
else:
    print("❌ KEINE Einwilligung - Anruf NICHT erlaubt!")
    print("→ Zuerst Consent-Email senden!")
```

**Via API:**

```bash
curl -X GET "http://localhost:8000/gdpr/consent/check?candidate_id=123"
```

**Antwort:**

```json
{
  "candidate_id": 123,
  "has_valid_consent": true,
  "consent_given": true,
  "consent_timestamp": "2025-11-21T10:30:45",
  "consent_method": "web",
  "consent_version": "v1.0",
  "opted_out": false,
  "data_retention_until": "2027-11-21T10:30:45",
  "recording_consent": true,
  "marketing_consent": false
}
```

### Schritt 7: Telefonat führen (NUR wenn Einwilligung vorhanden)

```python
from src.main import make_test_call

# NUR wenn has_valid_consent() == True
make_test_call(phone="+4915112345678")
```

**Wichtig:** Der AI-Agent erwähnt zu Beginn des Gesprächs:
> "Vielen Dank, dass Sie uns Ihre Einwilligung erteilt haben!"

---

## 📧 Email-Automatisierung

### Vollständiges Beispiel-Script

**`scripts/send_consent_emails.py`:**

```python
#!/usr/bin/env python3
"""
Send consent request emails to candidates
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from src.candidate_manager import CandidateManager
from src.config import settings

def send_consent_email(candidate_id: int, candidate_email: str):
    """Send consent request email to a candidate"""

    # 1. Generate consent link
    response = requests.post(
        f"{settings.public_url}/gdpr/consent/send-link",
        json={
            "candidate_id": candidate_id,
            "email": candidate_email,
            "validity_days": 7
        }
    )

    if not response.ok:
        print(f"❌ Error generating link for candidate {candidate_id}")
        return False

    data = response.json()
    consent_url = data["consent_url"]

    # 2. Load email template
    with open('docs/templates/email_initial_consent_request.md') as f:
        template = Template(f.read())

    # 3. Get candidate data
    manager = CandidateManager()
    candidate = manager.get_candidate(candidate_id=candidate_id)

    # 4. Render template
    email_body = template.render(
        CANDIDATE_NAME=candidate.name,
        COMPANY_NAME=settings.company_name,
        CONSENT_LINK=consent_url,
        JOB_BENEFITS=settings.job_benefits,
        PRIVACY_POLICY_URL=settings.privacy_policy_url,
        CONTACT_EMAIL=settings.contact_email,
        CONTACT_PHONE=settings.contact_phone,
        RECRUITER_NAME="Sarah Schmidt",  # TODO: Make configurable
        COMPANY_WEBSITE="https://ihrefirma.de",  # TODO: Add to settings
        COMPANY_ADDRESS="Musterstraße 123",  # TODO: Add to settings
        COMPANY_CITY="12345 Musterstadt",  # TODO: Add to settings
        CURRENT_DATE="21.11.2025"
    )

    # 5. Send email via SMTP
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Einwilligung erforderlich: Karrieremöglichkeiten | {settings.company_name}'
    msg['From'] = settings.contact_email
    msg['To'] = candidate_email

    msg.attach(MIMEText(email_body, 'plain', 'utf-8'))

    try:
        # TODO: Configure SMTP settings
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('your-email@gmail.com', 'your-password')
            server.send_message(msg)

        print(f"✅ Consent-Email sent to {candidate.name} ({candidate_email})")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def send_bulk_consent_emails(max_candidates: int = 10):
    """Send consent emails to all candidates without consent"""

    manager = CandidateManager()

    # Get all candidates without consent
    conn = manager._get_connection()
    rows = conn.execute("""
        SELECT id, name, email
        FROM candidates
        WHERE (consent_given = 0 OR consent_given IS NULL)
        AND email IS NOT NULL
        AND opted_out = 0
        LIMIT ?
    """, (max_candidates,)).fetchall()

    candidates = [dict(row) for row in rows]

    print(f"\n📧 Sending consent emails to {len(candidates)} candidates...\n")

    success_count = 0
    for candidate in candidates:
        if send_consent_email(
            candidate_id=candidate['id'],
            candidate_email=candidate['email']
        ):
            success_count += 1

        # Delay between emails to avoid spam filters
        import time
        time.sleep(2)

    print(f"\n✅ Successfully sent {success_count}/{len(candidates)} emails")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        max_count = int(sys.argv[1])
    else:
        max_count = 10

    send_bulk_consent_emails(max_candidates=max_count)
```

**Verwendung:**

```bash
# Consent-Emails an max. 10 Kandidaten senden
python scripts/send_consent_emails.py 10

# Consent-Emails an max. 50 Kandidaten senden
python scripts/send_consent_emails.py 50
```

---

## 🔐 Sicherheits-Features

### Token-Sicherheit

✅ **64-Zeichen zufälliger Token** (URL-safe Base64)
✅ **Einmalige Verwendung** - Token ungültig nach Submit
✅ **Ablaufdatum** - Standard 7 Tage
✅ **Validierung** bei jedem Request
✅ **Automatische Cleanup** alter Tokens

### Audit-Trail

Für jeden Consent wird protokolliert:
- ✅ Kandidaten-ID & Name
- ✅ Digitale Signatur (eingegebener Name)
- ✅ Zeitstempel (ISO 8601)
- ✅ IP-Adresse
- ✅ User-Agent (Browser)
- ✅ Consent-Methode (`web`)
- ✅ Privacy Policy Version (`v1.0`)

### DSGVO-Konformität

✅ **Klare Informationen** - Vollständige Datenschutzerklärung
✅ **Freiwilligkeit** - Keine Koppelung, keine Nachteile bei Ablehnung
✅ **Granularität** - Separate Checkboxen für verschiedene Zwecke
✅ **Widerrufbarkeit** - Jederzeit möglich, prominent kommuniziert
✅ **Nachweisbarkeit** - Vollständiger Audit-Trail
✅ **Dokumentation** - Token + Signatur + IP + Timestamp

---

## 📊 Monitoring & Statistiken

### Token-Statistiken

```bash
curl -X GET "http://localhost:8000/gdpr/tokens/stats"
```

**Antwort:**

```json
{
  "success": true,
  "statistics": {
    "total_tokens": 150,
    "unused_tokens": 45,
    "used_tokens": 100,
    "expired_tokens": 5
  },
  "timestamp": "2025-11-21T12:00:00"
}
```

### Consent-Statistiken

```python
from src.candidate_manager import CandidateManager

manager = CandidateManager()
stats = manager.get_statistics()

print(f"Kandidaten gesamt: {stats['total_candidates']}")
print(f"Mit Einwilligung: {stats['consent_given']}")
print(f"Opted-out: {stats['opted_out']}")
```

### Abgelaufene Tokens bereinigen

```bash
# Tokens älter als 30 Tage löschen
curl -X POST "http://localhost:8000/gdpr/tokens/cleanup?days_old=30"
```

---

## 🎯 Best Practices

### DO ✅

1. **Email VOR Anruf** - Immer zuerst Consent-Email senden
2. **Einwilligung prüfen** - Vor JEDEM Anruf `has_valid_consent()` checken
3. **Link-Gültigkeit** - 7 Tage ist optimal (nicht zu kurz, nicht zu lang)
4. **Freundliche Emails** - Professionell aber nicht zu formell
5. **Klare CTAs** - Button "Einwilligung bestätigen" prominent platzieren
6. **Reminder senden** - Nach 3-4 Tagen Erinnerung bei fehlender Antwort
7. **Audit-Trail bewahren** - Mindestens 3 Jahre für Nachweispflicht

### DON'T ❌

1. **Nicht ohne Consent anrufen** - Rechtlich problematisch!
2. **Keine vorangekreuzten Boxen** - DSGVO-Verstoß
3. **Keine Koppelung** - Consent muss freiwillig sein
4. **Keine undurchsichtigen Texte** - Klare, verständliche Sprache
5. **Nicht zu viele Zwecke** - Max. 3-4 Checkboxen
6. **Keine zu kurzen Tokens** - Min. 48 Bytes (64 Zeichen)
7. **Keine ungesicherten Links** - Immer HTTPS verwenden

---

## 🔧 Troubleshooting

### Problem: Link funktioniert nicht

**Fehlermeldung:** "Invalid or expired consent link"

**Ursachen:**
1. Token bereits verwendet
2. Token abgelaufen (> 7 Tage)
3. Token ungültig

**Lösung:**
```python
# Neuen Token generieren
response = requests.post(
    "http://localhost:8000/gdpr/consent/send-link",
    json={"candidate_id": 123, "email": "max@example.com"}
)

new_link = response.json()["consent_url"]
# Neue Email mit neuem Link senden
```

### Problem: Formular wird nicht angezeigt

**Ursache:** Templates-Ordner nicht gefunden

**Lösung:**
```bash
# Prüfen ob Template existiert
ls -la src/templates/consent_form.html

# Falls nicht: Sicherstellen dass Datei vorhanden
# Pfad muss relativ zum Projektroot sein
```

### Problem: Email kommt nicht an

**Ursachen:**
1. SMTP-Konfiguration falsch
2. Email landet im Spam
3. Email-Adresse ungültig

**Lösung:**
```python
# SMTP-Verbindung testen
import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-password')
    print("✅ SMTP connection successful")
    server.quit()
except Exception as e:
    print(f"❌ SMTP error: {e}")
```

---

## 📚 Weitere Ressourcen

- **API-Dokumentation:** http://localhost:8000/docs
- **DSGVO-Guide:** `docs/DSGVO_COMPLIANCE_GUIDE.md`
- **Email-Templates:** `docs/templates/`
- **Code-Beispiele:** `scripts/`

---

**Version:** 2.0
**Letzte Aktualisierung:** November 2025
