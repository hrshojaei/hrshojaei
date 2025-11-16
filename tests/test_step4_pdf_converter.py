#!/usr/bin/env python3
"""
SCHRITT 4: PDF Converter testen
Testet die Bild-zu-PDF Konvertierung
"""

import sys
from pathlib import Path

# Füge src zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw
from src.pdf_converter import PDFConverter

def create_test_image():
    """Erstellt ein Test-Bild."""
    print("\n📄 Erstelle Test-Bild...")

    img = Image.new('RGB', (800, 400), color='lightblue')
    draw = ImageDraw.Draw(img)

    # Text
    draw.text((50, 50), "Test-Dokument für PDF-Konvertierung", fill='black')
    draw.text((50, 100), "Dies ist ein Testbild.", fill='black')
    draw.rectangle([50, 150, 750, 350], outline='red', width=3)

    # Speichern
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    img_path = temp_dir / "test_image.jpg"
    img.save(str(img_path))

    print(f"✅ Test-Bild erstellt: {img_path}")
    return img_path

def test_pdf_converter():
    """Teste PDF Converter."""
    print("=" * 60)
    print("SCHRITT 4: PDF Converter Test")
    print("=" * 60)

    try:
        # PDF Converter initialisieren
        print("\n🔧 Initialisiere PDF Converter...")
        converter = PDFConverter(quality=95)
        print("✅ PDF Converter initialisiert")

        # Test-Bild erstellen
        img_path = create_test_image()

        # Zu PDF konvertieren
        print("\n📄 Konvertiere Bild zu PDF...")
        pdf_path = converter.image_to_pdf(img_path)

        print(f"✅ PDF erstellt: {pdf_path}")

        # Prüfe ob PDF existiert
        if pdf_path.exists():
            file_size = pdf_path.stat().st_size
            print(f"   Dateigröße: {file_size / 1024:.2f} KB")

            # Prüfe ob es wirklich ein PDF ist
            with open(pdf_path, 'rb') as f:
                header = f.read(4)
                if header == b'%PDF':
                    print("   Format: ✅ Gültiges PDF")
                else:
                    print("   Format: ❌ Kein gültiges PDF!")
                    return False

            print("\n🎉 PDF-Konvertierung funktioniert!")
            print("=" * 60)
            return True
        else:
            print("\n❌ PDF wurde nicht erstellt!")
            return False

    except Exception as e:
        print(f"\n❌ Fehler beim PDF-Converter-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_converter()
    sys.exit(0 if success else 1)
