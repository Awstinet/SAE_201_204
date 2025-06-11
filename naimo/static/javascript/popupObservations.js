document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('overlay');
    const popupContent = document.getElementById('popupContent');
    const closeBtn = document.getElementById('closePopup');

    // Lorsqu’un bouton est cliqué
    document.querySelectorAll(".menu-item").forEach(button => {
        button.addEventListener("click", (event) => {
            let clicked = event.target.id;

            // Requête vers Flask pour le contenu
            fetch("/observations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ clicked: clicked })
            })
            .then(response => response.text())
            .then(html => {
                popupContent.innerHTML = html;
                overlay.classList.add("active"); // Affiche avec animation
            })
            .catch(error => {
                console.log("Erreur :", error);
            });
        });
    });

    // Fermeture du popup
    closeBtn.addEventListener("click", () => {
        overlay.classList.remove("active");
    });

    // Clic en dehors du popup (optionnel)
    overlay.addEventListener("click", e => {
        if (e.target === overlay) {
            overlay.classList.remove("active");
        }
    });
});
