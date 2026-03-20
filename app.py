from dotenv import load_dotenv
load_dotenv()

from nicegui import ui
from kinoverwaltungssystem.constants import Genre, Altersfreigabe
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.user_model import User
from kinoverwaltungssystem.view.home_ui import Home_UI
from kinoverwaltungssystem.model.movie_model import Movie

db = Database()

@ui.page('/')
def home_page():
    movies = db.load_movies()
    home = Home_UI(movies)
    home.render()

if __name__ in {"__main__", "__mp_main__"}:
    db.init_db()
    ui.run(title="Kinoverwaltungssystem", reload=True)