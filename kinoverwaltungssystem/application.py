import os

from dotenv import load_dotenv

load_dotenv()

from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.ui.home_ui import HomeUI
from kinoverwaltungssystem.ui.login_ui import LoginUI
from kinoverwaltungssystem.ui.movie_ui import MovieUI
from kinoverwaltungssystem.ui.ticket_ui import TicketUI
from kinoverwaltungssystem.ui.ticket_success_ui import TicketSuccessUI

database = Database()


class Kinoverwaltungssystem:
    def __init__(self):
        database.init_db()

    def run(self) -> None:
        """Startet den NiceGUI-Webserver."""
        ui.run(
            title="Kinoverwaltungssystem",
            storage_secret="kino-geheim-schluessel",
            port=int(os.environ.get("PORT", 8080)),
            reload=False,
        )


@ui.page('/')
def home_page():
    HomeUI(database.load_movies()).render()


@ui.page('/login')
def login_page():
    if nicegui_app.storage.user.get('authenticated'):
        ui.navigate.to('/')
        return
    LoginUI(database).render()


@ui.page('/movies')
def movies_page():
    MovieUI(database).render()


@ui.page('/tickets')
def tickets_page(movie_id: int = None):
    TicketUI(database, movie_id).render()


@ui.page('/tickets/success')
def tickets_success_page(order_id: str = ''):
    TicketSuccessUI(database, order_id).render()
