# 📊 Test-Kandidaten in Notion importieren

## 📁 Verfügbare CSV-Dateien

### 1. **test-kandidaten.csv** (Basis)
- 20 Test-Kandidaten
- Wichtigste Felder
- Schneller Import

### 2. **test-kandidaten-erweitert.csv** (Vollständig)
- 20 Test-Kandidaten
- Alle Felder inkl. Gehalt, Geburtsdatum, etc.
- Für kompletten Test

---

## 📥 **Import in Notion - Schritt für Schritt**

### **Methode 1: CSV direkt in Notion importieren**

1. **Notion öffnen:** https://notion.so

2. **Kandidaten-Datenbank öffnen**

3. **Import-Funktion:**
   - Oben rechts: **•••** (Drei Punkte)
   - **Import** wählen
   - **CSV** auswählen

4. **CSV-Datei hochladen:**
   - `test-kandidaten.csv` oder `test-kandidaten-erweitert.csv`
   - **Import** klicken

5. **Spalten zuordnen:**
   - Notion fragt welche CSV-Spalte zu welcher Notion-Property gehört
   - Zuordnung prüfen und bestätigen

6. **Fertig!** ✅

---

### **Methode 2: Via Copy & Paste**

1. **CSV in Excel/Google Sheets öffnen**

2. **Alle Zeilen markieren und kopieren**

3. **In Notion:**
   - Kandidaten-Datenbank öffnen
   - Unten auf leere Zeile klicken
   - **STRG+V** (oder CMD+V)
   - Notion erkennt automatisch die Spalten

4. **Fertig!** ✅

---

## 🎯 **Test-Kandidaten Übersicht**

### **Städte-Verteilung:**
```
Stuttgart:     4 Kandidaten
Frankfurt:     2 Kandidaten
München:       4 Kandidaten
Köln:          1 Kandidat
Hamburg:       1 Kandidat
Heidelberg:    2 Kandidaten
Düsseldorf:    1 Kandidat
Leipzig:       2 Kandidaten
Berlin:        1 Kandidat
Dresden:       1 Kandidat
Karlsruhe:     1 Kandidat
Mainz:         1 Kandidat
```

### **Status-Verteilung:**
```
Aktiv:         13 Kandidaten (sehr interessiert)
Interessiert:  5 Kandidaten (moderat interessiert)
Passiv:        2 Kandidaten (nur bei gutem Angebot)
```

### **Positionen:**
```
Hörgeräteakustiker:         9
Hörgeräteakustiker-Meister: 4
Filialleitung:              2
Hörgeräteakustikerin:       5
```

---

## 🧪 **Workflow testen**

**Nach dem Import:**

1. **Alle Kandidaten haben KEINE Zuordnung**
   - Feld "Zukünftiger Arbeitgeber" ist leer
   - Perfekt zum Testen!

2. **n8n Workflow ausführen:**
   - Distanz setzen (z.B. 50 km)
   - Execute Workflow
   - Kandidaten werden automatisch zugeordnet

3. **Erwartetes Ergebnis:**
   - Stuttgart-Kandidaten → Fachgeschäft in Stuttgart
   - München-Kandidaten → Fachgeschäft in München
   - etc.

---

## 📊 **Erwartete Zuordnungen (Beispiel bei 50 km Radius)**

Abhängig von Ihren Fachgeschäften in Notion!

**Falls Sie Geschäfte in diesen Städten haben:**
- ✅ Stuttgart (4 Kandidaten) → Sollten zugeordnet werden
- ✅ München (4 Kandidaten) → Sollten zugeordnet werden
- ✅ Frankfurt (2 Kandidaten) → Sollten zugeordnet werden

**Falls nicht:**
- ❌ Kandidaten ohne passendes Geschäft → Bleiben ohne Zuordnung

---

## 🗑️ **Test-Daten wieder löschen**

**Nach dem Test:**

1. **In Notion:**
   - Filtern Sie nach Status = "Aktiv", "Interessiert", "Passiv"
   - Alle Test-Kandidaten markieren
   - **Delete** klicken

2. **Oder Filter nutzen:**
   ```
   Name contains "Mustermann" OR
   Name contains "Schmidt" OR
   Name contains "Müller" OR
   ...
   ```

3. **Bulk-Delete:**
   - Alle auswählen → Löschen

---

## 🔍 **Troubleshooting**

### **Problem: Spalten passen nicht**

**Lösung:**
- Notion-Spalten VORHER umbenennen
- Oder CSV-Header anpassen

### **Problem: Datum-Format falsch**

**Lösung:**
- Geburtsdatum ist im Format: DD.MM.YYYY
- Falls Notion ISO will: In CSV ändern zu YYYY-MM-DD

### **Problem: Telefonnummern als Zahl interpretiert**

**Lösung:**
- In CSV sind sie mit +49 Vorwahl (wird als Text erkannt)
- Falls Problem: Spalte in Notion als "Text" setzen

---

## ✅ **Bereit zum Import!**

Wählen Sie eine der beiden CSV-Dateien und importieren Sie sie in Notion!

**Dann:**
1. n8n Workflow ausführen
2. Schauen ob Zuordnungen funktionieren
3. Ergebnis prüfen

Viel Erfolg! 🚀
