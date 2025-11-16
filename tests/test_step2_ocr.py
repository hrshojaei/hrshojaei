#!/usr/bin/env python3
"""
SCHRITT 2: OCR Service testen
Erstellt ein Test-Bild mit Text und versucht OCR
"""

import sys
from pathlib import Path

# Füge src zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont
from src.ocr_service import OCRService

def create_test_image():
    """Erstellt ein Test-Bild mit Text."""
    print("\n📄 Erstelle Test-Bild...")

    # Erstelle Bild mit weißem Hintergrund
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)

    # Text hinzufügen
    test_text = """
    RECHNUNG

    Telekom Deutschland GmbH
    Rechnungsnummer: 12345
    Datum: 15.01.2024

    Betrag: 49.99 EUR
    """

    # Zeichne Text (nutze Standard-Font)
    y_position = 50
    for line in test_text.strip().split('\n'):
        draw.text((50, y_position), line.strip(), fill='black')
        y_position += 30

    # Speichern
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    img_path = temp_dir / "test_rechnung.png"
    img.save(str(img_path))

    print(f"✅ Test-Bild erstellt: {img_path}")
    return img_path

def test_ocr():
    """Teste OCR Service."""
    print("=" * 60)
    print("SCHRITT 2: OCR Service Test")
    print("=" * 60)

    try:
        # Prüfe ob Tesseract verfügbar ist
        import pytesseract
        try:
            version = pytesseract.get_tesseract_version()
            print(f"\n✅ Tesseract gefunden: Version {version}")
        except Exception as e:
            print(f"\n❌ Tesseract nicht installiert: {e}")
            print("\n📝 Installation erforderlich:")
            print("   Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-deu")
            print("   macOS: brew install tesseract tesseract-lang")
            print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            return False

        # OCR Service initialisieren
        print("\n🔧 Initialisiere OCR Service (Tesseract)...")
        ocr = OCRService(provider="tesseract", language="deu")
        print("✅ OCR Service initialisiert")

        # Test-Bild erstellen
        img_path = create_test_image()

        # OCR durchführen
        print("\n🔍 Führe OCR aus...")
        text = ocr.extract_text_from_image(img_path)

        print(f"\n📄 Extrahierter Text ({len(text)} Zeichen):")
        print("-" * 60)
        print(text)
        print("-" * 60)

        # Prüfe ob wichtige Wörter erkannt wurden
        keywords = ["RECHNUNG", "Telekom", "EUR"]
        found = [kw for kw in keywords if kw.lower() in text.lower()]

        print(f"\n✅ Erkannte Keywords: {found}")

        if len(found) >= 2:
            print("\n🎉 OCR funktioniert!")
            print("=" * 60)
            return True
        else:
            print("\n⚠️  OCR hat Probleme - zu wenige Keywords erkannt")
            print("=" * 60)
            return False

    except Exception as e:
        print(f"\n❌ Fehler beim OCR-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ocr()
    sys.exit(0 if success else 1)
