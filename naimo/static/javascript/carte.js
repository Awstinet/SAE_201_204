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
                    div.addEventListener("click", () => {
                      showFishList(station.libelle_station || 'Nom inconnu');
                    });

                    stationZone.appendChild(div);
                  });
                } else {
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

const fishPopup = document.getElementById("fishPopup");
const popupList = document.getElementById("popupList");
const closePopup = document.getElementById("closePopup");

closePopup.addEventListener("click", () => {
  fishPopup.classList.remove("visible");
});

// Simulation de poissons par station (remplace ça par un appel serveur plus tard si tu veux)
const poissonsParStation = {
  "Station ABC": ["Truite", "Brochet"],
  "Station DEF": ["Anguille", "Carpe"]
};

// Quand on clique sur une station
function showFishList(stationName) {
  popupList.innerHTML = `<h4>Poissons à ${stationName}</h4>`;

  // const poissons = poissonsParStation[stationName] || ["Aucun poisson répertorié"];
  

  const poissons = ["Truite", "Brochet", "Silure", "Truite", "Brochet", "Silure",];

  poissons.forEach(p => {
    const item = document.createElement("div");
    item.textContent = p;
    item.style.cursor = "pointer";
    item.style.marginBottom = "0.5em";
    item.addEventListener("click", () => showFishDetails(stationName, p));
    popupList.appendChild(item);
  });

  fishPopup.classList.add("visible");
}

function showFishDetails(stationName, poisson) {
  popupList.innerHTML = `
    <h4>${poisson}</h4>
    <p>Détails de ${poisson} (ex. habitat, poids moyen, statut, etc).</p>
    <button onclick="showFishList('${stationName}')">⬅ Retour</button>
  `;
}
