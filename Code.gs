// ============ CONFIGURATION — à adapter avant utilisation ============
const SHEET_NAME = 'Pointages';
const DOMICILE_LAT = 44.8378;        // <-- latitude du domicile à pointer (à remplacer)
const DOMICILE_LNG = -0.5792;        // <-- longitude du domicile à pointer (à remplacer)
const RAYON_TOLERANCE_METRES = 150;  // distance acceptée sans déclencher d'alerte
const SALARIEES = ['Salariée 1', 'Salariée 2']; // noms affichés dans le menu déroulant
// =======================================================================

function doGet() {
  const template = HtmlService.createTemplateFromFile('Index');
  template.salariees = SALARIEES;
  return template.evaluate()
    .setTitle('Pointage à domicile')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      'Horodatage serveur', 'Type', 'Salariée', 'Latitude', 'Longitude',
      'Précision (m)', 'Distance domicile (m)', 'Statut'
    ]);
  }
  return sheet;
}

// Fonction appelée depuis la page HTML (via google.script.run)
function enregistrerPointage(type, salariee, lat, lng, precision) {
  const sheet = getSheet_();
  const now = new Date(); // horodatage côté serveur : impossible à modifier depuis le téléphone

  let distance = null;
  let statut = 'Position non fournie';
  if (lat != null && lng != null) {
    distance = distanceMetres_(lat, lng, DOMICILE_LAT, DOMICILE_LNG);
    statut = distance <= RAYON_TOLERANCE_METRES ? 'OK' : 'À VÉRIFIER — hors zone';
  }

  sheet.appendRow([
    now, type, salariee,
    lat || '', lng || '', precision || '',
    distance !== null ? Math.round(distance) : '',
    statut
  ]);

  return {
    ok: true,
    statut: statut,
    distance: distance !== null ? Math.round(distance) : null
  };
}

function distanceMetres_(lat1, lng1, lat2, lng2) {
  const R = 6371000;
  const toRad = (deg) => deg * Math.PI / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLng / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}
