"""
Unit-Tests für die Preisberechnungslogik (TicketPerson.calculate_price).

Getestete Regeln:
  - Grundpreis CHF 15.00
  - Kind  (≤12 J.)  : 50 % Rabatt
  - Senior (≥65 J.) : 30 % Rabatt
  - Student          : 20 % Rabatt auf Basispreis
  - Wochenende       : +CHF 2.00 Zuschlag
  - Spätvorstellung  : 10 % Rabatt (Uhrzeit ≥ 22)
"""

from kinoverwaltungssystem.ui.ticket_ui import (
    TicketPerson,
    TICKET_GRUNDGEBUEHR,
    RABATT_KIND,
    RABATT_STUDENT,
    RABATT_SENIOR,
    WOCHENEND_ZUSCHLAG,
    SPAETVORSTELLUNG_RABATT,
)


# ---------- Hilfsfunktion ----------

def price(age: int, is_student: bool = False, is_late: bool = False, is_weekend: bool = False) -> float:
    """Berechnet den Preis für eine Person mit den angegebenen Parametern."""
    p = TicketPerson("Test", age, is_student)
    result, _ = p.calculate_price(is_late, is_weekend)
    return round(result, 2)


# ---------- TC_001: Grundpreis Erwachsener ----------

def test_subtotal_adult_no_discounts():
    """TC_001 – Erwachsener (30 J.), kein Rabatt, kein Zuschlag → Grundpreis CHF 15.00."""
    assert price(30) == TICKET_GRUNDGEBUEHR


# ---------- TC_002: Kinderrabatt ----------

def test_subtotal_child_discount():
    """TC_002 – Kind (10 J.) erhält 50 % Rabatt → CHF 7.50."""
    expected = round(TICKET_GRUNDGEBUEHR * RABATT_KIND, 2)
    assert price(10) == expected


# ---------- TC_003: Seniorenrabatt ----------

def test_subtotal_senior_discount():
    """TC_003 – Senior (70 J.) erhält 30 % Rabatt → CHF 10.50."""
    expected = round(TICKET_GRUNDGEBUEHR * RABATT_SENIOR, 2)
    assert price(70) == expected


# ---------- TC_004: Studentenrabatt ----------

def test_subtotal_student_discount():
    """TC_004 – Student (22 J.) erhält 20 % Rabatt → CHF 12.00."""
    expected = round(TICKET_GRUNDGEBUEHR * RABATT_STUDENT, 2)
    assert price(22, is_student=True) == expected


# ---------- TC_005: Wochenendzuschlag ----------

def test_weekend_surcharge_applied():
    """TC_005 – Wochenende: CHF 2.00 Zuschlag wird addiert → CHF 17.00."""
    expected = round(TICKET_GRUNDGEBUEHR + WOCHENEND_ZUSCHLAG, 2)
    assert price(30, is_weekend=True) == expected


# ---------- TC_006b: Spätvorstellungsrabatt ----------

def test_late_show_discount_applied():
    """TC_006b – Spätvorstellung (≥22 Uhr): 10 % Rabatt auf den Grundpreis → CHF 13.50."""
    expected = round(TICKET_GRUNDGEBUEHR * SPAETVORSTELLUNG_RABATT, 2)
    assert price(30, is_late=True) == expected

    # Sicherstellen dass der Rabatt in der Beschreibungsliste auftaucht
    p = TicketPerson("Test", 30, False)
    _, discounts = p.calculate_price(is_late=True, is_weekend=False)
    assert any("Spaetvorstellung" in d or "spät" in d.lower() for d in discounts)


# ---------- TC_006: Kein Rabatt unter dem Schwellenwert ----------

def test_no_discount_below_threshold():
    """TC_006 – Erwachsener (13–64 J.), kein Student, kein Wochenende, keine Spätvorstellung → kein Rabatt."""
    assert price(25) == TICKET_GRUNDGEBUEHR
    # Sicherstellen, dass kein ungewollter Rabatt greift
    p = TicketPerson("Test", 25, False)
    _, discounts = p.calculate_price(False, False)
    assert discounts == []
