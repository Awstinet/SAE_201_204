import sqlite3
import os
import pandas 

# Chemin d'accès de la base de données
dbPath = os.path.join(os.path.dirname(__file__), "poisson.db")   

# Fonction permettant la connexion à la base de données quand on l'appel
def connect_db():
    return sqlite3.connect(dbPath)

def getStations(zone: str, nomZone: str):
    """Récupère toutes les stations qui se trouvent dans la zone (Département ou Région), suivi du nom de celle-ci."""
    conn = connect_db()
    query = f"""SELECT libelle_station FROM Stations WHERE Stations.code_{zone} IN 
    (SELECT code_{zone} FROM {zone.capitalize()}s WHERE nom_{"reg" if zone == "region" else "dept"} = ?) ORDER BY libelle_station  ;"""
    stations = pandas.read_sql_query(query, conn, params=(nomZone,))
    conn.close()
    return stations


