from Programmierprojekt_Kinoverwaltungssystem_v2.kinoverwaltungssystem.db.database import Database
from Programmierprojekt_Kinoverwaltungssystem_v2.kinoverwaltungssystem.view.home_ui import Home_ui


class HomeController:
    def __init__(self):
        self.db = Database()
        self.home_ui = Home_ui
        self.movies_data = self.db.load_movies()
