document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('overlay');
    const popupContent = document.getElementById('popupContent');
    const closeBtn = document.getElementById('closePopup');

    let clicked = null;

    document.querySelectorAll(".menu-item").forEach(button => {
        button.addEventListener("click", (event) => {
            clicked = event.currentTarget.id; // On s'assure de récupérer l'ID de la carte, pas d'un sous-élément

            popupContent.innerHTML = `
                <div class="loading-indicator">
                    <div class="spinner"></div>
                    <div>Chargement des données...</div>
                </div>
            `;
            overlay.classList.add("active");

            fetch("/observations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    clicked: clicked,
                    selectionDepartement: "Val-d'Oise",
                    selectionPoisson: "all"
                })
            })
            .then(response => response.text())
            .then(html => {
                console.log("Contenu reçu :", html);

                if (popupContent) {
                    popupContent.innerHTML = html;

                    const hiddenInput = document.createElement("input");
                    hiddenInput.type = "hidden";
                    hiddenInput.name = "clicked";
                    hiddenInput.value = clicked;

                    const form = document.getElementById("selectAnnee");
                    if (form) {
                        form.appendChild(hiddenInput);
                    }

                    // Supprimer d'abord le script existant s'il existe déjà
                    const existingScript = document.querySelector('script[src="/static/javascript/anneeObservation.js"]');
                    if (existingScript) {
                        existingScript.remove();
                    }

                    // Recharger le script dynamiquement
                    const script = document.createElement('script');
                    script.src = "/static/javascript/anneeObservation.js";
                    script.onload = () => {
                        if (typeof initialiserSelectAnnee === 'function') {
                            initialiserSelectAnnee();
                        } else {
                            console.warn("initialiserSelectAnnee n'est pas défini dans le script.");
                        }
                    };
                    document.body.appendChild(script);
                }
            })
            .catch(error => {
                console.error("Erreur lors du chargement des données :", error);
                popupContent.innerHTML = `<p class="error">Une erreur est survenue lors du chargement des données.</p>`;
            });
        });
    });

    closeBtn.addEventListener("click", () => {
        overlay.classList.remove("active");
    });

    overlay.addEventListener("click", e => {
        if (e.target === overlay) {
            overlay.classList.remove("active");
        }
    });
});
