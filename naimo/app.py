from flask import Flask, render_template, request
import matplotlib
import data.datas as db
# from utils.graphiques import generate_histogram, generate_boxplot



# Déclaration d'application Flask
app = Flask(__name__)

# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')


# Route pour la page d'accueil
@app.route('/accueil')
def accueil():
    # Affichage du template
    return render_template('accueil.html')

# Route pour la page d'à propos
@app.route('/apropos')
def apropos():
    # Affichage du template
    return render_template('apropos.html')

# Route pour la page d'à propos
@app.route('/contact')
def contact():
    # Affichage du template
    return render_template('contact.html')

# Route pour la page d'à propos
@app.route('/observations')
def observations():
    # Affichage du template
    return render_template('observations.html')

# Route pour la page d'à propos
@app.route('/')
def prelevements():
    # Affichage du template
    return render_template('prelevements.html')



if __name__ == '__main__':
    app.run(debug=True)