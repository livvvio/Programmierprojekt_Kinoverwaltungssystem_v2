from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Integer, Float, Text, TypeDecorator
from kinoverwaltungssystem.constants import Genre, Altersfreigabe


class GenreType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, Genre):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return Genre(value)
        return value


class AltersfreigabeType(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, Altersfreigabe):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return Altersfreigabe(int(value))
        return value


class Movie(SQLModel, table=True):
    __tablename__ = "movies"

    id: Optional[int] = Field(default=None, primary_key=True)
    titel: str = Field(sa_column=Column("title", String, nullable=False))
    genre: Genre = Field(sa_column=Column("genre", GenreType, nullable=False))
    dauer: int = Field(sa_column=Column("duration", Integer, nullable=False))
    altersfreigabe: Altersfreigabe = Field(sa_column=Column("ageRating", AltersfreigabeType, nullable=False))
    erscheinungsjahr: int = Field(sa_column=Column("releaseYear", Integer, nullable=False))
    regisseur: Optional[str] = Field(default=None, sa_column=Column("director", String, nullable=True))
    produktionsfirma: Optional[str] = Field(default=None, sa_column=Column("productionCompany", String, nullable=True))
    beschreibung: Optional[str] = Field(default=None, sa_column=Column("description", Text, nullable=True))
    bewertung: float = Field(default=0.0, sa_column=Column("rating", Float, default=0.0))
    imageUrl: str = Field(default="", sa_column=Column("imageUrl", String, default=""))
    createdAt: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        sa_column=Column("createdAt", String, nullable=False,
                         default=lambda ctx: datetime.utcnow().isoformat())
    )