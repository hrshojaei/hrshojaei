// ZUORDNUNGS-CODE OHNE GEOCODING
// Verwendet vorberechnete Koordinaten oder macht Zuordnung ohne Distanzberechnung

const items = $input.all();

console.log("=== ZUORDNUNG STARTEN (OHNE GEOCODING) ===");
console.log(`Gesamt Items: ${items.length}`);

// Items kategorisieren
const kandidaten = [];
const fachgeschaefte = [];

for (const item of items) {
  const data = item.json;

  if (data.property_wohnadresse && data.property_wohnadresse.trim() !== '') {
    kandidaten.push(data);
  }
  else if (data.property_adresse && data.property_adresse.trim() !== '') {
    fachgeschaefte.push(data);
  }
}

console.log(`Kandidaten: ${kandidaten.length}`);
console.log(`Fachgeschäfte: ${fachgeschaefte.length}`);

// Für den Test: ALLE Kandidaten ALLEN Fachgeschäften zuordnen
// (später mit echtem Geocoding ersetzen)
const ergebnis = kandidaten.map(kandidat => {
  return {
    json: {
      kandidat_id: kandidat.id,
      kandidat_name: kandidat.property_name,
      kandidat_adresse: kandidat.property_wohnadresse,
      fachgeschaefte_ids: fachgeschaefte.map(g => g.id),
      fachgeschaefte_namen: fachgeschaefte.map(g => g.property_name),
      anzahl: fachgeschaefte.length,
      hinweis: "TEST: Alle Fachgeschäfte zugeordnet (ohne Distanzprüfung)"
    }
  };
});

return ergebnis;
