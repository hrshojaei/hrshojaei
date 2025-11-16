"""
Konvertiert Bilder automatisch zu PDF-Dateien.
"""

from pathlib import Path
from typing import List, Optional
from PIL import Image
from loguru import logger


class PDFConverter:
    """Konvertiert Bilder zu PDF."""

    def __init__(self, quality: int = 95):
        """
        Initialisiert den PDF Converter.

        Args:
            quality: JPEG-Qualität (1-100, Standard: 95)
        """
        self.quality = quality
        logger.info(f"PDF Converter initialisiert (Qualität: {quality})")

    def image_to_pdf(self, image_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Konvertiert ein Bild zu PDF.

        Args:
            image_path: Pfad zum Bild
            output_path: Ziel-PDF-Pfad (optional, sonst .pdf Extension)

        Returns:
            Pfad zur erstellten PDF
        """
        try:
            # Ausgabepfad generieren
            if output_path is None:
                output_path = image_path.with_suffix('.pdf')

            logger.info(f"Konvertiere {image_path.name} zu PDF...")

            # Bild laden
            image = Image.open(image_path)

            # In RGB konvertieren (für PDF-Kompatibilität)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Erstelle weißen Hintergrund
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # Als PDF speichern
            image.save(
                str(output_path),
                'PDF',
                resolution=100.0,
                quality=self.quality,
                optimize=True
            )

            logger.info(f"✅ PDF erstellt: {output_path.name}")
            return output_path

        except Exception as e:
            logger.error(f"Fehler bei PDF-Konvertierung: {e}")
            raise

    def images_to_pdf(self, image_paths: List[Path], output_path: Path) -> Path:
        """
        Kombiniert mehrere Bilder zu einem mehrseitigen PDF.

        Args:
            image_paths: Liste von Bildpfaden
            output_path: Ziel-PDF-Pfad

        Returns:
            Pfad zur erstellten PDF
        """
        try:
            logger.info(f"Kombiniere {len(image_paths)} Bilder zu PDF...")

            # Bilder laden und konvertieren
            images = []
            for img_path in image_paths:
                img = Image.open(img_path)

                # RGB konvertieren
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                images.append(img)

            # Erstes Bild als Basis, Rest als zusätzliche Seiten
            if images:
                images[0].save(
                    str(output_path),
                    'PDF',
                    resolution=100.0,
                    quality=self.quality,
                    optimize=True,
                    save_all=True,
                    append_images=images[1:] if len(images) > 1 else []
                )

            logger.info(f"✅ Mehrseitiges PDF erstellt: {output_path.name}")
            return output_path

        except Exception as e:
            logger.error(f"Fehler bei mehrseitigem PDF: {e}")
            raise

    def should_convert(self, file_path: Path) -> bool:
        """
        Prüft ob Datei zu PDF konvertiert werden sollte.

        Args:
            file_path: Pfad zur Datei

        Returns:
            True wenn Konvertierung sinnvoll
        """
        return file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']


def convert_image_to_pdf(image_path: Path, quality: int = 95) -> Path:
    """
    Utility-Funktion: Konvertiert Bild zu PDF.

    Args:
        image_path: Pfad zum Bild
        quality: JPEG-Qualität

    Returns:
        Pfad zur PDF
    """
    converter = PDFConverter(quality=quality)
    return converter.image_to_pdf(image_path)
