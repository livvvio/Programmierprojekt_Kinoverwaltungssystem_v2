from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.constants import Genre, Altersfreigabe, CURRENT_YEAR


class Movie_UI:
    def __init__(self, db: Database):
        self.db = db

    def render(self):
        ui.query('body').style(
            'background-color: #141414; color: white; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;'
        )

        is_admin = nicegui_app.storage.user.get('is_admin', False)
        authenticated = nicegui_app.storage.user.get('authenticated', False)
        username = nicegui_app.storage.user.get('username', 'Gast')
        is_guest = nicegui_app.storage.user.get('is_guest', True)

        def logout():
            nicegui_app.storage.user.clear()
            ui.navigate.to('/')

        def go_to_login():
            ui.navigate.to('/login')

        # ── Navbar ──────────────────────────────────────────────────────────
        with ui.header().classes(
                'bg-black/80 backdrop-blur-md border-none p-4 justify-between items-center fixed top-0 w-full z-50'):
            ui.label('Kinoverwaltungssystem').classes('text-red-600 text-3xl font-black tracking-tighter cursor-pointer').on('click', lambda: ui.navigate.to('/'))
            with ui.row().classes('items-center gap-6'):
                ui.link('Home', '/').classes('text-gray-300 no-underline hover:text-white')
                ui.link('Filme', '/movies').classes('text-white font-bold no-underline')
                if is_admin:
                    ui.link('Tickets', '/tickets').classes('text-gray-300 no-underline hover:text-white')
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
        with ui.column().classes('w-full px-12 pt-24 pb-12'):

            with ui.row().classes('w-full items-center justify-between mb-6'):
                ui.label('Filmverwaltung').classes('text-3xl font-black text-white')
                if is_admin:
                    ui.button('+ Film hinzufügen', on_click=lambda: self._open_movie_dialog(None)).props(
                        'no-caps unelevated'
                    ).classes('text-white font-bold rounded px-4 py-2').style('background-color: #e50914 !important;')

            # Search bar
            search_input = ui.input(placeholder='🔍  Film suchen...').props('dark outlined').classes('w-full mb-6').style(
                'max-width: 500px;'
            )

            # Movie table container
            table_container = ui.column().classes('w-full')

            def refresh_table(search: str = ''):
                table_container.clear()
                movies = self.db.load_movies()
                if search:
                    movies = [m for m in movies if search.lower() in m.titel.lower()
                              or search.lower() in m.genre.value.lower()
                              or search.lower() in (m.regisseur or '').lower()]

                with table_container:
                    if not movies:
                        ui.label('Keine Filme gefunden.').classes('text-gray-400 text-center mt-8 w-full')
                        return

                    # Header row
                    with ui.row().classes('w-full items-center gap-2 px-4 py-2 text-gray-400 text-xs font-bold uppercase tracking-wider').style('border-bottom: 1px solid #333;'):
                        ui.label('Poster').classes('w-12')
                        ui.label('Titel').classes('flex-1 min-w-0')
                        ui.label('Genre').classes('w-28 hidden sm:block')
                        ui.label('Jahr').classes('w-16 text-center hidden sm:block')
                        ui.label('Dauer').classes('w-20 text-center hidden md:block')
                        ui.label('FSK').classes('w-14 text-center hidden md:block')
                        ui.label('Rating').classes('w-16 text-center hidden lg:block')
                        if is_admin:
                            ui.label('Aktionen').classes('w-28 text-center')

                    for movie in movies:
                        self._render_movie_row(movie, table_container, refresh_table, is_admin)

            search_input.on('input', lambda e: refresh_table(e.args if isinstance(e.args, str) else search_input.value))
            search_input.on('keyup', lambda: refresh_table(search_input.value))

            # Trigger initial load
            ui.timer(0.05, lambda: refresh_table(), once=True)

    def _render_movie_row(self, movie: Movie, container, refresh_fn, is_admin: bool):
        with ui.row().classes('w-full items-center gap-2 px-4 py-3 rounded-lg hover:bg-white/5 transition-colors').style('border-bottom: 1px solid #222;'):
            # Poster thumbnail
            if movie.imageUrl:
                ui.image(movie.imageUrl).classes('w-12 h-16 object-cover rounded shadow-md').style('flex-shrink: 0;')
            else:
                with ui.element('div').classes('w-12 h-16 rounded flex items-center justify-center').style('background-color: #333; flex-shrink: 0;'):
                    ui.icon('movie').classes('text-gray-500 text-2xl')

            # Title + description
            with ui.column().classes('flex-1 min-w-0'):
                ui.label(movie.titel).classes('text-white font-bold text-sm truncate')
                if movie.beschreibung:
                    ui.label(movie.beschreibung[:80] + ('...' if len(movie.beschreibung or '') > 80 else '')).classes('text-gray-500 text-xs truncate hidden sm:block')

            ui.label(movie.genre.value).classes('w-28 text-green-500 text-xs font-semibold hidden sm:block')
            ui.label(str(movie.erscheinungsjahr)).classes('w-16 text-gray-400 text-xs text-center hidden sm:block')
            ui.label(f'{movie.dauer} Min').classes('w-20 text-gray-400 text-xs text-center hidden md:block')

            fsk_colors = {0: 'bg-green-600', 6: 'bg-yellow-500', 12: 'bg-orange-500', 16: 'bg-red-600', 18: 'bg-red-800'}
            fsk_val = movie.altersfreigabe.value
            fsk_color = fsk_colors.get(fsk_val, 'bg-gray-600')
            with ui.element('div').classes(f'w-14 flex justify-center hidden md:flex'):
                ui.label(f'FSK {fsk_val}').classes(f'text-white text-[10px] font-bold px-2 py-0.5 rounded {fsk_color}')

            # Rating stars
            with ui.element('div').classes('w-16 text-center hidden lg:flex items-center justify-center gap-1'):
                ui.icon('star').classes('text-yellow-400 text-sm')
                ui.label(f'{movie.bewertung:.1f}').classes('text-gray-300 text-xs')

            if is_admin:
                with ui.row().classes('w-28 gap-1 justify-center'):
                    ui.button(icon='edit', on_click=lambda m=movie: self._open_movie_dialog(m)).props(
                        'flat round size=sm'
                    ).classes('text-blue-400 hover:text-blue-300')
                    ui.button(icon='delete', on_click=lambda m=movie: self._confirm_delete(m, refresh_fn)).props(
                        'flat round size=sm'
                    ).classes('text-red-500 hover:text-red-400')

    def _confirm_delete(self, movie: Movie, refresh_fn):
        with ui.dialog() as dialog, ui.card().classes('rounded-xl').style('background-color: #1f1f1f; min-width: 360px;'):
            ui.label('Film löschen').classes('text-white text-xl font-bold mb-2')
            ui.label(f'Soll "{movie.titel}" wirklich gelöscht werden?').classes('text-gray-300 mb-6')
            with ui.row().classes('w-full gap-3 justify-end'):
                ui.button('Abbrechen', on_click=dialog.close).props('flat no-caps').classes('text-gray-300')

                def do_delete():
                    self.db.delete_movie_by_id(movie.id)
                    dialog.close()
                    ui.notify(f'"{movie.titel}" wurde gelöscht.', color='positive')
                    refresh_fn()

                ui.button('Löschen', on_click=do_delete).props('no-caps unelevated').classes(
                    'text-white font-bold rounded px-4'
                ).style('background-color: #e50914 !important;')
        dialog.open()

    def _open_movie_dialog(self, movie: Movie | None):
        """Opens create/edit dialog. Pass None for new movie."""
        is_edit = movie is not None
        title_text = 'Film bearbeiten' if is_edit else 'Film hinzufügen'

        with ui.dialog() as dialog, ui.card().classes('rounded-xl w-full').style(
                'background-color: #1f1f1f; max-width: 640px; max-height: 90vh; overflow-y: auto;'
        ):
            ui.label(title_text).classes('text-white text-2xl font-bold mb-4')

            # Form fields
            titel_input = ui.input(
                label='Titel *', value=movie.titel if is_edit else ''
            ).props('dark outlined').classes('w-full mb-3')

            genre_options = [g.value for g in Genre]
            genre_select = ui.select(
                options=genre_options,
                label='Genre *',
                value=movie.genre.value if is_edit else genre_options[0]
            ).props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                dauer_input = ui.number(
                    label='Dauer (Min) *', value=movie.dauer if is_edit else 90,
                    min=1, max=600
                ).props('dark outlined').classes('flex-1')

                jahr_input = ui.number(
                    label='Erscheinungsjahr *', value=movie.erscheinungsjahr if is_edit else CURRENT_YEAR,
                    min=1900, max=CURRENT_YEAR + 2
                ).props('dark outlined').classes('flex-1')

            fsk_options = [str(a.value) for a in Altersfreigabe]
            fsk_select = ui.select(
                options=fsk_options,
                label='Altersfreigabe (FSK) *',
                value=str(movie.altersfreigabe.value) if is_edit else '0'
            ).props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                regisseur_input = ui.input(
                    label='Regisseur', value=movie.regisseur or '' if is_edit else ''
                ).props('dark outlined').classes('flex-1')

                produktionsfirma_input = ui.input(
                    label='Produktionsfirma', value=movie.produktionsfirma or '' if is_edit else ''
                ).props('dark outlined').classes('flex-1')

            beschreibung_input = ui.textarea(
                label='Beschreibung', value=movie.beschreibung or '' if is_edit else ''
            ).props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                bewertung_input = ui.number(
                    label='Bewertung (0-10)', value=movie.bewertung if is_edit else 0.0,
                    min=0.0, max=10.0, step=0.1, format='%.1f'
                ).props('dark outlined').classes('flex-1')

                imageurl_input = ui.input(
                    label='Bild-URL', value=movie.imageUrl or '' if is_edit else ''
                ).props('dark outlined').classes('flex-1')

            error_label = ui.label('').classes('text-red-500 text-sm mb-2')

            def save():
                # Validation
                if not titel_input.value.strip():
                    error_label.set_text('Bitte Titel eingeben.')
                    return
                try:
                    new_dauer = int(dauer_input.value)
                    new_jahr = int(jahr_input.value)
                    new_bewertung = float(bewertung_input.value)
                except (TypeError, ValueError):
                    error_label.set_text('Ungültige numerische Eingabe.')
                    return

                genre_enum = Genre(genre_select.value)
                fsk_enum = Altersfreigabe(int(fsk_select.value))

                if is_edit:
                    movie.titel = titel_input.value.strip()
                    movie.genre = genre_enum
                    movie.dauer = new_dauer
                    movie.erscheinungsjahr = new_jahr
                    movie.altersfreigabe = fsk_enum
                    movie.regisseur = regisseur_input.value.strip() or None
                    movie.produktionsfirma = produktionsfirma_input.value.strip() or None
                    movie.beschreibung = beschreibung_input.value.strip() or None
                    movie.bewertung = new_bewertung
                    movie.imageUrl = imageurl_input.value.strip()
                    self.db._session.add(movie)
                    self.db._session.commit()
                    ui.notify(f'"{movie.titel}" wurde aktualisiert.', color='positive')
                else:
                    new_movie = Movie(
                        titel=titel_input.value.strip(),
                        genre=genre_enum,
                        dauer=new_dauer,
                        erscheinungsjahr=new_jahr,
                        altersfreigabe=fsk_enum,
                        regisseur=regisseur_input.value.strip() or None,
                        produktionsfirma=produktionsfirma_input.value.strip() or None,
                        beschreibung=beschreibung_input.value.strip() or None,
                        bewertung=new_bewertung,
                        imageUrl=imageurl_input.value.strip(),
                    )
                    self.db.save_movie(new_movie)
                    ui.notify(f'"{new_movie.titel}" wurde hinzugefügt.', color='positive')

                dialog.close()
                ui.navigate.to('/movies')

            with ui.row().classes('w-full gap-3 justify-end mt-2'):
                ui.button('Abbrechen', on_click=dialog.close).props('flat no-caps').classes('text-gray-300')
                ui.button('Speichern', on_click=save).props('no-caps unelevated').classes(
                    'text-white font-bold rounded px-6'
                ).style('background-color: #e50914 !important;')

        dialog.open()
