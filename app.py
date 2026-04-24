import os
from dotenv import load_dotenv
load_dotenv()
from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.view.home_ui import Home_UI
from kinoverwaltungssystem.view.login_ui import Login_UI


db = Database()


@ui.page('/')
def home_page():
    movies = db.load_movies()
    Home_UI(movies).render()


@ui.page('/login')
def login_page():
    if nicegui_app.storage.user.get('authenticated'):
        ui.navigate.to('/')
        return
    Login_UI(db).render()


if __name__ in {"__main__", "__mp_main__"}:
    db.init_db()
    db.create_admin_if_not_exists(
        email="admin@kinoverwaltung.ch",
        password="admin123",
        username="Admin",
    )
    ui.run(title="Kinoverwaltungssystem", storage_secret="kino-geheim-schluessel",
           port=int(os.environ.get("PORT", 8080)), reload=True)