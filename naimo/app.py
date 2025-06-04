from flask import Flask, render_template, request, jsonify
import matplotlib
import data.datas as db
from utils.name import normaliser
from utils.majDonnes import updateDatabase


# Déclaration d'application Flask
app = Flask(__name__)

# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')

@app.route("/pageLoaded", methods=["POST"])
def pageLoaded():   
    updateDatabase()
    return "", 204


@app.route('/accueil')
def accueil():
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

    if zone == "region":
        nomZone = normaliser(nomZone) #On normalise le nom de la région pour que ça corresponde avec celui de la BDD

    stationsDF = db.getStations(zone, nomZone) #On récupère les stations se trouvant dans la zone indiquée, avec son nom.
    stations = stationsDF["libelle_station"].tolist() #On convertit ça en liste
    return jsonify({"stations": stations}) #On retourne toutes les stations qu'on renverra par la suite sur le HTML





if __name__ == '__main__':
    app.run(debug=True)