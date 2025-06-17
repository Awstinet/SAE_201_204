import requests

def getFishByDept(nomDept: str ):

    """Récupère tous les poissons présents dans le département indiqué."""

    print(nomDept)
    
    setPoissons = set()

    url = (
        f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?"
        f"libelle_departement={nomDept}&"
        f"fields=nom_commun_taxon"
    )

    response = requests.get(url)
   
    if not response.ok:
        raise ValueError(f"Erreur pour {nomDept}")
    
    data = response.json().get("data", [])

    for poisson in data:
        setPoissons.add(poisson.get("nom_commun_taxon"))

    return setPoissons