# Contributing to AI Calling Agent

Vielen Dank für dein Interesse, zum AI Calling Agent beizutragen! Dieses Dokument beschreibt, wie du am besten beitragen kannst.

## Wie kann ich beitragen?

### 🐛 Bugs melden

Wenn du einen Bug findest:
1. Prüfe, ob der Bug bereits als Issue existiert
2. Erstelle ein neues Issue mit:
   - Klare Beschreibung des Problems
   - Schritte zum Reproduzieren
   - Erwartetes vs. tatsächliches Verhalten
   - Log-Ausgaben (falls relevant)
   - Umgebung (Python-Version, OS, etc.)

### 💡 Features vorschlagen

Neue Feature-Ideen sind willkommen:
1. Erstelle ein Issue mit dem Tag "enhancement"
2. Beschreibe:
   - Was das Feature macht
   - Warum es nützlich wäre
   - Mögliche Implementierung (optional)

### 📝 Code beitragen

#### Setup für Entwicklung

```bash
# Repository forken und klonen
git clone https://github.com/your-username/calling-agent.git
cd calling-agent

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Pre-commit hooks installieren (optional)
pip install pre-commit
pre-commit install
```

#### Workflow

1. **Branch erstellen**
   ```bash
   git checkout -b feature/dein-feature-name
   # oder
   git checkout -b fix/bug-beschreibung
   ```

2. **Code schreiben**
   - Folge dem bestehenden Code-Stil
   - Füge Docstrings hinzu
   - Schreibe Tests (falls zutreffend)

3. **Tests ausführen**
   ```bash
   # Unit tests (wenn vorhanden)
   pytest tests/

   # Manuelle Tests
   python -m src.candidate_manager init
   python -m src.main add
   ```

4. **Committen**
   ```bash
   git add .
   git commit -m "feat: Beschreibung deines Features"
   # oder
   git commit -m "fix: Beschreibung des Bugfixes"
   ```

   **Commit-Message-Format:**
   - `feat:` - Neues Feature
   - `fix:` - Bugfix
   - `docs:` - Dokumentation
   - `style:` - Code-Formatierung
   - `refactor:` - Code-Refactoring
   - `test:` - Tests hinzufügen
   - `chore:` - Build/Tool-Änderungen

5. **Push und Pull Request**
   ```bash
   git push origin feature/dein-feature-name
   ```
   Erstelle dann einen Pull Request auf GitHub.

## Code-Stil

### Python

- **PEP 8** Standard befolgen
- **Type Hints** verwenden wo möglich
- **Docstrings** für alle Funktionen und Klassen

Beispiel:
```python
def add_candidate(
    self,
    name: str,
    phone: str,
    email: Optional[str] = None
) -> int:
    """
    Add a new candidate to the database

    Args:
        name: Full name of the candidate
        phone: Phone number with country code
        email: Optional email address

    Returns:
        The ID of the newly created candidate

    Raises:
        ValueError: If name or phone is empty
    """
    # Implementation
    pass
```

### Logging

Nutze `loguru` für Logging:
```python
from loguru import logger

logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

### Error Handling

```python
try:
    # Code
    pass
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    # Handle error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle generic error
```

## Projektstruktur

```
calling-agent/
├── src/
│   ├── main.py              # FastAPI server & CLI
│   ├── config.py            # Konfiguration
│   ├── candidate_manager.py # Datenbank-Management
│   ├── ai_engine.py         # AI-Konversation
│   ├── twilio_client.py     # Twilio-Integration
│   ├── call_handler.py      # Call-Flow-Logik
│   └── prompts.py           # Conversation Templates
├── scripts/                 # Utility Scripts
├── data/                    # Datenbank (gitignored)
├── logs/                    # Log-Dateien (gitignored)
└── tests/                   # Tests (noch zu erstellen)
```

## Testing

### Manuelle Tests

Vor einem PR, teste folgende Szenarien:

1. **Kandidaten-Management**
   ```bash
   python -m src.main add
   python -m src.main stats
   ```

2. **Server-Start**
   ```bash
   python -m src.main server
   # In anderem Terminal:
   curl http://localhost:8000/
   ```

3. **Test-Anruf** (falls Twilio konfiguriert)
   ```bash
   python -m src.main call +49XXXXXXXXX
   ```

### Unit Tests (TODO)

Wir suchen noch Beiträge für Unit Tests! Bereiche:
- `candidate_manager.py` - Datenbank-Operationen
- `ai_engine.py` - AI-Response-Logik
- `call_handler.py` - Call-Flow
- `twilio_client.py` - TwiML-Generierung

## Dokumentation

Beiträge zur Dokumentation sind sehr willkommen:
- README.md verbessern
- QUICKSTART.md erweitern
- Code-Kommentare hinzufügen
- Beispiele erstellen

## Pull Request Prozess

1. Stelle sicher, dass dein Code den Style-Guidelines folgt
2. Update die README.md falls nötig
3. Update die CHANGELOG.md (falls vorhanden)
4. Der PR wird von einem Maintainer reviewt
5. Nach Approval wird gemerged

## Lizenz

Durch deinen Beitrag stimmst du zu, dass deine Beiträge unter der MIT-Lizenz lizenziert werden.

## Fragen?

Bei Fragen:
- Erstelle ein Issue
- Oder kontaktiere die Maintainer

Vielen Dank für deinen Beitrag! 🙏
