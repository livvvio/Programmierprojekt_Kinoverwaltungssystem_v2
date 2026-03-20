import os
import json
from pathlib import Path
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from kinoverwaltungssystem.constants import Genre, Altersfreigabe
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.model.user_model import User


class Database:
    def __init__(self):
        self.db = None

    def init_db(self) -> None:
        key_json = os.environ.get("FIRESTORE_KEY")

        if key_json:
            key_dict = json.loads(key_json)
            cred = credentials.Certificate(key_dict)
            print("🔑 Firebase Key aus Umgebungsvariable geladen")
        else:
            BASE_DIR = Path(__file__).resolve().parent.parent.parent
            KEY_PATH = BASE_DIR / "serviceAccountKey.json"
            cred = credentials.Certificate(str(KEY_PATH))
            print(f"🔑 Firebase Key aus Datei geladen: {KEY_PATH}")

        firebase_admin.initialize_app(cred)
        self.db = firestore.client(database_id="kinoverwaltung")
        print("Firebase verbunden ✅")

    def save_movie(self, movie: Movie) -> str:
        _, doc_ref = self.db.collection("movies").add({
            "title": movie.titel,
            "genre": movie.genre.value,
            "duration": movie.dauer,
            "ageRating": movie.altersfreigabe.value,
            "releaseYear": movie.erscheinungsjahr,
            "director": movie.regisseur,
            "productionCompany": movie.produktionsfirma,
            "description": movie.beschreibung,
            "rating": movie.bewertung,
            "imageUrl": movie.imageUrl,
            "createdAt": datetime.utcnow()
        })
        print(f"🎬 Film gespeichert: {movie.titel} (ID: {doc_ref.id})")
        return doc_ref.id

    def load_movies(self) -> list[Movie]:
        docs = self.db.collection("movies").stream()
        movies = []
        for doc in docs:
            m = doc.to_dict()
            movies.append(Movie(
                titel=m["title"],
                genre=Genre(m["genre"]),
                dauer=m["duration"],
                altersfreigabe=Altersfreigabe(int(m["ageRating"])),
                erscheinungsjahr=m["releaseYear"],
                beschreibung=m.get("description", ""),
                produktionsfirma=m["productionCompany"],
                regisseur=m["director"],
                bewertung=m.get("rating", 0.0),
                imageUrl=m.get("imageUrl", "")
            ))
        return movies

    def delete_movie_by_title(self, title: str):
        docs = self.db.collection("movies").where(
            filter=FieldFilter("title", "==", title)
        ).stream()
        deleted = 0
        for doc in docs:
            doc.reference.delete()
            deleted += 1
        print(f"🗑️ {deleted} Film(e) gelöscht: {title}")

    def delete_movie_by_id(self, doc_id: str):
        self.db.collection("movies").document(doc_id).delete()
        print(f"🗑️ Film gelöscht (ID: {doc_id})")

    def save_user(self, user: User) -> str:
        _, doc_ref = self.db.collection("users").add({
            "username": user.username,
            "email": user.email,
            "passwordHash": user.password_hash,
            "displayName": user.display_name,
            "createdAt": datetime.utcnow()
        })
        print(f"👤 User gespeichert: {user.username} (ID: {doc_ref.id})")
        return doc_ref.id

    def load_users(self) -> list[User]:
        docs = self.db.collection("users").stream()
        users = []
        for doc in docs:
            u = doc.to_dict()
            users.append(User(
                username=u["username"],
                email=u["email"],
                password_hash=u["passwordHash"],
                display_name=u.get("displayName", "")
            ))
        return users

    def get_user_by_email(self, email: str) -> User | None:
        docs = self.db.collection("users").where(
            filter=FieldFilter("email", "==", email)
        ).stream()
        for doc in docs:
            u = doc.to_dict()
            return User(
                username=u["username"],
                email=u["email"],
                password_hash=u["passwordHash"],
                display_name=u.get("displayName", "")
            )
        return None

    def delete_user_by_email(self, email: str):
        docs = self.db.collection("users").where(
            filter=FieldFilter("email", "==", email)
        ).stream()
        deleted = 0
        for doc in docs:
            doc.reference.delete()
            deleted += 1
        print(f"🗑️ {deleted} User gelöscht: {email}")