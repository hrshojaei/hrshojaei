# 🧪 Schritt-für-Schritt Tests

Diese Test-Scripte helfen Ihnen, das Document Sorting System schrittweise aufzubauen und zu testen.

## 📋 Übersicht

Führen Sie die Tests in dieser Reihenfolge aus:

```bash
# 1. Configuration testen
python tests/test_step1_config.py

# 2. OCR Service testen (benötigt Tesseract)
python tests/test_step2_ocr.py

# 3. Document Classifier testen (benötigt ANTHROPIC_API_KEY)
python tests/test_step3_classifier.py

# 4. PDF Converter testen
python tests/test_step4_pdf_converter.py

# 5. Integration Test (kompletter Workflow)
python tests/test_step5_integration.py
```

## 🚀 Schnellstart

### Alle Tests auf einmal

```bash
bash tests/run_all_tests.sh
```

## 📝 Einzelne Test-Beschreibungen

### SCHRITT 1: Configuration Test

**Was wird getestet:**
- Ob `.env` korrekt geladen wird
- Welche API Keys gesetzt sind
- Aktuelle Konfiguration

**Voraussetzungen:**
- Keine

**Erwartetes Ergebnis:**
- ✅ Config lädt erfolgreich
- Liste aller Einstellungen
- Warnung wenn API Keys fehlen

---

### SCHRITT 2: OCR Service Test

**Was wird getestet:**
- Tesseract Installation
- Texterkennung aus Bildern
- Deutsche Sprache

**Voraussetzungen:**
- Tesseract OCR installiert

**Installation:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-deu

# macOS
brew install tesseract tesseract-lang

# Windows
# Download: https://github.com/UB-Mannheim/tesseract/wiki
```

**Erwartetes Ergebnis:**
- ✅ Tesseract gefunden
- Test-Bild mit "RECHNUNG" wird erstellt
- Text wird korrekt extrahiert

---

### SCHRITT 3: Document Classifier Test

**Was wird getestet:**
- Claude AI API Verbindung
- Intelligente Dokumenten-Klassifizierung
- Metadaten-Extraktion

**Voraussetzungen:**
- `ANTHROPIC_API_KEY` in `.env` gesetzt

**Erwartetes Ergebnis:**
- ✅ Claude AI antwortet
- Rechnung wird als "Finanzen" klassifiziert
- Absender, Datum, Ordnerstruktur werden erkannt

---

### SCHRITT 4: PDF Converter Test

**Was wird getestet:**
- Bild zu PDF Konvertierung
- PDF-Validierung

**Voraussetzungen:**
- Pillow installiert

**Erwartetes Ergebnis:**
- ✅ Test-Bild wird erstellt
- PDF wird generiert
- PDF ist gültig (Header: %PDF)

---

### SCHRITT 5: Integration Test

**Was wird getestet:**
- Kompletter Workflow
- Bild → PDF → OCR → Klassifizierung
- Ohne Google Drive Upload

**Voraussetzungen:**
- Tesseract OCR (optional)
- ANTHROPIC_API_KEY

**Erwartetes Ergebnis:**
- ✅ Kompletter Workflow funktioniert
- AOK-Rechnung wird korrekt klassifiziert
- Ordnerstruktur wird vorgeschlagen

---

## 🔧 Troubleshooting

### Test schlägt fehl: "Tesseract not found"

**Lösung:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu poppler-utils
```

### Test schlägt fehl: "ANTHROPIC_API_KEY not set"

**Lösung:**
1. Öffne `.env`
2. Füge hinzu: `ANTHROPIC_API_KEY=sk-ant-...`
3. Speichere und teste erneut

### Test schlägt fehl: "ModuleNotFoundError"

**Lösung:**
```bash
pip install -r requirements.txt
```

## 📊 Nächste Schritte

Nach erfolgreichen Tests:

1. **Google Drive Setup:**
   ```bash
   python document_sorter_main.py --mode setup
   ```

2. **Telegram Bot Setup:**
   - Erstelle Bot bei @BotFather
   - Füge Token in `.env` hinzu

3. **System starten:**
   ```bash
   python document_sorter_main.py --mode bot
   ```

## 💡 Tipps

- Führen Sie Tests einzeln aus für besseres Debugging
- Prüfen Sie Logs in `logs/` bei Problemen
- Tests erstellen Test-Dateien in `temp/` (werden nicht committed)
