# DSGVO-Compliance Guide für AI Recruiting Call Agent

**Version:** 1.0
**Stand:** November 2025
**Für:** Betreiber des AI Recruiting Call Agent Systems

---

## 📋 Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Rechtliche Grundlagen](#rechtliche-grundlagen)
3. [Implementierte Features](#implementierte-features)
4. [Einrichtung und Konfiguration](#einrichtung-und-konfiguration)
5. [Einwilligungsprozess](#einwilligungsprozess)
6. [DSGVO-Rechte verwalten](#dsgvo-rechte-verwalten)
7. [Automatische Datenlöschung](#automatische-datenlöschung)
8. [API-Dokumentation](#api-dokumentation)
9. [Best Practices](#best-practices)
10. [Checkliste](#checkliste)

---

## 1. Überblick

Dieses System verarbeitet personenbezogene Daten von Kandidaten für Recruiting-Zwecke und muss daher DSGVO-konform betrieben werden.

### Was ist neu?

✅ **Einwilligungsverwaltung** - Tracking von Consent in der Datenbank
✅ **DSGVO-Rechte API** - Auskunft, Löschung, Export, Widerruf
✅ **Datenschutzerklärung** - Template auf Deutsch
✅ **Email-Templates** - Für alle DSGVO-Kommunikationen
✅ **AI-Prompts** - Einwilligungsabfrage während Anruf
✅ **Automatische Migration** - Bestehende Datenbanken werden erweitert

---

## 2. Rechtliche Grundlagen

### 2.1 Relevante Gesetzesgrundlagen

**DSGVO (EU):**
- Art. 6 Abs. 1 lit. a - Einwilligung
- Art. 6 Abs. 1 lit. b - Vertragsanbahnung
- Art. 7 - Bedingungen für die Einwilligung
- Art. 15 - Auskunftsrecht
- Art. 17 - Recht auf Löschung ("Recht auf Vergessenwerden")
- Art. 20 - Recht auf Datenübertragbarkeit
- Art. 21 - Widerspruchsrecht

**BDSG (Deutschland):**
- § 26 - Datenverarbeitung für Zwecke des Beschäftigungsverhältnisses

**UWG (Deutschland):**
- § 7 - Unzumutbare Belästigungen (Cold Calling)

### 2.2 Cold Calling in Deutschland

⚠️ **WICHTIG:** Cold Calling ist in Deutschland grundsätzlich nur zulässig bei:
- **B2B-Kontext** mit mutmaßlichem Interesse
- **Bestandskunden** mit vorheriger Geschäftsbeziehung
- **Expliziter Einwilligung** des Angerufenen

**Empfehlung:**
1. Nur Kandidaten anrufen, die mutmaßliches berufliches Interesse haben
2. Zu Beginn des Anrufs Einwilligung einholen
3. Bei Ablehnung sofort beenden und nicht erneut kontaktieren

---

## 3. Implementierte Features

### 3.1 Datenbank-Erweiterungen

Die `candidates` Tabelle wurde um folgende Felder erweitert:

```sql
-- DSGVO/Privacy fields
consent_given INTEGER DEFAULT 0
consent_timestamp TIMESTAMP
consent_method TEXT  -- 'phone', 'email', 'web', 'sms'
consent_version TEXT  -- z.B. 'v1.0'
recording_consent INTEGER DEFAULT 0
marketing_consent INTEGER DEFAULT 0
data_retention_until TIMESTAMP
opted_out INTEGER DEFAULT 0
opted_out_at TIMESTAMP
```

**Automatische Migration:**
Beim Start des Systems werden bestehende Datenbanken automatisch erweitert. Keine manuelle Migration erforderlich!

### 3.2 CandidateManager Methoden

**Neue DSGVO-Methoden:**

```python
# Einwilligung setzen
manager.set_consent(
    candidate_id=123,
    consent_given=True,
    consent_method='phone',
    recording_consent=True,
    retention_days=730  # 2 Jahre
)

# Einwilligung prüfen
has_consent = manager.has_valid_consent(candidate_id=123)

# Einwilligung widerrufen
manager.revoke_consent(candidate_id=123)

# Daten exportieren
export_data = manager.export_candidate_data(candidate_id=123)

# Daten löschen/anonymisieren
manager.delete_candidate_data(candidate_id=123, anonymize=False)

# Kandidaten mit abgelaufener Speicherfrist
expired = manager.get_candidates_needing_deletion()
```

### 3.3 GDPR API Endpunkte

Die API ist unter `/gdpr/*` verfügbar:

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/gdpr/consent/give` | POST | Einwilligung erteilen |
| `/gdpr/consent/revoke` | POST | Einwilligung widerrufen |
| `/gdpr/consent/check` | GET | Einwilligung prüfen |
| `/gdpr/data/export` | GET | Datenexport (Art. 20) |
| `/gdpr/data/delete` | POST | Datenlöschung (Art. 17) |
| `/gdpr/retention/expired` | GET | Abgelaufene Speicherfristen |
| `/gdpr/health` | GET | Health Check |

**API-Dokumentation:** Nach Start des Servers unter `/docs` verfügbar (Swagger UI)

### 3.4 AI-Agent Einwilligungsabfrage

Der AI-Agent wurde angepasst:

✅ Fragt zu Beginn des Gesprächs nach Einwilligung
✅ Erklärt Zweck der Datenverarbeitung
✅ Informiert über Widerrufsrecht
✅ Erwähnt Speicherdauer (2 Jahre)
✅ Beendet Gespräch bei fehlender Einwilligung

---

## 4. Einrichtung und Konfiguration

### 4.1 Erforderliche Anpassungen in `.env`

Fügen Sie folgende Variablen hinzu:

```bash
# Company Information (für Datenschutzerklärung)
COMPANY_NAME="Ihre Firma GmbH"
COMPANY_ADDRESS="Musterstraße 123"
COMPANY_CITY="12345 Musterstadt"
COMPANY_WEBSITE="https://ihrefirma.de"

# Kontakt für DSGVO-Anfragen
CONTACT_EMAIL="datenschutz@ihrefirma.de"
CONTACT_PHONE="+49 123 456789"

# URLs
PUBLIC_URL="https://ihre-domain.de"
PRIVACY_POLICY_URL="https://ihre-domain.de/datenschutz"

# Optional: Email-Versand für DSGVO-Benachrichtigungen
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-password"
SMTP_FROM="noreply@ihrefirma.de"
```

### 4.2 Datenschutzerklärung veröffentlichen

1. **Template anpassen:**
   ```bash
   docs/templates/datenschutzerklaerung_kandidaten.md
   ```

2. **Platzhalter ersetzen:**
   - `{{ COMPANY_NAME }}`
   - `{{ COMPANY_ADDRESS }}`
   - `{{ CONTACT_EMAIL }}`
   - etc.

3. **Veröffentlichen:**
   - Als PDF auf Ihrer Website
   - Unter der URL, die in `PRIVACY_POLICY_URL` angegeben ist

### 4.3 Email-Templates konfigurieren

Passen Sie die Templates in `docs/templates/` an:
- `email_consent_confirmation.md`
- `email_double_optin_request.md`
- `email_consent_revoked.md`
- `email_data_export.md`

---

## 5. Einwilligungsprozess

### 5.1 Methode A: Telefonische Einwilligung (Standard)

**Ablauf:**
1. AI-Agent ruft Kandidaten an
2. Nach Begrüßung: Datenschutz-Hinweis
3. Kandidat stimmt verbal zu ("Ja, einverstanden")
4. Einwilligung wird im Transkript dokumentiert
5. System setzt Consent-Flag in Datenbank

**Implementierung:**
```python
# Im call_handler nach erfolgreicher Einwilligung:
manager = CandidateManager()
manager.set_consent(
    candidate_id=candidate_id,
    consent_given=True,
    consent_method='phone',
    recording_consent=True,  # Falls Aufzeichnung
    retention_days=730
)
```

**Empfehlung:** Zusätzlich Bestätigungs-Email senden (siehe Methode B)

### 5.2 Methode B: Double-Opt-In per Email (Empfohlen)

**Ablauf:**
1. Nach Telefonat: Email mit Bestätigungslink
2. Kandidat klickt auf "Einwilligung bestätigen"
3. System registriert Einwilligung mit Timestamp
4. Bestätigungs-Email wird gesendet

**Vorteile:**
- ✅ Bessere Nachweisbarkeit
- ✅ Schriftliche Dokumentation
- ✅ DSGVO-konformer

**Beispiel-URL:**
```
https://ihre-domain.de/gdpr/consent/confirm?token=SECURE_TOKEN
```

### 5.3 Methode C: Web-Formular

**Ablauf:**
1. Kandidat füllt Online-Formular aus
2. Explizite Checkboxen für verschiedene Einwilligungen
3. System speichert Einwilligung mit IP + Timestamp

**HTML-Formular Beispiel:**
```html
<form action="/gdpr/consent/give" method="POST">
  <input type="hidden" name="candidate_id" value="123">

  <label>
    <input type="checkbox" name="consent_given" required>
    Ich willige in die Verarbeitung meiner Daten ein
  </label>

  <label>
    <input type="checkbox" name="recording_consent">
    Einwilligung zur Aufzeichnung von Gesprächen
  </label>

  <label>
    <input type="checkbox" name="marketing_consent">
    Einwilligung zu Marketing-Kommunikation
  </label>

  <button type="submit">Bestätigen</button>
</form>
```

---

## 6. DSGVO-Rechte verwalten

### 6.1 Auskunftsrecht (Art. 15 DSGVO)

**Kandidat fragt:** "Welche Daten haben Sie über mich gespeichert?"

**Prozess:**
1. Kandidat kontaktiert Sie per Email
2. Identität prüfen (zur Sicherheit)
3. API-Call zum Datenexport

**Beispiel:**
```bash
curl -X GET "http://localhost:8000/gdpr/data/export?phone=%2B4915112345678"
```

**Antwort:**
```json
{
  "success": true,
  "export_data": {
    "candidate": {
      "id": 123,
      "name": "Max Mustermann",
      "phone": "+4915112345678",
      "email": "max@example.com",
      "consent_given": true,
      "consent_timestamp": "2025-11-20 10:30:00"
    },
    "call_logs": [...],
    "conversation_history": [...]
  },
  "export_timestamp": "2025-11-21 09:00:00"
}
```

**Nächste Schritte:**
1. JSON in lesbares Format konvertieren (oder Email-Template nutzen)
2. Email an Kandidaten senden (Template: `email_data_export.md`)
3. Als Anhang: JSON-Datei

### 6.2 Löschungsrecht (Art. 17 DSGVO)

**Kandidat fragt:** "Bitte löschen Sie meine Daten."

**Zwei Optionen:**

**Option 1: Vollständige Löschung**
```bash
curl -X POST "http://localhost:8000/gdpr/data/delete" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+4915112345678", "anonymize": false}'
```

**Option 2: Anonymisierung**
```bash
curl -X POST "http://localhost:8000/gdpr/data/delete" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+4915112345678", "anonymize": true}'
```

**Empfehlung:** Anonymisierung für statistische Zwecke, wenn keine gesetzlichen Aufbewahrungspflichten bestehen.

**Nach Löschung:**
- Bestätigungs-Email senden (Template: `email_consent_revoked.md`)
- Dokumentieren für interne Nachweise

### 6.3 Widerrufsrecht (Art. 7 Abs. 3 DSGVO)

**Kandidat sagt:** "Ich widerrufe meine Einwilligung."

**Prozess:**
```bash
curl -X POST "http://localhost:8000/gdpr/consent/revoke" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+4915112345678"}'
```

**Effekt:**
- `opted_out = 1` in Datenbank
- `consent_given = 0`
- Kandidat wird nicht mehr kontaktiert
- Daten bleiben (vorerst) gespeichert für rechtliche Nachweisbarkeit

**Nach Widerruf:**
- Keine weiteren Anrufe oder Emails!
- Optional: Daten nach Ablauf von Nachweis-Frist (z.B. 3 Jahre) löschen

### 6.4 Berichtigungsrecht (Art. 16 DSGVO)

**Kandidat sagt:** "Meine Email-Adresse ist falsch."

**Prozess:**
```python
from src.candidate_manager import CandidateManager

manager = CandidateManager()
candidate = manager.get_candidate(phone="+4915112345678")

# Manuelle Berichtigung in Datenbank (oder via API-Endpoint)
# TODO: Könnte als weiteres API-Feature implementiert werden
```

**Empfehlung:** API-Endpoint für Berichtigung hinzufügen (zukünftiges Feature)

---

## 7. Automatische Datenlöschung

### 7.1 Speicherfristen

**Standard:**
- Kandidaten-Daten: **2 Jahre** nach letztem Kontakt
- Call-Logs: **2 Jahre**
- Transkripte: **2 Jahre**

**Konfigurierbar:**
```python
manager.set_consent(
    candidate_id=123,
    retention_days=730  # Standard
)
```

### 7.2 Automatisches Cleanup-Script

**Empfehlung:** Täglicher Cron-Job

**Script erstellen:**
```python
# scripts/cleanup_expired_data.py
from src.candidate_manager import CandidateManager
from loguru import logger

def cleanup_expired_candidates():
    manager = CandidateManager()

    # Kandidaten mit abgelaufener Frist finden
    expired = manager.get_candidates_needing_deletion()

    logger.info(f"Found {len(expired)} candidates with expired retention")

    for candidate in expired:
        logger.info(f"Deleting data for candidate {candidate.id}: {candidate.name}")

        # Anonymisierung statt vollständiger Löschung
        manager.delete_candidate_data(
            candidate_id=candidate.id,
            anonymize=True
        )

    logger.info("Cleanup completed")

if __name__ == "__main__":
    cleanup_expired_candidates()
```

**Cron-Job einrichten:**
```bash
# Täglich um 2:00 Uhr
0 2 * * * cd /path/to/project && python scripts/cleanup_expired_data.py
```

### 7.3 API-Endpoint für Cleanup

```bash
# Manuelle Prüfung
curl -X GET "http://localhost:8000/gdpr/retention/expired"
```

**Antwort:**
```json
{
  "count": 5,
  "candidates": [
    {
      "id": 123,
      "name": "Max Mustermann",
      "phone": "+4915112345678",
      "data_retention_until": "2023-11-20",
      "days_expired": 365
    }
  ]
}
```

---

## 8. API-Dokumentation

### 8.1 Swagger UI

Nach Start des Servers:
```
http://localhost:8000/docs
```

### 8.2 Beispiel-Aufrufe

**Einwilligung prüfen:**
```bash
curl -X GET "http://localhost:8000/gdpr/consent/check?candidate_id=123"
```

**Einwilligung erteilen:**
```bash
curl -X POST "http://localhost:8000/gdpr/consent/give" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 123,
    "consent_method": "web",
    "recording_consent": true,
    "marketing_consent": false,
    "retention_days": 730
  }'
```

**Datenexport:**
```bash
curl -X GET "http://localhost:8000/gdpr/data/export?candidate_id=123" \
  -o candidate_123_export.json
```

---

## 9. Best Practices

### 9.1 Einwilligungsverwaltung

✅ **DO:**
- Einwilligung VOR dem ersten Anruf einholen (wenn möglich)
- Doppelte Bestätigung per Email (Double-Opt-In)
- Klare und verständliche Sprache nutzen
- Widerrufsrecht prominent kommunizieren
- Alle Einwilligungen dokumentieren (Timestamp, Methode, Version)

❌ **DON'T:**
- Einwilligung voraussetzen
- Unklare oder versteckte Formulierungen
- Gekoppelte Einwilligungen (alles oder nichts)
- Vorangekreuzte Checkboxen

### 9.2 Datensparsamkeit

✅ **Nur notwendige Daten erheben:**
- Name, Telefon, Email: **JA**
- Geburtsdatum, Adresse: **NEIN** (außer erforderlich)
- Sensible Daten (Gesundheit, Religion): **NIEMALS**

### 9.3 Datensicherheit

✅ **Technische Maßnahmen:**
- HTTPS für alle API-Endpunkte
- Sichere Passwörter für Datenbank
- Zugriffsbeschränkungen (nur autorisierte Mitarbeiter)
- Regelmäßige Backups (verschlüsselt)
- Audit-Logs für Datenzugriffe

### 9.4 Transparenz

✅ **Dokumentation:**
- Verarbeitungsverzeichnis führen (Art. 30 DSGVO)
- Datenschutzerklärung aktuell halten
- Datenschutz-Folgenabschätzung durchführen
- Auftragsverarbeitungsverträge mit Dienstleistern (Twilio, OpenAI, etc.)

---

## 10. Checkliste

### Vor dem produktiven Einsatz:

- [ ] `.env` vollständig konfiguriert (Company Info, Kontaktdaten)
- [ ] Datenschutzerklärung angepasst und veröffentlicht
- [ ] Email-Templates angepasst und getestet
- [ ] SMTP für Email-Versand konfiguriert
- [ ] Double-Opt-In Workflow implementiert
- [ ] Automatisches Cleanup-Script eingerichtet (Cron-Job)
- [ ] API-Endpunkte getestet (`/gdpr/*`)
- [ ] Logging und Monitoring aktiviert
- [ ] Backup-Strategie definiert
- [ ] Auftragsverarbeitungsverträge mit Dienstleistern abgeschlossen
- [ ] Datenschutzbeauftragten informiert (falls erforderlich)
- [ ] Team geschult (DSGVO-Anfragen bearbeiten)
- [ ] Notfall-Plan für Data Breach (Datenpanne)

### Regelmäßige Wartung:

- [ ] Wöchentlich: Abgelaufene Retentions prüfen
- [ ] Monatlich: Statistiken zu Einwilligungen prüfen
- [ ] Quartalsweise: Datenschutzerklärung auf Aktualität prüfen
- [ ] Jährlich: Datenschutz-Folgenabschätzung aktualisieren

---

## Kontakt und Support

Bei Fragen zu DSGVO-Compliance oder technischen Problemen:

📧 **Email:** support@ihrefirma.de
📞 **Telefon:** +49 123 456789
📄 **Dokumentation:** https://ihre-domain.de/docs

---

## Rechtlicher Hinweis

⚠️ **Disclaimer:** Diese Dokumentation bietet allgemeine Hinweise zur DSGVO-Compliance, ersetzt jedoch keine Rechtsberatung. Konsultieren Sie einen Fachanwalt für Datenschutzrecht für Ihre spezifische Situation.

---

**Stand:** November 2025
**Version:** 1.0
**Autor:** AI Recruiting System Team
