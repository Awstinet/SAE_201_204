function initialiserSelectAnnee() {
    const select = document.getElementById("poissonAnneeSelection");
    if (select) {
        select.addEventListener("change", function () {
            const selectedAnnee = select.value;

            const clickedInput = document.querySelector('input[name="clicked"]');
            const deptSelect = document.getElementById("selectionDepartement");
            const fishSelect = document.getElementById("selectionPoisson");

            const clicked = clickedInput ? clickedInput.value : "";
            const selectedDept = deptSelect ? deptSelect.value : "Val-d'Oise";
            const selectedPoisson = fishSelect ? fishSelect.value : "all";

            fetch("/observations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    clicked: clicked,
                    selectionDepartement: selectedDept,
                    selectionPoisson: selectedPoisson,
                    poissonAnneeSelection: selectedAnnee
                })
            })
            .then(response => response.text())
            .then(html => {
                const popupContent = document.getElementById("popupContent");
                popupContent.innerHTML = html;

                // Recharge le script et réinitialise les événements
                const script = document.createElement('script');
                script.src = "/static/javascript/anneeObservation.js";
                script.onload = () => {
                    if (typeof initialiserSelectAnnee === 'function') {
                        initialiserSelectAnnee();
                    }
                };
                document.body.appendChild(script);
            })
            .catch(err => console.error("Erreur : ", err));
        });
    }
}