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
      'Précision (m)', 'Distance client (m)', 'Statut', 'Détail erreur', 'Vérifié par le manager'
    ]);
    // Colonne "Vérifié par le manager" en case à cocher (colonne K), pour que
    // l'employeur puisse valider chaque pointage directement dans le Sheet.
    const rule = SpreadsheetApp.newDataValidation().requireCheckbox().build();
    sheet.getRange('K2:K').setDataValidation(rule);
  }
  return sheet;
}

// Fonction appelée depuis la page HTML (via google.script.run).
// Ne lève jamais d'exception : toute erreur est renvoyée sous forme { ok: false, error }
// pour que le client puisse afficher un message clair, sans jamais perdre la tentative de pointage.
function enregistrerPointage(type, salariee, client, lat, lng, precision, raisonEchecGeoloc) {
  try {
    if (!type || !salariee || !client) {
      return { ok: false, error: 'Champs manquants — merci de sélectionner salarié et client.' };
    }

    const sheet = getSheet_();
    const now = new Date(); // horodatage côté serveur : impossible à modifier depuis le téléphone
    const ref = CLIENTS[client];

    let distance = null;
    let statut;
    let detail = '';

    if (!ref) {
      statut = 'ERREUR — client inconnu';
      detail = 'Le client "' + client + '" n\'existe pas dans la configuration.';
    } else if (lat != null && lng != null) {
      distance = distanceMetres_(lat, lng, ref.lat, ref.lng);
      statut = distance <= RAYON_TOLERANCE_METRES ? 'OK' : 'À VÉRIFIER — hors zone';
    } else {
      // La géolocalisation a échoué côté téléphone (refusée, désactivée, timeout...).
      // Le pointage est quand même enregistré : il ne doit jamais être bloqué,
      // mais le manager doit voir clairement qu'il n'y a pas eu de vérification GPS.
      statut = 'À VÉRIFIER — position indisponible';
      detail = raisonEchecGeoloc || 'Raison non précisée par le téléphone';
    }

    sheet.appendRow([
      now, type, salariee, client,
      lat || '', lng || '', precision || '',
      distance !== null ? Math.round(distance) : '',
      statut, detail,
      false
    ]);

    return {
      ok: true,
      statut: statut,
      distance: distance !== null ? Math.round(distance) : null
    };

  } catch (err) {
    // Erreur inattendue côté serveur (Sheet verrouillé, quota dépassé, etc.)
    return { ok: false, error: 'Erreur serveur : ' + err.message };
  }
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