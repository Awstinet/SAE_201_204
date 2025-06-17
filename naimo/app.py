from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_mail import Mail
from datetime import datetime, timedelta
import matplotlib
import data.datas as db
from utils.name import normaliser
from utils.majDonnes import updateDatabase, getLastDate
from utils.graphiques import *
from utils.nbObservations import get_observations_count
from utils.poissonsParZone import getFishByDept

# Déclaration d'application Flask
app = Flask(__name__)

###################################
##       Pour les messages       ##
###################################

app.secret_key = 'aquaexotica-secret-key'

# Configuration Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mail.test@gmail.com'
app.config['MAIL_PASSWORD'] = 'motDePasse'
app.config['MAIL_DEFAULT_SENDER'] = 'mail.test@gmail.com'

mail = Mail(app)

# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')

@app.route("/pageLoaded", methods=["POST"])
def pageLoaded():   
    updateDatabase()
    # Test de connexion API au démarrage
    return "", 204


@app.route("/")
def accueil():
    lastDate = getLastDate()
    nbObservations = get_observations_count()
    nbStations = db.getNbStations()
    return render_template("accueil.html", nbStations=nbStations, nbObservations=nbObservations, lastDate=lastDate)

@app.route('/apropos')
def apropos():
    #Affichage du template
    return render_template('apropos.html')

@app.route('/observations', methods=['GET', 'POST'])
def observations():
    if request.method == 'POST':
        # Récupération des données JSON (qu'elles viennent du 1er clic ou d'une sélection)
        req_data = request.get_json(force=True)

        # Initialisation et récupération des données envoyées
        data = req_data.get("clicked", "")
        selectedDept = req_data.get("selectionDepartement", "Val-d'Oise")
        selectedPoisson = req_data.get("selectionPoisson", "all")

        try:
            selectedAnnee = int(req_data.get("poissonAnneeSelection"))
        except (TypeError, ValueError):
            selectedAnnee = None

        # Récupération de tous les départements
        allDepts = db.getAllDepts()

        if not selectedDept or selectedDept not in allDepts:
            selectedDept = "Val-d'Oise"

        # Récupération des poissons disponibles dans le département
        poissonsDispo = ""

        # Titre dynamique selon le bouton cliqué
        mappingTitre = {
            "evoPoissonsZone": "Graphique évolutif des poissons par année dans une zone.",
            "totalPoissonsZone": "Population de poissons par zone",
            "nbPrelevZones": "Nombre de prélèvements par zone"
        }

        titre = mappingTitre.get(data, "")

        # Initialisation pour le template
        annees = []
        dct = {}
        image = ""

        if data == "evoPoissonsZone":
            # Récupération des poissons disponibles dans le département
            poissonsDispo = sorted(fish for fish in getFishByDept(selectedDept) if fish is not None)

            if not selectedPoisson:
                selectedPoisson = "all"
            annees = [annee for annee in range(1995, int(getLastDate()[:4]) + 1, 6)]

            if selectedAnnee is not None:
                for i in range(selectedAnnee, selectedAnnee + 6):
                    # Appel de la fonction corrigée
                    effectif = poissonsParDepartement(selectedDept, i, selectedPoisson)
                    dct[i] = effectif if effectif is not None else 0

                if all(v == 0 for v in dct.values()):
                    dct = "NaN"
                else:
                    image = graphePoissonsParDepartement(list(dct.keys()), list(dct.values()))

        elif data == "totalPoissonsZone":
            pass  # À compléter
        elif data == "nbPrelevZones":
            annees = [annee for annee in range(1995, int(getLastDate()[:4]) + 1, 6)]

            if selectedAnnee is not None:
                for i in range(selectedAnnee, selectedAnnee + 6):
                    # Appel de la fonction corrigée
                    nbObservations = getObservations(i, selectedDept)
                    dct[i] = nbObservations if nbObservations is not None else 0

                if all(v == 0 for v in dct.values()):
                    dct = "NaN"
                else:
                    image = grapheNbObservations(list(dct.keys()), list(dct.values()))

        return render_template(
            'popupObservation.html',
            titre=titre,
            annees=annees,
            selectedAnnee=selectedAnnee,
            selectedDept=selectedDept,
            selectedPoisson=selectedPoisson,
            image=image,
            dct=dct,
            poissonsDispo=poissonsDispo,
            allDepts=allDepts,
            clicked=data
        )

    # Requête GET (page initiale)
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
    
    if zone == "region":
        nomZone = normaliser(nomZone)

    stationsDF = db.getStations(zone, nomZone)
    stations = stationsDF.to_dict(orient='records')
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
