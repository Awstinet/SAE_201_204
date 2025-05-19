import requests

url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/operations"

response = requests.get(url)
data = response.json()

for obs in data.get("data", []):
    print("=" * 60)
    print(f"📍 STATION : {obs.get('libelle_station')} ({obs.get('code_station')})")
    print(f"🗺️  Commune : {obs.get('libelle_commune')} ({obs.get('code_commune')})")
    print(f"📍 Département : {obs.get('libelle_departement')} | Région : {obs.get('libelle_region')}")
    print(f"🌐 Latitude/Longitude : {obs.get('latitude')}, {obs.get('longitude')}")
    print()

    print(f"📅 Date opération : {obs.get('date_operation')} | Code opération : {obs.get('code_operation')}")
    print(f"📄 État avancement : {obs.get('etat_avancement_operation')}")
    print(f"🎯 Objectifs : {', '.join(obs.get('objectifs_operation', []))}")
    print(f"💬 Commentaire : {obs.get('commentaire')}")
    print()

    print("🐟 Espèce ciblée :")
    print(f"   - Nom commun : {obs.get('espece_ciblee_nom_commun_taxon')}")
    print(f"   - Nom latin  : {obs.get('espece_ciblee_nom_latin_taxon')}")
    print(f"   - Code taxon : {obs.get('espece_ciblee_code_taxon')}")
    print(f"   - Est ciblée ? {obs.get('espece_ciblee')}")
    print()

    print("🌡️ Conditions environnementales :")
    print(f"   - Température eau (instantanée) : {obs.get('temperature_instantanee')} °C")
    print(f"   - Température air station : {obs.get('temperature_air_station')} °C")
    print(f"   - Conductivité : {obs.get('conductivite')} µS/cm")
    print(f"   - Débit journalier : {obs.get('debit_journalier')} m³/s")
    print(f"   - Tendance débit : {obs.get('libelle_tendance_debit')}")
    print(f"   - Conditions hydrologiques : {obs.get('libelle_conditions_hydrologiques')}")
    print(f"   - Turbidité : {obs.get('libelle_turbidite')}")
    print()

    print("🏞️ Habitat & structure du cours d’eau :")
    print(f"   - Végétation aquatique : {obs.get('libelle_abondance_vegetation_aquatique')}")
    print(f"   - Abris rocheux : {obs.get('libelle_abondance_abris_rocheux')}")
    print(f"   - Sous-berges : {obs.get('libelle_abondance_sous_berges')}")
    print(f"   - Trous/fosses : {obs.get('libelle_abondance_trous_fosses')}")
    print(f"   - Embâcles/souches : {obs.get('libelle_abondance_embacles_souches')}")
    print(f"   - Végétation bordure : {obs.get('libelle_abondance_vegetation_bordure')}")
    print()

    print("🔧 Paramètres physiques :")
    print(f"   - Profondeur : {obs.get('profondeur')} m")
    print(f"   - Largeur lame d’eau : {obs.get('largeur_lame_eau')} m")
    print(f"   - Pente ligne d’eau : {obs.get('pente_ligne_eau')}")
    print(f"   - Pourcentage courant : {obs.get('pourcentage_courant')} %")
    print()

    print("👥 Acteurs de l’opération :")
    print(f"   - Opérateur : {obs.get('operateur_libelle')}")
    print(f"   - Expert technique : {obs.get('expert_technique_libelle')}")
    print(f"   - Commanditaire : {obs.get('commanditaire_libelle')}")
    print()

    print("📝 Observations :")
    print(f"   - Générales : {obs.get('observations_generales')}")
    print(f"   - Station : {obs.get('observations_station')}")
    print(f"   - Hydrologie : {obs.get('observations_hydrologie')}")
    print(f"   - Végétation : {obs.get('observations_vegetation')}")
    print(f"   - Repeuplement : {obs.get('presence_repeuplement')}")
    print(f"   - Morphologie modifiée : {obs.get('presence_modification_morphologique')}")
    print("=" * 60)
    print()
