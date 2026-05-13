import os
from dotenv import load_dotenv

load_dotenv()
from nicegui import ui, app as nicegui_app

from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.ui.home_ui import Home_UI
from kinoverwaltungssystem.ui.login_ui import Login_UI
from kinoverwaltungssystem.ui.movie_ui import Movie_UI
from kinoverwaltungssystem.ui.ticket_ui import Ticket_UI

database = Database()


class Kinoverwaltungssystem:

    def __init__(self):
        database.init_db()

    def run(self):
        ui.run(title="Kinoverwaltungssystem", storage_secret="kino-geheim-schluessel",
               port=int(os.environ.get("PORT", 8080)), reload=False)


@ui.page('/')
def home_page():
    movies = database.load_movies()
    Home_UI(movies).render()


@ui.page('/login')
def login_page():
    if nicegui_app.storage.user.get('authenticated'):
        ui.navigate.to('/')
        return
    Login_UI(database).render()


@ui.page('/movies')
def movies_page():
    Movie_UI(database).render()


@ui.page('/tickets')
def tickets_page(movie_id: int = None):
    Ticket_UI(database, movie_id).render()
