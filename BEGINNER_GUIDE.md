# Anfänger-Anleitung: n8n und Notion einrichten

**Für Einsteiger - Schritt-für-Schritt ohne Vorkenntnisse**

## Was Sie brauchen (5 Minuten Vorbereitung)

- [ ] Einen Computer mit Internet
- [ ] Python 3.10+ installiert ([Python Download](https://www.python.org/downloads/))
- [ ] Einen kostenlosen Notion Account ([Notion Anmeldung](https://www.notion.so/signup))
- [ ] Einen kostenlosen n8n Account ([n8n Cloud](https://n8n.io/))

---

## Teil 1: Python und Projekt vorbereiten (10 Minuten)

### Schritt 1: Projekt herunterladen

```bash
# Terminal öffnen (Windows: cmd, Mac: Terminal, Linux: Terminal)
# Navigiere zu deinem gewünschten Ordner
cd Desktop

# Wenn du das Projekt noch nicht geklont hast:
git clone https://github.com/hrshojaei/hrshojaei.git
cd hrshojaei
```

### Schritt 2: Python-Pakete installieren

```bash
# Im Projekt-Ordner (hrshojaei)
pip install -r requirements.txt
```

**⏱️ Warte 1-2 Minuten** - es werden alle benötigten Pakete heruntergeladen.

### Schritt 3: Konfigurationsdatei erstellen

```bash
# Kopiere die Beispiel-Konfiguration
cp .env.example .env
```

**Windows (wenn cp nicht funktioniert):**
```bash
copy .env.example .env
```

✅ **Jetzt hast du eine `.env` Datei!** Diese bearbeitest du gleich.

---

## Teil 2: Notion einrichten (15 Minuten)

### Schritt 1: Notion Integration erstellen

1. **Öffne:** [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. **Klicke:** "+ New Integration"
3. **Name eingeben:** "AI Recruiting Agent"
4. **Workspace wählen:** Dein Workspace
5. **Klicke:** "Submit"

📋 **WICHTIG:** Kopiere den **Internal Integration Token** (beginnt mit `secret_...`)
   - Sieht aus wie: `secret_Ab12Cd34Ef56...`
   - **Speichere ihn temporär in einem Texteditor!**

### Schritt 2: Notion-Datenbank erstellen

1. **Öffne Notion** in deinem Browser
2. **Erstelle neue Seite:** Klicke links unten auf "+ New Page"
3. **Name:** "Recruiting Kandidaten"
4. **Füge Datenbank hinzu:** Tippe `/table` und wähle "Table - Full page"

### Schritt 3: Datenbank-Spalten erstellen

Klicke auf jede Spaltenüberschrift und füge diese hinzu:

| Spaltenname | Typ | So erstellen |
|-------------|-----|--------------|
| Name | Title | (Schon vorhanden) |
| Candidate ID | Number | Klicke "+", wähle "Number" |
| Telefon | Phone | Klicke "+", wähle "Phone" |
| Email | Email | Klicke "+", wähle "Email" |
| Status | Select | Klicke "+", wähle "Select", füge Optionen hinzu: new, contacted, interested, not_interested |
| Aktueller Arbeitgeber | Text | Klicke "+", wähle "Text" |
| Position | Text | Klicke "+", wähle "Text" |
| Berufserfahrung (Jahre) | Number | Klicke "+", wähle "Number" |
| Notizen | Text | Klicke "+", wähle "Text" |
| Letzter Anruf | Date | Klicke "+", wähle "Date" |
| Anruf-Ergebnis | Select | Klicke "+", wähle "Select", füge Optionen hinzu: interested, not_interested, callback_requested |

### Schritt 4: Integration mit Datenbank verbinden

1. **In deiner Datenbank:** Klicke oben rechts auf "..." (drei Punkte)
2. **Scrolle zu:** "Connections"
3. **Klicke:** "+ Add connections"
4. **Wähle:** "AI Recruiting Agent" (deine Integration)

### Schritt 5: Database ID kopieren

1. **Öffne die Datenbank** in deinem Browser
2. **Schaue in die URL-Leiste**, die URL sieht so aus:
   ```
   https://www.notion.so/workspace/abc123def456?v=...
                                  ^^^^^^^^^^^^
                                  Dies ist die Database ID!
   ```
3. **Kopiere die Database ID** (der Teil zwischen / und ?)

📋 **Database ID gespeichert?** Gut, weiter geht's!

---

## Teil 3: n8n einrichten (10 Minuten)

### Schritt 1: n8n Account erstellen

1. **Gehe zu:** [https://n8n.io/](https://n8n.io/)
2. **Klicke:** "Get Started" oder "Sign Up"
3. **Registriere dich** mit Email
4. **Wähle:** "Cloud" (einfacher für Anfänger)

### Schritt 2: Workflow importieren

1. **In n8n:** Klicke "+ New Workflow"
2. **Klicke oben rechts:** Die drei Punkte ⋮
3. **Wähle:** "Import from File"
4. **Navigiere zu:** `n8n-workflows/basic-recruiting-workflow.json` in deinem Projekt
5. **Öffne die Datei**

✅ Der Workflow ist jetzt importiert!

### Schritt 3: Webhook URL kopieren

1. **Im Workflow:** Klicke auf den **"Webhook"** Node (ganz links)
2. **Kopiere** die "Production URL" 
   - Sieht aus wie: `https://deine-n8n.app.n8n.cloud/webhook/recruiting-events`
3. **Speichere sie in deinem Texteditor!**

### Schritt 4: Workflow aktivieren

1. **Oben rechts:** Schalte den Toggle auf **"Active"** (wird blau)
2. **Klicke:** "Save" (falls gefragt)

✅ Der Workflow läuft jetzt!

---

## Teil 4: Alles verbinden (5 Minuten)

### Schritt 1: .env Datei öffnen

**Windows:**
```bash
notepad .env
```

**Mac/Linux:**
```bash
nano .env
```

**Oder:** Öffne `.env` mit einem Texteditor deiner Wahl

### Schritt 2: Deine Daten eintragen

Suche diese Zeilen und fülle sie aus:

```env
# Notion Integration
NOTION_API_KEY=secret_...              # ← Dein Notion Token hier einfügen
NOTION_DATABASE_ID=abc123...           # ← Deine Database ID hier einfügen
NOTION_ENABLED=true                    # ← Auf true setzen

# n8n Webhook Integration
N8N_WEBHOOK_URL=https://...            # ← Deine n8n Webhook URL hier einfügen
N8N_ENABLED=true                       # ← Auf true setzen
```

**Beispiel (mit echten Werten):**
```env
NOTION_API_KEY=secret_Ab12Cd34Ef56Gh78Ij90Kl12Mn34Op56
NOTION_DATABASE_ID=1a2b3c4d5e6f7g8h9i0j
NOTION_ENABLED=true

N8N_WEBHOOK_URL=https://meine-n8n.app.n8n.cloud/webhook/recruiting-events
N8N_ENABLED=true
```

### Schritt 3: Datei speichern

- **Windows Notepad:** Datei → Speichern
- **Mac/Linux nano:** Strg+O, Enter, Strg+X
- **Anderer Editor:** Speichern und schließen

✅ **Konfiguration fertig!**

---

## Teil 5: Testen (5 Minuten)

### Schritt 1: Test-Script ausführen

```bash
# Im Projekt-Ordner
python scripts/test_integration.py
```

**Was passiert:**
- Ein Test-Kandidat wird erstellt
- Notion wird aktualisiert
- n8n erhält Events

### Schritt 2: Ergebnisse prüfen

**In Notion:**
1. Öffne deine "Recruiting Kandidaten" Datenbank
2. Du solltest einen Eintrag "Max Mustermann (Demo)" sehen

**In n8n:**
1. Öffne deinen Workflow
2. Klicke auf "Executions" (oben rechts)
3. Du solltest mehrere erfolgreiche Executions sehen

**Im Terminal:**
- Es sollten ✓ Meldungen erscheinen
- Keine Fehler

✅ **Wenn alles funktioniert: Glückwunsch, du bist fertig! 🎉**

---

## Bei Problemen

### Fehler: "Notion integration disabled"

**Lösung:**
1. Prüfe in `.env`: `NOTION_ENABLED=true` (nicht false!)
2. Prüfe: Hast du `NOTION_API_KEY` eingetragen?
3. Starte das Script neu

### Fehler: "n8n webhook integration disabled"

**Lösung:**
1. Prüfe in `.env`: `N8N_ENABLED=true`
2. Prüfe: Hast du `N8N_WEBHOOK_URL` eingetragen?
3. Starte das Script neu

### Fehler: "Module not found"

**Lösung:**
```bash
pip install -r requirements.txt
```

### n8n Workflow empfängt keine Events

**Lösung:**
1. Prüfe: Ist der Workflow in n8n auf "Active"?
2. Prüfe: Stimmt die Webhook URL in `.env`?
3. Teste manuell:
   ```bash
   curl -X POST https://deine-n8n-url/webhook/recruiting-events \
     -H "Content-Type: application/json" \
     -d '{"event":"test","data":{}}'
   ```

### Notion zeigt keine Daten

**Lösung:**
1. Prüfe: Ist die Integration mit der Datenbank verbunden? (Schritt 4 von Teil 2)
2. Prüfe: Stimmt die Database ID?
3. Schaue in die Logs: `tail -f logs/calling_agent_*.log`

---

## Nächste Schritte

Jetzt wo alles läuft:

1. **Echte Kandidaten hinzufügen:**
   ```bash
   python -m src.main add
   ```

2. **Server starten:**
   ```bash
   python -m src.main server
   ```

3. **Workflow anpassen:**
   - Öffne den Workflow in n8n
   - Konfiguriere Slack Node mit deinem Workspace
   - Konfiguriere Email Node mit deinen SMTP-Daten
   - Füge weitere Nodes hinzu (z.B. Google Sheets, Trello, etc.)

4. **Dokumentation lesen:**
   - Detailliert: `N8N_NOTION_GUIDE.md`
   - Übersicht: `INTEGRATION_OVERVIEW.md`

---

## Zusammenfassung

✅ **Was du jetzt hast:**
- Notion-Datenbank für Kandidaten
- n8n Workflow für Automatisierung
- Beide verbunden mit dem Recruiting Agent
- Automatische Benachrichtigungen bei interessierten Kandidaten
- Call-Logs in Notion

✅ **Was automatisch passiert:**
- Neue Kandidaten → erscheinen in Notion
- Kandidat interessiert → Slack/Email Notification
- Anruf beendet → wird in Notion dokumentiert

**Bei weiteren Fragen, siehe die ausführliche Dokumentation oder erstelle ein Issue!**
