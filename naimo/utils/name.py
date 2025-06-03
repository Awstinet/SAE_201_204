import unicodedata

def normaliser(nom: str):
    """Permet de normaliser le nom mis en argument pour que ça puisse récupérer le nom dans le BDD. Sinon ça ne fonctionne pas"""
    nfkd = unicodedata.normalize('NFKD', nom)
    sans_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return sans_accents.upper().replace("’", "'").replace("'", "-")