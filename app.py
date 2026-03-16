from nicegui import ui

from Programmierprojekt_Kinoverwaltungssystem_v2.kinoverwaltungssystem.constants import Genre, Altersfreigabe
from Programmierprojekt_Kinoverwaltungssystem_v2.kinoverwaltungssystem.view.home_ui import Home_UI
from kinoverwaltungssystem.model.movie_model import Movie


@ui.page('/')
def home_page():
    # Testdaten
    movies = [Movie("Inception", Genre.SCIENCE_FICTION, 148, Altersfreigabe.FSK12, 2010, "Ein Dieb stiehlt Geheimnisse aus Träumen.", "Warner Bros.","Christopher Nolan", 9.3,
                    "https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg"),
              Movie("The Matrix", Genre.SCIENCE_FICTION, 136, Altersfreigabe.FSK16, 1999, "Ein Hacker entdeckt die wahre Natur der Realität.","Warner Bros.", "The Wachowskis", 8.7,
                    "https://cdn.zeise.de/image/044/001.250w.jpg"),
              Movie("Interstellar", Genre.SCIENCE_FICTION, 169, Altersfreigabe.FSK12, 2014,"Astronauten reisen durch ein Wurmloch, um die Menschheit zu retten.", "Paramount Pictures","Christopher Nolan", 8.6,
                    "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg")]
    home = Home_UI(movies)
    home.render()

def init():
    """""
    # 1. Datenbank verbinden
    db = Database()
    db.init_db()

    # 2. Testfilm speichern
    film_id = db.save_movie(Movie(
        titel="Inception",
        genre="Sci-Fi",
        dauer=148,
        altersfreigabe=12,
        erscheinungsjahr=2010,
        beschreibung="Ein Dieb stiehlt Geheimnisse aus Träumen.",
        produktionsfirma="Warner Bros.",
        regisseur="Christopher Nolan",
        bewertung=9.3,
        imageUrl="https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg"
    ))

    # 3. Testuser speichern
    user_id = db.save_user(User(
        username="simonmoor",
        email="simon@example.com",
        password_hash="hashed_passwort_123",
        display_name="Simon Moor"
    ))

    # 4. Filme laden & ausgeben
    print("\n🎬 Filme:")
    for film in db.load_movies():
        print(f"  {film.titel} ({film.erscheinungsjahr}) ⭐ {film.bewertung}")
        print(f"  🖼  {film.imageUrl}")

    # 5. Users laden & ausgeben
    print("\n👤 Users:")
    for user in db.load_users():
        print(f"  {user.username} - {user.email}")

    db.delete_movie_by_title("Inception")
    db.delete_user_by_email("simon@example.com")
    """
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Kinoverwaltungssystem", reload=True)