import requests
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def get_total_poissons_zone(departement: str, annee: int) -> dict:
    """
    Récupère le total des poissons observés dans un département donné et une année.
    Retourne un dictionnaire {nom_taxon: effectif_total}.
    """
    url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"
    params = {
        "code_departement": departement,
        "date_debut": f"{annee}-01-01",
        "date_fin": f"{annee + 5}-01-01",  # Large plage pour plus de données
        "size": 10000
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", [])
        
        dct = {}
        for obs in data:
            espece = obs.get("nom_taxon")
            nb = obs.get("effectif_total", 0)
            if espece:
                dct[espece] = dct.get(espece, 0) + nb

        return dct
    except Exception as e:
        print(f"[Erreur Hub’Eau] {e}")
        return {}

def generer_camembert(dct_poissons: dict) -> str | None:
    """
    Génère un graphique camembert à partir d’un dictionnaire {nom_taxon: total}.
    Retourne une image encodée en base64 (data URI).
    """
    if not dct_poissons or sum(dct_poissons.values()) == 0:
        return None

    labels = list(dct_poissons.keys())
    sizes = list(dct_poissons.values())

    # Simplification si trop d’espèces
    if len(labels) > 10:
        labels, sizes = zip(*sorted(zip(labels, sizes), key=lambda x: x[1], reverse=True)[:10])
        labels = list(labels) + ['Autres']
        sizes = list(sizes) + [sum(dct_poissons.values()) - sum(sizes)]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # cercle parfait

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return f"data:image/png;base64,{img_base64}"

def get_camembert_total_poissons_zone(departement: str, annee: int) -> tuple[dict, str | None]:
    """
    Fonction complète pour le back-end Flask.
    Retourne (dictionnaire de poissons, image base64 du camembert).
    """
    dct = get_total_poissons_zone(departement, annee)
    image = generer_camembert(dct)
    return dct, image
