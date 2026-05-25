"""
Integrationstests – vollständiger Ticketbuchungsfluss.

Testet das Zusammenspiel von TicketPerson, Preisberechnung und PDF-Generierung
so wie es in der echten Anwendung abläuft.
"""

import pytest
from sqlmodel import create_engine, Session, SQLModel

from kinoverwaltungssystem.constants import Genre, Altersfreigabe
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.ui.ticket_ui import (
    TicketPerson,
    TICKET_GRUNDGEBUEHR,
    RABATT_KIND,
    RABATT_STUDENT,
)


# ---------- Fixtures ----------

@pytest.fixture
def db() -> Database:
    """Frische In-Memory-DB für jeden Integrationstest."""
    instance = Database()
    instance.engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(instance.engine)
    instance._session = Session(instance.engine)
    return instance


@pytest.fixture
def sample_movie(db: Database) -> Movie:
    """Speichert einen Beispielfilm und gibt ihn zurück."""
    movie = Movie(
        titel="Interstellar",
        genre=Genre.SCIENCE_FICTION,
        dauer=169,
        erscheinungsjahr=2014,
        altersfreigabe=Altersfreigabe.FSK12,
        bewertung=8.6,
        imageUrl="",
    )
    db.save_movie(movie)
    return movie


# ---------- TC_010: Checkout mit einer Person erstellt korrekten Gesamtbetrag ----------

def test_checkout_single_person_correct_total(sample_movie: Movie):
    """TC_010 – Checkout mit einem Erwachsenen ohne Rabatte ergibt CHF 15.00."""
    persons = [TicketPerson("Anna", 30, False)]
    total = sum(p.calculate_price(False, False)[0] for p in persons)

    assert round(total, 2) == TICKET_GRUNDGEBUEHR


# ---------- TC_011: Checkout mit mehreren Personen wendet Rabatte korrekt an ----------

def test_checkout_multiple_persons_discount_applied(sample_movie: Movie):
    """TC_011 – Checkout mit Kind + Student + Erwachsenem berechnet jeden Preis korrekt."""
    persons = [
        TicketPerson("Kind", 10, False),  # 50 % Rabatt → 7.50
        TicketPerson("Student", 22, True),  # 20 % Rabatt → 12.00
        TicketPerson("Erwachsener", 35, False),  # kein Rabatt → 15.00
    ]
    prices = [round(p.calculate_price(False, False)[0], 2) for p in persons]

    assert prices[0] == round(TICKET_GRUNDGEBUEHR * RABATT_KIND, 2)
    assert prices[1] == round(TICKET_GRUNDGEBUEHR * RABATT_STUDENT, 2)
    assert prices[2] == TICKET_GRUNDGEBUEHR

    total = round(sum(prices), 2)
    assert total == round(
        TICKET_GRUNDGEBUEHR * RABATT_KIND
        + TICKET_GRUNDGEBUEHR * RABATT_STUDENT
        + TICKET_GRUNDGEBUEHR,
        2,
    )


# ---------- TC_012: PDF-Ticket wird generiert und enthält Bytes ----------

def test_checkout_generates_pdf_bytes(sample_movie: Movie):
    """TC_012 – Nach dem Checkout liefert generate_ticket_pdf ein nicht-leeres Bytes-Objekt."""
    pytest.importorskip("reportlab", reason="reportlab nicht installiert")

    from kinoverwaltungssystem.service.ticket_service import generate_ticket_pdf

    persons = [TicketPerson("Laura", 28, False)]
    total = sum(p.calculate_price(False, False)[0] for p in persons)

    pdf_bytes = generate_ticket_pdf(
        movie=sample_movie,
        persons=persons,
        total=total,
        show_hour=20,
        is_weekend=False,
        order_id="TC012",
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # PDF-Magic-Bytes prüfen
    assert pdf_bytes[:4] == b"%PDF"
