"""
Hauptservice für automatische Dokumentensortierung.
Orchestriert OCR, KI-Klassifizierung und Google Drive Organisation.
"""

import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from loguru import logger

from src.google_drive_manager import GoogleDriveManager
from src.ocr_service import OCRService
from src.document_classifier import DocumentClassifier
from src.pdf_converter import PDFConverter
from src.config import get_settings


class DocumentSorter:
    """Hauptservice für Dokumentensortierung."""

    def __init__(
        self,
        drive_manager: GoogleDriveManager,
        ocr_service: OCRService,
        classifier: DocumentClassifier,
        base_folder_name: str = "Sortierte Dokumente",
        convert_images_to_pdf: bool = True
    ):
        """
        Initialisiert den Document Sorter.

        Args:
            drive_manager: Google Drive Manager Instanz
            ocr_service: OCR Service Instanz
            classifier: Document Classifier Instanz
            base_folder_name: Name des Hauptordners auf Google Drive
            convert_images_to_pdf: Bilder automatisch zu PDF konvertieren
        """
        self.drive = drive_manager
        self.ocr = ocr_service
        self.classifier = classifier
        self.base_folder_name = base_folder_name
        self.convert_images_to_pdf = convert_images_to_pdf

        # PDF Converter
        self.pdf_converter = PDFConverter(quality=95)

        # Folder-Cache für Performance
        self.folder_cache: Dict[str, str] = {}

        logger.info("Document Sorter initialisiert")

    async def process_document(
        self,
        file_path: Path,
        original_name: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict:
        """
        Verarbeitet ein Dokument komplett: OCR → Klassifizierung → Upload → Sortierung.

        Args:
            file_path: Pfad zur lokalen Datei
            original_name: Originaler Dateiname
            user_id: Telegram User ID (optional)

        Returns:
            Dict mit Verarbeitungsergebnis
        """
        start_time = datetime.now()
        file_name = original_name or file_path.name

        logger.info(f"📄 Starte Verarbeitung: {file_name}")

        try:
            # 0. Bilder zu PDF konvertieren (falls aktiviert)
            upload_file_path = file_path
            upload_extension = file_path.suffix

            if self.convert_images_to_pdf and self.pdf_converter.should_convert(file_path):
                logger.info("📄 Konvertiere Bild zu PDF...")
                pdf_path = self.pdf_converter.image_to_pdf(file_path)
                upload_file_path = pdf_path
                upload_extension = '.pdf'
                logger.info(f"✅ PDF erstellt: {pdf_path.name}")

            # 1. OCR - Text extrahieren
            logger.info("🔍 Extrahiere Text (OCR)...")
            text = self.ocr.extract_text(upload_file_path)
            logger.info(f"✅ Text extrahiert: {len(text)} Zeichen")

            # 2. KI-Klassifizierung
            logger.info("🤖 Klassifiziere Dokument mit Claude AI...")
            classification = self.classifier.classify_document(text, file_name)
            logger.info(f"✅ Klassifiziert als: {classification['category']} - {classification['document_type']}")

            # 3. Ordnerstruktur erstellen
            logger.info("📁 Erstelle Ordnerstruktur auf Google Drive...")
            folder_id = self._get_or_create_folder_for_document(classification)

            # 4. Dateiname generieren
            new_filename = self._generate_filename(classification, upload_extension)

            # 5. Upload zu Google Drive
            logger.info(f"☁️ Lade hoch nach: {'/'.join(classification['folder_path'])}/{new_filename}")
            upload_result = self.drive.upload_file(
                upload_file_path,
                folder_id=folder_id,
                new_name=new_filename
            )

            # Temporäre PDF löschen (falls erstellt)
            if upload_file_path != file_path and upload_file_path.exists():
                upload_file_path.unlink()
                logger.debug("Temporäre PDF gelöscht")

            # Verarbeitungszeit
            duration = (datetime.now() - start_time).total_seconds()

            result = {
                'success': True,
                'file_id': upload_result['file_id'],
                'url': upload_result['url'],
                'category': classification['category'],
                'document_type': classification['document_type'],
                'folder': '/'.join(classification['folder_path']),
                'filename': new_filename,
                'sender': classification['sender'],
                'date': classification['date'],
                'summary': classification['summary'],
                'tags': classification['tags'],
                'priority': classification['priority'],
                'processing_time': f"{duration:.2f}s"
            }

            logger.info(f"✅ Dokument erfolgreich verarbeitet in {duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"❌ Fehler bei Dokumentverarbeitung: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_name': file_name
            }

    def _get_or_create_folder_for_document(self, classification: Dict) -> str:
        """
        Erstellt Ordnerstruktur für klassifiziertes Dokument.

        Args:
            classification: Klassifizierungs-Dict

        Returns:
            Folder-ID des Zielordners
        """
        folder_path = classification['folder_path']

        # Cache-Key erstellen
        cache_key = '/'.join(folder_path)

        # Prüfe Cache
        if cache_key in self.folder_cache:
            return self.folder_cache[cache_key]

        # Erstelle Ordnerhierarchie
        folder_id = self.drive.get_or_create_folder_path(folder_path)

        # Cache speichern
        self.folder_cache[cache_key] = folder_id

        return folder_id

    def _generate_filename(self, classification: Dict, file_extension: str) -> str:
        """
        Generiert aussagekräftigen Dateinamen.

        Format: YYYY-MM-DD_Kategorie_Absender_Betreff.ext

        Args:
            classification: Klassifizierungs-Dict
            file_extension: Dateiendung (z.B. .pdf)

        Returns:
            Generierter Dateiname
        """
        date = classification['date']
        category = self._sanitize_filename(classification['document_type'])
        sender = self._sanitize_filename(classification['sender'])
        subject = self._sanitize_filename(classification['subject'])

        # Kürze lange Texte
        sender = sender[:30]
        subject = subject[:50]

        # Baue Dateinamen
        filename = f"{date}_{category}_{sender}"

        if subject and subject != 'Kein Betreff':
            filename += f"_{subject}"

        filename += file_extension

        return filename

    def _sanitize_filename(self, text: str) -> str:
        """
        Bereinigt Text für Dateinamen.

        Args:
            text: Zu bereinigender Text

        Returns:
            Bereinigter Text
        """
        # Ersetze ungültige Zeichen
        text = text.replace(' ', '_')
        text = text.replace('/', '-')
        text = text.replace('\\', '-')
        text = text.replace(':', '-')
        text = text.replace('*', '')
        text = text.replace('?', '')
        text = text.replace('"', '')
        text = text.replace('<', '')
        text = text.replace('>', '')
        text = text.replace('|', '')

        # Entferne mehrfache Unterstriche
        while '__' in text:
            text = text.replace('__', '_')

        return text.strip('_')

    async def process_inbox_folder(self, inbox_folder_id: Optional[str] = None) -> Dict:
        """
        Verarbeitet alle unsortierten Dokumente in einem Inbox-Ordner.

        Args:
            inbox_folder_id: Google Drive Folder-ID (None = Root)

        Returns:
            Dict mit Verarbeitungsstatistik
        """
        logger.info("📥 Verarbeite Inbox-Ordner...")

        files = self.drive.list_files_in_folder(inbox_folder_id)

        stats = {
            'total': len(files),
            'processed': 0,
            'failed': 0,
            'skipped': 0
        }

        for file in files:
            file_id = file['id']
            file_name = file['name']
            mime_type = file['mimeType']

            # Nur relevante Dateien verarbeiten
            if mime_type not in [
                'application/pdf',
                'image/jpeg',
                'image/png'
            ]:
                logger.debug(f"Überspringe {file_name} (MIME: {mime_type})")
                stats['skipped'] += 1
                continue

            try:
                # Download zu temp
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                temp_path = temp_dir / file_name

                success = self.drive.download_file(file_id, temp_path)
                if not success:
                    stats['failed'] += 1
                    continue

                # Verarbeite Dokument
                result = await self.process_document(temp_path, file_name)

                if result['success']:
                    stats['processed'] += 1

                    # Optional: Originaldatei aus Inbox löschen
                    # self.drive.delete_file(file_id)
                else:
                    stats['failed'] += 1

                # Temp-Datei löschen
                if temp_path.exists():
                    temp_path.unlink()

            except Exception as e:
                logger.error(f"Fehler bei {file_name}: {e}")
                stats['failed'] += 1

        logger.info(f"✅ Inbox verarbeitet: {stats['processed']} erfolgreich, {stats['failed']} fehlgeschlagen")
        return stats

    def create_default_folder_structure(self) -> Dict[str, str]:
        """
        Erstellt Standard-Ordnerstruktur auf Google Drive.

        Returns:
            Dict mit {kategorie: folder_id}
        """
        logger.info("Erstelle Standard-Ordnerstruktur...")

        categories = [
            'Finanzen',
            'Versicherungen',
            'Behörden',
            'Gesundheit',
            'Verträge',
            'Arbeit',
            'Wohnung',
            'Bildung',
            'Post',
            'Sonstiges'
        ]

        # Erstelle Hauptordner
        base_folder_id = self.drive.create_folder(self.base_folder_name)

        folder_map = {'base': base_folder_id}

        # Erstelle Kategorieordner
        for category in categories:
            folder_id = self.drive.create_folder(category, parent_id=base_folder_id)
            folder_map[category] = folder_id

        logger.info(f"✅ {len(categories)} Kategorieordner erstellt")
        return folder_map


async def create_sorter(
    use_cloud_vision: bool = False,
    base_folder_name: str = "Sortierte Dokumente"
) -> DocumentSorter:
    """
    Factory-Funktion zum Erstellen eines Document Sorters.

    Args:
        use_cloud_vision: True für Google Cloud Vision OCR
        base_folder_name: Name des Hauptordners

    Returns:
        DocumentSorter Instanz
    """
    settings = get_settings()

    # Google Drive Manager
    drive_manager = GoogleDriveManager()

    # OCR Service
    provider = "cloud_vision" if use_cloud_vision else "tesseract"
    ocr_service = OCRService(provider=provider, language="deu")

    # Document Classifier
    classifier = DocumentClassifier()

    return DocumentSorter(
        drive_manager=drive_manager,
        ocr_service=ocr_service,
        classifier=classifier,
        base_folder_name=base_folder_name
    )
