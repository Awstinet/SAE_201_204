import sqlite3
import requests
import os

# Chemin vers la base de données SQLite
db_path = os.path.join(os.path.dirname(__file__), "Poisson.db")

# Connexion à la base de données
def connect_db():
    return sqlite3.connect(db_path)

# Création de la table Stations
def create_table_stations():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Stations (
            code_station TEXT PRIMARY KEY,
            libelle_station TEXT,
            code_commune TEXT,
            code_departement TEXT,
            code_region TEXT,
            latitude REAL,
            longitude REAL
        );
    """)
    conn.commit()
    conn.close()

# Insertion en bloc dans la table Stations
def inserer_stations(conn, stations):
    cursor = conn.cursor()
    query = """
        INSERT OR IGNORE INTO Stations (
            code_station, libelle_station, code_commune,
            code_departement, code_region, latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    cursor.executemany(query, stations)
    conn.commit()

# Récupération des stations pour un département donné
def recuperer_stations_par_departement(code_departement):
    url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/stations"
    page = 1
    page_size = 1000
    stations = []

    while True:
        params = {
            "code_departement": code_departement,
            "page": page,
            "size": page_size,
            "statut_station": "true"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            donnees = data.get("data", [])
            if not donnees:
                break
            for station in donnees:
                stations.append((
                    station.get("code_station"),
                    station.get("libelle_station"),
                    station.get("code_commune"),
                    station.get("code_departement"),
                    station.get("code_region"),
                    station.get("latitude"),
                    station.get("longitude")
                ))
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération des stations pour le département {code_departement} : {e}")
            break

    return stations

# Liste des codes de départements (extrait du référentiel SANDRE)
codes_departements = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09',
    '10', '11', '12', '13', '14', '15', '16', '17', '18',
    '19', '21', '22', '23', '24', '25', '26', '27', '28',
    '29', '2A', '2B', '30', '31', '32', '33', '34', '35',
    '36', '37', '38', '39', '40', '41', '42', '43', '44',
    '45', '46', '47', '48', '49', '50', '51', '52', '53',
    '54', '55', '56', '57', '58', '59', '60', '61', '62',
    '63', '64', '65', '66', '67', '68', '69', '70', '71',
    '72', '73', '74', '75', '76', '77', '78', '79', '80',
    '81', '82', '83', '84', '85', '86', '87', '88', '89',
    '90', '91', '92', '93', '94', '95'
]

# Création de la table Stations
create_table_stations()

# Récupération et insertion des stations pour chaque département
for code_dept in codes_departements:
    print(f"Traitement du département {code_dept}...")
    stations = recuperer_stations_par_departement(code_dept)
    if stations:
        conn = connect_db()
        inserer_stations(conn, stations)
        conn.close()
        print(f"{len(stations)} stations insérées pour le département {code_dept}.")
    else:
        print(f"Aucune station trouvée pour le département {code_dept}.")
