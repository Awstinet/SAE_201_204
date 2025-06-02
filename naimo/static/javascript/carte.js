const map = L.map('map').setView([46.8, 2.5], 6);

L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap',
  maxZoom: 18,
}).addTo(map);

fetch('/static/tools/departements.geojson')
  .then(response => response.json())
  .then(geojson => {
    L.geoJSON(geojson, {
      onEachFeature: function (feature, layer) {
        layer.bindTooltip(feature.properties.nom);

        layer.on('click', function () {
          alert("Département : " + feature.properties.nom);
        });

        layer.setStyle({
          color: "#333",
          weight: 1,
          fillColor: "#58a",
          fillOpacity: 0.6
        });
      }
    }).addTo(map);
  });
