import matplotlib as plt
from io import BytesIO
import base64
import requests
from data.datas import getCities, getDepts

# def poissonsParRegion(nomReg, annee, poisson=None):
#     print(annee)
#     # villes = getCities(nomReg)
#     totalPoissons = 0  # Total des poissons pour l’année donnée

#     print(f"Région traitée : {nomReg}")

#     # Base de l’URL avec filtres de date
#     url = (
#         f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?"
#         f"libelle_region={nomReg}&"
#         f"fields=effectif_lot&"
#         f"date_debut_operation={annee}-01-01&"
#         f"date_fin_operation={annee}-12-31"
#     )

#     if poisson:
#         url += f"&nom_commun_taxon={poisson}"

#     page = 1
#     while True:
#         print(f"Page traitée : {page}")
#         response = requests.get(url, params={"page": page, "size": 10000})

#         if not response.ok:
#             print(f"Erreur API pour {nomReg}, page {page}")
#             break

#         data = response.json().get("data", [])
#         if not data:
#             break

#         for obs in data:
#             try:
#                 effectif = int(obs.get("effectif_lot", 0))
#             except ValueError:
#                 effectif = 0
#             except TypeError:
#                 effectif = 0
#             totalPoissons += effectif

#         page += 1

#     return {annee: totalPoissons}


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

