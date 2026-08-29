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

// Carte en lecture seule pour vérifier un pointage : position capturée (📍) vs
// position attendue du client (🏠), avec le rayon de tolérance pour visualiser l'écart.
function initMapVerif(mapDivId, pointageLat, pointageLng, clientLat, clientLng, rayonTolerance) {
  const map = L.map(mapDivId, { zoomControl: true, dragging: true, scrollWheelZoom: false });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);

  const points = [];

  if (clientLat != null && clientLng != null) {
    L.marker([clientLat, clientLng], {
      icon: L.divIcon({ html: '🏠', className: 'icone-carte', iconSize: [26, 26] })
    }).addTo(map).bindPopup('Position attendue (client)');
    points.push([clientLat, clientLng]);

    if (rayonTolerance) {
      L.circle([clientLat, clientLng], {
        radius: rayonTolerance, color: '#2e7d32', weight: 1, fillOpacity: 0.07
      }).addTo(map);
    }
  }

  if (pointageLat != null && pointageLng != null) {
    L.marker([pointageLat, pointageLng], {
      icon: L.divIcon({ html: '📍', className: 'icone-carte', iconSize: [26, 26] })
    }).addTo(map).bindPopup('Position du pointage');
    points.push([pointageLat, pointageLng]);
  }

  if (points.length === 2) {
    L.polyline(points, { color: '#c62828', weight: 2, dashArray: '5,5' }).addTo(map);
    map.fitBounds(points, { padding: [40, 40] });
  } else if (points.length === 1) {
    map.setView(points[0], 15);
  } else {
    map.setView([44.8378, -0.5792], 12);
  }
}
