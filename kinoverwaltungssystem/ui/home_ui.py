from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.constants import Genre, Altersfreigabe, CURRENT_YEAR



class Home_UI:
    def __init__(self, movies: list[Movie], db=None):
        self.movies = movies
        self.db = db

    def render(self):
        ui.query('body').style(
            'background-color: #141414; color: white; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;')

        authenticated = nicegui_app.storage.user.get('authenticated', False)
        username = nicegui_app.storage.user.get('username', 'Gast')
        is_guest = nicegui_app.storage.user.get('is_guest', True)
        is_admin = nicegui_app.storage.user.get('is_admin', False)


        # ── Main Content ─────────────────────────────────────────────────────
        with ui.column().classes('w-full px-10 pt-8 pb-16'):

            if authenticated and not is_guest:
                ui.label(f'Willkommen zurück, {username}!').classes('text-2xl font-bold mb-2 text-white')

            if not self.movies:
                with ui.column().classes('items-center w-full mt-24 gap-4'):
                    ui.icon('movie').classes('text-gray-600 text-8xl')
                    ui.label('Noch keine Filme vorhanden.').classes('text-gray-500 text-xl')
                    if is_admin:
                        ui.button('Ersten Film hinzufügen',
                                  on_click=lambda: ui.navigate.to('/movies')).props('no-caps unelevated').classes(
                            'text-white font-bold rounded px-6 py-2'
                        ).style('background-color: #e50914 !important;')
                return

            with ui.row().classes('items-center justify-between mb-6 mt-4'):
                ui.label('Alle Filme').classes('text-2xl font-black text-white')
                with ui.row().classes('items-center gap-4'):
                    ui.label(f'{len(self.movies)} Titel').classes('text-gray-500 text-sm')
                    if is_admin:
                        ui.button('+ Film hinzufügen', on_click=lambda: self._open_add_dialog()).props(
                            'no-caps unelevated'
                        ).classes('text-white font-bold rounded px-4 py-2').style('background-color: #e50914 !important;')

            grid = ui.element('div').style(
                'display: grid;'
                'grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));'
                'gap: 20px; width: 100%;'
            )

            def refresh_grid():
                grid.clear()
                movies = self.db.load_movies() if self.db else self.movies
                with grid:
                    for movie in movies:
                        self._render_card(movie, is_admin=is_admin, refresh_fn=refresh_grid)

            with grid:
                for movie in self.movies:
                    self._render_card(movie, is_admin=is_admin, refresh_fn=refresh_grid)

    def _render_card(self, movie: Movie, is_admin: bool = False, refresh_fn=None):
        with ui.element('div').classes(
            'relative overflow-hidden rounded-xl cursor-pointer group bg-gray-900'
            ' transition-all duration-300'
            ' hover:scale-105 hover:-translate-y-1 hover:z-10'
            ' hover:shadow-2xl hover:ring-2 hover:ring-red-600'
        ).on('click', lambda m=movie: ui.navigate.to(f'/tickets?movie_id={m.id}')):

            # Poster
            if movie.imageUrl:
                ui.image(movie.imageUrl).classes('w-full aspect-[2/3] object-cover block')
            else:
                with ui.element('div').classes(
                    'w-full aspect-[2/3] flex items-center justify-center bg-gray-800'
                ):
                    ui.icon('movie').classes('text-gray-600 text-6xl')

            # Hover overlay
            with ui.element('div').classes(
                'absolute inset-0 flex flex-col justify-end p-3 gap-1'
                ' opacity-0 group-hover:opacity-100 transition-opacity duration-300'
            ).style('background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.4) 50%, transparent 100%);'):
                if is_admin:
                    with ui.element('div').classes('absolute top-2 right-2').on('click.stop', lambda: None):
                        ui.button(icon='delete', on_click=lambda m=movie: self._confirm_delete(m, refresh_fn)).props(
                            'flat round size=sm'
                        ).classes('text-white').style('background-color: rgba(229,9,20,0.85) !important;')
                ui.label(movie.titel).classes('text-white font-extrabold text-sm leading-tight')
                with ui.row().classes('gap-2 items-center'):
                    ui.label(movie.genre.value).classes('text-green-500 text-xs font-semibold')
                    ui.label(str(movie.erscheinungsjahr)).classes('text-gray-400 text-xs')
                    ui.label(f'{movie.dauer} Min').classes('text-gray-400 text-xs')
                ui.label(f'★ {movie.bewertung:.1f}  ·  FSK {movie.altersfreigabe.value}').classes(
                    'text-yellow-400 text-xs font-bold')

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
                    if refresh_fn:
                        refresh_fn()

                ui.button('Löschen', on_click=do_delete).props('no-caps unelevated').classes(
                    'text-white font-bold rounded px-4'
                ).style('background-color: #e50914 !important;')
        dialog.open()

    def _open_add_dialog(self):
        with ui.dialog() as dialog, ui.card().classes('rounded-xl w-full').style(
            'background-color: #1f1f1f; max-width: 640px; max-height: 90vh; overflow-y: auto;'
        ):
            ui.label('Film hinzufügen').classes('text-white text-2xl font-bold mb-4')

            titel_input = ui.input(label='Titel *').props('dark outlined').classes('w-full mb-3')
            genre_options = [g.value for g in Genre]
            genre_select = ui.select(options=genre_options, label='Genre *', value=genre_options[0]).props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                dauer_input = ui.number(label='Dauer (Min) *', value=90, min=1, max=600).props('dark outlined').classes('flex-1')
                jahr_input = ui.number(label='Erscheinungsjahr *', value=CURRENT_YEAR, min=1900, max=CURRENT_YEAR + 2).props('dark outlined').classes('flex-1')

            fsk_options = [str(a.value) for a in Altersfreigabe]
            fsk_select = ui.select(options=fsk_options, label='Altersfreigabe (FSK) *', value='0').props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                regisseur_input = ui.input(label='Regisseur').props('dark outlined').classes('flex-1')
                produktionsfirma_input = ui.input(label='Produktionsfirma').props('dark outlined').classes('flex-1')

            beschreibung_input = ui.textarea(label='Beschreibung').props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                bewertung_input = ui.number(label='Bewertung (0-10)', value=0.0, min=0.0, max=10.0, step=0.1, format='%.1f').props('dark outlined').classes('flex-1')
                imageurl_input = ui.input(label='Bild-URL').props('dark outlined').classes('flex-1')

            error_label = ui.label('').classes('text-red-500 text-sm mb-2')

            def save():
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

                new_movie = Movie(
                    titel=titel_input.value.strip(),
                    genre=Genre(genre_select.value),
                    dauer=new_dauer,
                    erscheinungsjahr=new_jahr,
                    altersfreigabe=Altersfreigabe(int(fsk_select.value)),
                    regisseur=regisseur_input.value.strip() or None,
                    produktionsfirma=produktionsfirma_input.value.strip() or None,
                    beschreibung=beschreibung_input.value.strip() or None,
                    bewertung=new_bewertung,
                    imageUrl=imageurl_input.value.strip(),
                )
                self.db.save_movie(new_movie)
                ui.notify(f'"{new_movie.titel}" wurde hinzugefügt.', color='positive')
                dialog.close()
                ui.navigate.to('/')

            with ui.row().classes('w-full gap-3 justify-end mt-2'):
                ui.button('Abbrechen', on_click=dialog.close).props('flat no-caps').classes('text-gray-300')
                ui.button('Speichern', on_click=save).props('no-caps unelevated').classes(
                    'text-white font-bold rounded px-6'
                ).style('background-color: #e50914 !important;')

        dialog.open()