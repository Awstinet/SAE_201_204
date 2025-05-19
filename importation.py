import sqlite3
import requests
import time
import json

# Connexion à la base de données SQLite (créée si elle n'existe pas)
conn = sqlite3.connect("Poisson.db")
cursor = conn.cursor()

# Création des tables si elles n'existent pas déjà
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

CREATE TABLE IF NOT EXISTS Operations (
    code_operation TEXT PRIMARY KEY,
    code_station TEXT,
    date_operation DATE,
    FOREIGN KEY (code_station) REFERENCES Stations(code_station)
);

CREATE TABLE IF NOT EXISTS Observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_operation TEXT,
    code_espece_poisson TEXT,
    nombre_poissons INTEGER,
    FOREIGN KEY (code_operation) REFERENCES Operations(code_operation)
);

CREATE TABLE IF NOT EXISTS Indicateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_station TEXT,
    code_operation TEXT,
    code_indicateur TEXT,
    valeur REAL,
    FOREIGN KEY (code_station) REFERENCES Stations(code_station),
    FOREIGN KEY (code_operation) REFERENCES Operations(code_operation)
);
""")
conn.commit()

# Fonction pour récupérer et insérer les données d'une API
def recuperer_et_inserer(api_url, table_name, fields):
    page = 1
    has_next = True
    total_inserts = 0

    while has_next:
        params = {
            "size": 100,
            "page": page
        }
        
        # Pour les stations et opérations, on peut demander des champs spécifiques
        # Pour les observations et indicateurs, on récupère tous les champs
        if table_name in ["Stations", "Operations"]:
            params["fields"] = ",".join(fields)

        print(f"\n🔄 Récupération {table_name} - page {page}")
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # Déclenche une exception en cas d'erreur HTTP
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la requête à {api_url}: {e}")
            break

        try:
            data = response.json()
            # Afficher un petit échantillon pour vérifier la structure
            if page == 1:
                print(f"Structure de réponse: {list(data.keys())}")
                if "data" in data and len(data["data"]) > 0:
                    print(f"Structure d'un élément: {list(data['data'][0].keys())}")
        except ValueError as e:
            print(f"❌ Erreur lors du parsing JSON: {e}")
            break

        if not data.get("data"):
            print(f"⚠️ Aucune donnée trouvée pour {table_name} à la page {page}")
            break

        # Vérifier les clés pour comprendre la structure de l'API
        inserted_count = 0
        for item in data["data"]:
            # Préparer les valeurs à insérer
            values = []
            missing_fields = False
            
            for field in fields:
                if field in item:
                    values.append(item[field])
                else:
                    print(f"⚠️ Champ manquant: {field} dans {item}")
                    missing_fields = True
                    break
            
            if missing_fields:
                continue
                
            # Insérer les données
            placeholders = ",".join(["?"] * len(fields))
            champs = ",".join(fields)
            sql = f"INSERT OR IGNORE INTO {table_name} ({champs}) VALUES ({placeholders})"
            
            try:
                cursor.execute(sql, values)
                if cursor.rowcount > 0:
                    inserted_count += 1
            except sqlite3.Error as e:
                print(f"⚠️ Erreur SQL pour {table_name}: {e}")
                print(f"Requête: {sql}")
                print(f"Valeurs: {values}")

        conn.commit()
        print(f"✅ {inserted_count} enregistrements insérés dans {table_name} (page {page})")
        total_inserts += inserted_count

        # Vérifier s'il y a une page suivante
        if data.get("next") and inserted_count > 0:
            page += 1
            time.sleep(0.5)  # Pause pour éviter de surcharger l'API
        else:
            has_next = False

    print(f"🎉 Total des données insérées dans {table_name}: {total_inserts}")
    
# Fonction pour compléter les données géographiques
def completer_donnees_geo():
    # Récupérer les communes, départements et régions manquants
    cursor.execute("SELECT DISTINCT code_commune FROM Stations WHERE code_commune IS NOT NULL")
    communes = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT code_departement FROM Stations WHERE code_departement IS NOT NULL")
    departements = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT code_region FROM Stations WHERE code_region IS NOT NULL")
    regions = [row[0] for row in cursor.fetchall()]
    
    # Compléter les communes
    for code_commune in communes:
        try:
            url = f"https://geo.api.gouv.fr/communes/{code_commune}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                cursor.execute(
                    "INSERT OR IGNORE INTO Communes (code_commune, nom_com, code_departement) VALUES (?, ?, ?)",
                    (code_commune, data.get("nom"), data.get("codeDepartement"))
                )
        except Exception as e:
            print(f"Erreur lors de la récupération de la commune {code_commune}: {e}")
    
    # Compléter les départements
    for code_dept in departements:
        try:
            url = f"https://geo.api.gouv.fr/departements/{code_dept}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                cursor.execute(
                    "INSERT OR IGNORE INTO Departements (code_departement, nom_dept, code_region) VALUES (?, ?, ?)",
                    (code_dept, data.get("nom"), data.get("codeRegion"))
                )
        except Exception as e:
            print(f"Erreur lors de la récupération du département {code_dept}: {e}")
    
    # Compléter les régions
    for code_region in regions:
        try:
            url = f"https://geo.api.gouv.fr/regions/{code_region}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                cursor.execute(
                    "INSERT OR IGNORE INTO Regions (code_region, nom_reg) VALUES (?, ?)",
                    (code_region, data.get("nom"))
                )
        except Exception as e:
            print(f"Erreur lors de la récupération de la région {code_region}: {e}")
    
    conn.commit()
    print("✅ Données géographiques complétées")

# Définition des APIs et des champs à importer
apis = [
    {
        "url": "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/stations",
        "table": "Stations",
        "fields": ["code_station", "libelle_station", "code_commune", "code_departement", "code_region", "latitude", "longitude"]
    },
    {
        "url": "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/operations",
        "table": "Operations",
        "fields": ["code_operation", "code_station", "date_operation"]
    },
    {
        "url": "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations",
        "table": "Observations",
        "fields": ["code_operation", "code_espece_poisson", "nombre_poissons"]
    },
    {
        "url": "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/indicateurs",
        "table": "Indicateurs",
        "fields": ["code_station", "code_operation", "code_indicateur", "valeur"]
    }
]

# Récupération des données pour chaque API
for api in apis:
    recuperer_et_inserer(api["url"], api["table"], api["fields"])

# Compléter les données géographiques
completer_donnees_geo()

# Analyser les données chargées
def analyser_donnees():
    print("\n📊 Analyse des données chargées:")
    
    tables = ["Stations", "Operations", "Observations", "Indicateurs", "Communes", "Departements", "Regions"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"- Table {table}: {count} enregistrements")
    
    # Espèces de poissons les plus courantes
    cursor.execute("""
        SELECT code_espece_poisson, SUM(nombre_poissons) as total
        FROM Observations
        GROUP BY code_espece_poisson
        ORDER BY total DESC
        LIMIT 5
    """)
    print("\n🐟 Top 5 des espèces de poissons les plus nombreuses:")
    for espece, total in cursor.fetchall():
        print(f"- {espece}: {total} poissons")

# Analyser les données chargées
analyser_donnees()

# Fermeture
conn.close()
print("\n🎉 Importation terminée avec succès !")