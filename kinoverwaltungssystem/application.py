import os
from dotenv import load_dotenv

load_dotenv()
from nicegui import ui, app as nicegui_app

from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.ui.home_ui import Home_UI
from kinoverwaltungssystem.ui.login_ui import Login_UI

database = Database()


class Kinoverwaltungssystem:

    def __init__(self):
        # hier müssen DB und die Services initialisiert werden
        database.init_db()

    def run(self):
        ui.run(title="Kinoverwaltungssystem", storage_secret="kino-geheim-schluessel",
               port=int(os.environ.get("PORT", 8080)), reload=True)


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
