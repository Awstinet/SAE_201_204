# Pierre

import requests
import time

# URL de base de l'API
base_url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/indicateurs"

# Paramètres généraux de la requête
params = {
    "size": 100,  # Nombre de résultats par page (max 100)
    "page": 1     # Page actuelle (on va boucler)
}

# Liste des champs qu'on souhaite conserver
champs_souhaites = [
    "code_operation",
    "date_operation",
    "etat_avancement_operation",
    "code_qualification_operation",
    "libelle_qualification_operation",
    "code_station",
    "libelle_station",
    "coordonnee_x_station",
    "coordonnee_y_station",
    "code_epsg_projection_station",
    "code_projection_station",
    "libelle_projection_station",
    "code_point_prelevement_aspe",
    "code_point_prelevement",
    "coordonnee_x_point_prelevement",
    "coordonnee_y_point_prelevement",
    "code_epsg_projection_point_prelevement",
    "code_projection_point_prelevement",
    "libelle_projection_point_prelevement",
    "lieu_dit_point_prelevement",
    "localisation_precise_point_prelevement",
    "code_entite_hydrographique",
    "libelle_entite_hydrographique",
    "code_commune",
    "libelle_commune",
    "code_departement",
    "libelle_departement",
    "code_region",
    "libelle_region",
    "code_bassin",
    "libelle_bassin",
    "codes_dispositifs_collecte",
    "libelles_dispositifs_collecte",
    "protocole_peche",
    "objectifs_operation",
    "ipr_date_execution",
    "ipr_version",
    "ipr_surface_prospectee",
    "ipr_code_unite_hydrographique",
    "ipr_superficie_bassin_versant",
    "ipr_distance_source",
    "ipr_largeur_eau",
    "ipr_pente",
    "ipr_profondeur",
    "ipr_altitude",
    "ipr_temperature_air_janvier",
    "ipr_temperature_air_juillet",
    "ipr_effectif",
    "ipr_a",
    "ipr_g",
    "ipr_v",
    "ipr_t1",
    "ipr_t2",
    "ipr_nte_observe",
    "ipr_ner_observe",
    "ipr_nel_observe",
    "ipr_dit_observe",
    "ipr_dii_observe",
    "ipr_dio_observe",
    "ipr_dti_observe",
    "ipr_nte_theorique",
    "ipr_ner_theorique",
    "ipr_nel_theorique",
    "ipr_dit_theorique",
    "ipr_dii_theorique",
    "ipr_dio_theorique",
    "ipr_dti_theorique",
    "ipr_nte",
    "ipr_ner",
    "ipr_nel",
    "ipr_dit",
    "ipr_dii",
    "ipr_dio",
    "ipr_dti",
    "ipr_note",
    "ipr_code_classe",
    "ipr_libelle_classe",
    "ipr_codes_taxon",
    "ipr_codes_alternatifs_taxon",
    "ipr_noms_communs_taxon",
    "ipr_noms_latins_taxon",
    "ipr_effectifs_taxon",
    "ipr_probabilites_presence_taxon",
    "iprplus_date_execution ",
    "iprplus_version",
    "iprplus_strategie_echantillonnage",
    "iprplus_code_formation_geologique",
    "iprplus_code_unite_hydrographique",
    "iprplus_code_regime_hydrologique ",
    "iprplus_zone_huet",
    "iprplus_superficie_bassin_versant",
    "iprplus_pente ",
    "iprplus_largeur_eau",
    "iprplus_precipitation_bassin_versant",
    "iprplus_amplitude_thermique_air",
    "iprplus_temperature_air_bassin_versant",
    "iprplus_temperature_air_station",
    "iprplus_debit",
    "iprplus_effectif",
    "iprplus_evaporation",
    "iprplus_puissance",
    "iprplus_ric_util",
    "iprplus_run_off",
    "iprplus_seuil_taux_0_plus",
    "iprplus_taux_0_plus",
    "iprplus_abondance_hintol_observe",
    "iprplus_abondance_juveniles_truites_observe", 
    "iprplus_abondance_o2intol_observe",
    "iprplus_abondance_rhpar_observe",
    "iprplus_intol_observe ",
    "iprplus_limno_observe",
    "iprplus_lipar_observe",
    "iprplus_o2intol_observe",
    "iprplus_omni_observe",
    "iprplus_stther_observe",
    "iprplus_tol_observe",
    "iprplus_abondance_hintol_theorique",
    "iprplus_abondance_juveniles_truites_theoriques",
    "iprplus_abondance_o2intol_theorique",
    "iprplus_abondance_rhpar_theorique ",
    "iprplus_intol_theorique",
    "iprplus_limno_theorique",
    "iprplus_lipar_theorique",
    "iprplus_o2intol_theorique",
    "iprplus_omni_theorique",
    "iprplus_stther_theorique",
    "iprplus_tol_theorique",
    "iprplus_abondance_hintol",
    "iprplus_abondance_juveniles_truites", 
    "iprplus_abondance_o2intol",
    "iprplus_abondance_rhpar",
    "iprplus_intol",
    "iprplus_limno",
    "iprplus_lipar",
    "iprplus_o2intol",
    "iprplus_omni",
    "iprplus_stther",
    "iprplus_tol",
    "iprplus_note",
    "iprplus_code_classe",
    "iprplus_libelle_classe",
    "iprplus_codes_taxon",
    "iprplus_codes_alternatifs_taxon",
    "iprplus_noms_communs_taxon",
    "iprplus_noms_latins_taxon",
    "iprplus_uris_taxon",
    "iprplus_probabilite_presence_taxon",
    "libelle_point_prelevement_wama",
    "code_point_prelevement_wama",
    "geometry",
    "longitude",
    "latitude",
]


has_next = True
indicateur_total = 0

while has_next:
    print(f"🔄 Récupération de la page {params['page']}...")
    response = requests.get(base_url, params=params)
    data = response.json()

    if "data" in data:
        for i, indicateur in enumerate(data["data"], 1):
            indicateur_total += 1
            print(f"\n--- Indicateur filtré #{indicateur_total} ---")

            # Ne garder que les champs utiles
            indicateur_filtré = {k: v for k, v in indicateur.items() if k in champs_souhaites}

            for key, value in indicateur_filtré.items():
                print(f"{key} : {value}")
    else:
        print("⚠️ Aucun indicateur trouvé.")
        break

    # Passer à la page suivante si elle existe
    if data.get("next"):
        params["page"] += 1
        time.sleep(0.5)  # petite pause pour ne pas spammer l'API
    else:
        has_next = False

print(f"\n✅ {indicateur_total} indicateurs récupérés au total.")
