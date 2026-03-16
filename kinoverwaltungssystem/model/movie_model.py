from dataclasses import dataclass

from Programmierprojekt_Kinoverwaltungssystem_v2.kinoverwaltungssystem.constants import Altersfreigabe, Genre


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


