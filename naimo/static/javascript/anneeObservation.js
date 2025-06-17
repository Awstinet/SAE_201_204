//Fonction pour initialiser le comportement du bouton de sélection d'année
function initialiserSelectAnnee() {
    //On récupère le bouton de validation par son ID
    const validateBtn = document.getElementById('validateBtn');
    
    if (validateBtn) {
        //On remplace le bouton par un clone de lui-même.
        //Cela permet de supprimer tous les anciens écouteurs d’événements pour éviter les doublons
        validateBtn.replaceWith(validateBtn.cloneNode(true));
        
        //On récupère à nouveau le bouton de validation (le nouveau clone)
        const newValidateBtn = document.getElementById('validateBtn');
        
        //On ajoute un événement de clic sur ce nouveau bouton
        newValidateBtn.addEventListener('click', function() {
            //On récupère le formulaire contenant la sélection d'année
            const form = document.getElementById('selectAnnee');
            
            //On crée un objet FormData à partir du formulaire pour accéder aux données
            const formData = new FormData(form); 
            
            //On convertit les données du formulaire en objet JavaScript
            let data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            //On récupère le conteneur où seront affichés les résultats
            const resultsContainer = document.getElementById('resultsContainer');
            
            //Si le conteneur existe, on affiche un indicateur de chargement
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="loading-indicator">
                        <div class="spinner"></div>
                        <div>Chargement des données...</div>
                    </div>
                `;
            }

            //On envoie une requête POST au serveur avec les données du formulaire
            fetch("/observations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data) //On convertit les données en JSON
            })
            .then(response => response.text()) //On attend une réponse HTML
            .then(html => {
                //On crée un élément temporaire pour parser la réponse HTML
                const temp = document.createElement('div');
                temp.innerHTML = html;
                
                //On cherche dans la réponse soit un nouvel élément resultsContainer, soit le body
                const newContent = temp.querySelector('#resultsContainer') || temp.querySelector('body');
                
                //On remplace le contenu actuel du conteneur de résultats par le nouveau contenu
                if (resultsContainer && newContent) {
                    resultsContainer.innerHTML = newContent.innerHTML;
                }

                //On recharge dynamiquement un script JS, utile si des événements doivent être reinitialisés
                const script = document.createElement('script');
                script.src = "/static/javascript/anneeObservation.js";
                document.body.appendChild(script);
            })
            .catch(err => {
                //En cas d’erreur dans la requête, on affiche un message d'erreur
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