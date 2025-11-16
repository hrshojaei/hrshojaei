"""
OCR Service für Texterkennung aus gescannten Dokumenten.
Unterstützt Tesseract (kostenlos) und Google Cloud Vision (premium).
"""

import os
from pathlib import Path
from typing import Optional, Dict, Literal
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from loguru import logger

# Optional: Google Cloud Vision
try:
    from google.cloud import vision
    CLOUD_VISION_AVAILABLE = True
except ImportError:
    CLOUD_VISION_AVAILABLE = False
    logger.warning("Google Cloud Vision nicht installiert - nur Tesseract verfügbar")


class OCRService:
    """Service für Optical Character Recognition (OCR)."""

    def __init__(
        self,
        provider: Literal["tesseract", "cloud_vision"] = "tesseract",
        language: str = "deu"
    ):
        """
        Initialisiert den OCR Service.

        Args:
            provider: OCR-Provider ("tesseract" oder "cloud_vision")
            language: Sprache für OCR (deu=Deutsch, eng=Englisch)
        """
        self.provider = provider
        self.language = language

        if provider == "cloud_vision" and not CLOUD_VISION_AVAILABLE:
            logger.warning("Cloud Vision nicht verfügbar - wechsle zu Tesseract")
            self.provider = "tesseract"

        if provider == "cloud_vision":
            self.vision_client = vision.ImageAnnotatorClient()
        else:
            self.vision_client = None

        logger.info(f"OCR Service initialisiert: {self.provider} (Sprache: {language})")

    def extract_text_from_image(self, image_path: Path) -> str:
        """
        Extrahiert Text aus einem Bild.

        Args:
            image_path: Pfad zum Bild

        Returns:
            Extrahierter Text
        """
        if self.provider == "tesseract":
            return self._tesseract_image(image_path)
        else:
            return self._cloud_vision_image(image_path)

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extrahiert Text aus einem PDF.

        Args:
            pdf_path: Pfad zur PDF-Datei

        Returns:
            Extrahierter Text (alle Seiten kombiniert)
        """
        logger.info(f"Extrahiere Text aus PDF: {pdf_path.name}")

        try:
            # PDF zu Bildern konvertieren
            images = convert_from_path(
                str(pdf_path),
                dpi=300,  # Hohe Auflösung für bessere OCR
                fmt='jpeg'
            )

            logger.info(f"PDF hat {len(images)} Seite(n)")

            # OCR auf jeder Seite
            all_text = []
            for i, image in enumerate(images, start=1):
                logger.debug(f"Verarbeite Seite {i}/{len(images)}")

                # Bild temporär speichern
                temp_image = Path("temp") / f"page_{i}.jpg"
                temp_image.parent.mkdir(exist_ok=True)
                image.save(str(temp_image), 'JPEG')

                # Text extrahieren
                text = self.extract_text_from_image(temp_image)
                all_text.append(text)

                # Temp-Datei löschen
                temp_image.unlink()

            combined_text = "\n\n--- SEITE {} ---\n\n".join(all_text)
            logger.info(f"Text extrahiert: {len(combined_text)} Zeichen")

            return combined_text

        except Exception as e:
            logger.error(f"Fehler bei PDF-Verarbeitung: {e}")
            raise

    def extract_text(self, file_path: Path) -> str:
        """
        Extrahiert Text aus Datei (automatische Format-Erkennung).

        Args:
            file_path: Pfad zur Datei

        Returns:
            Extrahierter Text
        """
        suffix = file_path.suffix.lower()

        if suffix == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif suffix in ['.jpg', '.jpeg', '.png']:
            return self.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Nicht unterstütztes Dateiformat: {suffix}")

    def _tesseract_image(self, image_path: Path) -> str:
        """Tesseract OCR auf Bild."""
        try:
            image = Image.open(image_path)

            # Tesseract Config für bessere Genauigkeit
            custom_config = r'--oem 3 --psm 6'

            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=custom_config
            )

            return text.strip()

        except Exception as e:
            logger.error(f"Tesseract-Fehler: {e}")
            raise

    def _cloud_vision_image(self, image_path: Path) -> str:
        """Google Cloud Vision OCR auf Bild."""
        try:
            # Bild laden
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            # Text-Erkennung
            response = self.vision_client.document_text_detection(
                image=image,
                image_context={"language_hints": [self.language]}
            )

            if response.error.message:
                raise Exception(f"Cloud Vision Fehler: {response.error.message}")

            # Text extrahieren
            text = response.full_text_annotation.text if response.full_text_annotation else ""

            return text.strip()

        except Exception as e:
            logger.error(f"Cloud Vision Fehler: {e}")
            raise

    def get_detailed_analysis(self, file_path: Path) -> Dict:
        """
        Erweiterte Analyse eines Dokuments.

        Args:
            file_path: Pfad zur Datei

        Returns:
            Dict mit Text, Sprache, Konfidenz, etc.
        """
        text = self.extract_text(file_path)

        return {
            'text': text,
            'char_count': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n')),
            'provider': self.provider,
            'language': self.language,
            'file_name': file_path.name,
            'file_type': file_path.suffix
        }


def create_ocr_service(
    use_cloud_vision: bool = False,
    language: str = "deu"
) -> OCRService:
    """
    Factory-Funktion zum Erstellen eines OCR Service.

    Args:
        use_cloud_vision: True für Google Cloud Vision, False für Tesseract
        language: Sprache (deu, eng, etc.)

    Returns:
        OCRService Instanz
    """
    provider = "cloud_vision" if use_cloud_vision else "tesseract"
    return OCRService(provider=provider, language=language)
