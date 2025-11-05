# Production Deployment Guide

Dieses Dokument beschreibt, wie du den AI Calling Agent für den produktiven Einsatz auf einem Server deployed.

## Übersicht

Für den produktiven Betrieb benötigst du:
- **VPS/Server** mit Ubuntu/Debian (empfohlen: Hetzner, DigitalOcean, AWS)
- **Domain** für die Webhook-URLs
- **SSL-Zertifikat** (Let's Encrypt)
- **PostgreSQL** (optional, für bessere Performance als SQLite)
- **Monitoring** und Logging

## 1. Server Setup

### VPS auswählen

**Empfohlene Anbieter:**
- **Hetzner Cloud**: CX21 (~€5/Monat, 2 vCPU, 4 GB RAM)
- **DigitalOcean**: Basic Droplet ($12/Monat, 2 vCPU, 2 GB RAM)
- **AWS EC2**: t3.small (~$15/Monat, 2 vCPU, 2 GB RAM)

**Mindestanforderungen:**
- 2 vCPU
- 2 GB RAM
- 20 GB SSD
- Ubuntu 22.04 LTS

### Server einrichten

```bash
# SSH zum Server
ssh root@your-server-ip

# System aktualisieren
apt update && apt upgrade -y

# Firewall konfigurieren
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable

# Benutzer erstellen
adduser callingagent
usermod -aG sudo callingagent

# Als neuer Benutzer anmelden
su - callingagent
```

## 2. Dependencies installieren

```bash
# Python 3.10+
sudo apt install -y python3 python3-pip python3-venv

# Nginx (Reverse Proxy)
sudo apt install -y nginx

# Certbot (für SSL)
sudo apt install -y certbot python3-certbot-nginx

# Optional: PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Git
sudo apt install -y git

# Supervisor (Process Manager)
sudo apt install -y supervisor
```

## 3. Projekt deployen

### Code hochladen

**Option A - Git Clone:**
```bash
cd /opt
sudo mkdir calling-agent
sudo chown callingagent:callingagent calling-agent
cd calling-agent

git clone https://github.com/your-username/calling-agent.git .
```

**Option B - SCP Upload:**
```bash
# Lokal ausführen
scp -r /path/to/calling-agent callingagent@your-server-ip:/opt/calling-agent
```

### Virtual Environment einrichten

```bash
cd /opt/calling-agent

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### .env konfigurieren

```bash
cp .env.example .env
nano .env
```

Setze in der .env:
```env
# Deine Domain
PUBLIC_URL=https://calling-agent.deine-firma.de

# Produktions-Credentials
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+49...

AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Optional: PostgreSQL statt SQLite
# DATABASE_URL=postgresql://user:password@localhost/calling_agent

LOG_LEVEL=INFO
LOG_TO_FILE=true
```

### Datenbank initialisieren

```bash
python -m src.candidate_manager init
```

## 4. Domain & SSL einrichten

### Domain konfigurieren

Erstelle einen A-Record bei deinem DNS-Provider:
```
calling-agent.deine-firma.de  →  your-server-ip
```

Warte, bis DNS propagiert ist (max. 24h, meist viel schneller):
```bash
nslookup calling-agent.deine-firma.de
```

### Nginx konfigurieren

```bash
sudo nano /etc/nginx/sites-available/calling-agent
```

Inhalt:
```nginx
server {
    listen 80;
    server_name calling-agent.deine-firma.de;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts für lange Webhooks
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/;
    }
}
```

Aktivieren:
```bash
sudo ln -s /etc/nginx/sites-available/calling-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL-Zertifikat installieren

```bash
sudo certbot --nginx -d calling-agent.deine-firma.de

# Automatische Erneuerung testen
sudo certbot renew --dry-run
```

## 5. Systemd Service einrichten

```bash
sudo nano /etc/systemd/system/calling-agent.service
```

Inhalt:
```ini
[Unit]
Description=AI Calling Agent Service
After=network.target

[Service]
Type=simple
User=callingagent
Group=callingagent
WorkingDirectory=/opt/calling-agent
Environment="PATH=/opt/calling-agent/venv/bin"
ExecStart=/opt/calling-agent/venv/bin/python -m src.main server
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/opt/calling-agent/logs/service.log
StandardError=append:/opt/calling-agent/logs/service-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/calling-agent/data /opt/calling-agent/logs

[Install]
WantedBy=multi-user.target
```

Service aktivieren und starten:
```bash
sudo systemctl daemon-reload
sudo systemctl enable calling-agent
sudo systemctl start calling-agent

# Status prüfen
sudo systemctl status calling-agent
```

## 6. Optional: PostgreSQL einrichten

### PostgreSQL konfigurieren

```bash
sudo -u postgres psql

# In PostgreSQL:
CREATE DATABASE calling_agent;
CREATE USER calling_agent WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE calling_agent TO calling_agent;
\q
```

### Schema migrieren

```bash
# Install psycopg2 für PostgreSQL
source /opt/calling-agent/venv/bin/activate
pip install psycopg2-binary

# .env anpassen
nano /opt/calling-agent/.env
# Setze: DATABASE_URL=postgresql://calling_agent:your_secure_password@localhost/calling_agent

# Migration (Schema neu erstellen)
python -m src.candidate_manager init
```

## 7. Monitoring & Logging

### Logrotate einrichten

```bash
sudo nano /etc/logrotate.d/calling-agent
```

Inhalt:
```
/opt/calling-agent/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0644 callingagent callingagent
}
```

### Logs ansehen

```bash
# Service logs
sudo journalctl -u calling-agent -f

# Application logs
tail -f /opt/calling-agent/logs/calling_agent_*.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Health Monitoring

Erstelle ein Monitoring-Script:

```bash
nano /opt/calling-agent/scripts/health_check.sh
```

Inhalt:
```bash
#!/bin/bash
HEALTH_URL="https://calling-agent.deine-firma.de/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ "$RESPONSE" != "200" ]; then
    echo "❌ Service DOWN (HTTP $RESPONSE)"
    # Optional: Send alert email
    # echo "Service is down" | mail -s "Calling Agent Alert" admin@deine-firma.de
    exit 1
else
    echo "✅ Service UP"
    exit 0
fi
```

Mache es ausführbar und füge zu Cron hinzu:
```bash
chmod +x /opt/calling-agent/scripts/health_check.sh

crontab -e
# Füge hinzu (prüft alle 5 Minuten):
*/5 * * * * /opt/calling-agent/scripts/health_check.sh >> /opt/calling-agent/logs/health.log 2>&1
```

## 8. Backup einrichten

### Backup-Script

```bash
nano /opt/calling-agent/scripts/backup.sh
```

Inhalt:
```bash
#!/bin/bash
BACKUP_DIR="/opt/calling-agent/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /opt/calling-agent/data/candidates.db $BACKUP_DIR/candidates_$DATE.db

# Optional: PostgreSQL backup
# pg_dump calling_agent > $BACKUP_DIR/calling_agent_$DATE.sql

# Backup .env
cp /opt/calling-agent/.env $BACKUP_DIR/env_$DATE

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "✅ Backup completed: $DATE"
```

Täglich ausführen:
```bash
chmod +x /opt/calling-agent/scripts/backup.sh

crontab -e
# Füge hinzu (täglich um 3 Uhr):
0 3 * * * /opt/calling-agent/scripts/backup.sh >> /opt/calling-agent/logs/backup.log 2>&1
```

## 9. Security Hardening

### Fail2ban einrichten

```bash
sudo apt install -y fail2ban

sudo nano /etc/fail2ban/jail.local
```

Inhalt:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
```

```bash
sudo systemctl restart fail2ban
```

### SSH härten

```bash
sudo nano /etc/ssh/sshd_config
```

Änderungen:
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

```bash
sudo systemctl restart sshd
```

### Firewall überprüfen

```bash
sudo ufw status
```

Sollte nur SSH, HTTP, HTTPS erlauben.

## 10. Updates & Wartung

### Code aktualisieren

```bash
cd /opt/calling-agent

# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart calling-agent
```

### System-Updates

```bash
# Einmal pro Woche
sudo apt update && sudo apt upgrade -y
sudo systemctl restart calling-agent
```

## 11. Skalierung

### Mehrere Worker

Für höhere Last, verwende Gunicorn statt Uvicorn:

```bash
pip install gunicorn
```

Service anpassen:
```ini
ExecStart=/opt/calling-agent/venv/bin/gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 600
```

### Load Balancing

Für sehr hohe Last, nutze mehrere Server hinter einem Load Balancer.

## 12. Kostenoptimierung

### Twilio
- Nutze Twilio Elastic SIP Trunking für günstigere Minutenpreise bei hohem Volumen
- Kaufe Telefonnummern nur in benötigten Regionen

### AI Costs
- Claude ist günstiger als GPT-4 (~10x)
- Setze `max_tokens` niedrig (300-500) für kürzere Antworten
- Cache häufig verwendete Prompts

### Server
- Hetzner ist günstiger als AWS/DigitalOcean
- Nutze Reserved Instances bei Cloud-Providern für Rabatte

## Troubleshooting

### Service startet nicht
```bash
sudo journalctl -u calling-agent -n 100
```

### Webhooks kommen nicht an
```bash
# Prüfe Nginx
sudo nginx -t
tail -f /var/log/nginx/error.log

# Prüfe Firewall
sudo ufw status

# Teste URL direkt
curl https://calling-agent.deine-firma.de/
```

### Datenbankfehler
```bash
# SQLite Permissions
sudo chown -R callingagent:callingagent /opt/calling-agent/data

# PostgreSQL Connection
psql -U calling_agent -h localhost calling_agent
```

## Support & Monitoring Tools

- **Uptime Monitoring**: UptimeRobot (kostenlos)
- **Log Management**: Papertrail, Loggly
- **Error Tracking**: Sentry
- **APM**: New Relic, Datadog

## Checkliste vor Go-Live

- [ ] Domain konfiguriert und DNS propagiert
- [ ] SSL-Zertifikat installiert
- [ ] .env mit Produktions-Credentials
- [ ] Service läuft und startet automatisch
- [ ] Nginx Reverse Proxy funktioniert
- [ ] Test-Anruf erfolgreich
- [ ] Logs werden geschrieben
- [ ] Backups konfiguriert
- [ ] Health Monitoring aktiv
- [ ] Firewall konfiguriert
- [ ] SSH gehärtet
- [ ] Rechtliche Aspekte geklärt (DSGVO, Aufzeichnungen, etc.)

Viel Erfolg mit dem Deployment! 🚀
