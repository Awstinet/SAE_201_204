import sqlite3
import requests
import os
import pandas

# Définir le chemin vers la base de données SQLite (fichier Poisson.db situé dans le même dossier que le script)
db_path = os.path.join(os.path.dirname(__file__), "Poisson.db")

# Connexion à la base de données
def connect_db():
    return sqlite3.connect(db_path)

# Création des tables (si elles n'existent pas déjà)
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Regions (
        code_region TEXT PRIMARY KEY,
        nom_reg TEXT
    );

    CREATE TABLE IF NOT EXISTS Departements (
        code_departement TEXT PRIMARY KEY,
        nom_dept TEXT,
        code_region TEXT,
        FOREIGN KEY (code_region) REFERENCES Regions(code_region)
    );

    CREATE TABLE IF NOT EXISTS Communes (
        code_commune TEXT PRIMARY KEY,
        nom_com TEXT,
        code_departement TEXT,
        FOREIGN KEY (code_departement) REFERENCES Departements(code_departement)
    );

    CREATE TABLE IF NOT EXISTS Stations (
        code_station TEXT PRIMARY KEY,
        libelle_station TEXT,
        code_commune TEXT,
        code_departement TEXT,
        code_region TEXT,
        latitude REAL,
        longitude REAL,
        FOREIGN KEY (code_commune) REFERENCES Communes(code_commune),
        FOREIGN KEY (code_departement) REFERENCES Departements(code_departement),
        FOREIGN KEY (code_region) REFERENCES Regions(code_region)
    );
    
    -- (Optionnel) Index pour optimiser les recherches
    CREATE INDEX IF NOT EXISTS idx_station_commune ON Stations(code_commune);
    CREATE INDEX IF NOT EXISTS idx_commune_dept ON Communes(code_departement);
    CREATE INDEX IF NOT EXISTS idx_dept_region ON Departements(code_region);
    """)
    conn.commit()
    conn.close()

def getLine(conn, table: str, nomColonne: str, id):
    query = f"""SELECT * FROM "{table}" WHERE {nomColonne} = ?;"""
    line = pandas.read_sql_query(query, conn, params=(id,))
    return line.to_dict()


# Fonction pour insérer en bloc (batch insert) dans la base
def inserer_en_bloc(conn, table: str, columns: list, values_list: list):
    cursor = conn.cursor()
    placeholders = ", ".join("?" for _ in columns)
    columns_str = ", ".join(columns)
    query = f"INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders});"
    cursor.executemany(query, values_list)



# Mappage entre les clés JSON de l'API et les colonnes SQLite
apis = [
    {
        "table": "Stations",
        "mapping": {
            "code_station": "code_station",
            "libelle_station": "libelle_station",
            "code_commune": "code_commune",
            "code_departement": "code_departement",
            "code_region": "code_region",
            "latitude": "latitude",
            "longitude": "longitude"
        }
    },
    {
        "table": "Communes",
        "mapping": {
            "code_commune": "code_commune",
            "libelle_commune": "nom_com",
            "code_departement": "code_departement"
        }
    },
    {
        "table": "Departements",
        "mapping": {
            "code_departement": "code_departement",
            "libelle_departement": "nom_dept",
            "code_region": "code_region"
        }
    },
    {
        "table": "Regions",
        "mapping": {
            "code_region": "code_region",
            "libelle_region": "nom_reg"
        }
    }
]

# Création des tables à la première exécution
create_tables()

# URL de l'API Hubeau
url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"

# Taille de page et compteur de pagination
page = 1
page_size = 5000

# Ensemble des valeurs déjà insérées, pour éviter les doublons (utilisation de sets pour performance)
dctAjouts = {
    "Stations": set(),
    "Communes": set(),
    "Departements": set(),
    "Regions": set(),
}

# Boucle de récupération des données paginées
while True:
    print(f"\nRécupération de la page {page}...")
    response = requests.get(url, params={"page": page, "size": page_size})
    data = response.json()
    observations = data.get("data", [])

    # Si plus aucune donnée, on arrête la boucle
    if not observations:
        print(f"Aucune donnée trouvée à la page {page}. Fin de l'import.")
        break

    # Ouvre une seule connexion pour toute la page
    conn = connect_db()
    lstInsertions = {api["table"]: [] for api in apis}

    # Analyse des observations
    for api in apis:
        table = api["table"]
        mapping = api["mapping"]
        colonnes = list(mapping.values())
        clefs_api = list(mapping.keys())

        for obs in observations:
            valeurs = [obs.get(cle) for cle in clefs_api]
            if any(valeurs):  # Vérifie qu'au moins une valeur n'est pas None
                valeur_tuple = tuple(valeurs)
                if valeur_tuple not in dctAjouts[table]:
                    # Vérifie si cette ligne existe déjà dans la base
                    cle_primaire = colonnes[0]
                    valeur_cle = valeurs[0]
                    if not getLine(conn, table, cle_primaire, valeur_cle)[cle_primaire]:
                        lstInsertions[table].append(valeurs)
                    dctAjouts[table].add(valeur_tuple)


    # Insertion groupée pour chaque table
    for api in apis:
        table = api["table"]
        colonnes = list(api["mapping"].values())
        if lstInsertions[table]:
            inserer_en_bloc(conn, table, colonnes, lstInsertions[table])
            for ligne in lstInsertions[table]:
                print(f"[{table}] {dict(zip(colonnes, ligne))}")

    # Validation de la transaction
    conn.commit()
    conn.close()

    # Page suivante
    page += 1
