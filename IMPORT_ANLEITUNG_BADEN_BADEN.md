# 📊 Test-Kandidaten für Baden-Baden

## 🎯 **Speziell für Fachgeschäfte in Baden-Baden**

Diese Test-Kandidaten sind rund um Baden-Baden verteilt, um verschiedene Distanzen zu testen.

---

## 📁 **CSV-Dateien**

### **1. test-kandidaten-baden-baden.csv** (Basis)
- 20 Kandidaten rund um Baden-Baden
- Distanzen: 0-55 km
- Schneller Import

### **2. test-kandidaten-baden-baden-erweitert.csv** (Vollständig)
- 20 Kandidaten mit allen Feldern
- Inkl. erwartete Distanz-Angabe
- Für detaillierten Test

---

## 📍 **Kandidaten-Verteilung nach Entfernung**

### **0-5 km (Direkt in Baden-Baden):**
```
✅ Max Mustermann (Sophienstraße)
✅ Anna Schmidt (Lichtentaler Straße)
```
**Erwartung:** Bei JEDEM Radius gefunden (10, 20, 50, 100 km)

---

### **10 km (Rastatt):**
```
✅ Peter Müller (Hauptstraße Rastatt)
✅ Lisa Weber (Kaiserstraße Rastatt)
```
**Erwartung:** Ab 10 km Radius gefunden

---

### **15-20 km (Bühl & Gaggenau):**
```
✅ Thomas Becker (Bühl)
✅ Sarah Klein (Bühl)
✅ Felix Krause (Gaggenau)
✅ Nina Lehmann (Gaggenau)
```
**Erwartung:** Ab 20 km Radius gefunden

---

### **25 km (Achern):**
```
✅ Michael Fischer (Achern)
✅ Julia Hoffmann (Achern)
```
**Erwartung:** Ab 25-30 km Radius gefunden

---

### **30-40 km (Ettlingen, Malsch, Pfinztal):**
```
✅ Martin Bauer (Ettlingen)
✅ Katharina Richter (Ettlingen)
✅ Andreas Meyer (Malsch)
✅ Christina Wolf (Pfinztal)
```
**Erwartung:** Ab 40 km Radius gefunden

---

### **45 km (Karlsruhe):**
```
✅ Jan Zimmermann (Karlsruhe)
✅ Laura Schneider (Karlsruhe)
```
**Erwartung:** Ab 50 km Radius gefunden

---

### **55 km (Freudenstadt):**
```
✅ Tobias Koch (Freudenstadt)
✅ Maria Lang (Freudenstadt)
```
**Erwartung:** Ab 60 km oder 100 km Radius gefunden

---

### **35 km (Offenburg):**
```
✅ Daniel Wagner (Offenburg)
✅ Sophie Schulz (Offenburg)
```
**Erwartung:** Ab 40 km Radius gefunden

---

## 🧪 **Test-Szenarien**

### **Test 1: Nur direkte Umgebung (10 km)**
```
Distanz: 10 km
Erwartete Zuordnungen: 4 Kandidaten
- Max Mustermann (Baden-Baden)
- Anna Schmidt (Baden-Baden)
- Peter Müller (Rastatt)
- Lisa Weber (Rastatt)
```

### **Test 2: Erweiterte Umgebung (25 km)**
```
Distanz: 25 km
Erwartete Zuordnungen: 10 Kandidaten
- Alle von Test 1
- + Bühl (2)
- + Gaggenau (2)
- + Achern (2)
```

### **Test 3: Große Reichweite (50 km)**
```
Distanz: 50 km
Erwartete Zuordnungen: 16 Kandidaten
- Alle von Test 2
- + Ettlingen (2)
- + Malsch (1)
- + Pfinztal (1)
- + Karlsruhe (2)
```

### **Test 4: Maximale Reichweite (100 km)**
```
Distanz: 100 km
Erwartete Zuordnungen: 20 Kandidaten (ALLE!)
- Alle von Test 3
- + Offenburg (2)
- + Freudenstadt (2)
```

---

## 📥 **Import in Notion**

### **Schritt 1: CSV hochladen**
```
Notion → Kandidaten-Datenbank
→ ••• → Import → CSV
→ test-kandidaten-baden-baden.csv wählen
```

### **Schritt 2: Spalten zuordnen**
```
CSV-Spalte → Notion-Property
Name → Name
Wohnadresse → Wohnadresse
Status → Status
etc.
```

### **Schritt 3: Import bestätigen**
```
→ Import klicken
→ 20 Kandidaten werden hinzugefügt
```

---

## ✅ **Workflow testen**

### **Test 1: 10 km Radius**
```
1. n8n öffnen: https://8n8ai.de
2. Workflow öffnen
3. Node "⚙️ Distanz festlegen" → value: 10
4. Execute Workflow
5. Prüfen: 4 Kandidaten zugeordnet?
```

### **Test 2: 25 km Radius**
```
1. Zuordnungen in Notion löschen (Feld "Zukünftiger Arbeitgeber" leeren)
2. Node "⚙️ Distanz festlegen" → value: 25
3. Execute Workflow
4. Prüfen: 10 Kandidaten zugeordnet?
```

### **Test 3: 50 km Radius**
```
1. Zuordnungen löschen
2. Distanz → 50
3. Execute
4. Prüfen: 16 Kandidaten?
```

### **Test 4: 100 km Radius**
```
1. Zuordnungen löschen
2. Distanz → 100
3. Execute
4. Prüfen: ALLE 20 Kandidaten?
```

---

## 🗺️ **Karte der Kandidaten**

```
                Karlsruhe (45 km)
                    ↑
                    |
        Ettlingen (30 km)
             ↑
             |
    Rastatt (10 km)
         ↑
         |
    BADEN-BADEN (0 km) ← Ihre Fachgeschäfte
         |
         ↓
    Gaggenau (18 km)
         |
         ↓
    Achern (25 km)
         |
         ↓
    Offenburg (35 km)


    Freudenstadt (55 km) →
```

---

## 🔍 **Troubleshooting**

### **Problem: Weniger Kandidaten als erwartet**

**Mögliche Ursachen:**
1. **Fachgeschäft-Adresse ungenau**
   - Prüfen Sie in Notion die Adresse Ihrer Fachgeschäfte
   - Format: "Straße Hausnummer PLZ Ort"
   - Beispiel: "Lichtentaler Straße 10 76530 Baden-Baden"

2. **Google Maps findet Adresse nicht**
   - Schauen Sie im Code-Node in die Console-Logs
   - Zeigt es "Adresse nicht gefunden"?

3. **Distanz-Berechnung falsch**
   - Luftlinie vs. Straßenentfernung
   - Unsere Berechnung nutzt Luftlinie (Haversine)

---

### **Problem: Alle Kandidaten zugeordnet (auch bei 10 km)**

**Ursache:** Filter funktioniert nicht

**Lösung:**
- Im Code-Node prüfen: `MAX_DISTANZ_KM` wird korrekt gesetzt?
- Console-Log checken: Zeigt es die richtige Distanz?

---

### **Problem: Gar keine Zuordnungen**

**Ursache:** Fachgeschäfte-Datenbank leer oder falsche Adressen

**Lösung:**
1. Prüfen Sie die Fachgeschäfte-Datenbank in Notion
2. Mindestens 1 Geschäft in Baden-Baden muss existieren
3. Mit korrekter Adresse!

---

## 📊 **Nach dem Test**

### **Test-Daten löschen:**
```
Notion → Kandidaten-Datenbank
→ Filter: Status = "Aktiv", "Interessiert", "Passiv"
→ Alle auswählen → Delete
```

### **Oder einzeln:**
```
Filter: Name contains "Mustermann"
→ Delete
```

---

## ✅ **Bereit!**

Importieren Sie die CSV und testen Sie verschiedene Distanz-Radien!

**Erwartete Ergebnisse:**
- 10 km → 4 Kandidaten
- 25 km → 10 Kandidaten
- 50 km → 16 Kandidaten
- 100 km → 20 Kandidaten

Viel Erfolg! 🚀
