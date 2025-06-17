// Gestion des clics sur les cartes d'options
const optionCards = document.querySelectorAll(".option-card")

optionCards.forEach((card) => {
  card.addEventListener("click", function () {
    // Effet de clic simple
    this.style.transform = "translateY(-3px) scale(0.98)"
    setTimeout(() => {
      this.style.transform = ""
    }, 150)

    // Ici vous pouvez ajouter la logique pour ouvrir le popup correspondant
    const cardId = this.id
    console.log(`Carte cliquée: ${cardId}`)

    // Exemple d'ouverture de popup selon la carte
    let title = ""
    let content = ""

    switch (cardId) {
      case "evoPoissonsZone":
        title = "Évolution Temporelle"
        content = "<p>Graphique d'évolution des populations de poissons par année...</p>"
        break
      case "totalPoissonsZone":
        title = "Répartition Géographique"
        content = "<p>Graphique en secteurs de la distribution des espèces...</p>"
        break
      case "nbPrelevZones":
        title = "Densité d'Échantillonnage"
        content = "<p>Graphique en courbe du nombre de prélèvements...</p>"
        break
    }

    openPopup(title, content)
  })
})

// Gestion du popup
const overlay = document.getElementById("overlay")
const popup = document.getElementById("popup")
const closeBtn = document.getElementById("closePopup")

closeBtn.addEventListener("click", () => {
  overlay.classList.remove("active")
})

overlay.addEventListener("click", (e) => {
  if (e.target === overlay) {
    overlay.classList.remove("active")
  }
})

// Fonction pour ouvrir un popup
function openPopup(title, content) {
  document.getElementById("popupTitle").textContent = title
  document.getElementById("popupContent").innerHTML = content
  overlay.classList.add("active")
}

// Fermeture avec la touche Échap
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && overlay.classList.contains("active")) {
    overlay.classList.remove("active")
  }
})