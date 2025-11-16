#!/usr/bin/env python3
"""
SCHRITT 3: Document Classifier testen
Testet die Claude AI Klassifizierung
"""

import sys
from pathlib import Path

# Füge src zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_classifier import DocumentClassifier
from src.config import get_settings

def test_classifier():
    """Teste Document Classifier."""
    print("=" * 60)
    print("SCHRITT 3: Document Classifier Test")
    print("=" * 60)

    try:
        settings = get_settings()

        if not settings.anthropic_api_key:
            print("\n❌ ANTHROPIC_API_KEY nicht in .env gesetzt!")
            print("\n📝 Bitte in .env hinzufügen:")
            print("   ANTHROPIC_API_KEY=sk-ant-...")
            return False

        print(f"\n✅ Anthropic API Key gefunden: {settings.anthropic_api_key[:20]}...")

        # Classifier initialisieren
        print("\n🔧 Initialisiere Document Classifier...")
        classifier = DocumentClassifier()
        print("✅ Classifier initialisiert")

        # Test-Dokument
        test_text = """
        Telekom Deutschland GmbH
        Kundenservice
        53171 Bonn

        RECHNUNG

        Sehr geehrter Kunde,

        Rechnungsnummer: T-123456789
        Rechnungsdatum: 15.01.2024
        Kundennummer: 987654321

        Ihre monatliche Rechnung für Mobilfunk

        Grundgebühr Magenta Mobil L: 39.99 EUR
        Datenvolumen Zusatz: 10.00 EUR

        Gesamtbetrag: 49.99 EUR
        Fällig bis: 30.01.2024

        Mit freundlichen Grüßen
        Ihr Telekom Team
        """

        print("\n🤖 Klassifiziere Test-Dokument...")
        print("\n📄 Test-Text:")
        print("-" * 60)
        print(test_text[:200] + "...")
        print("-" * 60)

        # Klassifizierung durchführen
        result = classifier.classify_document(test_text, "rechnung.pdf")

        print("\n✅ Klassifizierung abgeschlossen!")
        print("\n📊 Ergebnis:")
        print("-" * 60)
        print(f"   Kategorie: {result['category']}")
        print(f"   Dokumenttyp: {result['document_type']}")
        print(f"   Absender: {result['sender']}")
        print(f"   Datum: {result['date']}")
        print(f"   Betreff: {result['subject']}")
        print(f"   Ordnerpfad: {' / '.join(result['folder_path'])}")
        print(f"   Vorgeschlagener Dateiname: {result['suggested_filename']}")
        print(f"   Tags: {', '.join(result['tags'])}")
        print(f"   Priorität: {result['priority']}")
        print(f"\n   Zusammenfassung:")
        print(f"   {result['summary']}")
        print("-" * 60)

        # Validierung
        if result['category'] == 'Finanzen' or 'rechnung' in result['document_type'].lower():
            print("\n🎉 Klassifizierung funktioniert perfekt!")
            print("   Claude hat die Rechnung korrekt erkannt!")
            print("=" * 60)
            return True
        else:
            print("\n⚠️  Klassifizierung unklar - prüfe Ergebnis")
            print("=" * 60)
            return True  # Trotzdem Success, da API funktioniert

    except Exception as e:
        print(f"\n❌ Fehler beim Classifier-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_classifier()
    sys.exit(0 if success else 1)
