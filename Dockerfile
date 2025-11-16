# Dockerfile für Document Sorting System
FROM python:3.11-slim

# Metadata
LABEL maintainer="Document Sorter"
LABEL description="AI-powered document sorting system with Telegram Bot and Google Drive integration"

# Umgebungsvariablen
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# System-Dependencies installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OCR-Engine
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    # PDF-Verarbeitung
    poppler-utils \
    # Bild-Verarbeitung
    libpng-dev \
    libjpeg-dev \
    # System-Tools
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Python Dependencies kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code kopieren
COPY src/ ./src/
COPY document_sorter_main.py .
COPY scripts/ ./scripts/

# Verzeichnisse für Runtime erstellen
RUN mkdir -p \
    /app/temp \
    /app/logs \
    /app/data

# Non-root User erstellen
RUN useradd -m -u 1000 docsorter && \
    chown -R docsorter:docsorter /app

# Zu non-root User wechseln
USER docsorter

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from src.config import get_settings; get_settings()" || exit 1

# Volumes für persistente Daten
VOLUME ["/app/logs", "/app/data", "/app/temp"]

# Exponiere Port (falls Web-Interface später hinzugefügt wird)
EXPOSE 8000

# Standard-Command
CMD ["python3", "document_sorter_main.py", "--mode", "bot"]
