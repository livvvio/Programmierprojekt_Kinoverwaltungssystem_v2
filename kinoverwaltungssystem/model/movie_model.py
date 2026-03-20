from dataclasses import dataclass
from kinoverwaltungssystem.constants import Genre, Altersfreigabe

@dataclass
class Movie:
    titel: str
    genre: Genre
    dauer: int
    altersfreigabe: Altersfreigabe
    erscheinungsjahr: int
    beschreibung: str
    produktionsfirma: str
    regisseur: str
    bewertung: float
    imageUrl: str


