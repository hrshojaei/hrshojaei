# 🗂️ Automatische Dokumentensortierung

KI-basiertes System zur automatischen Sortierung gescannter Dokumente auf Google Drive.

## ✨ Features

- **📱 Telegram Bot** - Sende Dokumente direkt per Telegram
- **🔍 OCR** - Texterkennung mit Tesseract (kostenlos) oder Google Cloud Vision
- **🤖 KI-Klassifizierung** - Claude AI analysiert Dokumente intelligent
- **📁 Auto-Organisation** - Erstellt automatisch sinnvolle Ordnerstrukturen
- **🔄 Auto-Polling** - Überwacht Google Drive alle 15 Minuten
- **📄 PDF-Konvertierung** - Bilder werden automatisch zu PDFs

## 🏗️ Architektur

```
Telegram Bot  →  OCR  →  Claude AI  →  Google Drive
     ↓                                      ↑
  Bilder/PDFs                        Sortierte Dokumente
```

## 📋 Voraussetzungen

### 1. Telegram Bot erstellen

1. Öffne [@BotFather](https://t.me/BotFather) in Telegram
2. Sende `/newbot`
3. Folge den Anweisungen
4. Kopiere den **Bot Token**

### 2. Google Drive API einrichten

1. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
2. Erstelle ein neues Projekt
3. Aktiviere **Google Drive API**
4. Gehe zu **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Wähle **Desktop App**
6. Lade `credentials.json` herunter
7. Speichere `credentials.json` im Projektverzeichnis

### 3. Anthropic API Key

1. Gehe zu [Anthropic Console](https://console.anthropic.com/)
2. Erstelle einen API Key
3. Kopiere den Key

### 4. System-Abhängigkeiten installieren

**Tesseract OCR** (für Text-Erkennung):

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-deu poppler-utils

# macOS
brew install tesseract tesseract-lang poppler

# Windows
# Download: https://github.com/UB-Mannheim/tesseract/wiki
```

## 🚀 Installation

### 1. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 2. Umgebungsvariablen konfigurieren

Kopiere `.env.example` zu `.env`:

```bash
cp .env.example .env
```

Bearbeite `.env` und füge hinzu:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=dein_telegram_bot_token

# Anthropic API
ANTHROPIC_API_KEY=dein_anthropic_api_key

# Google Drive (optional - Pfade anpassen)
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials.json
GOOGLE_DRIVE_TOKEN_PATH=token.json

# OCR Einstellungen
USE_CLOUD_VISION_OCR=false  # true für Google Cloud Vision (kostenpflichtig)
CONVERT_IMAGES_TO_PDF=true

# Polling Intervall
DOCUMENT_POLLING_INTERVAL_MINUTES=15
```

### 3. Google Drive authentifizieren

Beim ersten Start öffnet sich automatisch ein Browser-Fenster:

```bash
python document_sorter_main.py --mode setup
```

- Melde dich mit deinem Google-Konto an
- Erlaube Zugriff auf Google Drive
- Token wird automatisch in `token.json` gespeichert

## 📖 Verwendung

### Modus 1: Telegram Bot + Polling (Empfohlen)

Startet Telegram Bot und überwacht Google Drive alle 15 Minuten:

```bash
python document_sorter_main.py --mode bot
```

**Nutzung:**
1. Öffne deinen Telegram Bot
2. Sende `/start`
3. Sende ein Dokument (PDF, JPG, PNG)
4. Bot verarbeitet automatisch und sortiert auf Google Drive

### Modus 2: Nur Polling

Überwacht nur Google Drive (kein Telegram):

```bash
python document_sorter_main.py --mode polling
```

Nutze dies, wenn Dokumente direkt auf Google Drive hochgeladen werden.

### Modus 3: Einmaliger Durchlauf

Für Cron-Jobs oder Testing:

```bash
python document_sorter_main.py --mode once
```

### Modus 4: Ordnerstruktur erstellen

Erstellt Standard-Ordner auf Google Drive:

```bash
python document_sorter_main.py --mode setup
```

Erstellt folgende Struktur:
```
Sortierte Dokumente/
├── Finanzen/
├── Versicherungen/
├── Behörden/
├── Gesundheit/
├── Verträge/
├── Arbeit/
├── Wohnung/
├── Bildung/
├── Post/
└── Sonstiges/
```

## 🔧 Konfiguration

### OCR Provider wechseln

**Tesseract (Kostenlos):**
```bash
USE_CLOUD_VISION_OCR=false
```

**Google Cloud Vision (Premium, kostenpflichtig):**
```bash
USE_CLOUD_VISION_OCR=true
```

**Kosten:**
- Erste 1000 Seiten/Monat: **kostenlos**
- Danach: ~$1.50 pro 1000 Seiten

### Polling-Intervall anpassen

```bash
DOCUMENT_POLLING_INTERVAL_MINUTES=15  # Standard: 15 Minuten
```

### Bilder nicht zu PDF konvertieren

```bash
CONVERT_IMAGES_TO_PDF=false
```

## 📁 Beispiel-Workflow

**1. Dokument per Telegram senden:**

User sendet Rechnung als Foto →

**2. Automatische Verarbeitung:**
- OCR extrahiert Text
- Claude AI erkennt: "Rechnung von Telekom, Datum: 2024-01-15"
- Erstellt Ordner: `Finanzen/Rechnungen`
- Benennt Datei: `2024-01-15_Rechnung_Telekom.pdf`

**3. Ergebnis:**
```
Google Drive/
└── Sortierte Dokumente/
    └── Finanzen/
        └── Rechnungen/
            └── 2024-01-15_Rechnung_Telekom.pdf
```

## 🤖 Intelligente Kategorisierung

Claude AI erkennt automatisch:

### Dokumenttypen
- Rechnungen
- Verträge (Miet-, Arbeits-, Kauf-)
- Versicherungsdokumente
- Behördenbriefe
- Arztbriefe / Rezepte
- Kontoauszüge
- Gehaltsabrechnungen
- Nebenkostenabrechnungen
- Zeugnisse / Zertifikate

### Extrahierte Metadaten
- Absender
- Datum
- Betreff
- Kategorie
- Tags
- Priorität

### Beispiel-Klassifizierung

**Eingabe:** Gescannter Brief
```
Telekom Deutschland GmbH
Rechnung Nr. 12345
Rechnungsdatum: 15.01.2024
Betrag: 49.99 EUR
```

**Output:**
```json
{
  "category": "Finanzen",
  "document_type": "Rechnung",
  "sender": "Telekom",
  "date": "2024-01-15",
  "folder_path": ["Finanzen", "Rechnungen"],
  "filename": "2024-01-15_Rechnung_Telekom.pdf"
}
```

## 🛠️ Cron-Job einrichten (Linux/Mac)

Für automatische tägliche Ausführung:

```bash
crontab -e
```

Füge hinzu:
```cron
# Jeden Tag um 20:00 Uhr
0 20 * * * cd /pfad/zu/hrshojaei && /usr/bin/python3 document_sorter_main.py --mode once
```

## 🐛 Troubleshooting

### Fehler: "Tesseract not found"

**Lösung:**
```bash
# Ubuntu
sudo apt-get install tesseract-ocr tesseract-ocr-deu

# macOS
brew install tesseract

# Prüfen:
tesseract --version
```

### Fehler: "Google Drive authentication failed"

**Lösung:**
1. Lösche `token.json`
2. Führe `python document_sorter_main.py --mode setup` aus
3. Authentifiziere erneut im Browser

### Fehler: "ANTHROPIC_API_KEY not set"

**Lösung:**
Füge in `.env` hinzu:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### OCR erkennt Text nicht

**Lösungen:**
1. Bessere Bildqualität (min. 300 DPI)
2. Wechsel zu Google Cloud Vision:
   ```bash
   USE_CLOUD_VISION_OCR=true
   ```

## 📊 Logs

Logs werden gespeichert in:
```
logs/document_sorter.log
```

Anzeigen:
```bash
tail -f logs/document_sorter.log
```

## 🔒 Sicherheit

- **API Keys** niemals committen (`.env` ist in `.gitignore`)
- `credentials.json` und `token.json` **NICHT** ins Repository
- Telegram Bot nur für eigene Nutzung
- Google Drive OAuth auf "Desktop App" beschränken

## 🎯 Nächste Schritte

1. **Telegram Bot testen:**
   ```bash
   python document_sorter_main.py --mode bot
   ```

2. **Dokument senden** und warten

3. **Google Drive prüfen** → Dokument sollte sortiert sein

4. **Für Produktion:**
   - Als Systemd Service einrichten (Linux)
   - Oder via Docker deployen

## 📝 Support

Bei Problemen:
1. Prüfe Logs: `logs/document_sorter.log`
2. Teste mit `--mode once`
3. Prüfe `.env` Konfiguration

## 🚀 Deployment

Siehe [DEPLOYMENT_DOCUMENT_SORTER.md](DEPLOYMENT_DOCUMENT_SORTER.md) für:
- Docker Setup
- Systemd Service
- Cloud Deployment (AWS/GCP)
