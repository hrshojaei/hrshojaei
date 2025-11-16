#!/usr/bin/env python3
"""
Hauptscript für automatische Dokumentensortierung.

Features:
- Telegram Bot für Dokumentenempfang
- OCR (Tesseract oder Google Cloud Vision)
- KI-basierte Klassifizierung (Claude AI)
- Automatische Google Drive Organisation
- 15-Minuten Polling Service
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

from src.config import get_settings
from src.google_drive_manager import GoogleDriveManager
from src.ocr_service import OCRService
from src.document_classifier import DocumentClassifier
from src.document_sorter import DocumentSorter
from src.document_polling_service import start_polling_service
from src.telegram_bot import create_bot


async def setup_document_sorter() -> DocumentSorter:
    """
    Initialisiert den Document Sorter.

    Returns:
        DocumentSorter Instanz
    """
    settings = get_settings()

    logger.info("Initialisiere Document Sorter...")

    # Google Drive Manager
    drive_manager = GoogleDriveManager(
        credentials_path=settings.google_drive_credentials_path,
        token_path=settings.google_drive_token_path
    )

    # OCR Service
    provider = "cloud_vision" if settings.use_cloud_vision_ocr else "tesseract"
    ocr_service = OCRService(provider=provider, language="deu")

    # Document Classifier (Claude AI)
    classifier = DocumentClassifier()

    # Document Sorter
    sorter = DocumentSorter(
        drive_manager=drive_manager,
        ocr_service=ocr_service,
        classifier=classifier,
        base_folder_name=settings.document_base_folder_name,
        convert_images_to_pdf=settings.convert_images_to_pdf
    )

    logger.info("✅ Document Sorter erfolgreich initialisiert")
    return sorter


async def telegram_upload_callback(file_path: Path, original_name: str, user_id: int, sorter: DocumentSorter):
    """
    Callback für Telegram Bot: Verarbeitet hochgeladene Dokumente.

    Args:
        file_path: Pfad zur Datei
        original_name: Originaler Dateiname
        user_id: Telegram User ID
        sorter: DocumentSorter Instanz
    """
    return await sorter.process_document(file_path, original_name, user_id)


async def run_telegram_bot_and_polling():
    """
    Startet Telegram Bot und Polling Service parallel.
    """
    settings = get_settings()

    # Document Sorter initialisieren
    sorter = await setup_document_sorter()

    # Telegram Bot erstellen
    if settings.telegram_bot_token:
        logger.info("Starte Telegram Bot...")

        # Callback mit Sorter binden
        async def upload_callback(file_path, original_name, user_id):
            return await telegram_upload_callback(file_path, original_name, user_id, sorter)

        bot = create_bot(upload_callback=upload_callback)

        # Bot und Polling Service parallel starten
        await asyncio.gather(
            bot.start_async(),
            start_polling_service(
                sorter=sorter,
                inbox_folder_id=settings.google_drive_inbox_folder_id,
                poll_interval_minutes=settings.document_polling_interval_minutes
            )
        )
    else:
        logger.warning("Kein TELEGRAM_BOT_TOKEN gesetzt - nur Polling Service wird gestartet")

        # Nur Polling Service
        await start_polling_service(
            sorter=sorter,
            inbox_folder_id=settings.google_drive_inbox_folder_id,
            poll_interval_minutes=settings.document_polling_interval_minutes
        )


async def run_once():
    """
    Führt einen einmaligen Durchlauf aus (für Cron/Testing).
    """
    logger.info("Einmaliger Durchlauf...")

    sorter = await setup_document_sorter()

    settings = get_settings()
    stats = await sorter.process_inbox_folder(settings.google_drive_inbox_folder_id)

    logger.info(f"✅ Durchlauf abgeschlossen: {stats}")
    return stats


async def setup_folders():
    """
    Erstellt Standard-Ordnerstruktur auf Google Drive.
    """
    logger.info("Erstelle Standard-Ordnerstruktur...")

    sorter = await setup_document_sorter()
    folder_map = sorter.create_default_folder_structure()

    logger.info(f"✅ {len(folder_map)} Ordner erstellt")
    for category, folder_id in folder_map.items():
        logger.info(f"  - {category}: {folder_id}")

    return folder_map


def main():
    """Haupteinstiegspunkt."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automatische Dokumentensortierung mit KI"
    )
    parser.add_argument(
        '--mode',
        choices=['bot', 'polling', 'once', 'setup'],
        default='bot',
        help='Betriebsmodus: bot (Telegram+Polling), polling (nur Polling), once (einmaliger Durchlauf), setup (Ordnerstruktur erstellen)'
    )

    args = parser.parse_args()

    # Logging konfigurieren
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    if settings.log_to_file:
        log_path = Path("logs") / "document_sorter.log"
        log_path.parent.mkdir(exist_ok=True)
        logger.add(
            str(log_path),
            rotation="10 MB",
            retention="30 days",
            level=settings.log_level
        )

    logger.info(f"🚀 Starte Document Sorter (Modus: {args.mode})")

    try:
        if args.mode == 'bot':
            asyncio.run(run_telegram_bot_and_polling())
        elif args.mode == 'polling':
            settings.telegram_bot_token = None  # Deaktiviere Bot
            asyncio.run(run_telegram_bot_and_polling())
        elif args.mode == 'once':
            asyncio.run(run_once())
        elif args.mode == 'setup':
            asyncio.run(setup_folders())

    except KeyboardInterrupt:
        logger.info("⏹️ Programm durch Benutzer gestoppt")
    except Exception as e:
        logger.error(f"❌ Kritischer Fehler: {e}")
        raise


if __name__ == "__main__":
    main()
