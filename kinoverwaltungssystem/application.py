import os
from dotenv import load_dotenv
load_dotenv()

from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.ui.home_ui import Home_UI
from kinoverwaltungssystem.ui.login_ui import Login_UI
from kinoverwaltungssystem.ui.movie_ui import Movie_UI
from kinoverwaltungssystem.ui.ticket_ui import Ticket_UI

database = Database()


class Kinoverwaltungssystem:
    def __init__(self):
        database.init_db()

    def run(self):
        ui.run(title="Kinoverwaltungssystem", storage_secret="kino-geheim-schluessel",
               port=int(os.environ.get("PORT", 8080)), reload=False)


@ui.page('/')
def home_page():
    movies = database.load_movies()
    Home_UI(movies).render()


@ui.page('/login')
def login_page():
    if nicegui_app.storage.user.get('authenticated'):
        ui.navigate.to('/')
        return
    Login_UI(database).render()


@ui.page('/movies')
def movies_page():
    Movie_UI(database).render()


@ui.page('/tickets')
def tickets_page(movie_id: int = None):
    Ticket_UI(database, movie_id).render()


@ui.page('/tickets/success')
def tickets_success_page(order_id: str = ''):
    """Stripe leitet nach erfolgreichem Kauf hierher weiter."""
    from kinoverwaltungssystem.ui.navbar import Navbar
    ui.query('body').style(
        'background-color:#141414; color:white; font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;'
    )
    Navbar('tickets').render()

    # Bestelldaten aus dem User-Storage laden (wurden beim Checkout gespeichert)
    pending = nicegui_app.storage.user.get('pending_ticket', {})

    with ui.column().classes('w-full items-center justify-center pt-24 pb-16 gap-6'):
        ui.icon('check_circle').classes('text-green-500 text-8xl')
        ui.label('Zahlung erfolgreich!').classes('text-white text-4xl font-black')
        ui.label(f'Bestell-Nr.: {order_id}').classes('text-gray-400 text-lg')
        ui.label('Vielen Dank für Ihren Kauf. Wir freuen uns auf Ihren Besuch!').classes(
            'text-gray-400 text-base')

        # PDF-Download Block
        with ui.card().classes('rounded-xl mt-4').style(
            'background-color:#1f1f1f; min-width:380px; max-width:480px;'
        ):
            with ui.row().classes('w-full items-center gap-4 p-5'):
                ui.icon('picture_as_pdf').classes('text-green-500 text-5xl')
                with ui.column().classes('flex-1 gap-1'):
                    ui.label('PDF-Ticket herunterladen').classes('text-white text-lg font-black')
                    ui.label('Dein Ticket ist bereit – speichere es als PDF.').classes(
                        'text-gray-400 text-sm')

            if pending:
                # Bestelldetails anzeigen
                with ui.column().classes('w-full px-5 pb-2 gap-1'):
                    ui.separator().style('background-color:#333;').classes('mb-3')
                    movie_titel = pending.get('movie_titel', '–')
                    persons_count = pending.get('persons_count', 0)
                    total = pending.get('total', 0.0)
                    hour = pending.get('hour', 20)
                    is_wknd = pending.get('is_weekend', False)
                    with ui.row().classes('w-full justify-between'):
                        ui.label(movie_titel).classes('text-white text-sm font-bold')
                        with ui.row().classes('items-baseline gap-1'):
                            ui.label(f'{total:.2f}').classes('text-red-500 font-bold text-lg')
                            ui.label('CHF').classes('text-red-500 text-sm')
                    ui.label(
                        f'{persons_count} Person(en) · {hour:02d}:00 Uhr · '
                        f'{"Wochenende" if is_wknd else "Wochentag"}'
                    ).classes('text-gray-500 text-xs')

            with ui.column().classes('w-full px-5 pb-5 pt-3'):
                def download_pdf():
                    import uuid as _uuid
                    oid = order_id or str(_uuid.uuid4())[:8].upper()
                    p = nicegui_app.storage.user.get('pending_ticket', {})
                    if not p:
                        ui.notify('Keine Ticketdaten gefunden. Bitte erneut bestellen.', color='warning')
                        return
                    # Personen aus Storage rekonstruieren
                    from kinoverwaltungssystem.ui.ticket_ui import TicketPerson
                    persons = [
                        TicketPerson(pp['name'], pp['age'], pp['is_student'])
                        for pp in p.get('persons', [])
                    ]
                    if not persons:
                        ui.notify('Keine Personendaten gefunden.', color='warning')
                        return
                    movie_obj = database.load_movies()
                    movie_obj = next((m for m in movie_obj if m.id == p.get('movie_id')), None)
                    if not movie_obj:
                        ui.notify('Film nicht gefunden.', color='warning')
                        return
                    try:
                        from kinoverwaltungssystem.services.ticket_service import generate_ticket_pdf
                        pdf_bytes = generate_ticket_pdf(
                            movie=movie_obj,
                            persons=persons,
                            total=p.get('total', 0.0),
                            show_hour=p.get('hour', 20),
                            is_weekend=p.get('is_weekend', False),
                            order_id=oid,
                        )
                        ui.download(pdf_bytes, filename=f'ticket_{oid}.pdf')
                        ui.notify('📄 PDF-Ticket wird heruntergeladen...', color='positive')
                    except ImportError:
                        ui.notify('reportlab fehlt. pip install reportlab', color='negative')
                    except Exception as e:
                        ui.notify(f'PDF-Fehler: {e}', color='negative')

                ui.button('📄 PDF-Ticket herunterladen', on_click=download_pdf).props(
                    'no-caps unelevated'
                ).classes('w-full text-white font-bold rounded py-3 text-base').style(
                    'background-color:#16a34a !important;')

        ui.button('Zurück zur Startseite', on_click=lambda: ui.navigate.to('/')).props(
            'no-caps unelevated').classes('text-white font-bold rounded px-8 py-3').style(
            'background-color:#e50914 !important;')