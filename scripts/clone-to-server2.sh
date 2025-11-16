#!/bin/bash
# Alternative: Einfaches Git-Clone Setup für Server 2
# Kopiert nur Konfiguration, Docker Image wird auf Server 2 neu gebaut

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════╗
║  Setup für Server 2 (Git Clone Methode)  ║
╚═══════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Export-Verzeichnis
EXPORT_DIR="/tmp/document-sorter-config"
mkdir -p "$EXPORT_DIR"

echo ""
echo -e "${BLUE}📁 Kopiere Konfiguration und Credentials...${NC}"

# Nur wichtige Dateien kopieren
cd "$(dirname "$0")/.."

# Container stoppen für konsistente Daten
read -p "Container stoppen für Backup? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose stop
    RESTART_NEEDED=true
fi

# Kopiere Konfig-Dateien
cp .env "$EXPORT_DIR/" 2>/dev/null || echo "⚠️  .env nicht gefunden"
cp credentials.json "$EXPORT_DIR/" 2>/dev/null || echo "⚠️  credentials.json nicht gefunden"
cp token.json "$EXPORT_DIR/" 2>/dev/null || echo "⚠️  token.json nicht gefunden"

# Optional: Datenbank kopieren
if [ -d "data" ]; then
    tar -czf "$EXPORT_DIR/data-backup.tar.gz" data/
    echo -e "${GREEN}✅ Datenbank gebackupt${NC}"
fi

# Container wieder starten
if [ "$RESTART_NEEDED" = true ]; then
    docker-compose start
fi

# Setup-Script für Server 2
cat > "$EXPORT_DIR/setup-server2.sh" << 'SETUP_SCRIPT'
#!/bin/bash
# Setup-Script für Server 2 (nach Git Clone)

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setup auf Server 2...${NC}"

# Prüfe ob im richtigen Verzeichnis
if [ ! -f "docker-compose.yml" ]; then
    echo "Fehler: Führe dieses Script im hrshojaei-Verzeichnis aus!"
    exit 1
fi

# Konfiguration kopieren
echo ""
echo -e "${BLUE}1. Kopiere Konfiguration...${NC}"
if [ -f "/tmp/document-sorter-config/.env" ]; then
    cp /tmp/document-sorter-config/.env .
    echo -e "${GREEN}✅ .env kopiert${NC}"
fi

if [ -f "/tmp/document-sorter-config/credentials.json" ]; then
    cp /tmp/document-sorter-config/credentials.json .
    echo -e "${GREEN}✅ credentials.json kopiert${NC}"
fi

if [ -f "/tmp/document-sorter-config/token.json" ]; then
    cp /tmp/document-sorter-config/token.json .
    echo -e "${GREEN}✅ token.json kopiert${NC}"
fi

# Datenbank wiederherstellen
if [ -f "/tmp/document-sorter-config/data-backup.tar.gz" ]; then
    tar -xzf /tmp/document-sorter-config/data-backup.tar.gz
    echo -e "${GREEN}✅ Datenbank wiederhergestellt${NC}"
fi

# Docker starten
echo ""
echo -e "${BLUE}2. Starte Docker Container...${NC}"
bash scripts/docker-start.sh

echo ""
echo -e "${GREEN}✅ Setup abgeschlossen!${NC}"
SETUP_SCRIPT

chmod +x "$EXPORT_DIR/setup-server2.sh"

echo -e "${GREEN}✅ Konfiguration exportiert${NC}"

# Zusammenfassung
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════╗
║  ✅ Bereit für Server 2!                  ║
╚═══════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo "📦 Exportierte Dateien in: $EXPORT_DIR/"
ls -lh "$EXPORT_DIR/" | tail -n +2 | sed 's|^|   |'
echo ""
echo "📤 Nächste Schritte:"
echo ""
echo "1. Konfiguration zu Server 2 kopieren:"
echo "   scp -r $EXPORT_DIR user@server2:/tmp/"
echo ""
echo "2. Auf Server 2 Repository clonen:"
echo "   ssh user@server2"
echo "   git clone https://github.com/hrshojaei/hrshojaei.git"
echo "   cd hrshojaei"
echo "   git checkout claude/automated-document-sorting-011H871nPNknUa8rEQDxdzr6"
echo ""
echo "3. Setup ausführen:"
echo "   bash /tmp/document-sorter-config/setup-server2.sh"
echo ""
