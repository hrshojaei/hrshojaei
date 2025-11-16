#!/bin/bash
# Quick-Start Script für Docker Deployment

set -e

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════╗
║  Document Sorter - Docker Quick Start    ║
╚═══════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Funktion: Erfolgsmeldung
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Funktion: Warnung
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Funktion: Fehler
error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Funktion: Info
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Prüfe Docker
echo ""
info "Prüfe Docker Installation..."
if ! command -v docker &> /dev/null; then
    error "Docker ist nicht installiert!"
fi

if ! docker info &> /dev/null; then
    error "Docker läuft nicht oder Sie haben keine Berechtigung. Führen Sie aus: sudo usermod -aG docker $USER"
fi

success "Docker gefunden: $(docker --version)"

# Prüfe docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    error "docker-compose ist nicht installiert!"
fi

if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

success "Docker Compose gefunden"

# Prüfe .env
echo ""
info "Prüfe Konfiguration..."
if [ ! -f ".env" ]; then
    warning ".env fehlt - erstelle aus .env.example"
    cp .env.example .env
    warning "Bitte bearbeiten Sie .env und fügen Sie Ihre API Keys hinzu!"
    warning "Danach führen Sie dieses Script erneut aus."
    exit 0
fi

success ".env gefunden"

# Prüfe wichtige Variablen
if grep -q "your_telegram_bot_token" .env; then
    warning "TELEGRAM_BOT_TOKEN noch nicht gesetzt in .env"
    MISSING_CONFIG=true
fi

if grep -q "your_anthropic_api_key" .env; then
    warning "ANTHROPIC_API_KEY noch nicht gesetzt in .env"
    MISSING_CONFIG=true
fi

if [ "$MISSING_CONFIG" = true ]; then
    echo ""
    warning "Bitte konfigurieren Sie .env und führen Sie Script erneut aus:"
    echo ""
    echo "  nano .env"
    echo ""
    echo "Benötigte Keys:"
    echo "  - TELEGRAM_BOT_TOKEN (von @BotFather)"
    echo "  - ANTHROPIC_API_KEY (von console.anthropic.com)"
    exit 0
fi

# Prüfe credentials.json
if [ ! -f "credentials.json" ]; then
    warning "credentials.json fehlt!"
    echo ""
    echo "So erhalten Sie credentials.json:"
    echo "1. Gehe zu: https://console.cloud.google.com/"
    echo "2. Erstelle Projekt und aktiviere Google Drive API"
    echo "3. Erstelle OAuth 2.0 Credentials (Desktop App)"
    echo "4. Download credentials.json"
    echo "5. Kopiere nach $(pwd)/credentials.json"
    echo ""
    read -p "Fahren Sie trotzdem fort? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    success "credentials.json gefunden"
fi

# Verzeichnisse erstellen
echo ""
info "Erstelle Verzeichnisse..."
mkdir -p logs data temp
success "Verzeichnisse erstellt"

# Docker Image bauen
echo ""
info "Baue Docker Image..."
echo ""
if $COMPOSE_CMD build; then
    success "Docker Image erfolgreich gebaut"
else
    error "Fehler beim Bauen des Docker Images"
fi

# Frage ob Google Drive Auth nötig ist
echo ""
if [ ! -f "token.json" ]; then
    warning "token.json nicht gefunden - Google Drive Authentifizierung erforderlich"
    echo ""
    read -p "Möchten Sie jetzt Google Drive authentifizieren? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Starte interaktive Authentifizierung..."
        echo ""
        $COMPOSE_CMD run --rm document-sorter \
            python3 document_sorter_main.py --mode setup

        if [ -f "token.json" ]; then
            success "Google Drive erfolgreich authentifiziert!"
        else
            warning "Authentifizierung möglicherweise fehlgeschlagen"
        fi
    fi
fi

# Container starten
echo ""
info "Starte Container..."
echo ""
if $COMPOSE_CMD up -d; then
    success "Container erfolgreich gestartet!"
else
    error "Fehler beim Starten des Containers"
fi

# Status prüfen
sleep 2
echo ""
info "Container Status:"
$COMPOSE_CMD ps

# Zusammenfassung
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════╗
║         ✅ DEPLOYMENT ERFOLGREICH!        ║
╚═══════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo "📊 Nützliche Befehle:"
echo ""
echo "  Logs ansehen:     $COMPOSE_CMD logs -f"
echo "  Container stoppen: $COMPOSE_CMD stop"
echo "  Container starten: $COMPOSE_CMD start"
echo "  Status prüfen:    $COMPOSE_CMD ps"
echo "  In Container:     $COMPOSE_CMD exec document-sorter bash"
echo ""
echo "📖 Dokumentation:"
echo "  - Docker Guide:   DOCKER_DEPLOYMENT.md"
echo "  - Quick-Start:    DOCKER_QUICKSTART.md"
echo "  - Benutzerhandbuch: DOCUMENT_SORTING.md"
echo ""
echo "🎯 Nächste Schritte:"
echo "  1. Logs prüfen: $COMPOSE_CMD logs -f"
echo "  2. Telegram Bot testen"
echo "  3. Dokument hochladen"
echo "  4. Google Drive prüfen"
echo ""
success "System läuft jetzt 24/7!"
