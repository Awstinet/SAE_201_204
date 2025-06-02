#CHEREF Rayane et KAROU Maya

import requests

url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/stations"

params = {
    "statut_station": "true",
}

response = requests.get(url, params=params)
data = response.json()

compteur = 0  # compteur d'observations

for obs in data.get("data", []):
    compteur += 1  # incrémenter à chaque observation

    print("\n PARAMETRES STATIQUES ")
    print(f"Code station : {obs.get('code_station')}")
    print(f"Code region : {obs.get('code_region', 'N/A')}")
    print(f"Code departement : {obs.get('code_departement', 'N/A')}")
    print(f"Date de modification : {obs.get('date_modification_station', 'N/A')}")

    print("\n PARAMETRES DYNAMIQUES ")
    print(f"Nom de la station : {obs.get('libelle_station', 'N/A')}")
    print(f"Coordonnees : X = {obs.get('coordonnee_x_station')} | Y = {obs.get('coordonnee_y_station')}")
    print(f"Projection : {obs.get('libelle_projection_station', 'N/A')} ({obs.get('code_projection_station', 'N/A')})")
    print(f"Localisation precise : {obs.get('localisation_precise_station', 'N/A')}")
    print(f"Point de prelevement : {obs.get('libelle_point_prelevement_wama', 'N/A')} (code : {obs.get('code_point_prelevement_wama', 'N/A')})")
    print(f"URI : {obs.get('uri_station')}")

print(f"\nNombre total de stations affichees : {compteur}")
