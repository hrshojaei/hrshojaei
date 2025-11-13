# Notion Settings-Datenbank Anleitung

## Schritt 1: Settings-Datenbank in Notion erstellen

1. **Neue Datenbank erstellen** in deinem Notion Workspace
   - Name: `Workflow-Einstellungen`

2. **Felder konfigurieren:**
   - **Name** (Title/Text): bereits vorhanden
   - **Gewünschte Distanz** (Select): Neu erstellen mit Optionen:
     - `10km`
     - `20km`
     - `50km`
     - `75km`
     - `100km`

3. **Einen Eintrag erstellen:**
   - **Name**: `Distanz-Einstellung`
   - **Gewünschte Distanz**: Wähle z.B. `50km`

## Schritt 2: Datenbank-ID kopieren

1. Öffne die `Workflow-Einstellungen` Datenbank in Notion
2. Kopiere die URL - sie sieht so aus:
   ```
   https://www.notion.so/YOUR_WORKSPACE/1234567890abcdef1234567890abcdef?v=...
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                         Dies ist die Database ID
   ```
3. Kopiere die **32-stellige ID** (zwischen letztem `/` und `?`)

## Schritt 3: Workflow konfigurieren

1. **Workflow importieren** in n8n
2. **Node öffnen:** `⚙️ Settings aus Notion laden`
3. **Database ID einfügen:**
   - Ersetze `SETTINGS_DATABASE_ID_HIER_EINFUEGEN` mit deiner kopierten ID
4. **Workflow speichern**

## Schritt 4: Testen

1. **Workflow ausführen** (Execute Workflow)
2. Prüfe im Console Log: `=== DISTANZ AUS NOTION: 50 km ===`
3. Fertig! Der Workflow nutzt jetzt die Distanz aus Notion

## Für den Endbenutzer

Der Endbenutzer arbeitet **nur in Notion**:

1. Öffne `Workflow-Einstellungen` Datenbank
2. Ändere `Gewünschte Distanz` auf gewünschten Wert (z.B. `75km`)
3. Fertig!

Der Workflow läuft dann entweder:
- **Manuell** in n8n (Execute Workflow)
- **Automatisch** per Cron/Schedule Trigger (täglich um 10 Uhr)
- **Per Webhook** aus Notion Automation (Button in Notion)

---

## Felder-Namen in Notion

Wichtig: Die Feld-Namen müssen **exakt** so heißen:
- `Name` (Title)
- `Gewünschte Distanz` (Select)

Der Workflow liest das Feld als `property_gewunschte_distanz` (Umlaute werden zu normalen Buchstaben, Leerzeichen zu Unterstrichen).
