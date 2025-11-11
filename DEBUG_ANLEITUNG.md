# Debug-Anleitung für n8n Workflow

## Problem
Der Workflow findet die Fachgeschäfte nicht: "Keine Fachgeschäfte gefunden!"

## Lösung: Debug-Script ausführen

### Schritt 1: Debug-Script einfügen

1. Öffnen Sie Ihren n8n Workflow
2. Klicken Sie auf den Node **"🎯 Zuordnung berechnen"**
3. **LÖSCHEN** Sie den kompletten bestehenden Code
4. Kopieren Sie den kompletten Code aus `n8n-debug-script.js`
5. Fügen Sie ihn ein
6. Klicken Sie auf **"Execute Node"**

### Schritt 2: Console-Log überprüfen

Nach der Ausführung:

1. Scrollen Sie im Output-Bereich nach unten
2. Suchen Sie nach dem **Console-Log Symbol** (oft ein kleines Terminal/Console Icon)
3. Klicken Sie darauf, um die Console-Logs zu öffnen

### Schritt 3: Wichtige Informationen finden

In den Console-Logs sehen Sie:

#### A) Gesamt-Übersicht
```
=== DEBUG START ===
Gesamt Items: 20
```

#### B) Details für jedes Item
```
--- Item 1 ---
Alle Properties:
  property_name: Max Mustermann
  property_wohnadresse: Lichtentaler Straße 10, 76530 Baden-Baden
  property_status: Neu
  ...
```

#### C) Kategorisierung
```
=== KATEGORISIERUNG ===
Kandidaten gefunden: 15
  Adress-Feld: property_wohnadresse
  Alle Properties: id, property_name, property_wohnadresse, ...

Fachgeschäfte gefunden: 5
  Adress-Feld: property_adresse
  Alle Properties: id, property_name, property_adresse, ...
```

### Schritt 4: Informationen an mich senden

Bitte kopieren Sie die folgenden Informationen aus dem Console-Log und senden Sie sie mir:

1. **Gesamt Items**: Die Zahl bei "Gesamt Items"
2. **Kandidaten gefunden**: Die Zahl und das "Adress-Feld"
3. **Fachgeschäfte gefunden**: Die Zahl und das "Adress-Feld"
4. **Alle Properties von einem Fachgeschäft**: Die komplette Liste

Beispiel was ich brauche:
```
Kandidaten gefunden: 15
  Adress-Feld: property_wohnadresse

Fachgeschäfte gefunden: 5
  Adress-Feld: property_adresse_
  Alle Properties: id, property_name, property_adresse_, property_telefon, ...
```

### Schritt 5: Problem identifizieren

Mit diesen Informationen kann ich:
- Den exakten Property-Namen für Fachgeschäft-Adressen sehen
- Verstehen, warum sie nicht erkannt werden
- Den korrekten Code erstellen

## Mögliche Szenarien

### Szenario 1: Fachgeschäfte gefunden = 0
➡️ Die Fachgeschäfte-Datenbank ist nicht mit dem Workflow verbunden
➡️ Prüfen Sie im Node "📍 Notion - Fachgeschäfte laden" ob Daten kommen

### Szenario 2: Fachgeschäfte gefunden > 0 aber Adress-Feld ist anders
➡️ Der Property-Name ist nicht "property_adresse"
➡️ Ich passe den Code an den korrekten Namen an

### Szenario 3: Alle Items sind "Unbekannt"
➡️ Die Property-Namen sind komplett anders als erwartet
➡️ Wir müssen die Erkennungslogik komplett neu aufbauen

## Nächster Schritt

Nachdem Sie mir die Debug-Informationen gesendet haben, erstelle ich den korrekten Code für die Zuordnung.
