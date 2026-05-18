"""
ticket_service.py  –  PDF-Ticket Generator
Ablegen unter: kinoverwaltungssystem/services/ticket_service.py
Voraussetzung: pip install reportlab
"""
from __future__ import annotations
import io
from datetime import datetime


def generate_ticket_pdf(movie, persons: list, total: float,
                         show_hour: int, is_weekend: bool, order_id: str) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.pdfgen.canvas import Canvas
    except ImportError:
        raise RuntimeError("reportlab nicht installiert. Bitte 'pip install reportlab' ausführen.")

    W, H = A4
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=A4)

    # ── Hintergrund ──────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#0a0a0a'))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Roter Header-Banner ───────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#e50914'))
    c.rect(0, H - 75, W, 75, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 24)
    c.drawString(20*mm, H - 46, 'KINOVERWALTUNGSSYSTEM')
    c.setFont('Helvetica', 10)
    c.drawRightString(W - 20*mm, H - 32, 'Ihr offizielles Kinoticket')
    c.drawRightString(W - 20*mm, H - 45, f'Bestell-Nr.: {order_id}')

    y = H - 95

    # ── Filmtitel ─────────────────────────────────────────────────────────────
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 20)
    title = movie.titel if len(movie.titel) <= 45 else movie.titel[:42] + '...'
    c.drawString(20*mm, y, title)
    y -= 26

    # ── Badges ────────────────────────────────────────────────────────────────
    badges = [movie.genre.value, f'FSK {movie.altersfreigabe.value}',
              str(movie.erscheinungsjahr), f'{movie.dauer} Min']
    if movie.bewertung:
        badges.append(f'★ {movie.bewertung:.1f}')
    bx = 20*mm
    for badge in badges:
        tw = c.stringWidth(badge, 'Helvetica-Bold', 9) + 12
        c.setFillColor(colors.HexColor('#1f1f1f'))
        c.roundRect(bx, y - 4, tw, 16, 4, fill=1, stroke=0)
        c.setFillColor(colors.HexColor('#4ade80'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(bx + 6, y + 4, badge)
        bx += tw + 6
    y -= 26

    # ── Beschreibung ──────────────────────────────────────────────────────────
    if movie.beschreibung:
        desc = movie.beschreibung[:200] + ('…' if len(movie.beschreibung) > 200 else '')
        c.setFillColor(colors.HexColor('#888888'))
        c.setFont('Helvetica', 9)
        words, line = desc.split(), ''
        for w in words:
            test = (line + ' ' + w).strip()
            if c.stringWidth(test, 'Helvetica', 9) <= W - 40*mm:
                line = test
            else:
                c.drawString(20*mm, y, line); y -= 13; line = w
        if line:
            c.drawString(20*mm, y, line); y -= 13
        y -= 6

    # ── Trennlinie ────────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor('#333333'))
    c.line(20*mm, y, W - 20*mm, y); y -= 18

    # ── Vorstellungsdetails ───────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#e50914'))
    c.setFont('Helvetica-Bold', 10)
    c.drawString(20*mm, y, 'VORSTELLUNGSDETAILS'); y -= 18

    details = [
        ('Datum', datetime.now().strftime('%d.%m.%Y')),
        ('Uhrzeit', f'{show_hour:02d}:00 Uhr' + (' 🌙 Spätvorstellung' if show_hour >= 22 else '')),
        ('Typ', 'Wochenende (+2.00 CHF)' if is_weekend else 'Wochentag'),
        ('Ausgestellt', datetime.now().strftime('%d.%m.%Y %H:%M Uhr')),
    ]
    for lbl, val in details:
        c.setFillColor(colors.HexColor('#666666'))
        c.setFont('Helvetica', 10)
        c.drawString(20*mm, y, lbl + ':')
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(72*mm, y, val)
        y -= 16
    y -= 8

    # ── Trennlinie ────────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor('#333333'))
    c.line(20*mm, y, W - 20*mm, y); y -= 18

    # ── Tickets pro Person ────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#e50914'))
    c.setFont('Helvetica-Bold', 10)
    c.drawString(20*mm, y, f'TICKETS ({len(persons)} PERSON(EN))'); y -= 18

    is_late = show_hour >= 22
    for i, person in enumerate(persons):
        price, discounts = person.calculate_price(is_late, is_weekend)
        card_h = 22 + len(discounts) * 13
        c.setFillColor(colors.HexColor('#1a1a1a'))
        c.roundRect(20*mm, y - card_h + 18, W - 40*mm, card_h, 6, fill=1, stroke=0)

        c.setFillColor(colors.HexColor('#e50914'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(26*mm, y + 5, f'#{i+1:02d}')

        age_lbl = '👶 Kind' if person.age <= 12 else ('👴 Senior' if person.age >= 65 else '🧑 Erw.')
        student = '  🎓 Student' if person.is_student else ''
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(38*mm, y + 5, f'{person.name}  ({person.age} J.  {age_lbl}){student}')
        c.setFillColor(colors.HexColor('#e50914'))
        c.drawRightString(W - 22*mm, y + 5, f'CHF {price:.2f}')
        y -= 16

        for d in discounts:
            c.setFillColor(colors.HexColor('#666666'))
            c.setFont('Helvetica', 8)
            c.drawString(38*mm, y, f'↳ {d}'); y -= 13
        y -= 10

    # ── Gesamtbetrag ──────────────────────────────────────────────────────────
    c.setStrokeColor(colors.HexColor('#333333'))
    c.line(20*mm, y, W - 20*mm, y); y -= 18
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(20*mm, y, 'GESAMTBETRAG')
    c.setFillColor(colors.HexColor('#e50914'))
    c.setFont('Helvetica-Bold', 18)
    c.drawRightString(W - 20*mm, y - 2, f'CHF {total:.2f}')
    y -= 32

    # ── Ticket-Strich ─────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#1a1a1a'))
    c.roundRect(20*mm, y - 50, W - 40*mm, 50, 6, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#555555'))
    c.setFont('Helvetica', 9)
    c.drawCentredString(W/2, y - 16, '▓▓  Bitte dieses Ticket an der Kinokasse vorzeigen  ▓▓')
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#444444'))
    c.drawCentredString(W/2, y - 30, f'Bestell-Nr: {order_id}')
    c.drawCentredString(W/2, y - 42, f'Ausgestellt: {datetime.now().strftime("%d.%m.%Y %H:%M")}')

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#1a1a1a'))
    c.rect(0, 0, W, 30, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#555555'))
    c.setFont('Helvetica', 8)
    c.drawCentredString(W/2, 17, '© 2026 Kinoverwaltungssystem — BSc Wirtschaftsinformatik FHNW')
    c.drawCentredString(W/2, 8, 'Dieses Ticket ist nicht übertragbar.')

    c.save()
    return buf.getvalue()
