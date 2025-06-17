function initialiserSelectAnnee() {
    const validateBtn = document.getElementById('validateBtn');
    
    if (validateBtn) {
        // On supprime tout écouteur existant pour éviter les doublons
        validateBtn.replaceWith(validateBtn.cloneNode(true));
        
        // On récupère le nouveau bouton
        const newValidateBtn = document.getElementById('validateBtn');
        
        newValidateBtn.addEventListener('click', function() {
            const form = document.getElementById('selectAnnee');
            const formData = new FormData(form);
            let data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            // Affiche l'indicateur de chargement
            const resultsContainer = document.getElementById('resultsContainer');
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="loading-indicator">
                        <div class="spinner"></div>
                        <div>Chargement des données...</div>
                    </div>
                `;
            }

            fetch("/observations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            })
            .then(response => response.text())
            .then(html => {
                const temp = document.createElement('div');
                temp.innerHTML = html;
                const newContent = temp.querySelector('#resultsContainer') || temp.querySelector('body');
                
                if (resultsContainer && newContent) {
                    resultsContainer.innerHTML = newContent.innerHTML;
                }

                // Recharge le script
                const script = document.createElement('script');
                script.src = "/static/javascript/anneeObservation.js";
                document.body.appendChild(script);
            })
            .catch(err => {
                console.error("Erreur : ", err);
                if (resultsContainer) {
                    resultsContainer.innerHTML = `
                        <div class="error-message">
                            Une erreur est survenue lors du chargement des données.
                        </div>
                    `;
                }
            });
        });
    }
}