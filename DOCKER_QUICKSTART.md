# 🚀 Docker Quick-Start (5 Minuten)

Die **schnellste** Methode, um das Document Sorting System zu deployen.

## ✅ Was Sie brauchen

- Linux Server (oder Mac/Windows mit Docker Desktop)
- Docker installiert
- 5 Minuten Zeit

## 📦 Quick-Start

### 1️⃣ Docker installieren (falls noch nicht vorhanden)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Prüfen
docker --version
```

### 2️⃣ Repository clonen

```bash
git clone https://github.com/hrshojaei/hrshojaei.git
cd hrshojaei
git checkout claude/automated-document-sorting-011H871nPNknUa8rEQDxdzr6
```

### 3️⃣ Konfiguration

```bash
# .env erstellen
cp .env.example .env

# API Keys einfügen
nano .env
```

**Fügen Sie hinzu:**
```bash
TELEGRAM_BOT_TOKEN=IHR_BOT_TOKEN_VON_@BOTFATHER
ANTHROPIC_API_KEY=sk-ant-IHR_KEY_VON_CONSOLE_ANTHROPIC_COM
```

### 4️⃣ Google Drive Credentials

```bash
# credentials.json ins Verzeichnis kopieren
# (Download von https://console.cloud.google.com/)
cp ~/Downloads/credentials.json .
```

### 5️⃣ Starten!

```bash
# Alles auf einmal bauen und starten
docker-compose up -d

# Logs ansehen
docker-compose logs -f
```

### 6️⃣ Google Drive authentifizieren (nur beim ersten Mal)

```bash
# Container stoppen
docker-compose down

# Interaktiv starten für Google OAuth
docker-compose run --rm document-sorter \
  python3 document_sorter_main.py --mode setup

# Browser öffnet sich → Bei Google anmelden → Zugriff erlauben

# Normal starten
docker-compose up -d
```

---

## ✅ Das war's!

Ihr System läuft jetzt 24/7 und:
- ✅ Empfängt Dokumente per Telegram
- ✅ Erkennt Text via OCR
- ✅ Klassifiziert mit Claude AI
- ✅ Sortiert automatisch auf Google Drive

---

## 🧪 System testen

```bash
# 1. Telegram Bot finden
# Suche nach Ihrem Bot-Namen in Telegram

# 2. Bot starten
/start

# 3. Dokument senden
# Sende ein Foto oder PDF

# 4. Google Drive prüfen
# Ordner "Sortierte Dokumente" sollte erstellt sein
```

---

## 📊 Verwaltung

### Logs ansehen
```bash
docker-compose logs -f
```

### Stoppen
```bash
docker-compose stop
```

### Starten
```bash
docker-compose start
```

### Neustarten
```bash
docker-compose restart
```

### Updates installieren
```bash
git pull
docker-compose build
docker-compose up -d
```

---

## 🔧 Probleme?

### Container startet nicht
```bash
# Logs prüfen
docker-compose logs

# Neu bauen
docker-compose build --no-cache
docker-compose up -d
```

### API Keys werden nicht erkannt
```bash
# Container neu starten
docker-compose down
docker-compose up -d

# Umgebungsvariablen prüfen
docker-compose exec document-sorter env | grep API
```

### Google Drive funktioniert nicht
```bash
# token.json löschen und neu authentifizieren
rm token.json
docker-compose run --rm document-sorter \
  python3 document_sorter_main.py --mode setup
```

---

## 📖 Mehr Infos

- **Vollständige Anleitung:** [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Benutzerhandbuch:** [DOCUMENT_SORTING.md](DOCUMENT_SORTING.md)
- **Tests:** `tests/README.md`

---

## 💡 Tipps

**Autostart beim Server-Neustart:**
```bash
# Container wird automatisch neu gestartet
# (bereits konfiguriert in docker-compose.yml)
# restart: unless-stopped
```

**Backup erstellen:**
```bash
tar -czf backup.tar.gz logs/ data/ credentials.json token.json .env
```

**Resource-Nutzung prüfen:**
```bash
docker stats
```

---

**🎉 Fertig! Viel Spaß mit automatischer Dokumentensortierung!**
