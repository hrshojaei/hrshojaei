# 🐳 Docker Deployment Guide

Einfaches Deployment des Document Sorting Systems mit Docker.

## 🚀 Schnellstart (3 Minuten)

```bash
# 1. Repository clonen
git clone https://github.com/hrshojaei/hrshojaei.git
cd hrshojaei
git checkout claude/automated-document-sorting-011H871nPNknUa8rEQDxdzr6

# 2. .env konfigurieren
cp .env.example .env
nano .env  # API Keys einfügen

# 3. credentials.json platzieren
# (Download von Google Cloud Console)
cp ~/Downloads/credentials.json .

# 4. Docker starten
docker-compose up -d

# 5. Logs ansehen
docker-compose logs -f
```

**Das war's!** ✅ System läuft jetzt 24/7

---

## 📋 Voraussetzungen

### System
- Linux Server (Ubuntu, Debian, CentOS, etc.)
- Docker Engine 20.10+ installiert
- Docker Compose v2.0+ installiert

### Installation von Docker

#### Ubuntu/Debian
```bash
# Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose installieren
sudo apt-get update
sudo apt-get install docker-compose-plugin

# User zu docker Gruppe hinzufügen
sudo usermod -aG docker $USER
newgrp docker

# Prüfen
docker --version
docker compose version
```

#### CentOS/RHEL
```bash
sudo yum install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

---

## 🔧 Setup Schritt-für-Schritt

### 1. Repository clonen

```bash
git clone https://github.com/hrshojaei/hrshojaei.git
cd hrshojaei
git checkout claude/automated-document-sorting-011H871nPNknUa8rEQDxdzr6
```

### 2. Umgebungsvariablen konfigurieren

```bash
# .env erstellen
cp .env.example .env

# .env bearbeiten
nano .env
```

**Wichtige Variablen:**

```bash
# Telegram Bot (von @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Anthropic API (von console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# OCR Einstellungen
USE_CLOUD_VISION_OCR=false  # false = kostenlos, true = premium
CONVERT_IMAGES_TO_PDF=true

# Polling
DOCUMENT_POLLING_INTERVAL_MINUTES=15
```

### 3. Google Drive Credentials

#### 3.1 Google Cloud Console Setup

1. Gehe zu: https://console.cloud.google.com/
2. Erstelle neues Projekt: "Document Sorter"
3. Aktiviere **Google Drive API**
4. Gehe zu **Credentials** → **Create Credentials**
5. Wähle **OAuth 2.0 Client ID**
6. Application Type: **Desktop App**
7. Download `credentials.json`

#### 3.2 Credentials platzieren

```bash
# credentials.json ins Projektverzeichnis kopieren
cp ~/Downloads/credentials.json .

# Prüfen
ls -la credentials.json
```

### 4. Docker Image bauen

```bash
# Image bauen
docker-compose build

# Oder mit Cache löschen:
docker-compose build --no-cache
```

### 5. Container starten

```bash
# Im Hintergrund starten
docker-compose up -d

# Mit Logs (zum Debuggen)
docker-compose up
```

### 6. Erste Authentifizierung (nur einmal)

Beim **ersten Start** muss Google Drive authentifiziert werden:

```bash
# Container stoppen
docker-compose down

# Container interaktiv starten
docker-compose run --rm document-sorter python3 document_sorter_main.py --mode setup

# → Browser öffnet sich
# → Bei Google anmelden
# → Zugriff erlauben
# → token.json wird erstellt

# Normal starten
docker-compose up -d
```

---

## 📊 Container verwalten

### Status prüfen

```bash
# Container Status
docker-compose ps

# Logs anzeigen
docker-compose logs -f

# Nur letzte 100 Zeilen
docker-compose logs --tail=100 -f
```

### Stoppen & Starten

```bash
# Container stoppen
docker-compose stop

# Container starten
docker-compose start

# Container neustarten
docker-compose restart

# Container stoppen und löschen
docker-compose down
```

### Updates einspielen

```bash
# Code aktualisieren
git pull origin claude/automated-document-sorting-011H871nPNknUa8rEQDxdzr6

# Image neu bauen
docker-compose build

# Container neu starten
docker-compose up -d

# Alte Images löschen
docker image prune -f
```

---

## 🔍 Debugging

### Logs ansehen

```bash
# Live Logs
docker-compose logs -f

# Logs in Datei speichern
docker-compose logs > debug.log

# Nur Fehler
docker-compose logs | grep ERROR
```

### In Container einsteigen

```bash
# Shell im laufenden Container
docker-compose exec document-sorter bash

# Python-Shell
docker-compose exec document-sorter python3

# Test ausführen
docker-compose exec document-sorter python3 tests/test_step1_config.py
```

### Container-Zustand prüfen

```bash
# Prozesse im Container
docker-compose top

# Resource-Nutzung
docker stats

# Container-Details
docker inspect document-sorter
```

---

## 📁 Datenpersistenz

### Wichtige Volumes

```
./logs          → /app/logs          # Logs
./data          → /app/data          # Datenbank
./credentials.json → /app/credentials.json  # Google OAuth
./token.json    → /app/token.json    # Google Token
./temp          → /app/temp          # Temp-Dateien
```

### Backup erstellen

```bash
# Alle wichtigen Daten sichern
tar -czf backup-$(date +%Y%m%d).tar.gz \
    logs/ \
    data/ \
    credentials.json \
    token.json \
    .env

# Auf anderen Server kopieren
scp backup-*.tar.gz user@backup-server:/backups/
```

### Restore

```bash
# Backup entpacken
tar -xzf backup-20240115.tar.gz

# Container neu starten
docker-compose up -d
```

---

## ⚙️ Erweiterte Konfiguration

### Resource Limits anpassen

In `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Max 4 CPU-Kerne
      memory: 4G       # Max 4GB RAM
    reservations:
      cpus: '1.0'      # Min 1 CPU-Kern
      memory: 1G       # Min 1GB RAM
```

### Mehrere Modi laufen lassen

#### Polling-Only (kein Telegram)

```yaml
# docker-compose.override.yml erstellen
services:
  document-sorter:
    command: python3 document_sorter_main.py --mode polling
    environment:
      - TELEGRAM_BOT_TOKEN=
```

#### Einmal pro Tag (Cron-Job)

```bash
# Crontab bearbeiten
crontab -e

# Hinzufügen (täglich um 2 Uhr nachts)
0 2 * * * cd /opt/hrshojaei && docker-compose run --rm document-sorter python3 document_sorter_main.py --mode once
```

---

## 🔒 Sicherheit

### Firewall konfigurieren

```bash
# Nur SSH erlauben (Port 22)
sudo ufw allow 22/tcp
sudo ufw enable

# Kein Port-Forwarding nötig (Bot nutzt Webhook/Polling)
```

### Secrets Management

```bash
# .env Berechtigungen
chmod 600 .env

# credentials.json Berechtigungen
chmod 600 credentials.json

# Nie committen!
git status  # Prüfen ob in .gitignore
```

### Auto-Updates (optional)

```bash
# Watchtower installieren (Auto-Update Container)
docker run -d \
    --name watchtower \
    -v /var/run/docker.sock:/var/run/docker.sock \
    containrrr/watchtower \
    --interval 86400  # Täglich prüfen
```

---

## 🌐 Production Deployment

### Systemd Service erstellen

```bash
# Service-Datei erstellen
sudo nano /etc/systemd/system/document-sorter.service
```

```ini
[Unit]
Description=Document Sorter Docker Container
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/hrshojaei
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren
sudo systemctl daemon-reload
sudo systemctl enable document-sorter.service
sudo systemctl start document-sorter.service

# Status prüfen
sudo systemctl status document-sorter.service
```

### Monitoring

```bash
# Prometheus Exporter hinzufügen (optional)
docker run -d \
  -p 9323:9323 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  prometheusio/node-exporter
```

---

## 🔧 Troubleshooting

### Problem: Container startet nicht

```bash
# Logs prüfen
docker-compose logs

# Build-Logs
docker-compose build --no-cache

# Container Status
docker-compose ps -a
```

### Problem: API Keys nicht erkannt

```bash
# .env im Container prüfen
docker-compose exec document-sorter env | grep API

# .env neu laden
docker-compose down
docker-compose up -d
```

### Problem: Google Drive Auth schlägt fehl

```bash
# Interaktiv authentifizieren
docker-compose run --rm document-sorter \
  python3 document_sorter_main.py --mode setup

# token.json löschen und neu
rm token.json
docker-compose run --rm document-sorter \
  python3 document_sorter_main.py --mode setup
```

### Problem: Tesseract findet deutsche Sprache nicht

```bash
# Im Container prüfen
docker-compose exec document-sorter tesseract --list-langs

# Sollte zeigen: deu, eng

# Falls nicht, Image neu bauen
docker-compose build --no-cache
```

---

## 📊 Performance-Tipps

1. **SSD verwenden** für Docker-Volumes
2. **RAM**: Mindestens 2GB reservieren
3. **CPU**: 2+ Kerne empfohlen
4. **Logs rotieren**: Max 10MB pro Datei

```yaml
# In docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "5"
```

---

## 🎯 Nächste Schritte

Nach erfolgreichem Deployment:

1. **Telegram Bot testen:**
   - Bot suchen
   - `/start` senden
   - Dokument hochladen

2. **Google Drive prüfen:**
   - "Sortierte Dokumente" Ordner
   - Automatische Kategorisierung

3. **Monitoring einrichten:**
   - Logs regelmäßig prüfen
   - Disk Space überwachen

---

## 📞 Support

Bei Problemen:
1. Logs prüfen: `docker-compose logs -f`
2. Tests ausführen: `docker-compose exec document-sorter python3 tests/test_step1_config.py`
3. GitHub Issues: https://github.com/hrshojaei/hrshojaei/issues

---

**🎉 Viel Erfolg mit Ihrem automatisierten Dokumenten-Management!**
