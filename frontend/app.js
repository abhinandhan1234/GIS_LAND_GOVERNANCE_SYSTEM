const map = L.map('map').setView([15.3344, 74.7671], 11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }).addTo(map);

const colors = { Agricultural: '#5b9a48', Commercial: '#d57833', Residential: '#3f80c2', Government: '#7851a9' };
let parcelsLayer;

function esc(value) { const div = document.createElement('div'); div.textContent = value; return div.innerHTML; }

function showDetails(properties) {
  document.querySelector('#details').innerHTML = `
    <strong>Survey ${esc(properties.survey_number)} / ${esc(properties.hissa_number)}</strong><br>
    Owner: ${esc(properties.owner_name)}<br>
    Land type: ${esc(properties.land_type)}<br>
    Tax status: ${esc(properties.tax_status)}<br>
    Village: ${esc(properties.village_name)}`;
}

async function loadParcels() {
  const params = new URLSearchParams();
  const type = document.querySelector('#landType').value;
  const tax = document.querySelector('#taxStatus').value;
  if (type) params.set('land_type', type);
  if (tax) params.set('tax_status', tax);
  const response = await fetch(`/api/parcels?${params}`);
  const data = await response.json();
  if (parcelsLayer) map.removeLayer(parcelsLayer);
  parcelsLayer = L.geoJSON(data, {
    style: feature => ({ color: colors[feature.properties.land_type], weight: 1, fillOpacity: 0.55 }),
    onEachFeature: (feature, layer) => {
      layer.bindPopup(`<b>Survey ${esc(feature.properties.survey_number)} / ${esc(feature.properties.hissa_number)}</b><br>${esc(feature.properties.owner_name)}`);
      layer.on('click', () => showDetails(feature.properties));
    }
  }).addTo(map);
}

async function loadStatistics() {
  const response = await fetch('/api/statistics');
  const data = await response.json();
  document.querySelector('#summary').innerHTML = `<strong>${data.total_parcels}</strong> parcels<br><br>` + data.by_land_type.map(x => `<div class="legend-item"><span style="color:${colors[x.category]}">${x.category}</span><span>${x.count}</span></div>`).join('');
}

document.querySelector('#apply').addEventListener('click', loadParcels);
Promise.all([loadParcels(), loadStatistics()]).catch(error => {
  document.querySelector('#summary').textContent = `Unable to load data: ${error.message}`;
});

