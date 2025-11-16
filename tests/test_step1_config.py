#!/usr/bin/env python3
"""
SCHRITT 1: Configuration testen
"""

import sys
from pathlib import Path

# Füge src zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings

def test_config():
    """Teste ob Config geladen werden kann."""
    print("=" * 60)
    print("SCHRITT 1: Configuration Test")
    print("=" * 60)

    try:
        settings = get_settings()
        print("\n✅ Config erfolgreich geladen!")
        print(f"\n📋 Aktuelle Einstellungen:")
        print(f"   - Log Level: {settings.log_level}")
        print(f"   - Document Base Folder: {settings.document_base_folder_name}")
        print(f"   - Polling Interval: {settings.document_polling_interval_minutes} Min")
        print(f"   - Convert Images to PDF: {settings.convert_images_to_pdf}")
        print(f"   - Use Cloud Vision: {settings.use_cloud_vision_ocr}")

        # Prüfe ob kritische Keys gesetzt sind
        print(f"\n🔑 API Keys Status:")
        print(f"   - Anthropic API Key: {'✅ Gesetzt' if settings.anthropic_api_key else '❌ Nicht gesetzt'}")
        print(f"   - Telegram Bot Token: {'✅ Gesetzt' if settings.telegram_bot_token else '❌ Nicht gesetzt'}")

        if not settings.anthropic_api_key:
            print("\n⚠️  WARNUNG: ANTHROPIC_API_KEY nicht in .env gesetzt!")
            print("   Setzen Sie in .env: ANTHROPIC_API_KEY=sk-ant-...")

        if not settings.telegram_bot_token:
            print("\n⚠️  WARNUNG: TELEGRAM_BOT_TOKEN nicht in .env gesetzt!")
            print("   Setzen Sie in .env: TELEGRAM_BOT_TOKEN=...")

        print("\n" + "=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Fehler beim Laden der Config: {e}")
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
