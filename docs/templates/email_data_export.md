# Email-Vorlage: Datenauskunft (DSGVO Art. 15)

---

**Betreff:** Ihre Datenauskunft gemäß DSGVO – {{ COMPANY_NAME }}

---

Guten Tag {{ CANDIDATE_NAME }},

gemäß Artikel 15 der DSGVO übermitteln wir Ihnen hiermit eine vollständige Auskunft über die bei uns gespeicherten personenbezogenen Daten.

## 📊 Ihre bei uns gespeicherten Daten

### Stammdaten
- **Name:** {{ CANDIDATE_NAME }}
- **Telefon:** {{ CANDIDATE_PHONE }}
- **E-Mail:** {{ CANDIDATE_EMAIL }}
- **Erstellt am:** {{ CREATED_AT }}
- **Letzte Aktualisierung:** {{ UPDATED_AT }}
- **Letzter Kontakt:** {{ LAST_CONTACT_AT }}

### Berufliche Daten
- **Aktueller Arbeitgeber:** {{ CURRENT_COMPANY }}
- **Aktuelle Position:** {{ CURRENT_POSITION }}
- **Berufserfahrung:** {{ EXPERIENCE_YEARS }} Jahre
- **Status:** {{ STATUS }}

### Einwilligungen
- **Einwilligung erteilt:** {{ CONSENT_GIVEN }}
- **Einwilligung am:** {{ CONSENT_TIMESTAMP }}
- **Methode:** {{ CONSENT_METHOD }}
- **Privacy Policy Version:** {{ CONSENT_VERSION }}
- **Aufzeichnung zugestimmt:** {{ RECORDING_CONSENT }}
- **Marketing zugestimmt:** {{ MARKETING_CONSENT }}
- **Daten gespeichert bis:** {{ DATA_RETENTION_UNTIL }}

### Notizen und Kommentare
{{ NOTES }}

---

## 📞 Ihre Anruf-Historie

{{ CALL_LOGS_TABLE }}

---

## 💬 Gesprächstranskripte

{{ CONVERSATION_TRANSCRIPTS }}

---

## 🎯 Zweck der Datenverarbeitung

Wir verarbeiten Ihre Daten für folgende Zwecke:
- Vermittlung passender Stellenangebote (Recruiting)
- Kontaktaufnahme für relevante Karrieremöglichkeiten
- Dokumentation des Bewerbungsprozesses
- Qualitätssicherung unserer Dienstleistung

## ⚖️ Rechtsgrundlage

Die Verarbeitung erfolgt auf Grundlage von:
- **Art. 6 Abs. 1 lit. a DSGVO** (Einwilligung)
- **Art. 6 Abs. 1 lit. b DSGVO** (Vertragsanbahnung)
- **§ 26 BDSG** (Beschäftigungsverhältnis)

## 🌍 Empfänger Ihrer Daten

Ihre Daten wurden / werden weitergegeben an:
- **Auftragsverarbeiter:** Telefonie-Anbieter (Twilio/Sipgate), KI-Dienste (OpenAI/Anthropic), Cloud-Hosting
- **Potenzielle Arbeitgeber:** {{ SHARED_WITH_EMPLOYERS }}
- **Keine Weitergabe** an sonstige Dritte oder zu Werbezwecken

## ⏱️ Speicherdauer

Ihre Daten werden gespeichert bis:
- **{{ DATA_RETENTION_UNTIL }}** (automatische Löschung)
- Oder bis Sie Ihre Einwilligung widerrufen
- Oder bis gesetzliche Aufbewahrungsfristen ablaufen

## 📎 Vollständiger Datenexport (JSON)

Im Anhang dieser E-Mail finden Sie Ihre vollständigen Daten in maschinenlesbarem Format (JSON):
- **Datei:** `{{ CANDIDATE_NAME }}_datenexport_{{ EXPORT_DATE }}.json`

Diese Datei können Sie für eigene Zwecke nutzen oder an einen anderen Anbieter übermitteln (Datenübertragbarkeit gemäß Art. 20 DSGVO).

---

## 🛠️ Was können Sie mit diesen Daten tun?

### ✏️ Berichtigung beantragen
Falls Daten fehlerhaft sind, können Sie die Berichtigung verlangen:
📧 {{ CONTACT_EMAIL }}

### 🗑️ Löschung beantragen
Sie können die Löschung Ihrer Daten verlangen:
📧 {{ CONTACT_EMAIL }} (Betreff: "Löschung meiner Daten")

### 🔒 Verarbeitung einschränken
Sie können die Einschränkung der Verarbeitung verlangen:
📧 {{ CONTACT_EMAIL }} (Betreff: "Einschränkung der Verarbeitung")

### 🚫 Einwilligung widerrufen
Widerrufen Sie Ihre Einwilligung:
🔗 {{ OPT_OUT_LINK }}

---

## 📋 Beschwerderecht

Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweiden:
🔗 https://www.bfdi.bund.de/DE/Infothek/Anschriften_Links/anschriften_links-node.html

---

## ❓ Fragen zu Ihrer Auskunft?

Bei Fragen oder Unklarheiten kontaktieren Sie uns bitte:

📧 {{ CONTACT_EMAIL }}
📞 {{ CONTACT_PHONE }}

Wir beantworten Ihre Anfrage innerhalb von 30 Tagen.

---

Mit freundlichen Grüßen

**{{ COMPANY_NAME }} Datenschutz-Team**

---

**Anhänge:**
- 📄 `{{ CANDIDATE_NAME }}_datenexport_{{ EXPORT_DATE }}.json` ({{ FILE_SIZE }} KB)
- 📄 `Datenschutzerklaerung_{{ COMPANY_NAME }}.pdf`

---

_Diese E-Mail wurde als Antwort auf Ihre Auskunftsanfrage gemäß Art. 15 DSGVO erstellt._
