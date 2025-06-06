import sqlite3
import requests
import os
import pandas
from datetime import datetime


def connect_db():
    return sqlite3.connect(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/poisson.db")))

def getLastDate() -> str:
    """Récupère des dernières observations de l'API"""
    conn = connect_db()
    query = """SELECT dateMAJ FROM miseAJour;"""
    date = pandas.read_sql_query(query, conn)
    conn.close()
    return date.to_dict()["dateMAJ"][0]

def changeLastDate() -> None:
    #On va chercher la dernière date
    url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"
    response = requests.get(url)
    data = response.json()
    lastObs = data["data"][0].get("date_operation", "")[:10] #Récupération de la date de la dernière observartion. Faisable car elles sont triées par ordre chronologique
    lastObs = datetime.strptime(lastObs, "%Y-%m-%d") #On s'assure que la date soit bien sous le format YYYY-MM-DD

    #On met la nouvelle date dans la BDD
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE miseAJour SET dateMAJ = ?", (lastObs.date().isoformat(),))
    conn.commit()
    conn.close()
    return None


def updateDatabase() -> None:
    url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"
    response = requests.get(url)
    datas = response.json()

    last_date = getLastDate() #On récupère la date de la dernière observation (celle de la BDD)
    for obs in datas["data"]: #On parcourt les données d'observations 
        obs_date = obs.get("date_operation", "")[:10] #On récupère la date à chaque observation
        if obs_date > last_date: #Si elle n'est pas antérieure à celle qu'on a, arrête le script.
            importGen() 
            changeLastDate()
            return



#On regarde si la ligne existe dans la table spécifiée
def getLine(conn, table: str, nomColonne: str, id):
    query = f"""SELECT * FROM "{table}" WHERE {nomColonne} = ?;"""
    line = pandas.read_sql_query(query, conn, params=(id,))
    return line.to_dict()


# Fonction pour insérer en bloc dans la base, question d'optimisation
def insertionEnBloc(conn, table: str, columns: list, values_list: list):
    cursor = conn.cursor()
    placeholders = ", ".join("?" for _ in columns)
    columns_str = ", ".join(columns)
    query = f"INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders});"
    cursor.executemany(query, values_list)


#Fonction à appeler lorsque les données statiques ne sont plus à jour.
def importGen(url="https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations", page_size=5000, max_pages=None):
    """Cette fonction permet d'importer de manière massive toutes les données de l'API Hub'Eau en une seule exécution."""

    #Chacune des tables de notre BDD avec le mapping car les noms sont différents entre clefs de l'API & Colonne d'un tableau.
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

    #Set de dictionnaires de toutes les données qu'on a ajouté lors de l'exécution, pour ne pas ajouter 2 fois la même chose. 
    dctAjouts = {api["table"]: set() for api in apis}
    page = 1

    #Tant qu'on arrête pas la boucle
    while True:
        response = requests.get(url, params={"page": page, "size": page_size}) #Appel de l'API
        
        #En cas d'erreur lors de la récupération des données
        if not response.ok:
            print(f"Erreur lors de la requête page {page} : {response.status_code}")
            break

        #On stocke les réponses de l'API 
        data = response.json() 
        observations = data.get("data", [])

        #Si il n'y a plus rien, c'est que l'API a terminée d'être parcourue
        if not observations:
            break

        #Si on se rend compte qu'une des données a une date d'opération antiérieure à la date de la dernière mise à jour, on arrête l'importation car ça veut dire
        #Que la BDD est à jour elle aussi.
        if observations[0].get("date_operation")[:10] >= getLastDate():
            print("Donnée antérieure à la date de la dernière mise à jour.")
            break

        conn = connect_db() #Connexion à la base de données
        lstInsertions = {api["table"]: [] for api in apis} #Le bloc de données à insérer à la fin de la boucle

        #Pour chacune des tables de notre BDD
        for api in apis:
            #On récupère la table, la colonne associée dans la BDD, la clef des valeurs de l'API
            table = api["table"] 
            mapping = api["mapping"]
            colonnes = list(mapping.values())
            clefs_api = list(mapping.keys())

            #Pour chacune des observations
            for obs in observations:
                #On récupère toutes les valeurs du résultat qui nous intéressent
                valeurs = [obs.get(cle) for cle in clefs_api]
                #On vérifie qu'au moins une colonne n'est pas vide.
                if any(valeurs):
                    valeur_tuple = tuple(valeurs)
                    if valeur_tuple not in dctAjouts[table]:
                        # Vérifie si cette ligne existe déjà dans la base
                        cle_primaire = colonnes[0]
                        valeur_cle = valeurs[0]
                        if not getLine(conn, table, cle_primaire, valeur_cle)[cle_primaire]:
                            lstInsertions[table].append(valeurs)
                        dctAjouts[table].add(valeur_tuple)

        #L'insertion en bloc dans la BDD se fait ici
        for api in apis:
            table = api["table"]
            colonnes = list(api["mapping"].values())
            if lstInsertions[table]:
                insertionEnBloc(conn, table, colonnes, lstInsertions[table])
                for ligne in lstInsertions[table]:
                    print(f"[{table}] {dict(zip(colonnes, ligne))}")

        conn.commit()
        conn.close()

        page += 1
        if max_pages is not None and page > max_pages:
            print("Nombre maximal de pages atteint.")
            break