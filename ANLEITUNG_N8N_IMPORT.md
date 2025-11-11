# 🚀 n8n Workflow Import-Anleitung

## 📥 Schritt 1: Workflow importieren

1. **n8n öffnen**
2. **Workflows** → **Import from File** (oder "+ Add Workflow" → "Import from File")
3. **Datei auswählen:** `n8n-kandidaten-zuordnung-workflow.json`
4. **Import** klicken

✅ Der Workflow wird jetzt geladen!

---

## ⚙️ Schritt 2: Notion Credentials einrichten

### Notion API Key erstellen (falls noch nicht vorhanden):

1. Gehe zu: https://www.notion.so/my-integrations
2. **New Integration** klicken
3. Name: `n8n Kandidaten-Zuordnung`
4. **Submit** klicken
5. **Internal Integration Token** kopieren

### In n8n hinzufügen:

1. **Credentials** → **Add Credential**
2. Typ: **Notion API**
3. Name: `Notion API`
4. API Key einfügen: `ntn_b25383296344tHs967NBb56EtuuXnKOqZ77vdBaosz610A`
5. **Save** klicken

### Notion Datenbanken freigeben:

⚠️ **WICHTIG:** Jede Datenbank muss für die Integration freigegeben werden!

1. Öffne deine **Kandidaten-Datenbank** in Notion
2. Klicke oben rechts auf **•••** (Drei Punkte)
3. **Connections** → **Add connection**
4. Wähle deine Integration: `n8n Kandidaten-Zuordnung`
5. **Wiederholen für:**
   - Fachgeschäfte-Datenbank
   - Aktuelle Arbeitgeber-Datenbank

---

## 🔧 Schritt 3: Credentials in Workflow zuweisen

In den folgenden Nodes die Notion Credentials zuweisen:

1. **📋 Kandidaten ohne Zuordnung**
2. **🏪 Fachgeschäfte laden**
3. **👔 Aktuelle Arbeitgeber laden**
4. **💾 Kandidat in Notion updaten**

**So geht's:**
- Node anklicken
- Unter **Credential** → Dropdown öffnen
- **Notion API** auswählen

---

## ✅ Schritt 4: Distanz festlegen

1. Klicke auf den Node: **⚙️ Distanz festlegen (10-100 km)**
2. Ändere den Wert bei `distanz`: **25** → z.B. **50**
3. Mögliche Werte: 10, 20, 30, 40, 50, 75, 100

---

## 🧪 Schritt 5: Testen

### Test 1: Einzelne Nodes testen

1. Klicke auf **📋 Kandidaten ohne Zuordnung**
2. Klicke **Execute Node**
3. Siehst du Kandidaten? ✅

Wiederhole für:
- **🏪 Fachgeschäfte laden** → Fachgeschäfte sichtbar?
- **👔 Aktuelle Arbeitgeber laden** → Arbeitgeber sichtbar?

### Test 2: Kompletten Workflow ausführen

1. Klicke **Execute Workflow** (oben rechts)
2. Beobachte den Fortschritt
3. Schaue in die **Console** (bei Node "🎯 Zuordnung berechnen")
4. Prüfe in **Notion**, ob Kandidaten zugeordnet wurden

---

## 🎯 So funktioniert der Workflow

```
START
  ↓
Distanz festlegen (z.B. 50 km)
  ↓
┌─────────────────────────────┐
│ Parallel laden:             │
│ - Kandidaten ohne Zuordnung │
│ - Fachgeschäfte             │
│ - Aktuelle Arbeitgeber      │
└─────────────────────────────┘
  ↓
Daten zusammenführen
  ↓
Zuordnung berechnen (Google Maps + Haversine)
  ↓
Loop über alle Zuordnungen
  ↓
IF: Hat Zuordnung?
  ├─ JA → Notion Update → Warten (Rate Limit) → zurück zu Loop
  └─ NEIN → Zusammenfassung
```

---

## 📊 Was macht der Code-Node?

Der **🎯 Zuordnung berechnen** Node:

1. ✅ Liest alle Kandidaten, Fachgeschäfte und Arbeitgeber
2. ✅ Nutzt Google Maps Geocoding API für Adressen
3. ✅ Berechnet Luftlinie (Haversine-Formel)
4. ✅ Findet nächstes Fachgeschäft innerhalb der Distanz
5. ✅ Berechnet auch Distanz zum aktuellen Arbeitgeber
6. ✅ Gibt strukturierte Ergebnisse zurück

**Console Output Beispiel:**
```
=== START ZUORDNUNG ===
Maximale Distanz: 50 km
Kandidaten: 15
Fachgeschäfte: 8
Arbeitgeber: 12
✓ Max Mustermann → Akustik Köln (12.3 km) | Akt. AG: 45.1 km
✓ Anna Schmidt → Hörgeräte Berlin (8.7 km)
✗ Peter Meyer: Kein Geschäft innerhalb 50 km
=== FERTIG! 12 Kandidaten zugeordnet ===
```

---

## ⚠️ Häufige Probleme & Lösungen

### Problem 1: "Error: Page not found"
**Lösung:** Datenbanken in Notion für Integration freigeben (siehe Schritt 2)

### Problem 2: "Authentication failed"
**Lösung:** Notion API Key prüfen und neu eingeben

### Problem 3: Keine Kandidaten gefunden
**Lösung:** Filter prüfen - Feld ` Zukünftiger Arbeitgeber` (mit Leerzeichen!) muss leer sein

### Problem 4: Google Maps API Fehler
**Lösung:**
- API Key prüfen
- Geocoding API aktiviert?
- Abrechnungskonto verknüpft?

### Problem 5: "Too many requests"
**Lösung:** Wait-Node Dauer erhöhen (100ms → 200ms)

---

## 🔄 Workflow anpassen

### Andere Distanzen testen:

Klicke auf **⚙️ Distanz festlegen** und ändere den Wert:
- `10` = nur sehr nahe Geschäfte
- `25` = Standard
- `50` = mittlere Reichweite
- `100` = große Reichweite

### Nur bestimmte Kandidaten verarbeiten:

Im Node **📋 Kandidaten ohne Zuordnung** → **Filters** hinzufügen:
```
Status = "Aktiv"
UND
Zukünftiger Arbeitgeber = leer
```

### Andere Datenbanken nutzen:

Ändere die Database IDs in den Notion-Nodes:
- Kandidaten: `b3f1eeab2d1a42f2a9ba9792568bc217`
- Fachgeschäfte: `c6d33fd30f924e6d87fe4cb9fdb2c2aa`
- Arbeitgeber: `29a0974bd6228043850bf887c636d116`

---

## 📈 Performance-Tipps

1. **Geocoding-Cache:** Ist bereits eingebaut! Adressen werden nur 1x pro Lauf geocodiert
2. **Rate Limiting:** Wait-Node verhindert Notion API-Fehler
3. **Batch-Processing:** Loop verarbeitet Kandidaten einzeln (verhindert Timeout)

---

## 🎉 Fertig!

Jetzt können Sie:
- ✅ Distanz beliebig anpassen (10-100 km)
- ✅ Workflow manuell ausführen
- ✅ Oder per Webhook/Zeitplan automatisieren

Bei Fragen oder Problemen schauen Sie in die **Console-Logs** der einzelnen Nodes!

---

## 📞 Support

Bei Fehlern:
1. Schaue in die **Execution Log** (jeder Node zeigt Output)
2. Prüfe **Console** im Code-Node
3. Teste Notion-Zugriff einzeln

Viel Erfolg! 🚀
