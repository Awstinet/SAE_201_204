import sqlite3
import os
import pandas
import requests

# Chemin d'accès de la base de données
dbPath = os.path.join(os.path.dirname(__file__), "poisson.db")   

def connect_db():
    return sqlite3.connect(dbPath)

def getStations(zone: str, nomZone: str):
    """Récupère toutes les stations dans une zone (région ou département) avec leurs infos complètes."""
    conn = connect_db()

    try:
        if zone == "region":
            query = """
            SELECT
                Stations.code_station, 
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
            query = """
            SELECT
                Stations.code_station, 
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
        
        stations = pandas.read_sql_query(query, conn, params=(nomZone,))
        return stations
        
    except Exception as e:
        print("Erreur SQL :", e)
        return pandas.DataFrame()
    finally:
        conn.close()

def getNbStations():
    conn = connect_db()
    try:
        nbStations = pandas.read_sql_query("SELECT COUNT (*) as count FROM Stations;", conn)
        return nbStations["count"].iloc[0]
    except Exception as e:
        print(f"Erreur getNbStations: {e}")
        return 0
    finally:
        conn.close()

def getAllDepts():
    """Récupère la liste des départements depuis l'API Hub'eau"""
    try:
        from utils.poissonsParZone import getDepartmentsList
        return getDepartmentsList()
    except Exception as e:
        print(f"Erreur récupération départements: {e}")
        # Fallback minimal uniquement en cas d'erreur critique
        return ["Ain", "Bouches-du-Rhône", "Nord", "Paris", "Rhône"]
