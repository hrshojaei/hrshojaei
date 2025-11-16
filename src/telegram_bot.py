"""
Telegram Bot für den Empfang von gescannten Dokumenten.
Speichert empfangene Dokumente auf Google Drive.
"""

import os
from pathlib import Path
from typing import Optional
from loguru import logger
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.config import get_settings


class TelegramDocumentBot:
    """Telegram Bot zum Empfang von Dokumenten."""

    def __init__(self, token: str, upload_callback=None):
        """
        Initialisiert den Telegram Bot.

        Args:
            token: Telegram Bot Token
            upload_callback: Callback-Funktion zum Upload auf Google Drive
        """
        self.token = token
        self.upload_callback = upload_callback
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Registriert Message Handler."""
        # Commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # Document Handler
        self.application.add_handler(
            MessageHandler(filters.Document.ALL, self.handle_document)
        )

        # Photo Handler
        self.application.add_handler(
            MessageHandler(filters.PHOTO, self.handle_photo)
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler für /start Command."""
        welcome_message = (
            "🤖 *Dokument-Sortier-Bot*\n\n"
            "Willkommen! Ich helfe dir, deine gescannten Dokumente automatisch zu sortieren.\n\n"
            "📄 Sende mir einfach:\n"
            "• PDF-Dokumente\n"
            "• Fotos von Dokumenten\n"
            "• Gescannte Briefe\n\n"
            "Ich werde sie automatisch auf deinem Google Drive sortieren! 🗂️"
        )
        await update.message.reply_text(welcome_message, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler für /help Command."""
        help_message = (
            "ℹ️ *Hilfe*\n\n"
            "*Unterstützte Formate:*\n"
            "• PDF (.pdf)\n"
            "• Bilder (.jpg, .jpeg, .png)\n\n"
            "*So funktioniert's:*\n"
            "1. Sende mir ein Dokument\n"
            "2. Ich extrahiere den Text (OCR)\n"
            "3. KI analysiert den Inhalt\n"
            "4. Dokument wird automatisch sortiert\n\n"
            "*Befehle:*\n"
            "/start - Bot starten\n"
            "/help - Diese Hilfe anzeigen"
        )
        await update.message.reply_text(help_message, parse_mode="Markdown")

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler für Dokument-Uploads."""
        document = update.message.document
        user = update.message.from_user

        logger.info(f"Dokument empfangen von {user.username}: {document.file_name}")

        # Unterstützte Formate prüfen
        supported_formats = ['.pdf', '.jpg', '.jpeg', '.png']
        file_ext = Path(document.file_name).suffix.lower()

        if file_ext not in supported_formats:
            await update.message.reply_text(
                f"❌ Dateiformat {file_ext} wird nicht unterstützt.\n"
                f"Unterstützt: {', '.join(supported_formats)}"
            )
            return

        # Status-Nachricht
        status_msg = await update.message.reply_text(
            "⏳ Dokument wird verarbeitet..."
        )

        try:
            # Dokument herunterladen
            file = await document.get_file()

            # Temporärer Speicherort
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / document.file_name

            await file.download_to_drive(str(temp_path))
            logger.info(f"Dokument heruntergeladen: {temp_path}")

            # Upload zu Google Drive (falls Callback vorhanden)
            if self.upload_callback:
                result = await self.upload_callback(
                    temp_path,
                    original_name=document.file_name,
                    user_id=user.id
                )

                await status_msg.edit_text(
                    f"✅ *Dokument verarbeitet!*\n\n"
                    f"📁 Kategorie: {result.get('category', 'Unbekannt')}\n"
                    f"📂 Ordner: {result.get('folder', 'Inbox')}\n"
                    f"🔗 [Auf Google Drive öffnen]({result.get('url', '#')})",
                    parse_mode="Markdown"
                )
            else:
                await status_msg.edit_text(
                    "✅ Dokument empfangen! (Upload-Callback nicht konfiguriert)"
                )

            # Temporäre Datei löschen
            if temp_path.exists():
                temp_path.unlink()

        except Exception as e:
            logger.error(f"Fehler bei Dokumentverarbeitung: {e}")
            await status_msg.edit_text(
                f"❌ Fehler bei der Verarbeitung:\n{str(e)}"
            )

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler für Foto-Uploads."""
        photo = update.message.photo[-1]  # Höchste Auflösung
        user = update.message.from_user

        logger.info(f"Foto empfangen von {user.username}")

        status_msg = await update.message.reply_text(
            "⏳ Foto wird verarbeitet..."
        )

        try:
            # Foto herunterladen
            file = await photo.get_file()

            # Temporärer Speicherort
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / f"photo_{photo.file_id}.jpg"

            await file.download_to_drive(str(temp_path))
            logger.info(f"Foto heruntergeladen: {temp_path}")

            # Upload zu Google Drive
            if self.upload_callback:
                result = await self.upload_callback(
                    temp_path,
                    original_name=f"scan_{photo.file_id}.jpg",
                    user_id=user.id
                )

                await status_msg.edit_text(
                    f"✅ *Foto verarbeitet!*\n\n"
                    f"📁 Kategorie: {result.get('category', 'Unbekannt')}\n"
                    f"📂 Ordner: {result.get('folder', 'Inbox')}\n"
                    f"🔗 [Auf Google Drive öffnen]({result.get('url', '#')})",
                    parse_mode="Markdown"
                )
            else:
                await status_msg.edit_text(
                    "✅ Foto empfangen! (Upload-Callback nicht konfiguriert)"
                )

            # Temporäre Datei löschen
            if temp_path.exists():
                temp_path.unlink()

        except Exception as e:
            logger.error(f"Fehler bei Fotoverarbeitung: {e}")
            await status_msg.edit_text(
                f"❌ Fehler bei der Verarbeitung:\n{str(e)}"
            )

    def run(self):
        """Startet den Bot."""
        logger.info("Telegram Bot wird gestartet...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start_async(self):
        """Startet den Bot asynchron (für Integration in bestehende Event Loop)."""
        logger.info("Telegram Bot wird asynchron gestartet...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)


def create_bot(upload_callback=None) -> TelegramDocumentBot:
    """
    Factory-Funktion zum Erstellen eines Telegram Bots.

    Args:
        upload_callback: Callback für Google Drive Upload

    Returns:
        TelegramDocumentBot Instanz
    """
    settings = get_settings()

    if not settings.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN nicht in Umgebungsvariablen gesetzt!")

    return TelegramDocumentBot(
        token=settings.telegram_bot_token,
        upload_callback=upload_callback
    )
