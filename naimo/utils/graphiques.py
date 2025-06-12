import matplotlib as plt
from io import BytesIO
import base64
import requests
from data.datas import getCities

def getLastPage(url):
    params = {"size": 10000}
    response = requests.get(url, params=params)
    response.raise_for_status()
    jsonData = response.json()
    totalCount = jsonData.get("count")
    pageSize = 10000
    lastPage = (totalCount // pageSize) + (1 if totalCount % pageSize else 0)
    print(f"Nombre total de pages : {lastPage}")
    return lastPage


def evolutionPoissonsParRegion(zone: str, nomZone: str, poisson:str = None):

    """Génère une courbe qui montre l'évolution d'une population de poissons dans une zone."""

    url = f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?libelle_{zone}={nomZone}"
    if poisson:
        url += f"&nom_commun_taxon={poisson}"

    page = 1
    pageSize = 5000

    nbPages = getLastPage(url, zone, nomZone)
    dctAnnees = {}
    print(nbPages)

from concurrent.futures import ThreadPoolExecutor, as_completed


def fetchPage(page, url):
    params = {"page": page, "size": 10000}
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json().get("data", [])
        print(f"Page {page} récupérée avec {len(data)} entrées")
        return data
    except Exception as e:
        print(f"Erreur page {page} : {e}")
        return []

    

def fetchAllPages(maxWorkers, zone, nomZone, poisson = None):

    if zone == "region":
        villes = getCities(nomZone)
        print(villes)
        zone = "commune"
    
    allDatas = []

    for ville in villes:
        print(ville)
        url = f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?libelle_{zone}={ville}&fields=date_operation,effectif_lot,nom_commun_taxon"
        if poisson:
            url += f"&nom_commun_taxon={poisson}"

        with ThreadPoolExecutor(max_workers=maxWorkers) as executor:
            futures = [executor.submit(fetchPage, p, url) for p in range(1, getLastPage(url))]

            for f in as_completed(futures):
                allDatas.extend(f.result())

    return allDatas


def poissonsParRegion(nomReg, poisson=None):
    villes = getCities(nomReg)
    allDatas = dict()  # Clé = année, valeur = total poissons

    print(f"Les villes : {villes}")

    for ville in villes:
        print(f"Ville traitée : {ville}")
        url = f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?libelle_commune={ville}&fields=date_operation,effectif_lot,nom_commun_taxon"
        if poisson:
            url += f"&nom_commun_taxon={poisson}"

        page = 1

        while True:
            print(f"Page traitée : {page}")
            response = requests.get(url, params={"page": page, "size": 5000})  # Appel de l'API

            if not response.ok:
                print(f"Erreur lors de la récupération pour la ville : {ville}, page {page}")
                break

            data = response.json()
            poissons = data.get("data", [])

            if not poissons:
                break  # On sort de la boucle si aucune donnée

            for p in poissons:
                date = p.get("date_operation")
                effectif = p.get("effectif_lot", 0)

                if not date:
                    continue

                # Extraire l'année à partir de la date
                annee = date.split("-")[0]

                try:
                    effectif = int(effectif)
                except:
                    effectif = 0

                if annee in allDatas:
                    allDatas[annee] += effectif
                else:
                    allDatas[annee] = effectif

            print(allDatas)

            page += 1  # Page suivante

    return allDatas






        
