#!/bin/bash
# Führt alle Tests nacheinander aus

set -e

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Document Sorter - Alle Tests"
echo "==============================="
echo ""

# Test Counter
PASSED=0
FAILED=0

# Funktion: Test ausführen
run_test() {
    local test_file=$1
    local test_name=$2

    echo ""
    echo -e "${YELLOW}▶ $test_name${NC}"
    echo "---"

    if python3 "$test_file"; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        ((FAILED++))
        # Weiter mit nächstem Test (nicht abbrechen)
        return 0
    fi
}

# Tests ausführen
run_test "tests/test_step1_config.py" "SCHRITT 1: Configuration"
run_test "tests/test_step2_ocr.py" "SCHRITT 2: OCR Service"
run_test "tests/test_step3_classifier.py" "SCHRITT 3: Document Classifier"
run_test "tests/test_step4_pdf_converter.py" "SCHRITT 4: PDF Converter"
run_test "tests/test_step5_integration.py" "SCHRITT 5: Integration"

# Zusammenfassung
echo ""
echo "==============================="
echo "📊 Test-Zusammenfassung"
echo "==============================="
echo -e "${GREEN}✅ Bestanden: $PASSED${NC}"
echo -e "${RED}❌ Fehlgeschlagen: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALLE TESTS BESTANDEN!${NC}"
    echo ""
    echo "Nächste Schritte:"
    echo "1. Google Drive Setup: python document_sorter_main.py --mode setup"
    echo "2. System starten: python document_sorter_main.py --mode bot"
    exit 0
else
    echo -e "${YELLOW}⚠️  Einige Tests sind fehlgeschlagen${NC}"
    echo "Prüfe die Ausgabe oben für Details"
    exit 1
fi
