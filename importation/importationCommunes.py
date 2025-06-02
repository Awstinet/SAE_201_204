import requests
import sqlite3
import os
import time

# Connexion BDD
db_path = os.path.join(os.path.dirname(__file__), "Poisson.db")
def connect_db():
    return sqlite3.connect(db_path)

def inserer_communes(conn, liste_communes):
    cursor = conn.cursor()
    query = """
        INSERT OR IGNORE INTO Communes (code_commune, nom_com, code_departement)
        VALUES (?, ?, ?)
    """
    cursor.executemany(query, liste_communes)
    conn.commit()

# Liste des codes départements (métropole + outre-mer)
codes_dept = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
    '11', '12', '13', '14', '15', '16', '17', '18', '19', '2A', '2B',
    '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31',
    '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42',
    '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53',
    '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64',
    '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75',
    '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86',
    '87', '88', '89', '90', '91', '92', '93', '94', '95', '971', '972',
    '973', '974', '976'
]

def extraire_et_inserer_communes_par_departement():
    base_url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"
    total_communes = set()

    for code_dept in codes_dept:
        page = 1
        print(f"\nDépartement {code_dept}")
        while True:
            try:
                print(f"  → page {page}")
                response = requests.get(base_url, params={
                    "page": page,
                    "size": 10000,
                    "code_departement": code_dept
                }, timeout=15)

                response.raise_for_status()
                data = response.json().get("data", [])
                if not data:
                    print(f"  → Fin du département {code_dept}")
                    break

                nouvelles_communes = []

                for obs in data:
                    code_commune = obs.get("code_commune")
                    libelle_commune = obs.get("libelle_commune")
                    if not code_commune or not libelle_commune:
                        continue
                    commune_tuple = (code_commune, libelle_commune, code_dept)
                    if commune_tuple not in total_communes:
                        total_communes.add(commune_tuple)
                        nouvelles_communes.append(commune_tuple)

                if nouvelles_communes:
                    conn = connect_db()
                    inserer_communes(conn, nouvelles_communes)
                    conn.close()
                    print(f"  → {len(nouvelles_communes)} communes insérées")

                page += 1

            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ Erreur sur le département {code_dept}, page {page} : {e}")
                break

            time.sleep(0.5)  # Anti-surcharge

    print(f"\n✅ Import terminé. {len(total_communes)} communes uniques insérées.")

# Lancement
extraire_et_inserer_communes_par_departement()
