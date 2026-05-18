"""
ticket_success_ui.py  –  Erfolgsseite nach Stripe-Zahlung
Route: /tickets/success?order_id=XXX
"""
from __future__ import annotations
from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.ui.navbar import Navbar
from kinoverwaltungssystem.ui.ticket_ui import TicketPerson, _do_pdf_download


class TicketSuccess_UI:
    def __init__(self, db: Database, order_id: str):
        self.db = db
        self.order_id = order_id

    def render(self):
        ui.query('body').style(
            'background-color:#141414; color:white; '
            'font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;'
        )
        Navbar('tickets').render()

        # Bestelldaten aus User-Storage laden
        pending = nicegui_app.storage.user.get('pending_ticket', {})

        with ui.column().classes('w-full items-center pt-20 pb-16 px-6 gap-6'):

            # Erfolgs-Icon + Titel
            ui.icon('check_circle').classes('text-green-500').style('font-size:80px;')
            ui.label('Zahlung erfolgreich!').classes('text-white text-4xl font-black')
            ui.label(f'Bestell-Nr.: {self.order_id}').classes('text-gray-400 text-lg')
            ui.label('Vielen Dank fuer deinen Kauf. Wir freuen uns auf deinen Besuch!').classes(
                'text-gray-500 text-base text-center'
            )

            # ── Bestelldetails-Karte ──────────────────────────────────────────
            if pending:
                with ui.card().classes('rounded-xl w-full').style(
                    'background-color:#1f1f1f; max-width:500px;'
                ):
                    with ui.column().classes('w-full gap-3 p-5'):
                        ui.label('Bestelluebersicht').classes(
                            'text-gray-500 text-xs font-bold uppercase tracking-wider'
                        )
                        ui.label(pending.get('movie_titel', '-')).classes(
                            'text-white text-xl font-black'
                        )

                        with ui.row().classes('w-full gap-6'):
                            with ui.column().classes('gap-0'):
                                ui.label('Personen').classes(
                                    'text-gray-500 text-xs uppercase tracking-wide'
                                )
                                ui.label(
                                    str(pending.get('persons_count',
                                        len(pending.get('persons', []))))
                                ).classes('text-white text-sm font-semibold')
                            with ui.column().classes('gap-0'):
                                ui.label('Uhrzeit').classes(
                                    'text-gray-500 text-xs uppercase tracking-wide'
                                )
                                ui.label(
                                    f'{pending.get("hour", 20):02d}:00 Uhr'
                                ).classes('text-white text-sm font-semibold')
                            with ui.column().classes('gap-0'):
                                ui.label('Tag').classes(
                                    'text-gray-500 text-xs uppercase tracking-wide'
                                )
                                ui.label(
                                    'Wochenende' if pending.get('is_weekend') else 'Wochentag'
                                ).classes('text-white text-sm font-semibold')

                        ui.separator().style('background-color:#333;')

                        with ui.row().classes('w-full justify-between items-center'):
                            ui.label('Gesamtbetrag').classes('text-white font-black text-base')
                            with ui.row().classes('items-baseline gap-1'):
                                ui.label(
                                    f'{pending.get("total", 0.0):.2f}'
                                ).classes('text-red-500 font-black text-2xl')
                                ui.label('CHF').classes('text-red-500 font-bold')

            # ── PDF-Download Karte ────────────────────────────────────────────
            with ui.card().classes('rounded-xl w-full').style(
                'background-color:#162316; border:1px solid #1e4d1e; max-width:500px;'
            ):
                with ui.row().classes('w-full items-center gap-4 p-5'):
                    ui.icon('picture_as_pdf').classes('text-green-400').style('font-size:52px;')
                    with ui.column().classes('flex-1 gap-1'):
                        ui.label('PDF-Ticket herunterladen').classes(
                            'text-white text-lg font-black'
                        )
                        ui.label(
                            'Dein Ticket ist bereit. Speichere es als PDF und '
                            'zeige es an der Kinokasse vor.'
                        ).classes('text-gray-400 text-sm').style('line-height:1.5;')

                with ui.column().classes('w-full px-5 pb-5'):
                    def download_pdf():
                        p = nicegui_app.storage.user.get('pending_ticket', {})
                        if not p:
                            ui.notify(
                                'Keine Ticketdaten gefunden. Bitte erneut bestellen.',
                                color='warning'
                            )
                            return

                        # Personen aus Storage rekonstruieren
                        persons = [
                            TicketPerson(pp['name'], pp['age'], pp['is_student'])
                            for pp in p.get('persons', [])
                        ]
                        if not persons:
                            ui.notify('Keine Personendaten gefunden.', color='warning')
                            return

                        # Film aus DB laden
                        all_movies = self.db.load_movies()
                        movie_obj = next(
                            (m for m in all_movies if m.id == p.get('movie_id')), None
                        )
                        if not movie_obj:
                            ui.notify('Film nicht gefunden.', color='warning')
                            return

                        oid = self.order_id or p.get('order_id', 'UNBEKANNT')

                        _do_pdf_download(
                            movie=movie_obj,
                            persons=persons,
                            total=p.get('total', 0.0),
                            show_hour=p.get('hour', 20),
                            is_weekend=p.get('is_weekend', False),
                            order_id=oid,
                        )

                    ui.button('PDF-Ticket herunterladen', on_click=download_pdf).props(
                        'no-caps unelevated'
                    ).classes('w-full text-white font-bold rounded py-3 text-base').style(
                        'background-color:#16a34a !important;'
                    )

            # Zurueck-Button
            ui.button(
                'Zurueck zur Startseite',
                on_click=lambda: ui.navigate.to('/')
            ).props('no-caps unelevated').classes(
                'text-white font-bold rounded px-10 py-3'
            ).style('background-color:#e50914 !important;')