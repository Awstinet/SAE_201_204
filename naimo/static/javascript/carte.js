//Attend que tout le contenu de la page soit chargé avant d'exécuter le code
document.addEventListener("DOMContentLoaded", () => {
  
  //Initialise une carte Leaflet centrée sur la France (latitude 46.8, longitude 2.5) avec un zoom de 6
  const map = L.map('map').setView([46.8, 2.5], 6);

  //Ajoute une couche de tuiles OpenStreetMap pour afficher les cartes
  L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap', //Mention obligatoire du fournisseur
    maxZoom: 18, //Zoom maximal autorisé
  }).addTo(map); //Ajoute cette couche à la carte

  //Récupère l'élément <select> qui permet de choisir entre "région" ou "département"
  const select = document.getElementById("selectZone");

  //Fonction qui charge les données géographiques sur la carte selon le type choisi
  function chargerCarte(type) {
    //Détermine le chemin du fichier GeoJSON selon le type choisi
    const geojsonPath = type === "region"
      ? "/static/tools/regions.geojson"
      : "/static/tools/departements.geojson";

    //Charge le fichier GeoJSON (format de données pour les zones géographiques)
    fetch(geojsonPath)
      .then(res => res.json()) //Convertit la réponse en objet JavaScript
      .then(data => {
        //Ajoute les zones (régions ou départements) sur la carte
        L.geoJSON(data, {
          onEachFeature: (feature, layer) => {
            //Pour chaque zone (feature), on récupère son nom
            const nom = feature.properties.nom;

            //Affiche le nom de la zone au survol
            layer.bindTooltip(nom);

            //Ajoute un événement au clic sur la zone
            layer.on("click", () => {
              const type = select.value; //Relit le type actuel sélectionné
              console.log("Zone sélectionnée :", type);
              console.log("Nom :", nom);

              //Envoie les infos de la zone cliquée au serveur via une requête POST
              fetch("/departement", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nom: nom, zone: type }) //Envoie le nom et le type
              })
              .then(res => res.json()) //Attend une réponse au format JSON
              .then(data => {
                console.log("Stations reçues :", data.stations);

                //Cible la zone HTML où les stations seront affichées
                const stationZone = document.getElementById("stationZone");
                stationZone.innerHTML = "";  // Vide le contenu actuel

                //Si des stations ont été reçues, on les affiche
                if (data.stations.length > 0) {
                  data.stations.forEach(station => {
                    const div = document.createElement("div");
                    div.textContent = station; //Affiche chaque station
                    stationZone.appendChild(div);
                  });
                } else {
                  //Sinon, affiche un message indiquant qu'il n'y a pas de stations
                  stationZone.innerHTML = "<div>Aucune station trouvée</div>";
                }

                //Affiche la carte à 60% de largeur et la zone des stations à 40%
                document.getElementById("mapZone").style.width = "60%";
                stationZone.style.width = "40%";
                stationZone.style.opacity = "1"; // Rend visible la liste
              });
            });

            //Applique un style visuel à chaque zone
            layer.setStyle({
              color: "#333", //Bordure
              weight: 1, //Épaisseur de bordure
              fillColor: "#58a", //Couleur de remplissage
              fillOpacity: 0.6 //Transparence du remplissage
            });
          }
        }).addTo(map); //Ajoute toutes les zones sur la carte
      });
  }

  //Charge la carte au démarrage avec la valeur par défaut du menu déroulant
  chargerCarte(select.value);

  //Lorsque l'utilisateur change de type (région <-> département)
  select.addEventListener("change", () => {
    //Supprime les anciennes zones (GeoJSON) de la carte
    map.eachLayer(layer => {
      if (layer instanceof L.GeoJSON) map.removeLayer(layer);
    });

    //Recharge les données correspondantes
    chargerCarte(select.value);
  });
});
