from datetime import datetime, timedelta
import requests

# Cache pour les observations
observations_cache = {
    "count": 0,
    "last_updated": datetime.now() - timedelta(hours=1)
}

def get_observations_count():
    """Récupère le nombre total d'observations avec cache"""
    global observations_cache
    
    if datetime.now() - observations_cache["last_updated"] < timedelta(hours=1):
        return observations_cache["count"]
    
    try:
        response = requests.get(
            "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations",
            params={"size": 1},
            timeout=10
        )
        response.raise_for_status()
        count = response.json().get("count", 0)
        
        observations_cache = {
            "count": count,
            "last_updated": datetime.now()
        }
        return count
    except Exception as e:
        return None