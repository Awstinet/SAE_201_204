import matplotlib as plt
from io import BytesIO
import base64
import requests


def poissonsParRegion(departement, annee, poisson=None):

    if annee == None:
        return None

    print(f"Année : {annee}")

    totalPoissons = 0

    url = (
        f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?"
        f"libelle_departement={departement}&"
        f"date_operation_min={annee}-01-01&"
        f"date_operation_max={annee}-12-31&"
        f"fields=effectif_lot"
    )

    if poisson:
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

    print(f"Nombre total de poissons avec le département {departement} : {totalPoissons}")
        

    return totalPoissons

