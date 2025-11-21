# Email-Vorlage: Bestätigung Widerruf der Einwilligung

---

**Betreff:** Bestätigung: Widerruf Ihrer Einwilligung – {{ COMPANY_NAME }}

---

Guten Tag {{ CANDIDATE_NAME }},

wir bestätigen hiermit den Widerruf Ihrer Einwilligung zur Datenverarbeitung.

## Was haben wir unternommen?

✓ Ihre Einwilligung wurde am **{{ REVOCATION_DATE }}** widerrufen
✓ Ihre Daten wurden aus unserem aktiven Recruiting-System entfernt
✓ Sie erhalten keine weiteren Kontaktaufnahmen von uns
{{ IF_DELETE }}✓ Ihre Daten wurden vollständig gelöscht{{ /IF_DELETE }}
{{ IF_ANONYMIZE }}✓ Ihre Daten wurden anonymisiert (zu statistischen Zwecken){{ /IF_ANONYMIZE }}

## Ihre gespeicherten Daten

{{ IF_DELETE }}
**Alle Ihre personenbezogenen Daten wurden gelöscht:**
- Name, Kontaktdaten, Gesprächsprotokolle
- Call-Logs und Transkripte
- Notizen und Bewerbungsunterlagen
{{ /IF_DELETE }}

{{ IF_ANONYMIZE }}
**Folgende Daten wurden anonymisiert:**
- Name → "ANONYMIZED"
- Telefon → "DELETED"
- E-Mail → gelöscht
- Gesprächsinhalte → "ANONYMIZED"

**Hinweis:** Anonymisierte statistische Daten (ohne Personenbezug) verbleiben zu Analysezwecken.
{{ /IF_ANONYMIZE }}

## Was bedeutet das für Sie?

❌ Wir werden Sie nicht mehr für Stellenangebote kontaktieren
❌ Ihr Profil ist nicht mehr in unserer Kandidaten-Datenbank
✅ Sie haben Ihre DSGVO-Rechte erfolgreich ausgeübt

## Sie haben es sich anders überlegt?

Kein Problem! Falls Sie wieder Interesse an unseren Stellenangeboten haben, können Sie sich jederzeit neu registrieren:

📧 {{ CONTACT_EMAIL }}
📞 {{ CONTACT_PHONE }}
🌐 {{ COMPANY_WEBSITE }}

---

Wir bedauern, dass Sie nicht mehr an unseren Angeboten interessiert sind, respektieren aber selbstverständlich Ihre Entscheidung.

Vielen Dank für Ihr Vertrauen und alles Gute für Ihre berufliche Zukunft!

Mit freundlichen Grüßen

**{{ COMPANY_NAME }} Recruiting-Team**

📧 {{ CONTACT_EMAIL }}
📞 {{ CONTACT_PHONE }}

---

_Sie haben diese E-Mail erhalten, weil Sie den Widerruf Ihrer Einwilligung beantragt haben. Dies ist die letzte E-Mail, die Sie von uns erhalten._
