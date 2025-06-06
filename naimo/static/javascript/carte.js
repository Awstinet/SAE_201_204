// Attend que tout le contenu de la page soit chargé
document.addEventListener("DOMContentLoaded", () => {

  // Initialise la carte centrée sur la France
  const map = L.map('map').setView([46.8, 2.5], 6);

  // Ajoute les tuiles OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(map);

  const select = document.getElementById("selectZone");

  let geojsonLayer = null; // Stockera la couche GeoJSON active

  // Fonction pour charger les données géographiques
  function chargerCarte(type) {
    const geojsonPath = type === "region"
      ? "/static/tools/regions.geojson"
      : "/static/tools/departements.geojson";

    fetch(geojsonPath)
      .then(res => res.json())
      .then(data => {
        // Supprime l'ancienne couche si elle existe
        if (geojsonLayer) {
          map.removeLayer(geojsonLayer);
        }

        // Crée la nouvelle couche GeoJSON
        geojsonLayer = L.geoJSON(data, {
          onEachFeature: (feature, layer) => {
            const nom = feature.properties.nom;

            // Ajoute un tooltip et un événement au clic
            layer.bindTooltip(nom);
            layer.on("click", () => {
              const type = select.value;

              console.log("Zone sélectionnée :", type);
              console.log("Nom original :", nom);
              console.log("Feature properties:", feature.properties); // Debug pour voir toutes les propriétés
              const type = select.value; //Relit le type actuel sélectionné


              fetch("/departement", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nom: nom, zone: type })
              })
              .then(res => res.json())
              .then(data => {
                //Cible la zone HTML où les stations seront affichées
                const stationZone = document.getElementById("stationZone");
                stationZone.innerHTML = ""; // Vide l'ancien contenu

                // Vérification que les données existent et sont un tableau
                if (data.stations && Array.isArray(data.stations) && data.stations.length > 0) {
                  data.stations.forEach(station => {
                    console.log("Station:", station); // Debug
                    const div = document.createElement("div");
                    div.className = "station-card";
                    div.innerHTML = `
                      <div class="station-name">${station.libelle_station || 'Nom non disponible'}</div>
                      <div class="station-info">
                        <div class="info-item commune">
                          <span class="info-label">Commune</span>
                          <span class="info-value">${station.nom_com || 'Non renseigné'}</span>
                        </div>
                        <div class="info-item departement">
                          <span class="info-label">Département</span>
                          <span class="info-value">${station.nom_dept || 'Non renseigné'}</span>
                        </div>
                        <div class="info-item region">
                          <span class="info-label">Région</span>
                          <span class="info-value">${station.nom_reg || 'Non renseigné'}</span>
                        </div>
                      </div>
                    `;
                    stationZone.appendChild(div);
                  });
                } else {
                  console.log("Aucune station trouvée ou données invalides"); // Debug
                  const div = document.createElement("div");
                  div.className = "no-stations";
                  div.innerHTML = `<em>Aucune station trouvée pour cette zone.</em>`;
                  stationZone.appendChild(div);
                }

                // Affiche la zone d'infos
                stationZone.style.display = "block";
                stationZone.style.width = "40%";
              })
              .catch(error => {
                console.error("Erreur lors de la récupération des données:", error);
                const stationZone = document.getElementById("stationZone");
                stationZone.innerHTML = "";
                const div = document.createElement("div");
                div.className = "no-stations";
                div.innerHTML = `<em>Erreur lors du chargement des données.</em>`;
                stationZone.appendChild(div);
                stationZone.style.display = "block";
                stationZone.style.width = "40%";
              });

              // Change le style de la zone sélectionnée
              layer.setStyle({
                color: "#333",
                weight: 1,
                fillColor: "#58a",
                fillOpacity: 0.6
              });
            });
          }
        });

        geojsonLayer.addTo(map); // Ajoute la couche à la carte
      })
      .catch(error => {
        console.error("Erreur lors du chargement de la carte:", error);
      });
  }

  // Charge initialement la carte avec la sélection par défaut
  chargerCarte(select.value);

  // Recharge les données si on change le type
  select.addEventListener("change", () => {
    chargerCarte(select.value);
  });
});