function showPopUp(){
    let popup = document.getElementById("popupObservations");
}

document.addEventListener('DOMContentLoaded', function() {
    
    let menuItems = document.querySelectorAll(".menu-item"); //On récupère tous les boutons de .menu-item

    menuItems.forEach(item => { //Pour chaucn des boutons on ajoute un event à leur clique.
        item.addEventListener("click", event => {
            let clicked = event.target.id; //On récupère l'ID du bouton sur lequel on a cliqué
            console.log(clicked)

            fetch("/observations", { //La suite va se passer dans /observations (notre page)
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({clicked: clicked}) //On renvoie l'ID du bouton sur lequel on a cliqué dans notre Flask
            })
            .then(response => response.text())
            .then(result => {
                document.getElementById("popup").innerHTML = result;
            })
            .catch(error => {
                console.log("Erreur lors du fetch :", error);
            });
        });
    });

});
