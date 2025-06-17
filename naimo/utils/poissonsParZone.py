import requests
from functools import lru_cache
import time
from datetime import datetime

def getFishByDept(nomDept: str, annee: int = None, poisson: str = None):
    """
    Récupère les données de poissons exclusivement depuis l'API Hub'eau
    """
    print(f"=== APPEL API HUB'EAU ===")
    print(f"Département: {nomDept}, Période: {annee}-{annee + 4 if annee else 'toutes'}")
    
    try:
        # URL correcte de l'API Hub'eau pour les observations piscicoles
        url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"
        
        # Test initial pour vérifier la disponibilité de l'API
        print(f"Test API sans filtre...")
        test_response = requests.get(url, params={"size": 1, "format": "json"}, timeout=10)
        print(f"Test API Status: {test_response.status_code}")
        
        # Status codes acceptables : 200 (OK) et 206 (Partial Content)
        if test_response.status_code in [200, 206]:
            test_data = test_response.json()
            total_available = test_data.get('count', 0)
            print(f"✅ API fonctionne - Total observations disponibles: {total_available}")
            
            # Afficher la structure d'une observation pour debug
            if test_data.get('data') and len(test_data['data']) > 0:
                sample = test_data['data'][0]
                print("📋 Structure d'une observation:")
                for key, value in sample.items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ API ne répond pas correctement: {test_response.status_code}")
            print(f"Réponse: {test_response.text[:200]}")
            return {}
        
        # Paramètres pour la requête principale
        params = {
            "size": 1000,  # Nombre d'observations à récupérer
            "format": "json"
        }
        
        # Ajouter le filtre de département
        if nomDept:
            params["libelle_departement"] = nomDept
        
        # Ajouter les filtres de date si une année est spécifiée
        if annee:
            params["date_debut"] = f"{annee}-01-01"
            params["date_fin"] = f"{annee + 4}-12-31"
        
        print(f"🔍 Paramètres de recherche: {params}")
        
        # Appel principal à l'API
        response = requests.get(url, params=params, timeout=20)
        print(f"📡 Status de la requête principale: {response.status_code}")
        
        # Accepter les status codes 200 et 206
        if response.status_code in [200, 206]:
            data = response.json()
            observations = data.get("data", [])
            total_count = data.get("count", 0)
            
            print(f"📊 Observations trouvées: {len(observations)} sur {total_count} total")
            
            if not observations:
                print("⚠️ Aucune observation dans la réponse")
                
                # Essayer sans filtre de département pour voir s'il y a des données
                print("🔄 Essai sans filtre de département...")
                params_no_dept = {"size": 100, "format": "json"}
                if annee:
                    params_no_dept["date_debut"] = f"{annee}-01-01"
                    params_no_dept["date_fin"] = f"{annee + 4}-12-31"
                
                fallback_response = requests.get(url, params=params_no_dept, timeout=15)
                if fallback_response.status_code in [200, 206]:
                    fallback_data = fallback_response.json()
                    fallback_observations = fallback_data.get("data", [])
                    print(f"📊 Observations sans filtre département: {len(fallback_observations)}")
                    
                    if fallback_observations:
                        # Afficher les départements disponibles
                        depts_disponibles = set()
                        for obs in fallback_observations[:50]:  # Limiter pour l'affichage
                            dept = obs.get("libelle_departement")
                            if dept:
                                depts_disponibles.add(dept)
                        
                        print(f"🗺️ Départements disponibles dans l'API: {sorted(list(depts_disponibles))}")
                        
                        # Filtrer manuellement par département
                        filtered_obs = []
                        for obs in fallback_observations:
                            obs_dept = obs.get("libelle_departement", "")
                            if nomDept.lower() in obs_dept.lower() or obs_dept.lower() in nomDept.lower():
                                filtered_obs.append(obs)
                        
                        if filtered_obs:
                            observations = filtered_obs
                            print(f"✅ Observations filtrées manuellement: {len(observations)}")
                
                if not observations:
                    return {}
            
            # Traitement des données d'observations
            fish_counts = {}
            processed_count = 0
            
            print("🐟 Traitement des observations...")
            for obs in observations:
                processed_count += 1
                
                # Récupérer le nom du poisson (essayer différents champs)
                nom_poisson = (
                    obs.get("nom_commun_taxon") or 
                    obs.get("nom_latin_taxon") or 
                    obs.get("nom_taxon") or
                    obs.get("libelle_taxon") or
                    obs.get("espece")
                )
                
                if not nom_poisson:
                    continue
                
                nom_poisson = nom_poisson.strip()
                
                # Filtrer par poisson spécifique si demandé
                if poisson and poisson.lower() not in nom_poisson.lower():
                    continue
                
                # Récupérer l'effectif (essayer différents champs)
                effectif = (
                    obs.get("effectif_total") or 
                    obs.get("effectif") or 
                    obs.get("nombre") or
                    obs.get("quantite") or
                    obs.get("effectif_lot") or
                    1  # Valeur par défaut
                )
                
                # Convertir en entier
                try:
                    if isinstance(effectif, str) and effectif.strip() == "":
                        effectif = 1
                    effectif = int(float(effectif)) if effectif else 1
                    if effectif <= 0:
                        effectif = 1
                except (ValueError, TypeError):
                    effectif = 1
                
                # Accumuler les effectifs par espèce
                if nom_poisson in fish_counts:
                    fish_counts[nom_poisson] += effectif
                else:
                    fish_counts[nom_poisson] = effectif
                
                # Debug pour les premières observations
                if processed_count <= 3:
                    print(f"  Obs {processed_count}: {nom_poisson} = {effectif}")
                    print(f"    Champs disponibles: {list(obs.keys())}")
            
            print(f"📈 Observations traitées: {processed_count}")
            print(f"🎯 Espèces uniques trouvées: {len(fish_counts)}")
            
            if fish_counts:
                # Trier par effectif décroissant et limiter aux 12 espèces les plus observées
                sorted_fish = dict(sorted(fish_counts.items(), key=lambda x: x[1], reverse=True)[:12])
                
                print(f"🏆 Top des espèces:")
                for i, (espece, count) in enumerate(sorted_fish.items(), 1):
                    print(f"  {i}. {espece}: {count}")
                
                return sorted_fish
            else:
                print("❌ Aucune donnée valide après traitement")
                return {}
        
        else:
            print(f"❌ Erreur API: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Détail erreur: {error_data}")
            except:
                print(f"Réponse brute: {response.text[:500]}")
            return {}
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout lors de l'appel à l'API Hub'eau")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"🌐 Erreur de requête: {e}")
        return {}
    except Exception as e:
        print(f"💥 Erreur inattendue: {e}")
        return {}

def testApiConnection():
    """
    Teste la connexion à l'API Hub'eau et affiche des informations détaillées
    """
    print("=== TEST DÉTAILLÉ API HUB'EAU ===")
    
    try:
        # Test de base
        url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"
        response = requests.get(url, params={"size": 5}, timeout=10)
        
        print(f"1. Test connexion API:")
        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 206]:
            data = response.json()
            print(f"   ✅ Total observations: {data.get('count', 'N/A')}")
            
            if data.get('data'):
                print(f"   📊 Échantillon reçu: {len(data['data'])} observations")
                
                # Analyser la structure des données
                sample = data['data'][0]
                print(f"   📋 Champs disponibles:")
                for key, value in sample.items():
                    print(f"     - {key}: {type(value).__name__} = {str(value)[:50]}")
                
                # Test avec un département spécifique
                print(f"\n2. Test avec département 'Savoie':")
                dept_response = requests.get(url, params={
                    "size": 10,
                    "libelle_departement": "Savoie"
                }, timeout=10)
                
                if dept_response.status_code in [200, 206]:
                    dept_data = dept_response.json()
                    print(f"   Observations pour Savoie: {len(dept_data.get('data', []))}")
                    
                    if dept_data.get('data'):
                        savoie_sample = dept_data['data'][0]
                        print(f"   Exemple Savoie:")
                        print(f"     - Espèce: {savoie_sample.get('nom_commun_taxon', 'N/A')}")
                        print(f"     - Effectif: {savoie_sample.get('effectif_total', 'N/A')}")
                        print(f"     - Date: {savoie_sample.get('date_observation', 'N/A')}")
                
                # Récupérer les départements disponibles
                print(f"\n3. Départements disponibles:")
                all_response = requests.get(url, params={"size": 200}, timeout=15)
                if all_response.status_code in [200, 206]:
                    all_data = all_response.json()
                    departements = set()
                    for obs in all_data.get('data', []):
                        dept = obs.get('libelle_departement')
                        if dept:
                            departements.add(dept)
                    
                    dept_list = sorted(list(departements))
                    print(f"   Départements trouvés: {dept_list[:15]}...")
                    print(f"   Total départements: {len(dept_list)}")
                
                return True
        else:
            print(f"   ❌ Erreur: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   💥 Erreur test API: {e}")
        return False

@lru_cache(maxsize=1)
def getDepartmentsList():
    """
    Récupère la liste des départements disponibles depuis l'API Hub'eau
    """
    print("=== RÉCUPÉRATION DÉPARTEMENTS DEPUIS API ===")
    
    try:
        url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"
        response = requests.get(url, params={"size": 500}, timeout=15)
        
        if response.status_code in [200, 206]:
            data = response.json()
            observations = data.get("data", [])
            
            departements = set()
            for obs in observations:
                dept = obs.get("libelle_departement")
                if dept and dept.strip():
                    departements.add(dept.strip())
            
            dept_list = sorted(list(departements))
            print(f"✅ Départements API: {len(dept_list)} trouvés")
            print(f"Exemples: {dept_list[:10]}")
            
            if dept_list:
                return dept_list
    
    except Exception as e:
        print(f"❌ Erreur récupération départements: {e}")
    
    # Fallback avec départements français standards
    print("🔄 Utilisation de la liste de fallback")
    return [
        "Ain", "Aisne", "Allier", "Alpes-de-Haute-Provence", "Hautes-Alpes",
        "Alpes-Maritimes", "Ardèche", "Ardennes", "Ariège", "Aube", "Aude",
        "Aveyron", "Bouches-du-Rhône", "Calvados", "Cantal", "Charente",
        "Charente-Maritime", "Cher", "Corrèze", "Corse-du-Sud", "Haute-Corse",
        "Côte-d'Or", "Côtes-d'Armor", "Creuse", "Dordogne", "Doubs", "Drôme",
        "Eure", "Eure-et-Loir", "Finistère", "Gard", "Haute-Garonne", "Gers",
        "Gironde", "Hérault", "Ille-et-Vilaine", "Indre", "Indre-et-Loire",
        "Isère", "Jura", "Landes", "Loir-et-Cher", "Loire", "Haute-Loire",
        "Loire-Atlantique", "Loiret", "Lot", "Lot-et-Garonne", "Lozère",
        "Maine-et-Loire", "Manche", "Marne", "Haute-Marne", "Mayenne",
        "Meurthe-et-Moselle", "Meuse", "Morbihan", "Moselle", "Nièvre",
        "Nord", "Oise", "Orne", "Pas-de-Calais", "Puy-de-Dôme",
        "Pyrénées-Atlantiques", "Hautes-Pyrénées", "Pyrénées-Orientales",
        "Bas-Rhin", "Haut-Rhin", "Rhône", "Haute-Saône", "Saône-et-Loire",
        "Sarthe", "Savoie", "Haute-Savoie", "Paris", "Seine-Maritime",
        "Seine-et-Marne", "Yvelines", "Deux-Sèvres", "Somme", "Tarn",
        "Tarn-et-Garonne", "Var", "Vaucluse", "Vendée", "Vienne",
        "Haute-Vienne", "Vosges", "Yonne", "Territoire de Belfort",
        "Essonne", "Hauts-de-Seine", "Seine-Saint-Denis", "Val-de-Marne",
        "Val-d'Oise"
    ]
