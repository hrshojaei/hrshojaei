# 🚀 Komplette Setup-Anleitung von A bis Z

Diese Anleitung führt Sie Schritt-für-Schritt vom Start bis zum funktionierenden System.

**Zeitaufwand:** Ca. 30-45 Minuten
**Schwierigkeit:** ⭐⭐ Mittel (ich erkläre alles!)

---

## 📋 Überblick - Was wir machen werden

```
PHASE 1: Vorbereitung (15 Min)
  ├─ 1. Telegram Bot erstellen
  ├─ 2. Anthropic API Key
  └─ 3. Google Cloud Setup

PHASE 2: Server-Installation (10 Min)
  ├─ 4. Docker installieren
  ├─ 5. Repository clonen
  └─ 6. Konfiguration

PHASE 3: Start & Test (10 Min)
  ├─ 7. System starten
  ├─ 8. Google Drive verbinden
  └─ 9. Ersten Test

✅ FERTIG: System läuft!
```

---

# PHASE 1: Vorbereitung (API Keys beschaffen)

## ✅ Schritt 1: Telegram Bot erstellen (5 Minuten)

### Was brauchen Sie?
- Telegram App auf Handy oder PC

### So geht's:

1. **Öffnen Sie Telegram**

2. **Suchen Sie nach:** `@BotFather`
   - Das ist der offizielle Bot von Telegram zum Erstellen von Bots

3. **Chat mit BotFather starten:**
   ```
   Tippen Sie: /start
   ```

4. **Neuen Bot erstellen:**
   ```
   Tippen Sie: /newbot
   ```

5. **BotFather fragt nach Namen:**
   ```
   Beispiel: Mein Dokument Bot
   (Das ist der Anzeigename, kann alles sein)
   ```

6. **BotFather fragt nach Username:**
   ```
   Beispiel: MeinDokumentSorter_bot
   Wichtig: Muss auf "_bot" enden!
   Muss eindeutig sein (falls vergeben, anderen Namen wählen)
   ```

7. **BotFather antwortet mit:**
   ```
   Done! Congratulations on your new bot...

   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

8. **✅ WICHTIG: Token kopieren!**
   ```
   Beispiel: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

   ⚠️ Diesen Token NIEMANDEM zeigen!
   ⚠️ Nicht in öffentliche Repos committen!
   ```

9. **Token sicher speichern:**
   - In Textdatei auf PC
   - Oder in Password-Manager
   - Sie brauchen ihn gleich für die .env Datei

**✅ Geschafft! Telegram Bot ist erstellt**

---

## ✅ Schritt 2: Anthropic API Key (5 Minuten)

### Was brauchen Sie?
- Email-Adresse
- Kreditkarte (für Verifikation, aber kostenlose Nutzung verfügbar)

### So geht's:

1. **Gehen Sie zu:** https://console.anthropic.com/

2. **Account erstellen:**
   - Klicken Sie auf "Sign Up"
   - Email eingeben
   - Bestätigungs-Email öffnen
   - Account aktivieren

3. **Einloggen**

4. **API Key erstellen:**
   - Gehen Sie zu: **Settings** (oben rechts)
   - Klicken Sie: **API Keys**
   - Klicken Sie: **Create Key**
   - Name: "Document Sorter" (oder beliebig)
   - Klicken Sie: **Create Key**

5. **✅ Key kopieren!**
   ```
   Beispiel: sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx

   ⚠️ Wird nur EINMAL angezeigt!
   ⚠️ Sofort kopieren und speichern!
   ```

6. **Key sicher speichern:**
   - In Textdatei
   - Sie brauchen ihn gleich

**Kosten:**
- Erste Nutzung: ~$5 Gratis-Guthaben
- Danach: Pay-as-you-go
- Für 100 Dokumente/Monat: ~$0.50

**✅ Geschafft! Anthropic API Key erstellt**

---

## ✅ Schritt 3: Google Cloud Setup (10 Minuten)

### Was brauchen Sie?
- Google Account
- Google Drive (kostenlos)

### So geht's:

### 3.1 Google Cloud Projekt erstellen

1. **Gehen Sie zu:** https://console.cloud.google.com/

2. **Projekt erstellen:**
   - Klicken Sie oben: **Projekt auswählen** → **NEUES PROJEKT**
   - Projektname: "Document Sorter" (oder beliebig)
   - Organisation: (leer lassen)
   - Klicken Sie: **ERSTELLEN**
   - Warten Sie ~10 Sekunden

3. **Projekt auswählen:**
   - Klicken Sie oben: **Projekt auswählen**
   - Wählen Sie: "Document Sorter"

### 3.2 Google Drive API aktivieren

4. **API aktivieren:**
   - Linke Seite: **APIs & Dienste** → **Bibliothek**
   - Suchen Sie: "Google Drive API"
   - Klicken Sie auf: **Google Drive API**
   - Klicken Sie: **AKTIVIEREN**
   - Warten Sie ~5 Sekunden

### 3.3 OAuth Credentials erstellen

5. **Zu Credentials gehen:**
   - Linke Seite: **APIs & Dienste** → **Anmeldedaten**

6. **OAuth-Zustimmungsbildschirm konfigurieren:**
   - Klicken Sie: **OAuth-Zustimmungsbildschirm**
   - User Type: **Extern** (auswählen)
   - Klicken Sie: **ERSTELLEN**

   **App-Informationen:**
   - App-Name: "Document Sorter"
   - Nutzer-Support-E-Mail: Ihre Email
   - Entwickler-Kontaktdaten: Ihre Email
   - Klicken Sie: **SPEICHERN UND FORTFAHREN**

   **Scopes:**
   - Klicken Sie einfach: **SPEICHERN UND FORTFAHREN**

   **Testnutzer:**
   - Klicken Sie: **+ ADD USERS**
   - Ihre Google Email eingeben
   - Klicken Sie: **SPEICHERN UND FORTFAHREN**

   **Zusammenfassung:**
   - Klicken Sie: **ZURÜCK ZUM DASHBOARD**

7. **Credentials erstellen:**
   - Linke Seite: **Anmeldedaten**
   - Oben: **+ ANMELDEDATEN ERSTELLEN** → **OAuth-Client-ID**

   **Anwendungstyp:**
   - Wählen Sie: **Desktopanwendung**
   - Name: "Document Sorter Desktop"
   - Klicken Sie: **ERSTELLEN**

8. **✅ Credentials herunterladen:**
   - Popup erscheint: "OAuth-Client erstellt"
   - Klicken Sie: **JSON HERUNTERLADEN**
   - Datei wird heruntergeladen: `client_secret_xxxxx.json`
   - Umbenennen zu: `credentials.json`
   - Speichern Sie diese Datei sicher!

**✅ Geschafft! Google Cloud Setup fertig**

---

# PHASE 2: Server-Installation

## ✅ Schritt 4: Server vorbereiten (5 Minuten)

### Auf Ihrem Linux-Server:

```bash
# 1. Mit Server verbinden
ssh root@IHR-SERVER-IP

# 2. System aktualisieren
apt-get update

# 3. Docker installieren (falls noch nicht vorhanden)
curl -fsSL https://get.docker.com | sh

# 4. Docker Compose installieren
apt-get install -y docker-compose-plugin

# 5. Prüfen ob Docker läuft
docker --version
docker compose version

# Sollte zeigen:
# Docker version 24.x.x
# Docker Compose version v2.x.x
```

**✅ Docker ist installiert**

---

## ✅ Schritt 5: Repository clonen (2 Minuten)

```bash
# 1. Ins opt-Verzeichnis wechseln
cd /opt

# 2. Repository clonen
git clone https://github.com/hrshojaei/hrshojaei.git
cd hrshojaei

# 3. Branch auschecken
git checkout claude/automated-document-sorting-011H871nPNknUa8rEQDxdzr6

# 4. Prüfen
ls -la

# Sollte zeigen:
# docker-compose.yml
# Dockerfile
# DOCKER_QUICKSTART.md
# src/
# etc.
```

**✅ Repository ist da**

---

## ✅ Schritt 6: Konfiguration erstellen (5 Minuten)

### 6.1 .env Datei erstellen

```bash
# 1. .env aus Vorlage erstellen
cp .env.example .env

# 2. .env bearbeiten
nano .env
```

### 6.2 .env ausfüllen

**Suchen Sie diese Zeilen und ersetzen Sie:**

```bash
# Telegram Bot (Ihren Token von Schritt 1)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Anthropic API (Ihren Key von Schritt 2)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx

# OCR Einstellungen (so lassen!)
USE_CLOUD_VISION_OCR=false
CONVERT_IMAGES_TO_PDF=true

# Polling (so lassen!)
DOCUMENT_POLLING_INTERVAL_MINUTES=15
DOCUMENT_BASE_FOLDER_NAME=Sortierte Dokumente
```

**Speichern:**
- Drücken Sie: `Ctrl + O` (zum Speichern)
- Drücken Sie: `Enter`
- Drücken Sie: `Ctrl + X` (zum Beenden)

### 6.3 credentials.json hochladen

**Von Ihrem PC zur Server:**

```bash
# Öffnen Sie ein NEUES Terminal-Fenster auf Ihrem PC (nicht Server!)

# credentials.json zum Server kopieren
scp ~/Downloads/credentials.json root@IHR-SERVER-IP:/opt/hrshojaei/

# Zurück zum Server-Terminal
```

**Prüfen auf Server:**

```bash
ls -la credentials.json

# Sollte zeigen:
# -rw-r--r-- 1 root root 478 Jan 15 10:30 credentials.json
```

**✅ Konfiguration fertig**

---

# PHASE 3: Start & Test

## ✅ Schritt 7: Docker Container starten (3 Minuten)

```bash
# Im Verzeichnis /opt/hrshojaei

# 1. Docker starten
bash scripts/docker-start.sh

# Script wird Sie durch alles führen:
# - Docker-Check ✓
# - .env Validierung ✓
# - Image bauen (kann 5-10 Min dauern beim ersten Mal)
# - Container starten ✓
```

**Oder manuell:**

```bash
# Image bauen
docker-compose build

# Container starten
docker-compose up -d

# Status prüfen
docker-compose ps

# Sollte zeigen:
# NAME                STATE     PORTS
# document-sorter     Up        8000/tcp
```

**✅ Container läuft!**

---

## ✅ Schritt 8: Google Drive authentifizieren (3 Minuten)

**Nur beim ersten Mal nötig!**

```bash
# 1. Container stoppen
docker-compose down

# 2. Interaktiv starten für OAuth
docker-compose run --rm document-sorter \
  python3 document_sorter_main.py --mode setup

# 3. Browser öffnet sich automatisch
# → Bei Google anmelden
# → Wählen Sie Ihren Google Account
# → Klicken Sie: "Erweitert"
# → Klicken Sie: "Zu Document Sorter (unsicher) wechseln"
# → Klicken Sie: "Zulassen"
# → Klicken Sie nochmal: "Zulassen"

# 4. Browser zeigt: "The authentication flow has completed"

# 5. Zurück zum Terminal
# → Sollte zeigen: "token.json erstellt"

# 6. Normal starten
docker-compose up -d

# 7. Prüfen
ls -la token.json
# Sollte existieren!
```

**✅ Google Drive verbunden!**

---

## ✅ Schritt 9: System testen (5 Minuten)

### 9.1 Logs prüfen

```bash
# Live-Logs ansehen
docker-compose logs -f

# Sollte zeigen:
# ✅ Config erfolgreich geladen
# ✅ Document Sorter initialisiert
# ✅ Telegram Bot wird gestartet
# Polling Service gestartet

# Logs stoppen: Ctrl + C
```

### 9.2 Telegram Bot testen

**Auf Ihrem Handy/Telegram:**

1. **Bot suchen:**
   - Suchen Sie nach Ihrem Bot-Username (von Schritt 1)
   - Beispiel: `@MeinDokumentSorter_bot`

2. **Chat starten:**
   ```
   Tippen Sie: /start
   ```

3. **Bot sollte antworten:**
   ```
   🤖 Dokument-Sortier-Bot

   Willkommen! Ich helfe dir, deine gescannten Dokumente
   automatisch zu sortieren.

   📄 Sende mir einfach:
   • PDF-Dokumente
   • Fotos von Dokumenten
   • Gescannte Briefe

   Ich werde sie automatisch auf deinem Google Drive sortieren! 🗂️
   ```

**✅ Bot antwortet!**

### 9.3 Erstes Dokument sortieren

**Im Telegram:**

1. **Foto senden:**
   - Machen Sie ein Foto von einem Brief/Rechnung
   - Oder: Senden Sie ein Bild/PDF

2. **Bot antwortet:**
   ```
   ⏳ Dokument wird verarbeitet...
   ```

3. **Nach ~10-30 Sekunden:**
   ```
   ✅ Dokument verarbeitet!

   📁 Kategorie: Finanzen
   📂 Ordner: Finanzen/Rechnungen
   🔗 Auf Google Drive öffnen
   ```

4. **Google Drive prüfen:**
   - Öffnen Sie: https://drive.google.com/
   - Neuer Ordner: "Sortierte Dokumente"
   - Darin: Automatisch sortierte Dokumente!

**✅ FUNKTIONIERT!**

---

# 🎉 GESCHAFFT! System läuft

## ✅ Was jetzt funktioniert:

✅ **Telegram Bot** - Empfängt Dokumente
✅ **OCR** - Erkennt Text aus Scans
✅ **KI-Klassifizierung** - Claude sortiert intelligent
✅ **Google Drive** - Automatische Organisation
✅ **24/7 Betrieb** - Läuft im Hintergrund

---

## 📊 Tägliche Nutzung

### Dokumente sortieren

**Per Telegram:**
```
1. Telegram App öffnen
2. Ihren Bot suchen
3. Foto/PDF senden
4. Fertig! Automatisch sortiert
```

**Per Google Drive:**
```
1. Dokument in "Inbox"-Ordner hochladen
2. Warten (max. 15 Min - Polling)
3. Automatisch sortiert
```

### System verwalten

```bash
# Logs ansehen
docker-compose logs -f

# Container neustarten
docker-compose restart

# Container stoppen
docker-compose stop

# Container starten
docker-compose start

# Status prüfen
docker-compose ps
```

---

## 🔧 Troubleshooting

### Problem: Bot antwortet nicht

```bash
# Logs prüfen
docker-compose logs | grep ERROR

# Container neu starten
docker-compose restart

# Token prüfen
cat .env | grep TELEGRAM_BOT_TOKEN
```

### Problem: Google Drive Auth schlägt fehl

```bash
# token.json löschen
rm token.json

# Neu authentifizieren
docker-compose run --rm document-sorter \
  python3 document_sorter_main.py --mode setup
```

### Problem: OCR funktioniert nicht

```bash
# Container neu bauen
docker-compose build --no-cache
docker-compose up -d

# Im Container Tesseract prüfen
docker-compose exec document-sorter tesseract --version
```

### Problem: Container startet nicht

```bash
# Logs ansehen
docker-compose logs

# Docker Speicher aufräumen
docker system prune -a

# Neu bauen
docker-compose build
docker-compose up -d
```

---

## 📖 Weiterführende Dokumentation

- **Docker Guide:** [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Features:** [DOCUMENT_SORTING.md](DOCUMENT_SORTING.md)
- **Tests:** [tests/README.md](tests/README.md)
- **Migration:** Server-zu-Server mit `scripts/export-to-server2.sh`

---

## 🎯 Nächste Schritte

### Optional: Systemd Service einrichten

```bash
# Automatischer Start beim Server-Neustart
sudo nano /etc/systemd/system/document-sorter.service
```

```ini
[Unit]
Description=Document Sorter
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/hrshojaei
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

```bash
# Aktivieren
sudo systemctl daemon-reload
sudo systemctl enable document-sorter
sudo systemctl start document-sorter
```

### Optional: Backup einrichten

```bash
# Täglich um 3 Uhr
crontab -e

# Hinzufügen:
0 3 * * * cd /opt/hrshojaei && tar -czf /backup/doc-sorter-$(date +\%Y\%m\%d).tar.gz data/ logs/ .env credentials.json token.json
```

---

## 🎉 Herzlichen Glückwunsch!

Ihr automatisches Dokumenten-Management-System läuft!

**Bei Fragen:**
- Siehe Dokumentation
- GitHub Issues
- Oder fragen Sie mich! 😊
