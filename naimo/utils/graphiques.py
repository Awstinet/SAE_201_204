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

def poissonsParDepartement2(departement, annee, poisson):
    """
    Retourne un dictionnaire {nom_poisson: effectif} si poisson == 'all',
    sinon un total int pour une espèce donnée.
    """
    if annee is None:
        return None

    url = (
        f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?"
        f"libelle_departement={departement}&"
        f"date_operation_min={annee}-01-01&"
        f"date_operation_max={annee}-12-31&"
        f"fields=effectif_lot,nom_commun_taxon"
    )

    if poisson != "all":
        url += f"&nom_commun_taxon={poisson}"

    response = requests.get(url)
    if not response.ok:
        raise ValueError(f"Erreur pour le département {departement}")

    data = response.json().get("data", [])

    if poisson != "all":
        total = 0
        for obs in data:
            try:
                total += int(obs.get("effectif_lot", 0)) or 0
            except:
                continue
        return total

    # Cas "all" : retour d'un dictionnaire
    repartition = {}
    for obs in data:
        nom = obs.get("nom_commun_taxon", "Inconnu")
        try:
            effectif = int(obs.get("effectif_lot", 0)) or 0
        except:
            effectif = 0
        repartition[nom] = repartition.get(nom, 0) + effectif

    return repartition


def camembertPoissonsParDept(repartition):
    """Génère un camembert à partir d’un dictionnaire {nom_poisson: effectif}"""
    if not repartition:
        return None

    labels = []
    sizes = []
    other = 0
    total = sum(repartition.values())

    for nom, effectif in repartition.items():
        if effectif / total >= 0.05:
            labels.append(nom)
            sizes.append(effectif)
        else:
            other += effectif

    if other > 0:
        labels.append("Autres espèces")
        sizes.append(other)

    plt.figure(figsize=(8, 6))
    plt.pie(sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.tab20.colors)
    plt.title("Répartition des poissons")
    plt.axis('equal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
