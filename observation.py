#VERRIER Joris

import requests

# Requête pour récupérer des observations (ici sans filtre pour l'exemple, mais tu peux ajouter code_taxon, etc.)
url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"
params = {
    "size": 10  # Limite le nombre de résultats pour test ; augmente si nécessaire
}

cpt = 0

response = requests.get(url)
data = response.json()

for obs in data["data"]:
    print("----- Observation -----")
    print(f"📍 Station : {obs.get('code_station')} - {obs.get('libelle_station')}")
    print(f"🗺️  Localisation : {obs.get('libelle_commune')} ({obs.get('code_commune')}), "
          f"{obs.get('libelle_departement')} ({obs.get('code_departement')}), "
          f"{obs.get('libelle_region')} ({obs.get('code_region')})")
    print(f"🌊 Entité hydrographique : {obs.get('libelle_entite_hydrographique')} ({obs.get('code_entite_hydrographique')})")
    print(f"📅 Date de l'opération : {obs.get('date_operation')}")
    print(f"🧪 État de l'opération : {obs.get('etat_avancement_operation')}")
    print(f"🔬 Protocole de pêche : {obs.get('protocole_peche')}")
    print(f"📊 Passage n° : {obs.get('numero_passage')}")
    
    print(f"🐟 Espèce : {obs.get('nom_commun_taxon')} ({obs.get('nom_latin_taxon')})")
    print(f"🔢 Code taxon : {obs.get('code_taxon')}")
    print(f"👥 Effectif du lot : {obs.get('effectif_lot')}")
    print(f"📏 Taille (min - max) : {obs.get('taille_min_lot')} mm - {obs.get('taille_max_lot')} mm")
    print(f"⚖️ Poids (mesuré / estimé) : {obs.get('poids_lot_mesure')} g / {obs.get('poids_lot_estime')} g")

    # Individu (s'il y en a un mesuré)
    if obs.get('code_individu') is not None:
        print(f"👤 Individu ID : {obs.get('code_individu')}")
        print(f"  📏 Taille : {obs.get('taille_individu')} mm")
        print(f"  ⚖️ Poids : {obs.get('poids_individu_mesure')} g (estimé : {obs.get('poids_individu_estime')} g)")
        print(f"  🔬 Sexe : {obs.get('sexe_individu')} | Âge : {obs.get('age_individu')}")

    # Pathologies éventuelles
    patho_lot = obs.get("libelles_pathologies_lot", [])
    patho_indiv = obs.get("libelles_pathologies_individu", [])
    if patho_lot:
        print(f"🦠 Pathologies lot : {', '.join(patho_lot)}")
    if patho_indiv:
        print(f"🦠 Pathologies individu : {', '.join(patho_indiv)}")
    
    print("-----------------------\n")
    cpt+=1

print(cpt)