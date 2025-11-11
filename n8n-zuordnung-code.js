// ZUORDNUNGS-CODE - Ordnet Kandidaten zu Fachgeschäften basierend auf Distanz zu
// Diesen Code in den "🎯 Zuordnung berechnen" Node einfügen

// ========== KONFIGURATION ==========
const GOOGLE_MAPS_API_KEY = 'AIzaSyDPxA9a8qyRRhIzMVCR4n-vL2xEKqeC6no';

// Distanz aus dem ersten Input-Item lesen (falls vorhanden)
// Fallback: 25 km
let MAX_DISTANZ_KM = 25;
try {
  const firstItem = $input.first();
  if (firstItem && firstItem.json && firstItem.json.distanz_km) {
    MAX_DISTANZ_KM = firstItem.json.distanz_km;
  }
} catch (e) {
  // Fallback zu 25 km wenn keine Distanz gefunden
  MAX_DISTANZ_KM = 25;
}

// ========== HILFSFUNKTIONEN ==========

// Geocoding: Adresse -> Koordinaten
async function geocodeAddress(address) {
  if (!address || address.trim() === '') {
    return null;
  }

  const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${GOOGLE_MAPS_API_KEY}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (data.status === 'OK' && data.results.length > 0) {
      const location = data.results[0].geometry.location;
      return {
        lat: location.lat,
        lng: location.lng
      };
    }
    return null;
  } catch (error) {
    console.error(`Geocoding-Fehler für Adresse "${address}":`, error.message);
    return null;
  }
}

// Haversine-Formel: Distanz zwischen zwei Koordinaten
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Erdradius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const distance = R * c;

  return distance;
}

// ========== HAUPTLOGIK ==========

const items = $input.all();

console.log("=== ZUORDNUNG STARTEN ===");
console.log(`Max. Distanz: ${MAX_DISTANZ_KM} km`);
console.log(`Gesamt Items: ${items.length}`);

// Schritt 1: Items kategorisieren
const kandidaten = [];
const fachgeschaefte = [];

for (const item of items) {
  const data = item.json;

  // Kandidaten haben property_wohnadresse
  if (data.property_wohnadresse && data.property_wohnadresse.trim() !== '') {
    kandidaten.push(data);
  }
  // Fachgeschäfte haben property_adresse (aber nicht property_wohnadresse)
  else if (data.property_adresse && data.property_adresse.trim() !== '') {
    fachgeschaefte.push(data);
  }
}

console.log(`\nKandidaten: ${kandidaten.length}`);
console.log(`Fachgeschäfte: ${fachgeschaefte.length}`);

if (kandidaten.length === 0) {
  return [{
    json: {
      error: "Keine Kandidaten gefunden!",
      kandidaten_count: 0,
      fachgeschaefte_count: fachgeschaefte.length
    }
  }];
}

if (fachgeschaefte.length === 0) {
  return [{
    json: {
      error: "Keine Fachgeschäfte gefunden!",
      kandidaten_count: kandidaten.length,
      fachgeschaefte_count: 0
    }
  }];
}

// Schritt 2: Fachgeschäfte geocodieren
console.log("\n=== FACHGESCHÄFTE GEOCODIEREN ===");
for (const geschaeft of fachgeschaefte) {
  const coords = await geocodeAddress(geschaeft.property_adresse);
  geschaeft.coords = coords;

  if (coords) {
    console.log(`✓ ${geschaeft.property_name}: ${coords.lat}, ${coords.lng}`);
  } else {
    console.log(`✗ ${geschaeft.property_name}: Adresse nicht gefunden`);
  }
}

// Nur Fachgeschäfte mit gültigen Koordinaten behalten
const gueltigeFachgeschaefte = fachgeschaefte.filter(g => g.coords !== null);
console.log(`\nGültige Fachgeschäfte: ${gueltigeFachgeschaefte.length}`);

if (gueltigeFachgeschaefte.length === 0) {
  return [{
    json: {
      error: "Keine Fachgeschäfte mit gültigen Adressen gefunden!",
      hinweis: "Prüfen Sie die Adressen in der Fachgeschäfte-Datenbank"
    }
  }];
}

// Schritt 3: Kandidaten verarbeiten und zuordnen
console.log("\n=== KANDIDATEN ZUORDNEN ===");
const zuordnungen = [];

for (const kandidat of kandidaten) {
  const kandidatCoords = await geocodeAddress(kandidat.property_wohnadresse);

  if (!kandidatCoords) {
    console.log(`✗ ${kandidat.property_name}: Adresse nicht gefunden`);
    continue;
  }

  console.log(`\n${kandidat.property_name} (${kandidatCoords.lat}, ${kandidatCoords.lng})`);

  // Distanzen zu allen Fachgeschäften berechnen
  const naheGeschafte = [];

  for (const geschaeft of gueltigeFachgeschaefte) {
    const distanz = calculateDistance(
      kandidatCoords.lat,
      kandidatCoords.lng,
      geschaeft.coords.lat,
      geschaeft.coords.lng
    );

    if (distanz <= MAX_DISTANZ_KM) {
      naheGeschafte.push({
        id: geschaeft.id,
        name: geschaeft.property_name,
        distanz: Math.round(distanz * 10) / 10 // Runden auf 1 Dezimalstelle
      });

      console.log(`  ✓ ${geschaeft.property_name}: ${Math.round(distanz * 10) / 10} km`);
    }
  }

  if (naheGeschafte.length > 0) {
    zuordnungen.push({
      kandidat_id: kandidat.id,
      kandidat_name: kandidat.property_name,
      fachgeschaefte_ids: naheGeschafte.map(g => g.id),
      fachgeschaefte_namen: naheGeschafte.map(g => g.name),
      distanzen: naheGeschafte.map(g => g.distanz),
      anzahl_zuordnungen: naheGeschafte.length
    });
  } else {
    console.log(`  ✗ Keine Fachgeschäfte innerhalb ${MAX_DISTANZ_KM} km`);
  }
}

console.log("\n=== ZUORDNUNG ABGESCHLOSSEN ===");
console.log(`Kandidaten zugeordnet: ${zuordnungen.length}/${kandidaten.length}`);

// Schritt 4: Ergebnis zurückgeben
const ergebnis = zuordnungen.map(z => ({
  json: {
    kandidat_id: z.kandidat_id,
    kandidat_name: z.kandidat_name,
    fachgeschaefte_ids: z.fachgeschaefte_ids,
    fachgeschaefte_namen: z.fachgeschaefte_namen,
    distanzen_km: z.distanzen,
    anzahl: z.anzahl_zuordnungen,
    max_distanz_km: MAX_DISTANZ_KM
  }
}));

// Wenn keine Zuordnungen, trotzdem eine Info zurückgeben
if (ergebnis.length === 0) {
  return [{
    json: {
      info: "Keine Kandidaten innerhalb der gewählten Distanz gefunden",
      max_distanz_km: MAX_DISTANZ_KM,
      kandidaten_count: kandidaten.length,
      fachgeschaefte_count: gueltigeFachgeschaefte.length
    }
  }];
}

return ergebnis;
