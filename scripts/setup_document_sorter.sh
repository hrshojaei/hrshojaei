#!/bin/bash
# Setup Script für Document Sorter System

set -e

echo "🚀 Document Sorter Setup"
echo "========================"
echo ""

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# 1. Prüfe Python Version
echo "📋 Prüfe Python Version..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 ist nicht installiert!"
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
success "Python $PYTHON_VERSION gefunden"

# 2. Prüfe Tesseract
echo ""
echo "🔍 Prüfe Tesseract OCR..."
if ! command -v tesseract &> /dev/null; then
    warning "Tesseract OCR nicht gefunden!"
    echo ""
    echo "Installation:"
    echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-deu poppler-utils"
    echo "  macOS: brew install tesseract tesseract-lang poppler"
    echo "  Windows: https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
    read -p "Trotzdem fortfahren? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    TESSERACT_VERSION=$(tesseract --version | head -n1)
    success "$TESSERACT_VERSION gefunden"
fi

# 3. Virtual Environment erstellen
echo ""
echo "📦 Erstelle Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "Virtual Environment erstellt"
else
    warning "Virtual Environment existiert bereits"
fi

# 4. Aktiviere Virtual Environment
echo ""
echo "🔌 Aktiviere Virtual Environment..."
source venv/bin/activate
success "Virtual Environment aktiviert"

# 5. Installiere Dependencies
echo ""
echo "📥 Installiere Python Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
success "Dependencies installiert"

# 6. Erstelle .env Datei
echo ""
echo "⚙️  Konfiguriere Umgebungsvariablen..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    success ".env Datei erstellt"
    warning "Bitte bearbeite .env und füge deine API Keys hinzu!"
else
    warning ".env existiert bereits - wird nicht überschrieben"
fi

# 7. Prüfe credentials.json
echo ""
echo "🔑 Prüfe Google Drive Credentials..."
if [ ! -f "credentials.json" ]; then
    warning "credentials.json nicht gefunden!"
    echo ""
    echo "So erhältst du credentials.json:"
    echo "1. Gehe zu: https://console.cloud.google.com/"
    echo "2. Erstelle ein Projekt"
    echo "3. Aktiviere Google Drive API"
    echo "4. Erstelle OAuth 2.0 Credentials (Desktop App)"
    echo "5. Lade credentials.json herunter"
    echo "6. Speichere im Projektverzeichnis"
    echo ""
else
    success "credentials.json gefunden"
fi

# 8. Erstelle temp und logs Verzeichnisse
echo ""
echo "📁 Erstelle Verzeichnisse..."
mkdir -p temp
mkdir -p logs
mkdir -p data
success "Verzeichnisse erstellt"

# 9. Zusammenfassung
echo ""
echo "=============================="
echo "✨ Setup abgeschlossen!"
echo "=============================="
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. Bearbeite .env und füge hinzu:"
echo "   - TELEGRAM_BOT_TOKEN (von @BotFather)"
echo "   - ANTHROPIC_API_KEY (von console.anthropic.com)"
echo ""
echo "2. Platziere credentials.json im Projektverzeichnis"
echo ""
echo "3. Erstelle Ordnerstruktur auf Google Drive:"
echo "   python document_sorter_main.py --mode setup"
echo ""
echo "4. Starte das System:"
echo "   python document_sorter_main.py --mode bot"
echo ""
echo "📖 Dokumentation: DOCUMENT_SORTING.md"
echo ""

# Prüfe ob wichtige Keys gesetzt sind
echo "Überprüfung der Konfiguration:"
echo ""

if grep -q "your_telegram_bot_token" .env; then
    warning "TELEGRAM_BOT_TOKEN noch nicht gesetzt"
else
    success "TELEGRAM_BOT_TOKEN gesetzt"
fi

if grep -q "your_anthropic_api_key" .env; then
    warning "ANTHROPIC_API_KEY noch nicht gesetzt"
else
    success "ANTHROPIC_API_KEY gesetzt"
fi

echo ""
echo "Viel Erfolg! 🎉"
