import matplotlib.pyplot as plt
import matplotlib
import base64
from io import BytesIO
import numpy as np

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

def graphePoissonsParRegion(annees: list, effectifs: list):
    plt.figure(figsize=(5, 3))
    plt.plot(annees, effectifs, color="#0DAAEE", marker="o")
    plt.xlabel("Années")
    plt.ylabel("Nombre de poissons")
    plt.title("Évolution du nombre de poissons")
    plt.grid(axis="y", alpha=0.75)

    imageStream = BytesIO()
    plt.savefig(imageStream, format="png", bbox_inches="tight")
    plt.close()

    imageBase64 = base64.b64encode(imageStream.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{imageBase64}"


def getObservations(annee: int, departement: str):
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
    plt.figure(figsize=(5, 3))
    plt.plot(annees, nbObservations, color="#0DAAEE", marker="o")
    plt.xlabel("Années")
    plt.ylabel("Nombre de poissons")
    plt.title("Évolution du nombre de poissons")
    plt.grid(axis="y", alpha=0.75)

    imageStream = BytesIO()
    plt.savefig(imageStream, format="png", bbox_inches="tight")
    plt.close()

    imageBase64 = base64.b64encode(imageStream.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{imageBase64}"