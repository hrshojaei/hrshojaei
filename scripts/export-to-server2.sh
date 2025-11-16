#!/bin/bash
# Export Docker Container und Daten für Server 2
# Ausführen auf SERVER 1

set -e

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════╗
║  Export zu Server 2                       ║
╚═══════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Prüfe ob Docker läuft
if ! docker info &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker läuft nicht oder keine Berechtigung${NC}"
    exit 1
fi

# Export-Verzeichnis erstellen
EXPORT_DIR="/tmp/document-sorter-export"
mkdir -p "$EXPORT_DIR"

echo ""
echo -e "${BLUE}📦 Schritt 1: Docker Image exportieren...${NC}"

# Prüfe ob Image existiert
if ! docker image inspect document-sorter:latest &> /dev/null; then
    echo -e "${YELLOW}⚠️  Image 'document-sorter:latest' nicht gefunden${NC}"
    echo "Baue Image..."
    docker-compose build
fi

# Image exportieren
docker save document-sorter:latest | gzip > "$EXPORT_DIR/document-sorter-image.tar.gz"
echo -e "${GREEN}✅ Docker Image exportiert: $(du -h $EXPORT_DIR/document-sorter-image.tar.gz | cut -f1)${NC}"

echo ""
echo -e "${BLUE}📁 Schritt 2: Daten und Konfiguration packen...${NC}"

# Container stoppen (optional)
read -p "Container stoppen für konsistentes Backup? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stoppe Container..."
    docker-compose stop
    RESTART_NEEDED=true
fi

# Daten packen
cd "$(dirname "$0")/.."  # Zum Projekt-Root
tar -czf "$EXPORT_DIR/document-sorter-data.tar.gz" \
    --exclude='*.log' \
    --exclude='temp/*' \
    .env \
    credentials.json \
    token.json \
    data/ \
    docker-compose.yml \
    Dockerfile \
    src/ \
    document_sorter_main.py \
    scripts/ \
    2>/dev/null || true

echo -e "${GREEN}✅ Daten gepackt: $(du -h $EXPORT_DIR/document-sorter-data.tar.gz | cut -f1)${NC}"

# Container wieder starten
if [ "$RESTART_NEEDED" = true ]; then
    echo "Starte Container wieder..."
    docker-compose start
fi

echo ""
echo -e "${BLUE}📋 Schritt 3: Installations-Script erstellen...${NC}"

# Import-Script für Server 2 erstellen
cat > "$EXPORT_DIR/import-on-server2.sh" << 'IMPORT_SCRIPT'
#!/bin/bash
# Import-Script für Server 2
# Dieses Script auf Server 2 ausführen

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Importiere Document Sorter auf Server 2...${NC}"

# Zielverzeichnis
TARGET_DIR="/opt/hrshojaei"
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# Docker Image importieren
echo ""
echo -e "${BLUE}1. Importiere Docker Image...${NC}"
if [ -f "/tmp/document-sorter-export/document-sorter-image.tar.gz" ]; then
    docker load < /tmp/document-sorter-export/document-sorter-image.tar.gz
    echo -e "${GREEN}✅ Image importiert${NC}"
else
    echo "Fehler: Image nicht gefunden in /tmp/document-sorter-export/"
    exit 1
fi

# Daten entpacken
echo ""
echo -e "${BLUE}2. Entpacke Daten und Konfiguration...${NC}"
tar -xzf /tmp/document-sorter-export/document-sorter-data.tar.gz
echo -e "${GREEN}✅ Daten entpackt${NC}"

# Container starten
echo ""
echo -e "${BLUE}3. Starte Container...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ Container gestartet${NC}"

# Status
echo ""
echo -e "${BLUE}4. Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Import erfolgreich abgeschlossen!     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo "Logs ansehen:  docker-compose logs -f"
echo "Status prüfen: docker-compose ps"
echo ""
IMPORT_SCRIPT

chmod +x "$EXPORT_DIR/import-on-server2.sh"
echo -e "${GREEN}✅ Import-Script erstellt${NC}"

# Zusammenfassung
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════╗
║  ✅ Export abgeschlossen!                 ║
╚═══════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo "📦 Export-Dateien:"
echo "   $EXPORT_DIR/document-sorter-image.tar.gz"
echo "   $EXPORT_DIR/document-sorter-data.tar.gz"
echo "   $EXPORT_DIR/import-on-server2.sh"
echo ""
echo "📊 Größen:"
du -h "$EXPORT_DIR"/* | sed 's|^|   |'
TOTAL_SIZE=$(du -sh "$EXPORT_DIR" | cut -f1)
echo "   Total: $TOTAL_SIZE"
echo ""
echo "📤 Nächste Schritte:"
echo ""
echo "1. Zu Server 2 kopieren:"
echo "   scp -r $EXPORT_DIR user@server2:/tmp/"
echo ""
echo "2. Auf Server 2 ausführen:"
echo "   ssh user@server2"
echo "   bash /tmp/document-sorter-export/import-on-server2.sh"
echo ""
echo "3. Aufräumen (Server 1):"
echo "   rm -rf $EXPORT_DIR"
echo ""
