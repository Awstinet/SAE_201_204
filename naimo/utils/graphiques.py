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
    """
    Génère un graphique linéaire pour l'évolution des poissons
    """
    try:
        plt.figure(figsize=(10, 6))
        plt.clf()
        
        plt.plot(annees, effectifs, color="#0DAAEE", marker="o", linewidth=2, markersize=6)
        plt.xlabel("Années", fontsize=12)
        plt.ylabel("Nombre de poissons", fontsize=12)
        plt.title("Évolution du nombre de poissons", fontsize=14, fontweight='bold')
        plt.grid(axis="y", alpha=0.3)
        
        # Amélioration de l'apparence
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight",
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Erreur lors de la génération du graphique linéaire: {e}")
        plt.close()
        return None
