# Email & Dokumenten-Templates

Dieses Verzeichnis enthält DSGVO-konforme Templates für die Kommunikation mit Kandidaten.

## 📁 Verfügbare Templates

### Datenschutz-Dokumente

1. **`datenschutzerklaerung_kandidaten.md`**
   - Vollständige Datenschutzerklärung für Kandidaten (Deutsch)
   - Muss auf Ihrer Website veröffentlicht werden
   - DSGVO-konform mit allen erforderlichen Informationen

### Email-Templates

2. **`email_consent_confirmation.md`**
   - Bestätigung der Einwilligung nach Telefonat
   - Verwendung: Nach erstem Kontakt mit Kandidat

3. **`email_double_optin_request.md`**
   - Double-Opt-In Anfrage per Email
   - Verwendung: Wenn Kandidat Einwilligung per Email bestätigen soll

4. **`email_consent_revoked.md`**
   - Bestätigung des Widerrufs der Einwilligung
   - Verwendung: Nach Opt-out durch Kandidat

5. **`email_data_export.md`**
   - Datenauskunft gemäß DSGVO Art. 15
   - Verwendung: Wenn Kandidat Auskunft über gespeicherte Daten verlangt

## 🔧 Verwendung der Templates

### Schritt 1: Platzhalter ersetzen

Alle Templates enthalten Platzhalter im Format `{{ PLATZHALTER }}`:

**Allgemeine Platzhalter:**
- `{{ COMPANY_NAME }}` - Ihr Firmenname
- `{{ COMPANY_ADDRESS }}` - Ihre Firmenadresse
- `{{ COMPANY_CITY }}` - Stadt + PLZ
- `{{ COMPANY_WEBSITE }}` - Ihre Website-URL
- `{{ CONTACT_EMAIL }}` - Email für DSGVO-Anfragen
- `{{ CONTACT_PHONE }}` - Telefon für DSGVO-Anfragen
- `{{ PRIVACY_POLICY_URL }}` - URL zur Datenschutzerklärung

**Kandidaten-spezifische Platzhalter:**
- `{{ CANDIDATE_NAME }}` - Name des Kandidaten
- `{{ CANDIDATE_PHONE }}` - Telefonnummer
- `{{ CANDIDATE_EMAIL }}` - Email-Adresse
- `{{ CANDIDATE_ID }}` - Interne ID
- `{{ CONSENT_TIMESTAMP }}` - Zeitpunkt der Einwilligung
- `{{ DATA_RETENTION_DATE }}` - Datum bis Daten gespeichert werden

**Event-spezifische Platzhalter:**
- `{{ CALL_DATE }}` - Datum des Anrufs
- `{{ REVOCATION_DATE }}` - Datum des Widerrufs
- `{{ EXPORT_DATE }}` - Datum des Datenexports

### Schritt 2: Template-Engine integrieren (optional)

**Option A: Manuelle Ersetzung**
```python
def fill_template(template_path: str, data: dict) -> str:
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for key, value in data.items():
        content = content.replace(f"{{{{ {key} }}}}", str(value))

    return content

# Verwendung
template = fill_template(
    'docs/templates/email_consent_confirmation.md',
    {
        'COMPANY_NAME': 'Meine Firma GmbH',
        'CANDIDATE_NAME': 'Max Mustermann',
        'CANDIDATE_EMAIL': 'max@example.com',
        'CONSENT_TIMESTAMP': '2025-11-21 10:30:00'
    }
)
```

**Option B: Jinja2 (empfohlen)**
```python
from jinja2 import Template

with open('docs/templates/email_consent_confirmation.md') as f:
    template = Template(f.read())

email_content = template.render(
    COMPANY_NAME='Meine Firma GmbH',
    CANDIDATE_NAME='Max Mustermann',
    CANDIDATE_EMAIL='max@example.com'
)
```

### Schritt 3: Email versenden

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_gdpr_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = 'datenschutz@ihrefirma.de'
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-password')
        server.send_message(msg)

# Verwendung
send_gdpr_email(
    to_email='max@example.com',
    subject='Bestätigung Ihrer Einwilligung',
    body=email_content
)
```

## 📝 Anpassungshinweise

### Datenschutzerklärung

**Pflichtanpassungen:**
1. Firmendaten aktualisieren (Name, Adresse, Kontakt)
2. Drittanbieter-Liste prüfen und anpassen
3. Datenschutzbeauftragten eintragen (falls vorhanden)
4. Zuständige Aufsichtsbehörde für Ihr Bundesland

**Optionale Anpassungen:**
- Speicherdauer (Standard: 2 Jahre)
- Zusätzliche Datenverarbeitungen ergänzen
- Spezifische Rechtsgrundlagen hinzufügen

### Email-Templates

**Empfohlene Anpassungen:**
- Tone of Voice an Ihre Unternehmenskultur anpassen
- Corporate Design / Branding hinzufügen
- Footer mit Social Media Links
- Unternehmensspezifische Formulierungen

**Wichtig:** Rechtlich relevante Inhalte nicht verändern!

## 🌐 Mehrsprachigkeit

Für internationales Recruiting erstellen Sie Kopien der Templates in anderen Sprachen:

```
docs/templates/
  ├── de/  (Deutsch - Standard)
  │   ├── datenschutzerklaerung_kandidaten.md
  │   ├── email_consent_confirmation.md
  │   └── ...
  ├── en/  (Englisch)
  │   ├── privacy_policy_candidates.md
  │   ├── email_consent_confirmation.md
  │   └── ...
  └── fr/  (Französisch)
      └── ...
```

## 📊 Best Practices

### DO:
✅ Templates vor Verwendung testen
✅ Platzhalter vollständig ersetzen
✅ Email-Versand protokollieren (wer, wann, welches Template)
✅ Templates versionieren (v1.0, v1.1, etc.)
✅ Regelmäßig auf Aktualität prüfen (mind. jährlich)

### DON'T:
❌ Templates ohne Rechtsberatung stark verändern
❌ Platzhalter leer lassen oder mit "TODO" füllen
❌ Alte Versionen ohne Dokumentation verwenden
❌ Sensible Daten im Klartext in Emails senden

## 🔐 Datenschutz bei Email-Versand

**Sicherheitshinweise:**
- Verwenden Sie TLS-Verschlüsselung für SMTP
- Keine personenbezogenen Daten im Betreff
- Bei Datenexport: Anhang verschlüsseln oder sicherer Download-Link
- Empfänger-Email-Adresse vor Versand verifizieren
- Versand-Log für Nachweisbarkeit führen

## 📞 Support

Bei Fragen zu den Templates:
- **Email:** datenschutz@ihrefirma.de
- **Dokumentation:** `docs/DSGVO_COMPLIANCE_GUIDE.md`

## ⚖️ Rechtlicher Hinweis

Diese Templates wurden nach bestem Wissen und Gewissen erstellt, ersetzen jedoch keine individuelle Rechtsberatung. Lassen Sie die Templates vor produktivem Einsatz von einem Fachanwalt für Datenschutzrecht prüfen.

---

**Version:** 1.0
**Stand:** November 2025
