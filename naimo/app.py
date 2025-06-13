from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import requests
import matplotlib
import data.datas as db
from utils.name import normaliser
from utils.majDonnes import updateDatabase
from utils.majDonnes import getLastDate
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from utils.graphiques import *

# Déclaration d'application Flask
app = Flask(__name__)


###################################
##       Pour les messages       ##
###################################

app.secret_key = 'aquaexotica-secret-key'

# Configuration Flask-Mail (avec Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mail.test@gmail.com'         # <-- à remplacer
app.config['MAIL_PASSWORD'] = 'motDePasse'         # <-- mot de passe d'application Gmail
app.config['MAIL_DEFAULT_SENDER'] = 'mail.test@gmail.com'    # <-- même email

mail = Mail(app)


###################################
##             Reste             ##
###################################

# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')

@app.route("/pageLoaded", methods=["POST"])
def pageLoaded():   
    updateDatabase()
    return "", 204

# Cache pour les observations
observations_cache = {
    "count": 0,
    "last_updated": datetime.now() - timedelta(hours=1)
}

def get_observations_count():
    """Récupère le nombre total d'observations avec cache"""
    global observations_cache
    
    if datetime.now() - observations_cache["last_updated"] < timedelta(hours=1):
        return observations_cache["count"]
    
    try:
        response = requests.get(
            "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations",
            params={"size": 1},
            timeout=10
        )
        response.raise_for_status()
        count = response.json().get("count", 0)
        
        observations_cache = {
            "count": count,
            "last_updated": datetime.now()
        }
        return count
    except Exception as e:
        app.logger.error(f"Erreur comptage observations: {str(e)}")
        return None

@app.route("/")
def accueil():
    lastDate = getLastDate()
    nbObservations = get_observations_count()
    nbStations = db.getNbStations()
    return render_template("accueil.html", nbStations = nbStations, nbObservations = nbObservations, lastDate = lastDate)


@app.route('/apropos')
def apropos():
    # Affichage du template
    return render_template('apropos.html')


@app.route('/observations', methods=['GET', 'POST'])
def observations():
    if request.method == 'POST':
        data = request.form.get("clicked", "")
        try:
            selectedAnnee = int(request.form.get("poissonAnneeSelection"))
        except TypeError:
            selectedAnnee = "NaN"

        mappingTitre = {
            "evoPoissonsZone": "Graphique évolutif des poissons par année dans une zone.",
            "totalPoissonsZone": "Population de poissons par zone",
            "nbPrelevZones": "Nombre de prélèvements par zone"
        }

        titre = mappingTitre.get(data, "")

        annees = [annee for annee in range(1995, int(getLastDate()[:4]) + 1, 6)]

        dctPoissons = {}

        if not selectedAnnee == "NaN":
            for i in range(selectedAnnee, selectedAnnee + 6):
                dctPoissons[i] = poissonsParRegion("Savoie", i)
                if dctPoissons[selectedAnnee] == None:
                    dctPoissons = "NaN"
                    break

        return render_template(
            'popupObservation.html',
            titre=titre,
            annees=annees,
            selectedAnnee=selectedAnnee,
            dctPoissons=dctPoissons
        )

    return render_template("observations.html")





@app.route('/prelevements', methods=['GET'])
def prelevements():
    stations = [] #Par défaut, aucune station n'est affichée
    return render_template('prelevements.html', stations=stations)



@app.route('/departement', methods=['POST'])
def departement_post():
    data = request.get_json()
    nomZone = data.get("nom")
    zone = data.get("zone", "departement")
    
    # Normalisation pour les régions si nécessaire
    if zone == "region":
        nomZone = normaliser(nomZone)

    stationsDF = db.getStations(zone, nomZone)
    
    stations = stationsDF.to_dict(orient='records')  # Liste de dictionnaires
    
    result = {"stations": stations}
    
    return jsonify(result)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        message = request.form.get('message')

        date_envoi = datetime.now().strftime("%d/%m/%Y à %Hh%M")

        with open("private_messages.txt", "a", encoding="utf-8") as f:
            f.write(f"[{date_envoi}] {nom} <{email}> : {message}\n---\n")

        flash("Votre message a bien été enregistré ! Merci 💌", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/vitrygtr/messages')
def voir_messages():
    messages = []
    try:
        with open("private_messages.txt", "r", encoding="utf-8") as f:
            bloc = {}
            for line in f:
                if line.startswith('['):
                    bloc = {}
                    date_part, reste = line.split(']', 1)
                    bloc['date'] = date_part.strip('[]')
                    parts = reste.split(' : ')
                    if len(parts) == 2:
                        bloc['nom'], bloc['contenu'] = parts
                        bloc['nom'] = bloc['nom'].strip()
                        bloc['contenu'] = bloc['contenu'].strip()
                        bloc['email'] = "anonyme"
                        messages.append(bloc)
                elif '<' in line and '>' in line:
                    # ancien format : nom <email> : message
                    try:
                        nom_part, reste = line.split('<')
                        email_part, msg_part = reste.split('>')
                        bloc = {
                            "nom": nom_part.strip(),
                            "email": email_part.strip(),
                            "contenu": msg_part.split(':', 1)[-1].strip(),
                            "date": "Ancien message"
                        }
                        messages.append(bloc)
                    except:
                        continue
    except FileNotFoundError:
        messages = []

    return render_template('messages.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True)
