import matplotlib as plt
from io import BytesIO
import base64

url = "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations"


def evolutionPoissonsParRegion(zone, nomZone, poisson=None):
    """"""
    url += f"?libelle_{zone}={nomZone}"
    if poisson:
        url += f""