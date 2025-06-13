function initialiserSelectAnnee() {
    const select = document.getElementById("poissonAnneeSelection");
    if (select) {
        select.addEventListener("change", function () {
            const selectedAnnee = select.value;
            const hiddenInput = document.querySelector('input[name="clicked"]');
            const clicked = hiddenInput ? hiddenInput.value : "";

            fetch("/observations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    clicked: clicked,
                    poissonAnneeSelection: selectedAnnee
                })
            })
            .then(response => response.text())
            .then(html => {
                const popupContent = document.getElementById("popupContent");
                popupContent.innerHTML = html;

                initialiserSelectAnnee(); // on réattache le listener

            })
            .catch(err => console.error("Erreur : ", err));
        });
    }
}