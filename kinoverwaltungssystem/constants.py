from datetime import datetime
from enum import Enum

CURRENT_YEAR = datetime.now().year

class MovieAttribute(Enum):
    TITEL = "Titel"
    GENRE = "Genre"
    DAUER = "Dauer"
    ALTERSFREIGABE = "Altersfreigabe"
    ERSCHEINUNGSJAHR = "Erscheinungsjahr"
    BESCHREIBUNG = "Beschreibung"
    PRODUKTIONSFIRMA = "Produktionsfirma"
    REGISSEUR = "Regisseur"
    BEWERTUNG = "Bewertung"
    IMAGE_URL = "Image_URL"

class Genre(Enum):
    ABENTEUER = "Abenteuer"
    ACTION = "Action"
    THRILLER = "Thriller"
    DOKU = "Doku"
    DRAMA = "Drama"
    EROTIK = "Erotik"
    FANTASY = "Fantasy"
    HORROR = "Horror"
    KOMÖDIE = "Komödie"
    KRIMI = "Krimi"
    ROMANTIK = "Romantik"
    SCIENCE_FICTION = "Sci-Fi"
    WESTERN = "Western"
    SONSTIGE = "Sonstige"


class Altersfreigabe(Enum):
    FSK0 = 0
    FSK6 = 6
    FSK12 = 12
    FSK16 = 16
    FSK18 = 18