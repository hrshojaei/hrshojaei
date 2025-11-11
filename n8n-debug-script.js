// DEBUG SCRIPT - Zeigt alle Property-Namen für jedes Item
// Diesen Code in den "🎯 Zuordnung berechnen" Node einfügen

const items = $input.all();

console.log("=== DEBUG START ===");
console.log(`Gesamt Items: ${items.length}`);

// Für jedes Item alle Properties anzeigen
items.forEach((item, index) => {
  const data = item.json;
  console.log(`\n--- Item ${index + 1} ---`);
  console.log("Alle Properties:");

  const propertyNames = Object.keys(data);
  propertyNames.forEach(propName => {
    const value = data[propName];

    // Nur nicht-leere Werte anzeigen
    if (value !== null && value !== undefined && value !== '') {
      // Bei Strings nur ersten 50 Zeichen zeigen
      const displayValue = typeof value === 'string' ?
        (value.length > 50 ? value.substring(0, 50) + '...' : value) :
        JSON.stringify(value).substring(0, 50);

      console.log(`  ${propName}: ${displayValue}`);
    }
  });
});

// Jetzt versuchen wir die Items zu kategorisieren
console.log("\n=== KATEGORISIERUNG ===");

const kandidaten = [];
const fachgeschaefte = [];
const arbeitgeber = [];
const unbekannt = [];

for (const item of items) {
  const data = item.json;
  const propertyNames = Object.keys(data);

  // Suche nach Adress-Feldern
  const hasWohnadresse = propertyNames.some(p =>
    p.toLowerCase().includes('wohnadresse')
  );
  const hasAdresse = propertyNames.some(p =>
    p.toLowerCase().includes('adresse') && !p.toLowerCase().includes('wohn')
  );
  const hasArbeitgeber = propertyNames.some(p =>
    p.toLowerCase().includes('arbeitgeber')
  );

  if (hasWohnadresse) {
    kandidaten.push({
      type: 'Kandidat',
      properties: propertyNames,
      adressField: propertyNames.find(p => p.toLowerCase().includes('wohnadresse'))
    });
  } else if (hasAdresse) {
    fachgeschaefte.push({
      type: 'Fachgeschäft',
      properties: propertyNames,
      adressField: propertyNames.find(p => p.toLowerCase().includes('adresse'))
    });
  } else if (hasArbeitgeber) {
    arbeitgeber.push({
      type: 'Arbeitgeber',
      properties: propertyNames
    });
  } else {
    unbekannt.push({
      type: 'Unbekannt',
      properties: propertyNames
    });
  }
}

console.log(`\nKandidaten gefunden: ${kandidaten.length}`);
if (kandidaten.length > 0) {
  console.log("  Adress-Feld:", kandidaten[0].adressField);
  console.log("  Alle Properties:", kandidaten[0].properties.join(', '));
}

console.log(`\nFachgeschäfte gefunden: ${fachgeschaefte.length}`);
if (fachgeschaefte.length > 0) {
  console.log("  Adress-Feld:", fachgeschaefte[0].adressField);
  console.log("  Alle Properties:", fachgeschaefte[0].properties.join(', '));
}

console.log(`\nArbeitgeber gefunden: ${arbeitgeber.length}`);
if (arbeitgeber.length > 0) {
  console.log("  Alle Properties:", arbeitgeber[0].properties.join(', '));
}

console.log(`\nUnbekannt gefunden: ${unbekannt.length}`);
if (unbekannt.length > 0) {
  console.log("  Alle Properties:", unbekannt[0].properties.join(', '));
}

console.log("\n=== DEBUG END ===");

// Ausgabe für n8n
return [{
  json: {
    debug_info: {
      total_items: items.length,
      kandidaten_count: kandidaten.length,
      fachgeschaefte_count: fachgeschaefte.length,
      arbeitgeber_count: arbeitgeber.length,
      unbekannt_count: unbekannt.length
    },
    kandidaten_adress_field: kandidaten.length > 0 ? kandidaten[0].adressField : null,
    fachgeschaefte_adress_field: fachgeschaefte.length > 0 ? fachgeschaefte[0].adressField : null,
    message: "Debug-Informationen in Console-Log prüfen!"
  }
}];
