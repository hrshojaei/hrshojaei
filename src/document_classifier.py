"""
KI-basierter Dokumenten-Klassifizierer.
Nutzt Claude AI zur intelligenten Kategorisierung von Dokumenten.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import re
from loguru import logger

from src.config import get_settings


class DocumentClassifier:
    """KI-basierter Klassifizierer für Dokumente."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert den Classifier.

        Args:
            api_key: API Key (optional, sonst aus Settings)
        """
        settings = get_settings()
        self.provider = settings.ai_provider

        if self.provider == "anthropic":
            from anthropic import Anthropic
            api_key = api_key or settings.anthropic_api_key
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY nicht gesetzt!")
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"

        elif self.provider in ["openai", "perplexity"]:
            from openai import OpenAI
            api_key = api_key or settings.openai_api_key
            if not api_key:
                raise ValueError("OPENAI_API_KEY nicht gesetzt!")

            # Perplexity uses OpenAI-compatible API
            if self.provider == "perplexity":
                base_url = settings.openai_base_url or "https://api.perplexity.ai"
                self.client = OpenAI(api_key=api_key, base_url=base_url)
                self.model = settings.openai_model or "llama-3.1-sonar-large-128k-online"
            else:
                self.client = OpenAI(api_key=api_key)
                self.model = settings.openai_model or "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Unbekannter AI_PROVIDER: {self.provider}")

        logger.info(f"Document Classifier initialisiert ({self.provider})")

    def classify_document(self, text: str, filename: Optional[str] = None) -> Dict:
        """
        Klassifiziert ein Dokument basierend auf seinem Inhalt.

        Args:
            text: Extrahierter Text aus dem Dokument
            filename: Originaler Dateiname (optional)

        Returns:
            Dict mit Kategorisierungs-Informationen
        """
        logger.info(f"Klassifiziere Dokument: {filename or 'unbekannt'}")

        # Prompt für Claude
        system_prompt = """Du bist ein Experte für die Kategorisierung von Dokumenten.
Analysiere den gegebenen Text und kategorisiere das Dokument.

Deine Aufgabe:
1. Erkenne den Dokumenttyp (z.B. Rechnung, Vertrag, Behördenbrief, etc.)
2. Extrahiere wichtige Metadaten (Datum, Absender, Betreff, etc.)
3. Schlage eine intelligente Ordnerstruktur vor
4. Erstelle einen aussagekräftigen Dateinamen

Antworte IMMER im folgenden JSON-Format:
{
    "category": "Hauptkategorie des Dokuments",
    "subcategory": "Unterkategorie (optional)",
    "document_type": "Genauer Dokumenttyp",
    "sender": "Absender des Dokuments",
    "date": "Datum im Format YYYY-MM-DD",
    "subject": "Betreff/Thema des Dokuments",
    "folder_path": ["Ordner1", "Ordner2", "Ordner3"],
    "suggested_filename": "vorgeschlagener_dateiname.pdf",
    "tags": ["Tag1", "Tag2"],
    "priority": "low/medium/high",
    "summary": "Kurze Zusammenfassung (1-2 Sätze)"
}

Verfügbare Hauptkategorien:
- Finanzen (Rechnungen, Kontoauszüge, Steuern)
- Versicherungen (Krankenversicherung, Haftpflicht, etc.)
- Behörden (Ämter, Steuerbescheide, Meldebescheinigungen)
- Gesundheit (Arztbriefe, Rezepte, Befunde)
- Verträge (Miet-, Arbeits-, Kaufverträge)
- Post (allgemeine Korrespondenz)
- Bildung (Zeugnisse, Zertifikate)
- Arbeit (Gehaltsabrechnungen, Arbeitgeberbescheinigungen)
- Wohnung (Nebenkostenabrechnung, Hauspost)
- Sonstiges

Sei präzise und nutze deutsche Begriffe."""

        user_prompt = f"""Analysiere folgendes Dokument:

Dateiname: {filename or 'unbekannt'}

Text:
{text[:4000]}  # Limitiere auf 4000 Zeichen

Antworte NUR mit dem JSON-Objekt, ohne zusätzlichen Text."""

        try:
            # API Call basierend auf Provider
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                response_text = response.content[0].text

            elif self.provider in ["openai", "perplexity"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                response_text = response.choices[0].message.content

            logger.debug(f"AI Response: {response_text}")

            # JSON extrahieren
            result = self._parse_json_response(response_text)

            # Validierung & Defaults
            result = self._validate_and_enhance(result, filename)

            logger.info(f"Dokument klassifiziert: {result['category']} / {result['document_type']}")
            return result

        except Exception as e:
            logger.error(f"Fehler bei Klassifizierung: {e}")
            # Fallback
            return self._create_fallback_classification(filename)

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parst JSON aus Claude Response."""
        try:
            # Versuche direktes JSON-Parsing
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Extrahiere JSON aus Markdown Code-Block
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Extrahiere JSON ohne Code-Block
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            raise ValueError("Kein gültiges JSON in Response gefunden")

    def _validate_and_enhance(self, result: Dict, filename: Optional[str]) -> Dict:
        """Validiert und ergänzt Klassifizierungs-Ergebnis."""
        # Defaults setzen
        defaults = {
            'category': 'Sonstiges',
            'subcategory': None,
            'document_type': 'Unbekannt',
            'sender': 'Unbekannt',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'subject': 'Kein Betreff',
            'folder_path': ['Dokumente', 'Unsortiert'],
            'suggested_filename': filename or 'dokument.pdf',
            'tags': [],
            'priority': 'medium',
            'summary': 'Keine Zusammenfassung verfügbar'
        }

        # Merge mit Defaults
        for key, value in defaults.items():
            if key not in result or not result[key]:
                result[key] = value

        # Datum validieren
        if not self._is_valid_date(result['date']):
            result['date'] = datetime.now().strftime('%Y-%m-%d')

        # Folder-Path sicherstellen
        if not isinstance(result['folder_path'], list):
            result['folder_path'] = ['Dokumente', result['category']]

        # Tags normalisieren
        if not isinstance(result['tags'], list):
            result['tags'] = []

        return result

    def _is_valid_date(self, date_str: str) -> bool:
        """Prüft ob Datum im Format YYYY-MM-DD."""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except:
            return False

    def _create_fallback_classification(self, filename: Optional[str]) -> Dict:
        """Erstellt Fallback-Klassifizierung wenn KI fehlschlägt."""
        return {
            'category': 'Sonstiges',
            'subcategory': None,
            'document_type': 'Unbekanntes Dokument',
            'sender': 'Unbekannt',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'subject': 'Automatisch sortiert',
            'folder_path': ['Dokumente', 'Unsortiert'],
            'suggested_filename': filename or f"dokument_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            'tags': ['unsortiert'],
            'priority': 'low',
            'summary': 'Konnte nicht automatisch klassifiziert werden'
        }

    def suggest_folder_structure(self, categories: List[str]) -> Dict[str, List[str]]:
        """
        Schlägt intelligente Ordnerstruktur für Kategorien vor.

        Args:
            categories: Liste von Dokumentkategorien

        Returns:
            Dict mit {kategorie: [ordner_pfad]}
        """
        structure = {}

        for category in categories:
            if category == 'Finanzen':
                structure[category] = [
                    'Finanzen/Rechnungen',
                    'Finanzen/Kontoauszüge',
                    'Finanzen/Steuern',
                    'Finanzen/Belege'
                ]
            elif category == 'Versicherungen':
                structure[category] = [
                    'Versicherungen/Krankenversicherung',
                    'Versicherungen/Haftpflicht',
                    'Versicherungen/Sonstige'
                ]
            elif category == 'Behörden':
                structure[category] = [
                    'Behörden/Finanzamt',
                    'Behörden/Einwohnermeldeamt',
                    'Behörden/Sonstige'
                ]
            elif category == 'Gesundheit':
                structure[category] = [
                    'Gesundheit/Arztbriefe',
                    'Gesundheit/Rezepte',
                    'Gesundheit/Befunde'
                ]
            elif category == 'Verträge':
                structure[category] = [
                    'Verträge/Mietvertrag',
                    'Verträge/Arbeitsvertrag',
                    'Verträge/Sonstige'
                ]
            elif category == 'Arbeit':
                structure[category] = [
                    'Arbeit/Gehaltsabrechnungen',
                    'Arbeit/Bescheinigungen',
                    'Arbeit/Sonstiges'
                ]
            elif category == 'Wohnung':
                structure[category] = [
                    'Wohnung/Nebenkosten',
                    'Wohnung/Hauspost',
                    'Wohnung/Sonstiges'
                ]
            else:
                structure[category] = [f'{category}']

        return structure


def create_classifier(api_key: Optional[str] = None) -> DocumentClassifier:
    """
    Factory-Funktion zum Erstellen eines Classifiers.

    Args:
        api_key: API Key (optional)

    Returns:
        DocumentClassifier Instanz
    """
    return DocumentClassifier(api_key=api_key)
