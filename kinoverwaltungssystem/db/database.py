from pathlib import Path

from sqlalchemy import delete, inspect, text
from sqlmodel import create_engine, Session, select, SQLModel

from kinoverwaltungssystem.model.auth import hash_password
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.model.user_model import User


class Database:
    def __init__(self):
        self.engine = None
        self._session: Session | None = None

    def init_db(self) -> None:
        """Initialisiert die Datenbank, führt Migrationen durch und legt den Admin-User an."""
        base_dir = Path(__file__).resolve().parent.parent
        db_path = base_dir / "movies.db"
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        SQLModel.metadata.create_all(self.engine)
        self._migrate_is_admin_column()
        self._session = Session(self.engine)
        print(f"SQLite verbunden ✅ ({db_path})")
        self.create_admin_if_not_exists(
            email="admin@kinoverwaltung.ch",
            password="admin123",
            username="Admin",
        )

    def _migrate_is_admin_column(self) -> None:
        """Fügt die Spalte 'isAdmin' hinzu, falls sie in der bestehenden DB fehlt."""
        inspector = inspect(self.engine)
        columns = [col["name"] for col in inspector.get_columns("users")]
        if "isAdmin" not in columns:
            with self.engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN isAdmin BOOLEAN NOT NULL DEFAULT 0"))
            print("🛠  Migration: Spalte 'isAdmin' in users hinzugefügt")

    # ---------- MOVIES ----------

    def save_movie(self, movie: Movie) -> int:
        """Speichert einen neuen Film und gibt die vergebene ID zurück."""
        self._session.add(movie)
        self._session.commit()
        self._session.refresh(movie)
        print(f"🎬 Film gespeichert: {movie.titel} (ID: {movie.id})")
        return movie.id

    def update_movie(self, movie: Movie) -> None:
        """Persistiert Änderungen an einem bestehenden Film-Objekt."""
        self._session.add(movie)
        self._session.commit()

    def load_movies(self) -> list[Movie]:
        """Gibt alle Filme aus der Datenbank zurück."""
        return self._session.exec(select(Movie)).all()

    def delete_movie_by_id(self, movie_id: int) -> None:
        """Löscht einen Film anhand seiner ID."""
        self._session.execute(delete(Movie).where(Movie.id == movie_id))
        self._session.commit()
        print(f"🗑️ Film gelöscht (ID: {movie_id})")

    # ---------- USERS ----------

    def save_user(self, user: User) -> int:
        """Speichert einen neuen User und gibt die vergebene ID zurück."""
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        print(f"👤 User gespeichert: {user.username} (ID: {user.id})")
        return user.id

    def load_users(self) -> list[User]:
        """Gibt alle User aus der Datenbank zurück."""
        return self._session.exec(select(User)).all()

    def get_user_by_email(self, email: str) -> User | None:
        """Sucht einen User anhand der E-Mail-Adresse."""
        return self._session.exec(select(User).where(User.email == email)).first()

    def delete_user_by_email(self, email: str) -> None:
        """Löscht einen User anhand der E-Mail-Adresse."""
        result = self._session.execute(delete(User).where(User.email == email))
        self._session.commit()
        print(f"🗑️ {result.rowcount} User gelöscht: {email}")

    def create_admin_if_not_exists(self, email: str, password: str, username: str = "Admin") -> None:
        """Legt einen Admin-User an, falls noch keiner mit dieser E-Mail existiert."""
        existing = self.get_user_by_email(email)
        if existing is None:
            admin = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                display_name=username,
                is_admin=True,
            )
            self.save_user(admin)
            print(f"👑 Admin-User erstellt: {email}")
        elif not existing.is_admin:
            existing.is_admin = True
            self._session.commit()
            print(f"👑 Bestehenden User zum Admin gemacht: {email}")

    # ---------- Cleanup ----------

    def close(self) -> None:
        """Schliesst Session und Engine."""
        if self._session:
            self._session.close()
            self._session = None
        if self.engine:
            self.engine.dispose()
            self.engine = None
