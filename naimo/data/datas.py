import sqlite3
import os
import pandas as pd

# Chemin d'accès de la base de données
dbPath = os.path.join(os.path.dirname(__file__), "poisson.db")   

# Fonction permettant la connexion à la base de données quand on l'appel
def connect_db():
    return sqlite3.connect(dbPath)

def getStations(zone: str, nomZone: str):
    """Récupère toutes les stations dans une zone (région ou département) avec leurs infos complètes."""
    conn = connect_db()

    try:
        if zone == "region":
            # Pour les régions, utilise les vrais noms de colonnes
            query = """
            SELECT 
                Stations.libelle_station,
                Communes.nom_com,
                Departements.nom_dept,
                Regions.nom_reg
            FROM Stations
            JOIN Communes ON Stations.code_commune = Communes.code_commune
            JOIN Departements ON Stations.code_departement = Departements.code_departement
            JOIN Regions ON Stations.code_region = Regions.code_region
            WHERE LOWER(TRIM(Regions.nom_reg)) = LOWER(TRIM(?))
            ORDER BY Stations.libelle_station;
            """
        else:
            # Pour les départements, utilise les vrais noms de colonnes
            query = """
            SELECT 
                Stations.libelle_station,
                Communes.nom_com,
                Departements.nom_dept,
                Regions.nom_reg
            FROM Stations
            JOIN Communes ON Stations.code_commune = Communes.code_commune
            JOIN Departements ON Stations.code_departement = Departements.code_departement
            JOIN Regions ON Stations.code_region = Regions.code_region
            WHERE LOWER(TRIM(Departements.nom_dept)) = LOWER(TRIM(?))
            ORDER BY Stations.libelle_station;
            """
        
        print(f"Recherche pour zone: {zone}, nom: '{nomZone}'")  # Debug
        stations = pd.read_sql_query(query, conn, params=(nomZone,))
        print(f"Nombre de stations trouvées: {len(stations)}")  # Debug
        
        if len(stations) == 0:
            # Test pour voir quels noms existent dans la base
            if zone == "region":
                test_query = "SELECT DISTINCT nom_reg FROM Regions ORDER BY nom_reg"
            else:
                test_query = "SELECT DISTINCT nom_dept FROM Departements ORDER BY nom_dept"
            
            available_names = pd.read_sql_query(test_query, conn)
            print("Noms disponibles dans la base:")
            print(available_names.iloc[:, 0].tolist())  # Affiche la liste des noms
        
        return stations
        
    except Exception as e:
        print("Erreur SQL :", e)
        return pd.DataFrame()
    finally:
        conn.close()