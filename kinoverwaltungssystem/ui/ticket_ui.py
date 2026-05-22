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

TICKET_GRUNDGEBUEHR     = 15.00
RABATT_KIND             = 0.5
RABATT_STUDENT          = 0.8
RABATT_SENIOR           = 0.7
WOCHENEND_ZUSCHLAG      = 2.00
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
    try:
        from kinoverwaltungssystem.services.ticket_service import generate_ticket_pdf
    except ImportError as e:
        ui.notify(f'Import-Fehler: {e}', color='negative')
        return
    try:
        pdf_bytes = generate_ticket_pdf(
            movie=movie, persons=persons, total=total,
            show_hour=show_hour, is_weekend=is_weekend, order_id=order_id,
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
            'background-color:#0f0f0f; color:white; '
            'font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;'
        )
        ui.add_head_html('''<style>
            ::-webkit-scrollbar { width: 4px; }
            ::-webkit-scrollbar-track { background: #1a1a1a; }
            ::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
            .section-card { background: #181818; border: 1px solid #242424; border-radius: 10px; padding: 20px; }
        </style>''')

        Navbar('tickets').render()

        movies = self.db.load_movies()
        movie_by_id = {m.id: m for m in movies}
        movie_options = {m.id: m.titel for m in movies}
        default_id = (
            self.preselected_movie_id
            if self.preselected_movie_id and self.preselected_movie_id in movie_options
            else (movies[0].id if movies else None)
        )

        def _hour() -> int:
            return min(23, max(0, int(uhrzeit_input.value or 0)))

        def _get_total() -> float:
            return sum(
                p.calculate_price(_hour() >= 22, weekend_toggle.value)[0]
                for p in self.persons
            )

        # ── Film-Info Refresh ─────────────────────────────────────────────────
        def refresh_movie_info():
            movie_info_container.clear()
            movie_obj = movie_by_id.get(selected_movie_id.value)
            if not movie_obj:
                return
            with movie_info_container:
                with ui.row().style('gap: 16px; align-items: center; width: 100%;'):
                    if movie_obj.imageUrl:
                        ui.image(movie_obj.imageUrl).style(
                            'width: 72px; height: 108px; object-fit: cover; '
                            'border-radius: 6px; flex-shrink: 0;'
                        )
                    else:
                        with ui.element('div').style(
                            'width: 72px; height: 108px; background: #252525; '
                            'border-radius: 6px; flex-shrink: 0; display: flex; '
                            'align-items: center; justify-content: center;'
                        ):
                            ui.icon('movie').style('color: #444; font-size: 28px;')

                    with ui.element('div').style('flex: 1; min-width: 0;'):
                        ui.label(movie_obj.titel).style(
                            'color: white; font-size: 20px; font-weight: 900; '
                            'line-height: 1.2; margin-bottom: 6px;'
                        )
                        with ui.row().style('gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 6px;'):
                            ui.label(movie_obj.genre.value).style(
                                'color: #4ade80; font-size: 12px; font-weight: 600;'
                            )
                            ui.label('·').style('color: #333;')
                            ui.label(str(movie_obj.erscheinungsjahr)).style('color: #777; font-size: 12px;')
                            ui.label('·').style('color: #333;')
                            ui.label(f'{movie_obj.dauer} Min').style('color: #777; font-size: 12px;')
                            ui.label(f'FSK {movie_obj.altersfreigabe.value}').style(
                                'background: #e50914; color: white; font-size: 10px; '
                                'font-weight: 700; padding: 2px 6px; border-radius: 3px;'
                            )
                        with ui.row().style('gap: 4px; align-items: center; margin-bottom: 4px;'):
                            ui.icon('star').style('color: #f5c518; font-size: 14px;')
                            ui.label(f'{movie_obj.bewertung:.1f} / 10').style(
                                'color: #f5c518; font-size: 12px; font-weight: 700;'
                            )
                        if movie_obj.beschreibung:
                            desc = (movie_obj.beschreibung[:120] + '…') if len(movie_obj.beschreibung) > 120 else movie_obj.beschreibung
                            ui.label(desc).style(
                                'color: #666; font-size: 11px; line-height: 1.5;'
                            )

        # ── Zusammenfassung Refresh ───────────────────────────────────────────
        def refresh_summary():
            summary_container.clear()
            with summary_container:
                hour    = _hour()
                is_late = hour >= 22
                is_wknd = weekend_toggle.value

                # Vorstellungsinfo
                with ui.row().style(
                    'background: #212121; border-radius: 8px; padding: 10px 14px; '
                    'gap: 20px; margin-bottom: 14px; width: 100%;'
                ):
                    with ui.element('div'):
                        ui.label('UHRZEIT').style(
                            'color: #555; font-size: 9px; font-weight: 700; letter-spacing: 1.5px;'
                        )
                        ui.label(f'{hour:02d}:00').style(
                            'color: white; font-size: 16px; font-weight: 800;'
                        )
                        if is_late:
                            ui.label('Spätvorstellung').style('color: #a78bfa; font-size: 10px;')
                    with ui.element('div'):
                        ui.label('TAG').style(
                            'color: #555; font-size: 9px; font-weight: 700; letter-spacing: 1.5px;'
                        )
                        ui.label('Wochenende' if is_wknd else 'Wochentag').style(
                            'color: white; font-size: 16px; font-weight: 800;'
                        )
                        if is_wknd:
                            ui.label('+2.00 CHF').style('color: #fb923c; font-size: 10px;')

                # Personen
                if not self.persons:
                    with ui.element('div').style(
                        'text-align: center; padding: 20px 0; color: #444; font-size: 13px;'
                    ):
                        ui.label('Noch keine Personen hinzugefügt.')
                else:
                    # Ab 4 Personen: scrollbarer Container
                    with ui.element('div').style(
                        ('max-height: 220px; overflow-y: auto;' if len(self.persons) > 3 else '')
                        + ' margin-bottom: 0;'
                    ):
                        for i, person in enumerate(self.persons):
                            price, disc = person.calculate_price(is_late, is_wknd)
                            with ui.element('div').style(
                                'background: #212121; border-radius: 8px; padding: 10px 12px; '
                                'margin-bottom: 8px;'
                            ):
                                with ui.row().style('justify-content: space-between; align-items: center; width: 100%;'):
                                    ui.label(person.name).style(
                                        'color: white; font-weight: 600; font-size: 13px;'
                                    )
                                    with ui.row().style('align-items: center; gap: 6px;'):
                                        ui.label(f'{price:.2f} CHF').style(
                                            'color: white; font-weight: 700; font-size: 13px;'
                                        )
                                        ui.button(
                                            icon='close',
                                            on_click=lambda idx=i: remove_person(idx)
                                        ).props('flat round size=xs').style('color: #555;')
                                for d in (disc or [f'Grundpreis: {TICKET_GRUNDGEBUEHR:.2f} CHF']):
                                    ui.label(f'› {d}').style(
                                        'color: #555; font-size: 10px; margin-top: 2px;'
                                    )

                    # Total — immer ausserhalb des Scroll-Containers
                    total = sum(
                        p.calculate_price(is_late, is_wknd)[0] for p in self.persons
                    )
                    ui.element('div').style('height: 1px; background: #2a2a2a; margin: 12px 0;')
                    with ui.row().style(
                        'justify-content: space-between; align-items: baseline; '
                        'width: 100%; margin-bottom: 14px;'
                    ):
                        with ui.element('div'):
                            ui.label('TOTAL').style(
                                'color: #666; font-size: 10px; font-weight: 700; letter-spacing: 2px;'
                            )
                            ui.label(f'{len(self.persons)} Person(en)').style(
                                'color: #555; font-size: 11px;'
                            )
                        with ui.row().style('align-items: baseline; gap: 4px;'):
                            ui.label(f'{total:.2f}').style(
                                'color: #e50914; font-size: 28px; font-weight: 900;'
                            )
                            ui.label('CHF').style(
                                'color: #e50914; font-size: 14px; font-weight: 700;'
                            )

                    with ui.row().style('gap: 8px; width: 100%;'):
                        ui.button('Abbrechen', on_click=lambda: _cancel_order()).props(
                            'no-caps unelevated'
                        ).style(
                            'flex: 1; background: #242424 !important; color: #aaa; '
                            'font-weight: 600; border: 1px solid #333; border-radius: 6px; '
                            'font-size: 13px; padding: 8px 0;'
                        )
                        ui.button('Kaufen', on_click=lambda: _checkout()).props(
                            'no-caps unelevated'
                        ).style(
                            'flex: 1; background: #e50914 !important; color: white; '
                            'font-weight: 700; border-radius: 6px; font-size: 13px; padding: 8px 0;'
                        )

                # Preistabelle
                ui.element('div').style('height: 1px; background: #222; margin: 14px 0 10px 0;')
                ui.label('PREISTABELLE').style(
                    'color: #444; font-size: 9px; font-weight: 700; letter-spacing: 2px; margin-bottom: 8px;'
                )
                for lbl, val in [
                    ('Kind (≤12 J.)',         f'{TICKET_GRUNDGEBUEHR*RABATT_KIND:.2f} CHF'),
                    ('Erwachsener',            f'{TICKET_GRUNDGEBUEHR:.2f} CHF'),
                    ('Senior (≥65 J.)',        f'{TICKET_GRUNDGEBUEHR*RABATT_SENIOR:.2f} CHF'),
                    ('Student',                '−20% auf Basispreis'),
                    ('Wochenende',             f'+{WOCHENEND_ZUSCHLAG:.2f} CHF'),
                    ('Spätvorstellung (≥22h)', '−10%'),
                ]:
                    with ui.row().style('justify-content: space-between; width: 100%; margin-bottom: 4px;'):
                        ui.label(lbl).style('color: #555; font-size: 11px;')
                        ui.label(val).style('color: #555; font-size: 11px;')

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
                add_error.set_text('Ungültiges Alter.')
                return
            movie_obj = movie_by_id.get(selected_movie_id.value)
            if movie_obj and age < movie_obj.altersfreigabe.value:
                add_error.set_text(f'Zu jung für FSK {movie_obj.altersfreigabe.value}!')
                return
            self.persons.append(TicketPerson(name, age, student_toggle.value))
            person_name.value    = ''
            person_age.value     = 25
            student_toggle.value = False
            refresh_summary()

        def _cancel_order():
            self.persons.clear()
            refresh_summary()
            ui.notify('Bestellung abgebrochen.', color='warning')

        def _checkout():
            if not self.persons:
                ui.notify('Bitte zuerst Personen hinzufügen.', color='negative')
                return
            movie_obj = movie_by_id.get(selected_movie_id.value)
            if not movie_obj:
                ui.notify('Bitte einen Film auswählen.', color='negative')
                return
            hour    = _hour()
            is_wknd = weekend_toggle.value
            total   = _get_total()
            persons_snap = [TicketPerson(p.name, p.age, p.is_student) for p in self.persons]
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
                        f'{os.environ.get("APP_URL","http://localhost:8080")}'
                        f'/tickets/success?order_id={order_id}'
                    ),
                    cancel_url=f'{os.environ.get("APP_URL","http://localhost:8080")}/tickets',
                    metadata={'order_id': order_id, 'movie': movie_obj.titel},
                )
                ui.navigate.to(session.url)
            except Exception as e:
                ui.notify(f'Stripe-Fehler: {e}', color='negative')

        def _show_confirmation_dialog(
            movie_obj: Movie, total: float, hour: int,
            is_wknd: bool, persons_snap: list[TicketPerson]
        ):
            order_id = str(uuid.uuid4())[:8].upper()
            with ui.dialog() as dialog, ui.card().classes('rounded-xl').style(
                'background-color:#1a1a1a; min-width:420px; max-width:520px;'
            ):
                with ui.column().style('align-items: center; gap: 8px; padding: 24px 24px 16px;'):
                    ui.icon('check_circle').style('color: #22c55e; font-size: 52px;')
                    ui.label('Bestellung erfolgreich!').style(
                        'color: white; font-size: 22px; font-weight: 900;'
                    )
                    ui.label(f'Bestell-Nr.: {order_id}').style('color: #555; font-size: 13px;')

                ui.element('div').style('height: 1px; background: #242424; margin: 0 24px;')

                with ui.element('div').style('padding: 16px 24px;'):
                    ui.label(movie_obj.titel).style(
                        'color: white; font-weight: 700; font-size: 15px; margin-bottom: 4px;'
                    )
                    with ui.row().style('justify-content: space-between; align-items: center; width: 100%;'):
                        ui.label(
                            f'{len(persons_snap)} Person(en)  ·  {hour:02d}:00 Uhr  ·  '
                            f'{"Wochenende" if is_wknd else "Wochentag"}'
                        ).style('color: #666; font-size: 12px;')
                        with ui.row().style('align-items: baseline; gap: 3px;'):
                            ui.label(f'{total:.2f}').style(
                                'color: #e50914; font-size: 20px; font-weight: 900;'
                            )
                            ui.label('CHF').style('color: #e50914; font-size: 12px; font-weight: 700;')

                with ui.row().style(
                    'background: #1a1f1a; border-radius: 8px; padding: 12px 16px; '
                    'margin: 0 24px; gap: 12px; align-items: center;'
                ):
                    ui.icon('picture_as_pdf').style('color: #4ade80; font-size: 32px; flex-shrink: 0;')
                    with ui.element('div').style('flex: 1;'):
                        ui.label('PDF-Ticket herunterladen').style(
                            'color: white; font-size: 13px; font-weight: 700;'
                        )
                        ui.label('Dein Ticket als PDF speichern.').style(
                            'color: #555; font-size: 11px;'
                        )
                    def do_download(
                        _m=movie_obj, _p=persons_snap,
                        _t=total, _h=hour, _w=is_wknd, _o=order_id
                    ):
                        _do_pdf_download(_m, _p, _t, _h, _w, _o)
                    ui.button('Download', on_click=do_download).props('no-caps unelevated').style(
                        'background: #16a34a !important; color: white; '
                        'font-weight: 700; border-radius: 6px; font-size: 12px; padding: 6px 14px;'
                    )

                with ui.row().style(
                    'background: #1f1a0a; border: 1px solid #92400e; border-radius: 8px; '
                    'padding: 10px 14px; margin: 12px 24px; gap: 8px; align-items: flex-start;'
                ):
                    ui.icon('info').style('color: #f59e0b; font-size: 16px; margin-top: 1px; flex-shrink: 0;')
                    with ui.element('div'):
                        ui.label('Demo-Modus').style(
                            'color: #f59e0b; font-size: 11px; font-weight: 700;'
                        )
                        ui.label('Setze STRIPE_SECRET_KEY in der .env für echte Zahlungen.').style(
                            'color: #92400e; font-size: 11px;'
                        )

                with ui.element('div').style('padding: 12px 24px 20px;'):
                    ui.button(
                        'Schliessen',
                        on_click=lambda: (dialog.close(), _after_purchase())
                    ).props('no-caps unelevated').style(
                        'width: 100%; background: #242424 !important; color: #aaa; '
                        'font-weight: 600; border: 1px solid #333; border-radius: 6px;'
                    )
            dialog.open()

        def _after_purchase():
            self.persons.clear()
            refresh_summary()

        # ── UI Layout (zweispaltig) ───────────────────────────────────────────
        with ui.element('div').style(
            'padding: 88px 48px 32px 48px; display: flex; gap: 24px; '
            'min-height: 100vh; align-items: flex-start;'
        ):
            # ── Linke Spalte ─────────────────────────────────────────────────
            with ui.element('div').style('flex: 1; display: flex; flex-direction: column; gap: 16px; min-width: 0;'):

                # Film-Auswahl
                with ui.element('div').classes('section-card'):
                    ui.label('FILM').style(
                        'color: #555; font-size: 10px; font-weight: 700; '
                        'letter-spacing: 2px; margin-bottom: 12px;'
                    )
                    selected_movie_id = ui.select(
                        options=movie_options,
                        value=default_id,
                    ).props('dark outlined').style('width: 100%; margin-bottom: 16px;')
                    movie_info_container = ui.element('div').style('width: 100%;')

                # Vorstellungsdetails
                with ui.element('div').classes('section-card'):
                    ui.label('VORSTELLUNG').style(
                        'color: #555; font-size: 10px; font-weight: 700; '
                        'letter-spacing: 2px; margin-bottom: 14px;'
                    )
                    with ui.row().style('gap: 16px; align-items: center; flex-wrap: wrap;'):
                        uhrzeit_input = ui.number(
                            label='Uhrzeit (0–23)', value=20, min=0, max=23
                        ).props('dark outlined').style('width: 160px;')
                        with ui.element('div').style(
                            'display: flex; align-items: center; gap: 12px; '
                            'background: #212121; border-radius: 8px; padding: 10px 16px;'
                        ):
                            with ui.element('div'):
                                ui.label('Wochenende').style(
                                    'color: white; font-size: 13px; font-weight: 600;'
                                )
                                ui.label('Sa / So  +2.00 CHF').style(
                                    'color: #555; font-size: 11px;'
                                )
                            weekend_toggle = ui.switch('').props('color=red')

                # Person hinzufügen
                with ui.element('div').classes('section-card'):
                    ui.label('PERSON HINZUFÜGEN').style(
                        'color: #555; font-size: 10px; font-weight: 700; '
                        'letter-spacing: 2px; margin-bottom: 14px;'
                    )
                    with ui.row().style('gap: 12px; align-items: flex-end; flex-wrap: wrap;'):
                        person_name = ui.input(label='Name').props('dark outlined').style(
                            'flex: 1; min-width: 140px;'
                        )
                        person_age = ui.number(
                            label='Alter', value=25, min=0, max=120
                        ).props('dark outlined').style('width: 90px;')
                        with ui.element('div').style(
                            'display: flex; flex-direction: column; align-items: center; '
                            'gap: 2px; padding-bottom: 4px;'
                        ):
                            ui.label('Student').style('color: #666; font-size: 11px;')
                            student_toggle = ui.switch('').props('color=red')
                        ui.button('Hinzufügen', on_click=add_person).props(
                            'no-caps unelevated'
                        ).style(
                            'background: #242424 !important; color: white; '
                            'font-weight: 600; border: 1px solid #333; border-radius: 6px; '
                            'font-size: 13px; padding: 8px 20px; flex-shrink: 0;'
                        )
                    add_error = ui.label('').style('color: #f87171; font-size: 11px; margin-top: 6px;')

            # ── Rechte Spalte (Zusammenfassung) ──────────────────────────────
            with ui.element('div').style(
                'flex: 0 0 340px; position: sticky; top: 88px; '
                'max-height: calc(100vh - 110px); overflow-y: auto; '
                'background: #181818; border: 1px solid #242424; '
                'border-radius: 10px; padding: 20px;'
            ):
                ui.label('ZUSAMMENFASSUNG').style(
                    'color: #555; font-size: 10px; font-weight: 700; '
                    'letter-spacing: 2px; margin-bottom: 14px;'
                )
                summary_container = ui.element('div').style('width: 100%;')

        # ── Events ────────────────────────────────────────────────────────────
        selected_movie_id.on(
            'update:model-value',
            lambda: (refresh_movie_info(), refresh_summary())
        )
        uhrzeit_input.on('update:model-value', lambda: refresh_summary())
        weekend_toggle.on('update:model-value', lambda: refresh_summary())
        ui.timer(0.05, lambda: (refresh_movie_info(), refresh_summary()), once=True)