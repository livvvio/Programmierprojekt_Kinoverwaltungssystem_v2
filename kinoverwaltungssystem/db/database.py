import sqlite3
from pathlib import Path
from datetime import datetime
from kinoverwaltungssystem.constants import Genre, Altersfreigabe
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.model.user_model import User


class Database:
    def __init__(self):
        self.conn: sqlite3.Connection | None = None

    def init_db(self) -> None:
        BASE_DIR = Path(__file__).resolve().parent.parent
        DB_PATH = BASE_DIR / "movies.db"

        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row  # damit wir Spalten per Name ansprechen können
        self._create_tables()
        print(f"SQLite verbunden ✅ ({DB_PATH})")

    def _create_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                duration INTEGER NOT NULL,
                ageRating INTEGER NOT NULL,
                releaseYear INTEGER NOT NULL,
                director TEXT,
                productionCompany TEXT,
                description TEXT,
                rating REAL DEFAULT 0.0,
                imageUrl TEXT,
                createdAt TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                passwordHash TEXT NOT NULL,
                displayName TEXT,
                createdAt TEXT NOT NULL
            )
        """)
        self.conn.commit()

    # ---------- MOVIES ----------

    def save_movie(self, movie: Movie) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO movies (
                title, genre, duration, ageRating, releaseYear,
                director, productionCompany, description, rating, imageUrl, createdAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            movie.titel,
            movie.genre.value,
            movie.dauer,
            movie.altersfreigabe.value,
            movie.erscheinungsjahr,
            movie.regisseur,
            movie.produktionsfirma,
            movie.beschreibung,
            movie.bewertung,
            movie.imageUrl,
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()
        movie_id = cur.lastrowid
        print(f"🎬 Film gespeichert: {movie.titel} (ID: {movie_id})")
        return movie_id

    def load_movies(self) -> list[Movie]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM movies")
        rows = cur.fetchall()
        movies = []
        for m in rows:
            movies.append(Movie(
                titel=m["title"],
                genre=Genre(m["genre"]),
                dauer=m["duration"],
                altersfreigabe=Altersfreigabe(int(m["ageRating"])),
                erscheinungsjahr=m["releaseYear"],
                beschreibung=m["description"] or "",
                produktionsfirma=m["productionCompany"],
                regisseur=m["director"],
                bewertung=m["rating"] or 0.0,
                imageUrl=m["imageUrl"] or ""
            ))
        return movies

    def delete_movie_by_title(self, title: str) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM movies WHERE title = ?", (title,))
        self.conn.commit()
        print(f"🗑️ {cur.rowcount} Film(e) gelöscht: {title}")

    def delete_movie_by_id(self, movie_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        self.conn.commit()
        print(f"🗑️ Film gelöscht (ID: {movie_id})")

    # ---------- USERS ----------

    def save_user(self, user: User) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO users (username, email, passwordHash, displayName, createdAt)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user.username,
            user.email,
            user.password_hash,
            user.display_name,
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()
        user_id = cur.lastrowid
        print(f"👤 User gespeichert: {user.username} (ID: {user_id})")
        return user_id

    def load_users(self) -> list[User]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        users = []
        for u in rows:
            users.append(User(
                username=u["username"],
                email=u["email"],
                password_hash=u["passwordHash"],
                display_name=u["displayName"] or ""
            ))
        return users

    def get_user_by_email(self, email: str) -> User | None:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        u = cur.fetchone()
        if u is None:
            return None
        return User(
            username=u["username"],
            email=u["email"],
            password_hash=u["passwordHash"],
            display_name=u["displayName"] or ""
        )

    def delete_user_by_email(self, email: str) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM users WHERE email = ?", (email,))
        self.conn.commit()
        print(f"🗑️ {cur.rowcount} User gelöscht: {email}")

    # ---------- Cleanup ----------

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None