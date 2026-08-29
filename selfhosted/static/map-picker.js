// Sélecteur de position GPS — Leaflet + OpenStreetMap, sans clé API.
// Recherche d'adresse via Nominatim (usage léger, conforme à sa politique d'utilisation).

function initMapPicker(mapDivId, latInputId, lngInputId, initialLat, initialLng) {
  const latInput = document.getElementById(latInputId);
  const lngInput = document.getElementById(lngInputId);

  const lat = initialLat || 44.8378;
  const lng = initialLng || -0.5792;

  const map = L.map(mapDivId).setView([lat, lng], 14);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19
  }).addTo(map);

  const marker = L.marker([lat, lng], { draggable: true }).addTo(map);

  function majChamps(latlng) {
    latInput.value = latlng.lat.toFixed(8);
    lngInput.value = latlng.lng.toFixed(8);
  }

  marker.on('dragend', () => majChamps(marker.getLatLng()));
  map.on('click', (e) => {
    marker.setLatLng(e.latlng);
    majChamps(e.latlng);
  });

  // Stockées pour être réutilisées par rechercherAdresse()
  window['_map_' + mapDivId] = map;
  window['_marker_' + mapDivId] = marker;
}

async function rechercherAdresse(mapDivId, latInputId, lngInputId, query) {
  if (!query || !query.trim()) return;
  try {
    const res = await fetch('https://nominatim.openstreetmap.org/search?format=json&limit=1&q=' + encodeURIComponent(query));
    const data = await res.json();
    if (data.length === 0) {
      alert("Adresse introuvable, essaie une formulation différente ou pointe directement sur la carte.");
      return;
    }
    const { lat, lon } = data[0];
    const map = window['_map_' + mapDivId];
    const marker = window['_marker_' + mapDivId];
    map.setView([lat, lon], 16);
    marker.setLatLng([lat, lon]);
    document.getElementById(latInputId).value = parseFloat(lat).toFixed(8);
    document.getElementById(lngInputId).value = parseFloat(lon).toFixed(8);
  } catch (e) {
    alert("Recherche d'adresse indisponible pour le moment — pointe directement sur la carte.");
  }
}
