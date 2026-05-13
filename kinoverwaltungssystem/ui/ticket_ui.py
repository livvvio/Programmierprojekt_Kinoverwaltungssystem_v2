from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.movie_model import Movie

# Ticket pricing constants (same as old CLI version)
TICKET_GRUNDGEBUEHR = 15.00
RABATT_KIND = 0.5          # ≤ 12 Jahre
RABATT_STUDENT = 0.8       # Studenten
RABATT_SENIOR = 0.7        # ≥ 65 Jahre
WOCHENEND_ZUSCHLAG = 2.00
SPAETVORSTELLUNG_RABATT = 0.9  # nach 22:00 Uhr


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
            discounts.append(f'Kinderrabatt (≤12 J.): -{(1 - RABATT_KIND) * 100:.0f}%')
        elif self.age >= 65:
            price *= RABATT_SENIOR
            discounts.append(f'Seniorenrabatt (≥65 J.): -{(1 - RABATT_SENIOR) * 100:.0f}%')

        if self.is_student:
            price *= RABATT_STUDENT
            discounts.append(f'Studentenrabatt: -{(1 - RABATT_STUDENT) * 100:.0f}%')

        if is_weekend:
            price += WOCHENEND_ZUSCHLAG
            discounts.append(f'Wochenendezuschlag: +{WOCHENEND_ZUSCHLAG:.2f} CHF')

        if is_late:
            price *= SPAETVORSTELLUNG_RABATT
            discounts.append(f'Spätvorstellung (nach 22:00): -{(1 - SPAETVORSTELLUNG_RABATT) * 100:.0f}%')

        return price, discounts


class Ticket_UI:
    def __init__(self, db: Database, preselected_movie_id: int | None = None):
        self.db = db
        self.preselected_movie_id = preselected_movie_id
        self.persons: list[TicketPerson] = []
        self.selected_movie: Movie | None = None
        self.is_weekend = False
        self.show_hour = 20

    def render(self):
        ui.query('body').style(
            'background-color: #141414; color: white; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;'
        )

        authenticated = nicegui_app.storage.user.get('authenticated', False)
        username = nicegui_app.storage.user.get('username', 'Gast')
        is_guest = nicegui_app.storage.user.get('is_guest', True)
        is_admin = nicegui_app.storage.user.get('is_admin', False)

        def logout():
            nicegui_app.storage.user.clear()
            ui.navigate.to('/')

        def go_to_login():
            ui.navigate.to('/login')

        # ── Navbar ──────────────────────────────────────────────────────────
        with ui.header().classes(
                'bg-black/80 backdrop-blur-md border-none p-4 justify-between items-center fixed top-0 w-full z-50'):
            ui.label('Kinoverwaltungssystem').classes(
                'text-red-600 text-3xl font-black tracking-tighter cursor-pointer'
            ).on('click', lambda: ui.navigate.to('/'))
            with ui.row().classes('items-center gap-6'):
                ui.link('Home', '/').classes('text-gray-300 no-underline hover:text-white')
                ui.link('Filme', '/movies').classes('text-gray-300 no-underline hover:text-white')
                ui.link('Tickets', '/tickets').classes('text-white font-bold no-underline')
                if authenticated:
                    ui.label(f'{"Gast" if is_guest else username}').classes('text-gray-300 text-sm')
                    ui.button('Abmelden', on_click=logout).props('no-caps unelevated').classes(
                        'text-white text-sm font-bold rounded px-3 py-1'
                    ).style('background-color: #e50914 !important;')
                else:
                    ui.button('Anmelden', on_click=go_to_login).props('no-caps unelevated').classes(
                        'text-white text-sm font-bold rounded px-3 py-1'
                    ).style('background-color: #e50914 !important;')

        # ── Main Content ─────────────────────────────────────────────────────
        with ui.column().classes('w-full px-6 md:px-12 pt-24 pb-12 gap-6'):
            ui.label('Ticketpreise berechnen').classes('text-3xl font-black text-white')

            with ui.row().classes('w-full gap-6 items-start flex-wrap'):

                # ── LEFT: Configuration ──────────────────────────────────────
                with ui.card().classes('rounded-xl flex-1').style(
                        'background-color: #1f1f1f; min-width: 320px; max-width: 500px;'
                ):
                    ui.label('Vorstellungsdetails').classes('text-white text-lg font-bold mb-4')

                    # Movie selector
                    movies = self.db.load_movies()
                    movie_options = {m.id: f'{m.titel} (FSK {m.altersfreigabe.value})' for m in movies}

                    default_id = (
                        self.preselected_movie_id
                        if self.preselected_movie_id and self.preselected_movie_id in movie_options
                        else (movies[0].id if movies else None)
                    )
                    selected_movie_id = ui.select(
                        options=movie_options,
                        label='Film auswählen',
                        value=default_id
                    ).props('dark outlined').classes('w-full mb-4')

                    # Show time
                    with ui.row().classes('w-full gap-4 items-center mb-4'):
                        ui.label('Vorstellungszeit:').classes('text-gray-400 text-sm w-40')
                        uhrzeit_input = ui.number(
                            label='Stunde (0-23)', value=20, min=0, max=23
                        ).props('dark outlined').classes('flex-1')

                    # Weekend toggle
                    with ui.row().classes('w-full items-center justify-between mb-6 p-3 rounded-lg').style('background-color: #2a2a2a;'):
                        with ui.column().classes('gap-0'):
                            ui.label('Wochenende').classes('text-white text-sm font-semibold')
                            ui.label('Sa / So Zuschlag +2.00 CHF').classes('text-gray-500 text-xs')
                        weekend_toggle = ui.switch('').props('color=red')

                    ui.separator().style('background-color: #333;').classes('mb-4')

                    # ── Person adder ─────────────────────────────────────────
                    ui.label('Person hinzufügen').classes('text-white text-lg font-bold mb-3')

                    person_name = ui.input(label='Name').props('dark outlined').classes('w-full mb-3')
                    with ui.row().classes('w-full gap-3 mb-3'):
                        person_age = ui.number(label='Alter', value=25, min=0, max=120).props('dark outlined').classes('flex-1')
                        with ui.column().classes('flex-1 justify-center'):
                            ui.label('Student?').classes('text-gray-400 text-xs mb-1')
                            student_toggle = ui.switch('').props('color=red')

                    persons_container = ui.column().classes('w-full gap-2 mb-4')
                    add_error = ui.label('').classes('text-red-500 text-xs')

                    def refresh_persons():
                        persons_container.clear()
                        with persons_container:
                            for i, p in enumerate(self.persons):
                                with ui.row().classes('w-full items-center justify-between p-2 rounded-lg').style('background-color: #2a2a2a;'):
                                    with ui.column().classes('gap-0'):
                                        badge = '🎓 ' if p.is_student else ''
                                        ui.label(f'{badge}{p.name}, {p.age} Jahre').classes('text-white text-sm')
                                        age_label = '👶 Kind' if p.age <= 12 else ('👴 Senior' if p.age >= 65 else '🧑 Erwachsener')
                                        ui.label(age_label).classes('text-gray-500 text-xs')
                                    ui.button(icon='close', on_click=lambda idx=i: remove_person(idx)).props(
                                        'flat round size=xs'
                                    ).classes('text-gray-500 hover:text-red-400')

                    def remove_person(idx: int):
                        self.persons.pop(idx)
                        refresh_persons()
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

                        # FSK check
                        movie_id = selected_movie_id.value
                        if movie_id:
                            movie_obj = next((m for m in movies if m.id == movie_id), None)
                            if movie_obj and age < movie_obj.altersfreigabe.value:
                                add_error.set_text(
                                    f'Zu jung für FSK {movie_obj.altersfreigabe.value}! Mindestalter: {movie_obj.altersfreigabe.value} Jahre.'
                                )
                                return

                        self.persons.append(TicketPerson(name, age, student_toggle.value))
                        person_name.value = ''
                        person_age.value = 25
                        student_toggle.value = False
                        refresh_persons()
                        refresh_summary()

                    ui.button('Person hinzufügen', on_click=add_person).props('no-caps unelevated').classes(
                        'w-full text-white font-bold rounded mb-2'
                    ).style('background-color: #333 !important; border: 1px solid #555;')

                # ── RIGHT: Summary ───────────────────────────────────────────
                summary_card = ui.card().classes('rounded-xl flex-1').style(
                    'background-color: #1f1f1f; min-width: 300px; max-width: 480px;'
                )

                def refresh_summary():
                    summary_card.clear()
                    with summary_card:
                        ui.label('Zusammenfassung').classes('text-white text-lg font-bold mb-4')

                        movie_id = selected_movie_id.value
                        movie_obj = next((m for m in movies if m.id == movie_id), None) if movie_id else None
                        is_late = int(uhrzeit_input.value or 0) >= 22
                        is_wknd = weekend_toggle.value

                        # Show details
                        if movie_obj:
                            with ui.row().classes('w-full items-center gap-3 mb-4 p-3 rounded-lg').style('background-color: #2a2a2a;'):
                                if movie_obj.imageUrl:
                                    ui.image(movie_obj.imageUrl).classes('w-12 h-16 object-cover rounded')
                                with ui.column().classes('gap-0 flex-1'):
                                    ui.label(movie_obj.titel).classes('text-white font-bold text-sm')
                                    ui.label(f'{movie_obj.genre.value} • {movie_obj.dauer} Min • FSK {movie_obj.altersfreigabe.value}').classes('text-gray-400 text-xs')

                        # Show time info
                        with ui.row().classes('w-full gap-6 mb-4'):
                            with ui.column().classes('gap-0'):
                                ui.label('Uhrzeit').classes('text-gray-500 text-xs uppercase tracking-wide')
                                ui.label(f'{int(uhrzeit_input.value or 0):02d}:00 Uhr').classes('text-white text-sm font-semibold')
                                if is_late:
                                    ui.label('🌙 Spätvorstellung').classes('text-purple-400 text-xs')
                            with ui.column().classes('gap-0'):
                                ui.label('Tag').classes('text-gray-500 text-xs uppercase tracking-wide')
                                ui.label('Wochenende' if is_wknd else 'Wochentag').classes('text-white text-sm font-semibold')

                        if not self.persons:
                            ui.label('Noch keine Personen hinzugefügt.').classes('text-gray-500 text-sm text-center mt-4')
                        else:
                            ui.separator().style('background-color: #333;').classes('mb-3')
                            total = 0.0
                            for person in self.persons:
                                price, disc = person.calculate_price(is_late, is_wknd)
                                total += price
                                with ui.column().classes('w-full mb-3 p-3 rounded-lg').style('background-color: #2a2a2a;'):
                                    with ui.row().classes('w-full justify-between items-start'):
                                        ui.label(person.name).classes('text-white font-semibold text-sm')
                                        ui.label(f'{price:.2f} CHF').classes('text-white font-bold text-sm')
                                    for d in disc:
                                        ui.label(f'↳ {d}').classes('text-gray-500 text-xs mt-1')
                                    if not disc:
                                        ui.label(f'↳ Grundpreis: {TICKET_GRUNDGEBUEHR:.2f} CHF').classes('text-gray-500 text-xs mt-1')

                            ui.separator().style('background-color: #444;').classes('my-3')
                            with ui.row().classes('w-full justify-between items-center'):
                                with ui.column().classes('gap-0'):
                                    ui.label('Gesamtbetrag').classes('text-white font-black text-lg')
                                    ui.label(f'{len(self.persons)} Person(en)').classes('text-gray-500 text-xs')
                                with ui.row().classes('items-baseline gap-1'):
                                    ui.label(f'{total:.2f}').classes('text-red-500 font-black text-3xl')
                                    ui.label('CHF').classes('text-red-500 font-bold text-lg')

                            # Preisübersicht Legende
                            ui.separator().style('background-color: #333;').classes('my-3')
                            ui.label('Preistabelle').classes('text-gray-500 text-xs uppercase tracking-wide mb-2')
                            legend_items = [
                                ('👶 Kind (≤12 J.)', f'{TICKET_GRUNDGEBUEHR * RABATT_KIND:.2f} CHF'),
                                ('🧑 Erwachsener', f'{TICKET_GRUNDGEBUEHR:.2f} CHF'),
                                ('👴 Senior (≥65 J.)', f'{TICKET_GRUNDGEBUEHR * RABATT_SENIOR:.2f} CHF'),
                                ('🎓 Student (-20%)', 'auf Basispreis'),
                                ('📅 Wochenende', f'+{WOCHENEND_ZUSCHLAG:.2f} CHF'),
                                ('🌙 Spätvorstellung (≥22h)', '-10%'),
                            ]
                            for label_text, value_text in legend_items:
                                with ui.row().classes('w-full justify-between'):
                                    ui.label(label_text).classes('text-gray-400 text-xs')
                                    ui.label(value_text).classes('text-gray-400 text-xs')

                # Trigger on changes
                selected_movie_id.on('update:model-value', lambda: refresh_summary())
                uhrzeit_input.on('update:model-value', lambda: refresh_summary())
                weekend_toggle.on('update:model-value', lambda: refresh_summary())

                # Initial render
                ui.timer(0.05, lambda: refresh_summary(), once=True)
