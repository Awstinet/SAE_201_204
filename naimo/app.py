from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import matplotlib
import data.datas as db
from utils.name import normaliser
from utils.majDonnes import updateDatabase
from utils.majDonnes import getLastDate
from flask_mail import Mail, Message
from datetime import datetime
from data.datas import getStations, getNbStations

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


@app.route("/")
def accueil():
    lastDate = getLastDate()
    # nbObservations = 
    nbStations = db.getNbStations()
    return render_template("accueil.html", nbStations = nbStations, lastDate = lastDate)


@app.route('/apropos')
def apropos():
    # Affichage du template
    return render_template('apropos.html')


@app.route('/observations')
def observations():
    # Affichage du template
    return render_template('observations.html')

@app.route('/prelevements', methods=['GET'])
def prelevements():
    # Récupère les paramètres GET
    zone = request.args.get('zone', default='departement')
    recherche = request.args.get('recherche', default='')

    stations = []

    if recherche:
        stations_df = getStations(zone, recherche)
        stations = stations_df.to_dict(orient='records')
    else:
        stations = []  # Vide si aucune recherche (affiche message dans le HTML)

    nb_total = getNbStations()

    return render_template(
        'prelevements.html',
        stations=stations,
        nbStations=nb_total
    )

@app.route('/departement', methods=['POST'])
def departement_post():
    data = request.get_json()
    nomZone = data.get("nom")
    zone = data.get("zone", "departement")
    
    # Normalisation pour les régions si nécessaire
    if zone == "region":
        nomZone = normaliser(nomZone)

    stationsDF = db.getStations(zone, nomZone)
    
    if not stationsDF.empty:
        print(stationsDF.head())
    
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
