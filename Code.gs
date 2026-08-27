// ============ CONFIGURATION — à adapter avant utilisation ============
const SHEET_NAME = 'Pointages';
const RAYON_TOLERANCE_METRES = 150; // distance acceptée sans déclencher d'alerte

// Un salarié peut intervenir chez plusieurs clients : chacun a ses propres coordonnées.
const CLIENTS = {
  'Madame Sanchez': { lat: 44.844812194736136, lng: -0.6290475221000387 },
  'Monsieur CSOR':  { lat: 44.82652723012038,  lng: -0.5740482204182619 }
};

const SALARIEES = ['Salariée 1', 'Salariée 2']; // noms affichés dans le menu déroulant
// =======================================================================

function doGet() {
  const template = HtmlService.createTemplateFromFile('Index');
  template.salariees = SALARIEES;
  template.clients = Object.keys(CLIENTS);
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
      'Horodatage serveur', 'Type', 'Salariée', 'Client', 'Latitude', 'Longitude',
      'Précision (m)', 'Distance client (m)', 'Statut', 'Vérifié par le manager'
    ]);
    // Colonne "Vérifié par le manager" en case à cocher, pour que l'employeur
    // puisse valider chaque pointage directement dans le Sheet.
    const rule = SpreadsheetApp.newDataValidation().requireCheckbox().build();
    sheet.getRange('J2:J').setDataValidation(rule);
  }
  return sheet;
}

// Fonction appelée depuis la page HTML (via google.script.run)
function enregistrerPointage(type, salariee, client, lat, lng, precision) {
  const sheet = getSheet_();
  const now = new Date(); // horodatage côté serveur : impossible à modifier depuis le téléphone

  const ref = CLIENTS[client];
  let distance = null;
  let statut = 'Position non fournie';

  if (lat != null && lng != null && ref) {
    distance = distanceMetres_(lat, lng, ref.lat, ref.lng);
    statut = distance <= RAYON_TOLERANCE_METRES ? 'OK' : 'À VÉRIFIER — hors zone';
  } else if (!ref) {
    statut = 'Client inconnu';
  }

  sheet.appendRow([
    now, type, salariee, client,
    lat || '', lng || '', precision || '',
    distance !== null ? Math.round(distance) : '',
    statut,
    false // case "Vérifié par le manager" non cochée par défaut
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