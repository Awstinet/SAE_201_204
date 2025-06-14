import requests
import matplotlib.pyplot as plt
import base64
from io import BytesIO


def poissonsParDepartement(departement, annee, poisson):
    if annee is None:
        return None

    totalPoissons = 0

    url = (
        f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?"
        f"libelle_departement={departement}&"
        f"date_operation_min={annee}-01-01&"
        f"date_operation_max={annee}-12-31&"
        f"fields=effectif_lot"
    )

    if poisson != "all":
        url += f"&nom_commun_taxon={poisson}"

    response = requests.get(url)
    if not response.ok:
        raise ValueError(f"Erreur pour le département {departement}")

    data = response.json().get("data", [])

    for obs in data:
        try:
            effectif = int(obs.get("effectif_lot", 0)) or 0
        except (ValueError, TypeError):
            effectif = 0
        totalPoissons += effectif

    return totalPoissons


def graphePoissonsParRegion(annees: list, effectifs: list):
    plt.figure(figsize=(5, 3))
    plt.plot(annees, effectifs, color="#0DAAEE", marker="o")
    plt.xlabel("Années")
    plt.ylabel("Nombre de poissons")
    plt.title("Évolution du nombre de poissons")
    plt.grid(axis="y", alpha=0.75)

    imageStream = BytesIO()
    plt.savefig(imageStream, format="png", bbox_inches="tight")
    plt.close()

    imageBase64 = base64.b64encode(imageStream.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{imageBase64}"