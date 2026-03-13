from pathlib import Path
import sqlite3

from Programmierprojekt_Kinoverwaltungssystem_v2.kinoverwaltungssystem.model.movie_model import Movie

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'kino.db'

class Database:
    def __init__(self):
        pass

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(DB_PATH)


    def init_db(self) -> None:
       pass

    def save_movies(self, movies_data: list[Movie]):
        pass

    def load_movies(self):
        return [Movie("titel1", "abenteuer", 120, 12, 2022, "eee", "bbb", "rrr", "huuuu"),
                       Movie("titel2", "abenteuer", 120, 12, 2022, "eee", "bbb", "rrr", "huuuu"),
                       Movie("titel3", "abenteuer", 120, 12, 2022, "eee", "bbb", "rrr", "huuuu"),
                       Movie("titel4", "abenteuer", 120, 12, 2022, "eee", "bbb", "rrr", "huuuu"),
                       Movie("titel5", "abenteuer", 120, 12, 2022, "eee", "bbb", "rrr", "huuuu"),]

