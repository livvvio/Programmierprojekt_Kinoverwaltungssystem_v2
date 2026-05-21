"""
ticket_ui.py  –  Ticketkauf mit Kaufen/Abbrechen, Stripe und PDF nach dem Kauf
"""
from __future__ import annotations
import os
import uuid
from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.ui.navbar import Navbar

TICKET_GRUNDGEBUEHR    = 15.00
RABATT_KIND            = 0.5
RABATT_STUDENT         = 0.8
RABATT_SENIOR          = 0.7
WOCHENEND_ZUSCHLAG     = 2.00
SPAETVORSTELLUNG_RABATT = 0.9


class TicketPerson:
    def __init__(self, name: str, age: int, is_student: bool):
        self.name = name
        self.age = age
        self.is_student = is_student

    def calculate_price(self, is_late: bool, is_weekend: bool) -> tuple[float, list[str]]:
        price = TICKET_GRUNDGEBUEHR
        discounts: list[str] = []
        if self.age <= 12:
            price *= RABATT_KIND
            discounts.append(f'Kinderrabatt (<=12 J.): -{(1-RABATT_KIND)*100:.0f}%')
        elif self.age >= 65:
            price *= RABATT_SENIOR
            discounts.append(f'Seniorenrabatt (>=65 J.): -{(1-RABATT_SENIOR)*100:.0f}%')
        if self.is_student:
            price *= RABATT_STUDENT
            discounts.append(f'Studentenrabatt: -{(1-RABATT_STUDENT)*100:.0f}%')
        if is_weekend:
            price += WOCHENEND_ZUSCHLAG
            discounts.append(f'Wochenendezuschlag: +{WOCHENEND_ZUSCHLAG:.2f} CHF')
        if is_late:
            price *= SPAETVORSTELLUNG_RABATT
            discounts.append(f'Spaetvorstellung (nach 22:00): -{(1-SPAETVORSTELLUNG_RABATT)*100:.0f}%')
        return price, discounts


def _do_pdf_download(movie, persons: list[TicketPerson], total: float,
                     show_hour: int, is_weekend: bool, order_id: str):
    """
    Generiert das PDF und startet den Browser-Download.
    Kann aus ticket_ui und ticket_success_ui aufgerufen werden.
    """
    try:
        from kinoverwaltungssystem.service.ticket_service import generate_ticket_pdf
    except ImportError as e:
        ui.notify(f'Import-Fehler: {e}', color='negative')
        return
    try:
        pdf_bytes = generate_ticket_pdf(
            movie=movie,
            persons=persons,
            total=total,
            show_hour=show_hour,
            is_weekend=is_weekend,
            order_id=order_id,
        )
        ui.download(pdf_bytes, filename=f'ticket_{order_id}.pdf')
        ui.notify('PDF-Ticket wird heruntergeladen...', color='positive')
    except RuntimeError as e:
        ui.notify(str(e), color='negative')
    except Exception as e:
        ui.notify(f'PDF-Fehler: {e}', color='negative')


class Ticket_UI:
    def __init__(self, db: Database, preselected_movie_id: int | None = None):
        self.db = db
        self.preselected_movie_id = preselected_movie_id
        self.persons: list[TicketPerson] = []

    def render(self):
        ui.query('body').style(
            'background-color:#141414; color:white; '
            'font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;'
        )
        Navbar('tickets').render()

        movies = self.db.load_movies()
        movie_by_id = {m.id: m for m in movies}
        movie_options = {m.id: m.titel for m in movies}
        default_id = (
            self.preselected_movie_id
            if self.preselected_movie_id and self.preselected_movie_id in movie_options
            else (movies[0].id if movies else None)
        )

        # ── Hilfsfunktionen ───────────────────────────────────────────────────
        def _hour() -> int:
            return min(23, max(0, int(uhrzeit_input.value or 0)))

        def _get_total() -> float:
            return sum(
                p.calculate_price(_hour() >= 22, weekend_toggle.value)[0]
                for p in self.persons
            )

        def refresh_movie_info():
            movie_info_container.clear()
            movie_obj = movie_by_id.get(selected_movie_id.value)
            if not movie_obj:
                return
            with movie_info_container:
                with ui.row().classes('w-full gap-6 items-start'):
                    if movie_obj.imageUrl:
                        ui.image(movie_obj.imageUrl).classes(
                            'rounded-xl object-cover shadow-lg'
                        ).style('width:150px; height:225px; flex-shrink:0;')
                    else:
                        with ui.element('div').classes(
                            'rounded-xl flex items-center justify-center'
                        ).style('width:150px; height:225px; background-color:#333; flex-shrink:0;'):
                            ui.icon('movie').classes('text-gray-600 text-6xl')

                    with ui.column().classes('flex-1 gap-2 min-w-0'):
                        ui.label(movie_obj.titel).classes(
                            'text-white text-3xl font-black leading-tight'
                        )
                        with ui.row().classes('gap-2 flex-wrap items-center mt-1'):
                            ui.label(movie_obj.genre.value).classes(
                                'text-green-500 font-semibold text-sm'
                            )
                            ui.label('·').classes('text-gray-600')
                            ui.label(str(movie_obj.erscheinungsjahr)).classes('text-gray-400 text-sm')
                            ui.label('·').classes('text-gray-600')
                            ui.label(f'{movie_obj.dauer} Min').classes('text-gray-400 text-sm')
                            ui.label(f'FSK {movie_obj.altersfreigabe.value}').classes(
                                'text-white text-xs font-bold px-2 py-0.5 rounded'
                            ).style('background-color:#e50914;')
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('star').classes('text-yellow-400 text-base')
                            ui.label(f'{movie_obj.bewertung:.1f} / 10').classes(
                                'text-yellow-400 font-bold text-sm'
                            )
                        if movie_obj.regisseur:
                            ui.label(f'Regie: {movie_obj.regisseur}').classes('text-gray-400 text-sm')
                        if movie_obj.produktionsfirma:
                            ui.label(f'Produktion: {movie_obj.produktionsfirma}').classes(
                                'text-gray-400 text-sm'
                            )
                        if movie_obj.beschreibung:
                            ui.label(movie_obj.beschreibung).classes(
                                'text-gray-300 text-sm mt-2'
                            ).style('line-height:1.6;')

        def refresh_summary():
            summary_card.clear()
            with summary_card:
                ui.label('Zusammenfassung').classes('text-white text-lg font-bold mb-4')

                movie_obj = movie_by_id.get(selected_movie_id.value)
                hour     = _hour()
                is_late  = hour >= 22
                is_wknd  = weekend_toggle.value

                if movie_obj:
                    ui.label(movie_obj.titel).classes('text-white font-bold text-base mb-3')

                with ui.row().classes('w-full gap-6 mb-4 p-3 rounded-lg').style(
                    'background-color:#2a2a2a;'
                ):
                    with ui.column().classes('gap-0'):
                        ui.label('Uhrzeit').classes(
                            'text-gray-500 text-xs uppercase tracking-wide'
                        )
                        ui.label(f'{hour:02d}:00 Uhr').classes('text-white text-sm font-semibold')
                        if is_late:
                            ui.label('Spaetvorstellung').classes('text-purple-400 text-xs')
                    with ui.column().classes('gap-0'):
                        ui.label('Tag').classes(
                            'text-gray-500 text-xs uppercase tracking-wide'
                        )
                        ui.label(
                            'Wochenende' if is_wknd else 'Wochentag'
                        ).classes('text-white text-sm font-semibold')

                if not self.persons:
                    ui.label('Noch keine Personen hinzugefuegt.').classes(
                        'text-gray-500 text-sm text-center mt-4 mb-4'
                    )
                else:
                    ui.separator().style('background-color:#333;').classes('mb-3')
                    total = 0.0
                    for i, person in enumerate(self.persons):
                        price, disc = person.calculate_price(is_late, is_wknd)
                        total += price
                        with ui.column().classes('w-full mb-3 p-3 rounded-lg').style(
                            'background-color:#2a2a2a;'
                        ):
                            with ui.row().classes('w-full justify-between items-center'):
                                ui.label(person.name).classes('text-white font-semibold text-sm')
                                with ui.row().classes('items-center gap-1'):
                                    ui.label(f'{price:.2f} CHF').classes(
                                        'text-white font-bold text-sm'
                                    )
                                    ui.button(
                                        icon='close',
                                        on_click=lambda idx=i: remove_person(idx)
                                    ).props('flat round size=xs').classes('text-gray-500')
                            for d in (disc or [f'Grundpreis: {TICKET_GRUNDGEBUEHR:.2f} CHF']):
                                ui.label(f'> {d}').classes('text-gray-500 text-xs mt-1')

                    ui.separator().style('background-color:#444;').classes('my-3')

                    with ui.row().classes('w-full justify-between items-center mb-4'):
                        with ui.column().classes('gap-0'):
                            ui.label('Gesamtbetrag').classes('text-white font-black text-lg')
                            ui.label(f'{len(self.persons)} Person(en)').classes(
                                'text-gray-500 text-xs'
                            )
                        with ui.row().classes('items-baseline gap-1'):
                            ui.label(f'{total:.2f}').classes('text-red-500 font-black text-3xl')
                            ui.label('CHF').classes('text-red-500 font-bold text-lg')

                    # Kaufen / Abbrechen – PDF erscheint erst NACH dem Kauf
                    with ui.row().classes('w-full gap-3'):
                        ui.button('Abbrechen', on_click=lambda: _cancel_order()).props(
                            'no-caps unelevated'
                        ).classes('flex-1 text-white font-bold rounded').style(
                            'background-color:#333 !important; border:1px solid #555;'
                        )
                        ui.button('Kaufen', on_click=lambda: _checkout()).props(
                            'no-caps unelevated'
                        ).classes('flex-1 text-white font-bold rounded').style(
                            'background-color:#e50914 !important;'
                        )

                # Preistabelle
                ui.separator().style('background-color:#333;').classes('my-3')
                ui.label('Preistabelle').classes(
                    'text-gray-500 text-xs uppercase tracking-wide mb-2'
                )
                for lbl, val in [
                    ('Kind (<=12 J.)',       f'{TICKET_GRUNDGEBUEHR*RABATT_KIND:.2f} CHF'),
                    ('Erwachsener',          f'{TICKET_GRUNDGEBUEHR:.2f} CHF'),
                    ('Senior (>=65 J.)',     f'{TICKET_GRUNDGEBUEHR*RABATT_SENIOR:.2f} CHF'),
                    ('Student (-20%)',       'auf Basispreis'),
                    ('Wochenende',           f'+{WOCHENEND_ZUSCHLAG:.2f} CHF'),
                    ('Spaetvorstellung (>=22h)', '-10%'),
                ]:
                    with ui.row().classes('w-full justify-between'):
                        ui.label(lbl).classes('text-gray-400 text-xs')
                        ui.label(val).classes('text-gray-400 text-xs')

        # ── Aktionen ──────────────────────────────────────────────────────────
        def remove_person(idx: int):
            self.persons.pop(idx)
            refresh_summary()

        def add_person():
            add_error.set_text('')
            name = person_name.value.strip()
            if not name:
                add_error.set_text('Bitte einen Namen eingeben.')
                return
            try:
                age = int(person_age.value)
            except (TypeError, ValueError):
                add_error.set_text('Ungueltiges Alter.')
                return
            movie_obj = movie_by_id.get(selected_movie_id.value)
            if movie_obj and age < movie_obj.altersfreigabe.value:
                add_error.set_text(f'Zu jung fuer FSK {movie_obj.altersfreigabe.value}!')
                return
            self.persons.append(TicketPerson(name, age, student_toggle.value))
            person_name.value  = ''
            person_age.value   = 25
            student_toggle.value = False
            refresh_summary()

        def _cancel_order():
            self.persons.clear()
            refresh_summary()
            ui.notify('Bestellung abgebrochen.', color='warning')

        def _checkout():
            if not self.persons:
                ui.notify('Bitte zuerst Personen hinzufuegen.', color='negative')
                return
            movie_obj = movie_by_id.get(selected_movie_id.value)
            if not movie_obj:
                ui.notify('Bitte einen Film auswaehlen.', color='negative')
                return

            hour    = _hour()
            is_wknd = weekend_toggle.value
            total   = _get_total()

            # Personen-Snapshot fuer PDF einfrieren (vor moeglichem .clear())
            persons_snap = [
                TicketPerson(p.name, p.age, p.is_student) for p in self.persons
            ]

            stripe_key = os.environ.get('STRIPE_SECRET_KEY', '')
            if stripe_key:
                _start_stripe_checkout(movie_obj, total, hour, is_wknd, persons_snap)
            else:
                _show_confirmation_dialog(movie_obj, total, hour, is_wknd, persons_snap)

        def _start_stripe_checkout(
            movie_obj: Movie, total: float, hour: int,
            is_wknd: bool, persons_snap: list[TicketPerson]
        ):
            try:
                import stripe
            except ImportError:
                ui.notify('stripe nicht installiert. pip install stripe', color='negative')
                return

            stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
            order_id = str(uuid.uuid4())[:8].upper()

            # Bestelldaten fuer Erfolgsseite speichern
            nicegui_app.storage.user['pending_ticket'] = {
                'movie_id':     movie_obj.id,
                'movie_titel':  movie_obj.titel,
                'total':        total,
                'hour':         hour,
                'is_weekend':   is_wknd,
                'order_id':     order_id,
                'persons': [
                    {'name': p.name, 'age': p.age, 'is_student': p.is_student}
                    for p in persons_snap
                ],
            }

            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'chf',
                            'product_data': {
                                'name': f'Kinoticket - {movie_obj.titel}',
                                'description': (
                                    f'{len(persons_snap)} Person(en) | '
                                    f'{hour:02d}:00 Uhr | '
                                    f'{"Wochenende" if is_wknd else "Wochentag"}'
                                ),
                            },
                            'unit_amount': int(round(total * 100)),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=(
                        f'{os.environ.get("APP_URL", "http://localhost:8080")}'
                        f'/tickets/success?order_id={order_id}'
                    ),
                    cancel_url=(
                        f'{os.environ.get("APP_URL", "http://localhost:8080")}/tickets'
                    ),
                    metadata={'order_id': order_id, 'movie': movie_obj.titel},
                )
                ui.navigate.to(session.url)
            except Exception as e:
                ui.notify(f'Stripe-Fehler: {e}', color='negative')

        def _show_confirmation_dialog(
            movie_obj: Movie, total: float, hour: int,
            is_wknd: bool, persons_snap: list[TicketPerson]
        ):
            """Demo-Modus wenn kein Stripe-Key gesetzt ist."""
            order_id = str(uuid.uuid4())[:8].upper()

            # Daten im Storage speichern – identisch zu Stripe-Flow
            nicegui_app.storage.user['pending_ticket'] = {
                'movie_id':    movie_obj.id,
                'movie_titel': movie_obj.titel,
                'total':       total,
                'hour':        hour,
                'is_weekend':  is_wknd,
                'order_id':    order_id,
                'persons': [
                    {'name': p.name, 'age': p.age, 'is_student': p.is_student}
                    for p in persons_snap
                ],
            }

            with ui.dialog() as dialog, ui.card().classes('rounded-xl').style(
                'background-color:#1f1f1f; min-width:420px; max-width:560px;'
            ):
                # Erfolgs-Header
                with ui.column().classes('w-full items-center gap-2 py-5'):
                    ui.icon('check_circle').classes('text-green-500 text-6xl')
                    ui.label('Bestellung erfolgreich!').classes(
                        'text-white text-2xl font-black'
                    )
                    ui.label(f'Bestell-Nr.: {order_id}').classes('text-gray-400 text-sm')

                ui.separator().style('background-color:#333;').classes('my-1')

                # Bestellzusammenfassung
                with ui.column().classes('w-full gap-1 px-4 py-3'):
                    ui.label(movie_obj.titel).classes('text-white font-bold text-base')
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label(
                            f'{len(persons_snap)} Person(en)  |  {hour:02d}:00 Uhr  |  '
                            f'{"Wochenende" if is_wknd else "Wochentag"}'
                        ).classes('text-gray-400 text-sm')
                        with ui.row().classes('items-baseline gap-1'):
                            ui.label(f'{total:.2f}').classes('text-red-500 font-black text-xl')
                            ui.label('CHF').classes('text-red-500 text-sm font-bold')

                # Demo-Modus Hinweis
                with ui.row().classes('w-full items-start gap-2 mx-4 px-3 py-3 rounded-lg').style(
                    'background-color:#2a1a0a; border:1px solid #f59e0b; '
                    'margin-left:16px; margin-right:16px;'
                ):
                    ui.icon('info').classes('text-yellow-500 text-base mt-0.5')
                    with ui.column().classes('gap-0'):
                        ui.label('Demo-Modus').classes('text-yellow-400 text-xs font-bold')
                        ui.label(
                            'Setze STRIPE_SECRET_KEY in der .env Datei fuer echte Zahlungen.'
                        ).classes('text-yellow-600 text-xs')

                ui.separator().style('background-color:#333;').classes('my-1')

                # PDF-Download Block
                with ui.row().classes('w-full items-center gap-3 px-4 py-4').style(
                    'background-color:#162316; border-radius:0 0 12px 12px;'
                ):
                    ui.icon('picture_as_pdf').classes('text-green-400 text-4xl')
                    with ui.column().classes('flex-1 gap-0'):
                        ui.label('PDF-Ticket herunterladen').classes(
                            'text-white text-sm font-black'
                        )
                        ui.label(
                            'Dein Ticket ist bereit - speichere es als PDF.'
                        ).classes('text-gray-400 text-xs')

                    def do_download(
                        _m=movie_obj, _p=persons_snap,
                        _t=total, _h=hour, _w=is_wknd, _o=order_id
                    ):
                        _do_pdf_download(_m, _p, _t, _h, _w, _o)

                    ui.button('PDF herunterladen', on_click=do_download).props(
                        'no-caps unelevated'
                    ).classes('text-white font-bold rounded px-4 py-2').style(
                        'background-color:#16a34a !important;'
                    )

                # Schliessen
                with ui.row().classes('w-full px-4 pb-4 pt-2'):
                    ui.button(
                        'Schliessen',
                        on_click=lambda: (dialog.close(), _after_purchase())
                    ).props('no-caps unelevated').classes(
                        'w-full text-white font-bold rounded'
                    ).style('background-color:#333 !important; border:1px solid #555;')

            dialog.open()

        def _after_purchase():
            self.persons.clear()
            refresh_summary()

        # ── UI Layout ─────────────────────────────────────────────────────────
        with ui.column().classes('w-full px-6 md:px-12 pt-8 pb-12 gap-6'):

            # Film-Auswahl
            with ui.card().classes('w-full rounded-xl').style(
                'background-color:#1f1f1f; padding:1.5rem;'
            ):
                selected_movie_id = ui.select(
                    options=movie_options,
                    label='Film auswaehlen',
                    value=default_id,
                ).props('dark outlined').classes('mb-5').style('max-width:380px;')
                movie_info_container = ui.element('div').classes('w-full')

            # Vorstellungsdetails
            with ui.card().classes('w-full rounded-xl').style(
                'background-color:#1f1f1f; padding:1.5rem;'
            ):
                ui.label('Vorstellungsdetails').classes('text-white text-lg font-bold mb-4')
                with ui.row().classes('items-center gap-6 flex-wrap'):
                    uhrzeit_input = ui.number(
                        label='Uhrzeit (0-23 Uhr)', value=20, min=0, max=23
                    ).props('dark outlined').style('width:200px;')
                    with ui.row().classes('items-center gap-4 p-3 rounded-lg').style(
                        'background-color:#2a2a2a;'
                    ):
                        with ui.column().classes('gap-0'):
                            ui.label('Wochenende').classes('text-white text-sm font-semibold')
                            ui.label('Sa / So Zuschlag +2.00 CHF').classes('text-gray-500 text-xs')
                        weekend_toggle = ui.switch('').props('color=red')

            # Personen + Zusammenfassung
            with ui.row().classes('w-full gap-6 items-start flex-wrap'):
                with ui.card().classes('rounded-xl flex-1').style(
                    'background-color:#1f1f1f; min-width:300px; max-width:480px; padding:1.5rem;'
                ):
                    ui.label('Personen').classes('text-white text-lg font-bold mb-4')
                    person_name = ui.input(label='Name').props('dark outlined').classes(
                        'w-full mb-3'
                    )
                    with ui.row().classes('w-full gap-3 mb-2'):
                        person_age = ui.number(
                            label='Alter', value=25, min=0, max=120
                        ).props('dark outlined').classes('flex-1')
                        with ui.column().classes('flex-1 justify-center'):
                            ui.label('Student?').classes('text-gray-400 text-xs mb-1')
                            student_toggle = ui.switch('').props('color=red')
                    add_error = ui.label('').classes('text-red-500 text-xs mb-2')
                    ui.button('Person hinzufuegen', on_click=add_person).props(
                        'no-caps unelevated'
                    ).classes('w-full text-white font-bold rounded').style(
                        'background-color:#333 !important; border:1px solid #555;'
                    )

                summary_card = ui.card().classes('rounded-xl flex-1').style(
                    'background-color:#1f1f1f; min-width:300px; max-width:480px; padding:1.5rem;'
                )

        # ── Events ────────────────────────────────────────────────────────────
        selected_movie_id.on(
            'update:model-value',
            lambda: (refresh_movie_info(), refresh_summary())
        )
        uhrzeit_input.on('update:model-value', lambda: refresh_summary())
        weekend_toggle.on('update:model-value', lambda: refresh_summary())
        ui.timer(0.05, lambda: (refresh_movie_info(), refresh_summary()), once=True)