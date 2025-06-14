from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_mail import Mail
from datetime import datetime
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
    updateDatabase() #Met à jour la base de données quand le script est chargé.
    return "", 204


@app.route("/")
def accueil():
    lastDate = getLastDate() #Récupère la date de la dernière mise à jour des données (dernière observation faite.)
    nbObservations = get_observations_count() #Récupère le nombre total d'observations qui ont été faites.
    nbStations = db.getNbStations() #Récupère le nombre total de stations
    return render_template("accueil.html", nbStations = nbStations, nbObservations = nbObservations, lastDate = lastDate)


@app.route('/apropos')
def apropos():
    # Affichage du template
    return render_template('apropos.html')


@app.route('/observations', methods=['GET', 'POST'])
def observations():
    if request.method == 'POST': #Quand on ouvre le popup par le bouton

        #Initialisation des variables
        data = ""
        selectedAnnee = None
        selectedDept = None
        selectedPoisson = None

        #Si on ouvre le popup pour la première fois
        if request.is_json:
            req_data = request.get_json() #On récupère les données du formulaire
            data = req_data.get("clicked", "")
            selectedDept = req_data.get("selectionDepartement", "Val-d'Oise") #Le premier graphe est pour le Val-d'Oise
            selectedPoisson = req_data.get("selectionPoisson", "all") #Et tous les poissons
            try:
                selectedAnnee = int(req_data.get("poissonAnneeSelection")) #On regarde quelle année a été sélectionnée
            except (TypeError, ValueError):
                selectedAnnee = None
        else:
            data = request.form.get("clicked", "") #Si le popup est déjà ouvert
            selectedDept = request.form.get("selectionDepartement")
            selectedPoisson = request.form.get("selectionPoisson")
            try:
                selectedAnnee = int(request.form.get("poissonAnneeSelection"))
            except (TypeError, ValueError):
                selectedAnnee = None

        allDepts = db.getAllDepts() #On récupère tous les départements

        if not selectedDept or selectedDept not in allDepts:
            selectedDept = "Val-d'Oise"

        poissonsDispo = sorted(fish for fish in getFishByDept(selectedDept) if fish is not None) #On récupère tous les poissons

        if not selectedPoisson:
            selectedPoisson = "all"

        #Mapping entre l'ID des boutons et le titre qui sera affiché
        mappingTitre = {
            "evoPoissonsZone": "Graphique évolutif des poissons par année dans une zone.",
            "totalPoissonsZone": "Population de poissons par zone",
            "nbPrelevZones": "Nombre de prélèvements par zone"
        }

        titre = mappingTitre.get(data, "")

        annees = [] #Toutes les années qui seront disponibles
        dctPoissons = {} #Tous les poissons qui seront disponibles
        image = "" #Le graphique qui sera affiché


        #Si on ouvre le popUp de l'évolution des poissons par année dans un département
        if data == "evoPoissonsZone":
            annees = [annee for annee in range(1995, int(getLastDate()[:4]) + 1, 6)] #Tranches de tous les 5 ans
            if selectedAnnee is not None: #Si une année sélectionnée
                for i in range(selectedAnnee, selectedAnnee + 6):
                    poissonsAnnee = poissonsParDepartement(selectedDept, i, selectedPoisson) #On récupère les poissons par département

                    if selectedPoisson != "all":
                        poissonsAnnee = {k: v for k, v in poissonsAnnee.items() if k == selectedPoisson}

                    dctPoissons[i] = poissonsAnnee

                    if dctPoissons.get(selectedAnnee) is None:
                        dctPoissons = "NaN"
                        break

                if dctPoissons != "NaN":
                    image = graphePoissonsParRegion(dctPoissons.keys(), dctPoissons.values()) #On génère l'image à partir de nos données

        elif data == "totalPoissonsZone":
            pass
        elif data == "nbPrelevZones":
            pass

        #Template du popup
        return render_template(
            'popupObservation.html',
            titre=titre,
            annees=annees,
            selectedAnnee=selectedAnnee,
            selectedDept=selectedDept,
            selectedPoisson=selectedPoisson,
            image=image,
            dctPoissons=dctPoissons,
            poissonsDispo=poissonsDispo,
            allDepts=allDepts,
            clicked=data
        )

    return render_template("observations.html")





@app.route('/prelevements', methods=['GET'])
def prelevements():
    stations = [] #Par défaut, aucune station n'est affichée
    return render_template('prelevements.html', stations=stations)



@app.route('/departement', methods=['POST'])
def departement_post():
    data = request.get_json() #Récupère la zone sélectionnée (département ou région) et le nom de l'endroit.
    nomZone = data.get("nom")
    zone = data.get("zone", "departement")
    
    # Normalisation pour les régions si nécessaire
    if zone == "region":
        nomZone = normaliser(nomZone)

    stationsDF = db.getStations(zone, nomZone) #Dataframe des stations se situant à l'endroit sélectionné
    
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
