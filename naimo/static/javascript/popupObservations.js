document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('overlay');
    const popupContent = document.getElementById('popupContent');
    const closeBtn = document.getElementById('closePopup');

    let clicked = null;

    document.querySelectorAll(".menu-item").forEach(button => {
        button.addEventListener("click", (event) => {

            clicked = event.target.id;

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
                const hiddenInput = document.createElement("input");
                hiddenInput.type = "hidden";
                hiddenInput.name = "clicked";
                hiddenInput.value = clicked;
                const form = document.getElementById("selectAnnee");
                if (form) {
                    form.appendChild(hiddenInput);
                }
                overlay.classList.add("active");

                // Recharge et exécute anneeObservation.js
                const script = document.createElement('script');
                script.src = "/static/javascript/anneeObservation.js";
                script.onload = () => {
                    if (typeof initialiserSelectAnnee === 'function') {
                        initialiserSelectAnnee();
                    }
                };
                document.body.appendChild(script);
            })
            .catch(error => {
                console.log("Erreur :", error);
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
