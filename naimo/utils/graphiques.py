import matplotlib.pyplot as plt
import matplotlib
import base64
from io import BytesIO
import requests

# Configuration pour éviter les problèmes d'affichage
matplotlib.use('Agg')
plt.style.use('default')


def camembertPoissonsParDept(labels, sizes):
    """
    Génère un graphique en camembert pour la répartition des poissons
    """
    try:
        print(f"Génération camembert avec labels: {labels}, sizes: {sizes}")
        
        # Vérification des données
        if not labels or not sizes or len(labels) != len(sizes):
            print("Erreur: données invalides pour le camembert")
            return None
        
        if sum(sizes) == 0:
            print("Erreur: somme des effectifs = 0")
            return None
        
        # Configuration de la figure
        plt.figure(figsize=(10, 8))
        plt.clf()  # Nettoie la figure
        
        # Couleurs personnalisées
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                 '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
        
        # Création du camembert
        wedges, texts, autotexts = plt.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(labels)],
            textprops={'fontsize': 10}
        )
        
        # Amélioration de l'apparence
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.title("Répartition des espèces de poissons", fontsize=14, fontweight='bold', pad=20)
        plt.axis('equal')  # Assure un cercle parfait
        
        # Sauvegarde en base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Conversion en base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()  # Ferme la figure pour libérer la mémoire
        
        result = f"data:image/png;base64,{image_base64}"
        print("Camembert généré avec succès")
        return result
        
    except Exception as e:
        print(f"Erreur lors de la génération du camembert: {e}")
        plt.close()  # Assure la fermeture même en cas d'erreur
        return None
    

    
def poissonsParDepartement(departement, annee, poisson):
    """Récupère le.s poisson.s du département indiqué, à l'année indiquée."""

    #Si l'année est None, on renvoie None.
    if annee is None:
        return None

    totalPoissons = 0 #Total de poissons récupérés

    #Notre URL
    url = (
        f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?"
        f"libelle_departement={departement}&"
        f"date_operation_min={annee}-01-01&"
        f"date_operation_max={annee}-12-31&"
        f"fields=effectif_lot"
    )

    #Si un poisson est spéficié, il rentre en compte dans l'URL pour qu'on ne récupère que ses données.
    if poisson != "all":
        url += f"&nom_commun_taxon={poisson}"

    response = requests.get(url)
    if not response.ok:
        raise ValueError(f"Erreur pour le département {departement}")

    data = response.json().get("data", [])

    for obs in data: #Pour chacune des observations
        try:
            effectif = int(obs.get("effectif_lot", 0)) or 0 #On récupère l'effectif de l'observation pour incrémenter par la suite le total.
        except (ValueError, TypeError):
            effectif = 0
        totalPoissons += effectif

    return totalPoissons


def graphePoissonsParDepartement(annees: list, effectifs: list):
    """Retourne le graphique des évolutions des poissons par département."""
    plt.figure(figsize=(5, 3))
    plt.plot(annees, effectifs, color="#0DAAEE", marker="o")
    plt.xlabel("Années")
    plt.ylabel("Nombre de poissons")
    plt.grid(axis="y", alpha=0.75)

    imageStream = BytesIO()
    plt.savefig(imageStream, format="png", bbox_inches="tight")
    plt.close()

    imageBase64 = base64.b64encode(imageStream.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{imageBase64}"


def getObservations(annee: int, departement: str):
    """Retourne le nombre d'observations faite sur l'année spécifiée, dans le département spécifié."""

    if annee is None:
        return None
    
    totalObservations = 0

    url = (
        f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?"
        f"date_operation_min={annee}-01-01"
        f"&date_operation_max={annee}-12-31"
        f"&libelle_departement={departement}"
        f"&fields=date_operation"
    )

    response = requests.get(url)
    if not response.ok:
        raise ValueError(f"Erreur pour le département {departement}")

    data = response.json().get("data", [])

    for _ in data:
        try:
            totalObservations += 1
        except (ValueError, TypeError):
            continue
        
    return totalObservations
    

def grapheNbObservations(annees: int, nbObservations: int):
    """Génère un graphique évolutif pour voir le nombre d'observations sur 5 ans."""
    plt.figure(figsize=(5, 3))
    plt.plot(annees, nbObservations, color="#0DAAEE", marker="o")
    plt.xlabel("Années")
    plt.ylabel("Nombre d'observations")
    plt.grid(axis="y", alpha=0.75)

    imageStream = BytesIO()
    plt.savefig(imageStream, format="png", bbox_inches="tight")
    plt.close()

    imageBase64 = base64.b64encode(imageStream.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{imageBase64}"

def poissonsParDepartement2(departement, annee, poisson):
    """
    Retourne un dictionnaire {nom_poisson: effectif} si poisson == 'all',
    sinon un total int pour une espèce donnée.
    """
    if annee is None:
        return None

    url = (
        f"https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations?"
        f"libelle_departement={departement}&"
        f"date_operation_min={annee}-01-01&"
        f"date_operation_max={annee}-12-31&"
        f"fields=effectif_lot,nom_commun_taxon"
    )

    if poisson != "all":
        url += f"&nom_commun_taxon={poisson}"

    response = requests.get(url)
    if not response.ok:
        raise ValueError(f"Erreur pour le département {departement}")

    data = response.json().get("data", [])

    if poisson != "all":
        total = 0
        for obs in data:
            try:
                total += int(obs.get("effectif_lot", 0)) or 0
            except:
                continue
        return total

    # Cas "all" : retour d'un dictionnaire
    repartition = {}
    for obs in data:
        nom = obs.get("nom_commun_taxon", "Inconnu")
        try:
            effectif = int(obs.get("effectif_lot", 0)) or 0
        except:
            effectif = 0
        repartition[nom] = repartition.get(nom, 0) + effectif

    return repartition


def camembertPoissonsParDept(repartition):
    """Génère un camembert à partir d’un dictionnaire {nom_poisson: effectif}"""
    if not repartition:
        return None

    labels = []
    sizes = []
    other = 0
    total = sum(repartition.values())

    for nom, effectif in repartition.items():
        if effectif / total >= 0.05:
            labels.append(nom)
            sizes.append(effectif)
        else:
            other += effectif

    if other > 0:
        labels.append("Autres espèces")
        sizes.append(other)

    plt.figure(figsize=(5, 3))
    plt.pie(sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.tab20.colors)
    plt.title("Répartition des poissons")
    plt.axis('equal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
