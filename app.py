from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.model.user_model import User


def main() -> None:
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

if __name__ == '__main__':
    main()