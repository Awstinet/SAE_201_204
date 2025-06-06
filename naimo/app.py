from flask import Flask, render_template, request, jsonify
import matplotlib
import data.datas as db
from utils.name import normaliser
# from utils.graphiques import generate_histogram, generate_boxplot



# Déclaration d'application Flask
app = Flask(__name__)

# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')


@app.route('/accueil')
def accueil():
    # Affichage du template
    return render_template('accueil.html')

@app.route('/apropos')
def apropos():
    # Affichage du template
    return render_template('apropos.html')

@app.route('/contact')
def contact():
    # Affichage du template
    return render_template('contact.html')

@app.route('/observations')
def observations():
    # Affichage du template
    return render_template('observations.html')



@app.route('/', methods=['GET'])
def prelevements():
    stations = [] #Par défaut, aucune station n'est affichée
    return render_template('prelevements.html', stations=stations)


@app.route('/departement', methods=['POST'])
def departement_post():
    data = request.get_json()
    nomZone = data.get("nom")
    zone = data.get("zone", "departement")
    
    print(f"Requête reçue - Zone: {zone}, Nom: '{nomZone}'")  # Debug
    
    # Normalisation pour les régions si nécessaire
    if zone == "region":
        nomZone = normaliser(nomZone)
        print(f"Nom normalisé: '{nomZone}'")  # Debug

    stationsDF = db.getStations(zone, nomZone)
    print(f"DataFrame retourné: {len(stationsDF)} lignes")  # Debug
    
    if not stationsDF.empty:
        print("Premières stations trouvées:")
        print(stationsDF.head())
    
    stations = stationsDF.to_dict(orient='records')  # Liste de dictionnaires
    
    result = {"stations": stations}
    print(f"Résultat final: {len(stations)} stations")  # Debug
    
    return jsonify(result)






if __name__ == '__main__':
    app.run(debug=True)