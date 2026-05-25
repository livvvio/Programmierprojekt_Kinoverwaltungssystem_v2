"""
DB-Tests für die Database-Facade.

Jeder Test arbeitet mit einer eigenen In-Memory-SQLite-Datenbank,
damit keine persistente movies.db verändert wird.
"""

import pytest
from sqlmodel import create_engine, Session, SQLModel

from kinoverwaltungssystem.constants import Genre, Altersfreigabe
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.movie_model import Movie


# ---------- Fixture: isolierte In-Memory-DB ----------

@pytest.fixture
def db() -> Database:
    """Erstellt eine frische In-Memory-Datenbankinstanz für jeden Test."""
    instance = Database()
    instance.engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(instance.engine)
    instance._session = Session(instance.engine)
    return instance


def _sample_movie(**kwargs) -> Movie:
    """Gibt einen minimalen Film zurück, optional mit überschriebenen Feldern."""
    defaults = dict(
        titel="Testfilm",
        genre=Genre.ACTION,
        dauer=120,
        erscheinungsjahr=2024,
        altersfreigabe=Altersfreigabe.FSK12,
        bewertung=7.5,
        imageUrl="",
    )
    defaults.update(kwargs)
    return Movie(**defaults)


# ---------- TC_007: Filmkatalog gibt geseelte Daten zurück ----------

def test_menu_query_returns_seeded_movies(db: Database):
    """TC_007 – Nach dem Speichern von 2 Filmen gibt load_movies() genau diese zurück."""
    db.save_movie(_sample_movie(titel="Film A"))
    db.save_movie(_sample_movie(titel="Film B"))

    movies = db.load_movies()

    assert len(movies) == 2
    titles = {m.titel for m in movies}
    assert titles == {"Film A", "Film B"}


# ---------- TC_008: Film speichern persistiert korrekt ----------

def test_saving_movie_persists_all_fields(db: Database):
    """TC_008 – Ein gespeicherter Film enthält alle übergebenen Feldinhalte."""
    movie = _sample_movie(
        titel="Matrix",
        genre=Genre.SCIENCE_FICTION,
        dauer=136,
        erscheinungsjahr=1999,
        altersfreigabe=Altersfreigabe.FSK16,
        bewertung=8.7,
        regisseur="Wachowski Sisters",
    )
    new_id = db.save_movie(movie)

    loaded = db.load_movies()
    assert len(loaded) == 1
    m = loaded[0]
    assert m.id == new_id
    assert m.titel == "Matrix"
    assert m.dauer == 136
    assert m.erscheinungsjahr == 1999
    assert m.bewertung == pytest.approx(8.7, abs=0.01)
    assert m.regisseur == "Wachowski Sisters"


# ---------- TC_009: Leere DB – keine Filme ----------

def test_empty_db_returns_no_movies(db: Database):
    """TC_009 – Eine leere Datenbank liefert eine leere Filmliste zurück."""
    movies = db.load_movies()
    assert movies == []


# ---------- TC_009b: Leere DB – keine User ----------

def test_empty_db_returns_no_users(db: Database):
    """TC_009b – Eine leere Datenbank liefert eine leere Benutzerliste zurück."""
    users = db.load_users()
    assert users == []
