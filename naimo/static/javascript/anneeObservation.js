function initialiserSelectAnnee() {
    const select = document.getElementById("poissonAnneeSelection");
    if (select) {
        select.addEventListener("change", function () {
            document.getElementById("selectAnnee").submit(); // soumission automatique
        });
    }
}
