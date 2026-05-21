"""
ticket_service.py  –  PDF-Ticket Generator
Ablegen unter: kinoverwaltungssystem/service/ticket_service.py
Voraussetzung: pip install reportlab
"""
from __future__ import annotations
import io
from datetime import datetime


def generate_ticket_pdf(
    movie,
    persons: list,
    total: float,
    show_hour: int,
    is_weekend: bool,
    order_id: str,
) -> bytes:
    """
    Generiert ein PDF-Ticket und gibt die Bytes zurueck.
    Wird per ui.download() an den Browser gesendet.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.pdfgen.canvas import Canvas
    except ImportError:
        raise RuntimeError(
            "reportlab ist nicht installiert. Bitte 'pip install reportlab' ausfuehren."
        )

    W, H = A4  # 595.28 x 841.89 pt
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=A4)

    RED       = colors.HexColor('#e50914')
    DARK_BG   = colors.HexColor('#0d0d0d')
    CARD_BG   = colors.HexColor('#1e1e1e')
    CARD2_BG  = colors.HexColor('#2a2a2a')
    WHITE     = colors.white
    GRAY_LT   = colors.HexColor('#aaaaaa')
    GRAY_MID  = colors.HexColor('#666666')
    GREEN     = colors.HexColor('#4ade80')
    YELLOW    = colors.HexColor('#fbbf24')

    # ── Hintergrund ──────────────────────────────────────────────────────────
    c.setFillColor(DARK_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Roter Header-Banner ───────────────────────────────────────────────────
    c.setFillColor(RED)
    c.rect(0, H - 70, W, 70, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 22)
    c.drawString(20*mm, H - 40, 'KINOVERWALTUNGSSYSTEM')

    c.setFont('Helvetica', 9)
    c.drawRightString(W - 20*mm, H - 28, 'Offizielles Kinoticket')
    c.drawRightString(W - 20*mm, H - 40, f'Bestellung: {order_id}')
    c.drawRightString(W - 20*mm, H - 52, datetime.now().strftime('%d.%m.%Y  %H:%M Uhr'))

    # ── Beginn Content-Bereich ────────────────────────────────────────────────
    y = H - 85

    # ── Film-Karte ────────────────────────────────────────────────────────────
    film_card_h = 90
    c.setFillColor(CARD_BG)
    c.roundRect(15*mm, y - film_card_h, W - 30*mm, film_card_h, 6, fill=1, stroke=0)

    # Roter linker Akzentstreifen
    c.setFillColor(RED)
    c.roundRect(15*mm, y - film_card_h, 4, film_card_h, 3, fill=1, stroke=0)

    # Filmtitel
    title = movie.titel if len(movie.titel) <= 50 else movie.titel[:47] + '...'
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(25*mm, y - 20, title)

    # Genre + Jahr + Dauer in einer Zeile
    c.setFillColor(GREEN)
    c.setFont('Helvetica-Bold', 9)
    meta_line = (
        f'{movie.genre.value}   |   '
        f'{movie.erscheinungsjahr}   |   '
        f'{movie.dauer} Min   |   '
        f'FSK {movie.altersfreigabe.value}'
    )
    c.drawString(25*mm, y - 34, meta_line)

    # Bewertung
    if movie.bewertung and movie.bewertung > 0:
        c.setFillColor(YELLOW)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(25*mm, y - 46, f'Bewertung: {movie.bewertung:.1f} / 10')

    # Regisseur
    if movie.regisseur:
        c.setFillColor(GRAY_MID)
        c.setFont('Helvetica', 8)
        c.drawString(25*mm, y - 57, f'Regie: {movie.regisseur}')

    # Beschreibung (max 1 Zeile)
    if movie.beschreibung:
        desc = movie.beschreibung[:110] + ('...' if len(movie.beschreibung) > 110 else '')
        c.setFillColor(GRAY_MID)
        c.setFont('Helvetica', 8)
        c.drawString(25*mm, y - 70, desc)

    y -= film_card_h + 10

    # ── Vorstellungs-Karte ────────────────────────────────────────────────────
    vk_h = 58
    c.setFillColor(CARD_BG)
    c.roundRect(15*mm, y - vk_h, W - 30*mm, vk_h, 6, fill=1, stroke=0)

    c.setFillColor(RED)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(20*mm, y - 12, 'VORSTELLUNGSDETAILS')

    col1_x = 20*mm
    col2_x = W / 2

    details = [
        ('Datum',    datetime.now().strftime('%d.%m.%Y')),
        ('Uhrzeit',  f'{show_hour:02d}:00 Uhr' + ('  [Spaetvorstellung]' if show_hour >= 22 else '')),
        ('Tag',      'Wochenende  (+2.00 CHF)' if is_weekend else 'Wochentag'),
    ]
    dy = y - 26
    for lbl, val in details:
        c.setFillColor(GRAY_MID)
        c.setFont('Helvetica', 8)
        c.drawString(col1_x, dy, lbl + ':')
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(col1_x + 22*mm, dy, val)
        dy -= 13

    y -= vk_h + 10

    # ── Tickets-Abschnitt ─────────────────────────────────────────────────────
    c.setFillColor(RED)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(20*mm, y, f'TICKETS  ({len(persons)} PERSON(EN))')
    y -= 12

    is_late = show_hour >= 22

    for i, person in enumerate(persons):
        price, discounts = person.calculate_price(is_late, is_weekend)

        # Kartenhoehe berechnen
        card_h = 28 + max(len(discounts), 1) * 12

        c.setFillColor(CARD_BG)
        c.roundRect(15*mm, y - card_h, W - 30*mm, card_h, 5, fill=1, stroke=0)

        # Nummern-Badge
        c.setFillColor(RED)
        c.roundRect(17*mm, y - 14, 10, 14, 3, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(22*mm, y - 10, f'{i+1:02d}')

        # Altersgruppe als Text (kein Emoji)
        if person.age <= 12:
            age_group = 'Kind'
        elif person.age >= 65:
            age_group = 'Senior'
        else:
            age_group = 'Erwachsener'
        student_txt = '  [Student]' if person.is_student else ''

        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(30*mm, y - 10, f'{person.name}')

        c.setFillColor(GRAY_LT)
        c.setFont('Helvetica', 8)
        c.drawString(30*mm, y - 21, f'{person.age} Jahre  |  {age_group}{student_txt}')

        # Preis rechts
        c.setFillColor(RED)
        c.setFont('Helvetica-Bold', 12)
        c.drawRightString(W - 17*mm, y - 10, f'CHF {price:.2f}')

        # Rabatt-Zeilen
        disc_y = y - 30
        if discounts:
            for d in discounts:
                c.setFillColor(GRAY_MID)
                c.setFont('Helvetica', 7)
                c.drawString(30*mm, disc_y, f'  > {d}')
                disc_y -= 12
        else:
            c.setFillColor(GRAY_MID)
            c.setFont('Helvetica', 7)
            c.drawString(30*mm, disc_y, f'  > Grundpreis: CHF {15.00:.2f}')

        y -= card_h + 6

    # ── Gesamtbetrag ──────────────────────────────────────────────────────────
    y -= 4
    c.setStrokeColor(colors.HexColor('#444444'))
    c.setLineWidth(0.5)
    c.line(15*mm, y, W - 15*mm, y)
    y -= 16

    # Gesamtbetrag-Karte
    total_card_h = 36
    c.setFillColor(CARD_BG)
    c.roundRect(15*mm, y - total_card_h, W - 30*mm, total_card_h, 6, fill=1, stroke=0)

    c.setFillColor(GRAY_LT)
    c.setFont('Helvetica', 9)
    c.drawString(20*mm, y - 14, f'{len(persons)} Ticket(s)  |  inkl. aller Rabatte und Zuschlage')

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(20*mm, y - 28, 'GESAMTBETRAG')

    c.setFillColor(RED)
    c.setFont('Helvetica-Bold', 20)
    c.drawRightString(W - 20*mm, y - 30, f'CHF {total:.2f}')

    y -= total_card_h + 14

    # ── Vorzeigen-Banner ──────────────────────────────────────────────────────
    if y > 55:
        banner_h = 38
        c.setFillColor(CARD2_BG)
        c.roundRect(15*mm, y - banner_h, W - 30*mm, banner_h, 6, fill=1, stroke=0)

        c.setFillColor(GRAY_LT)
        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(W/2, y - 16, 'Bitte dieses Ticket an der Kinokasse vorzeigen')

        c.setFillColor(GRAY_MID)
        c.setFont('Helvetica', 8)
        c.drawCentredString(W/2, y - 28, f'Bestellnummer: {order_id}   |   Nicht uebertragbar')

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setFillColor(CARD_BG)
    c.rect(0, 0, W, 28, fill=1, stroke=0)
    c.setFillColor(GRAY_MID)
    c.setFont('Helvetica', 7)
    c.drawCentredString(W/2, 16, '(c) 2026 Kinoverwaltungssystem  |  BSc Wirtschaftsinformatik FHNW')
    c.drawCentredString(W/2, 8, 'Dieses Ticket ist personengebunden und nicht uebertragbar.')

    c.save()
    return buf.getvalue()