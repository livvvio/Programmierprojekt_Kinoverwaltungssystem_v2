"""
movie_ui.py  –  Filmverwaltung mit Filter, Sortierung und OMDb-Import (nur Admin)
"""
from __future__ import annotations
import os
from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.constants import Genre, Altersfreigabe, CURRENT_YEAR
from kinoverwaltungssystem.ui.navbar import Navbar


class Movie_UI:
    def __init__(self, db: Database):
        self.db = db

    def render(self):
        ui.query('body').style(
            'background-color:#141414; color:white; font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;'
        )
        is_admin = nicegui_app.storage.user.get('is_admin', False)
        Navbar('movies').render()

        with ui.column().classes('w-full px-6 md:px-12 pt-8 pb-12 gap-4'):

            # ── Header ────────────────────────────────────────────────────────
            with ui.row().classes('w-full items-center justify-between'):
                ui.label('Filmverwaltung').classes('text-3xl font-black text-white')
                if is_admin:
                    with ui.row().classes('gap-3'):
                        ui.button(
                            '🔍 Film via OMDb importieren',
                            on_click=lambda: self._open_omdb_dialog()
                        ).props('no-caps unelevated').classes(
                            'text-white font-bold rounded px-4 py-2'
                        ).style('background-color:#333 !important; border:1px solid #555;')
                        ui.button(
                            '+ Film manuell hinzufügen',
                            on_click=lambda: self._open_movie_dialog(None)
                        ).props('no-caps unelevated').classes(
                            'text-white font-bold rounded px-4 py-2'
                        ).style('background-color:#e50914 !important;')

            # ── Filter / Sortier-Toolbar ──────────────────────────────────────
            with ui.row().classes('w-full items-end gap-4 flex-wrap'):
                search_input = ui.input(
                    placeholder='🔍  Titel, Genre, Regisseur...'
                ).props('dark outlined').style('min-width:220px; max-width:400px;')

                genre_options = ['Alle Genres'] + [g.value for g in Genre]
                genre_filter = ui.select(
                    options=genre_options, value='Alle Genres', label='Genre'
                ).props('dark outlined').style('min-width:160px;')

                fsk_options = ['Alle FSK'] + [str(a.value) for a in Altersfreigabe]
                fsk_filter = ui.select(
                    options=fsk_options, value='Alle FSK', label='FSK'
                ).props('dark outlined').style('min-width:130px;')

                sort_options = {
                    'titel_asc':   'Titel A–Z',
                    'titel_desc':  'Titel Z–A',
                    'jahr_desc':   'Neueste zuerst',
                    'jahr_asc':    'Älteste zuerst',
                    'rating_desc': 'Beste Bewertung',
                    'dauer_asc':   'Kürzeste zuerst',
                    'dauer_desc':  'Längste zuerst',
                }
                sort_select = ui.select(
                    options=sort_options, value='titel_asc', label='Sortierung'
                ).props('dark outlined').style('min-width:180px;')

            result_label = ui.label('').classes('text-gray-500 text-sm')
            table_container = ui.column().classes('w-full')

            def refresh_table():
                movies = self.db.load_movies()

                q = search_input.value.strip().lower()
                if q:
                    movies = [m for m in movies if
                              q in m.titel.lower()
                              or q in m.genre.value.lower()
                              or q in (m.regisseur or '').lower()
                              or q in (m.beschreibung or '').lower()]

                gf = genre_filter.value
                if gf and gf != 'Alle Genres':
                    movies = [m for m in movies if m.genre.value == gf]

                ff = fsk_filter.value
                if ff and ff != 'Alle FSK':
                    movies = [m for m in movies if str(m.altersfreigabe.value) == ff]

                sort_key = sort_select.value or 'titel_asc'
                sort_map = {
                    'titel_asc':   lambda m: m.titel.lower(),
                    'titel_desc':  lambda m: m.titel.lower(),
                    'jahr_desc':   lambda m: -m.erscheinungsjahr,
                    'jahr_asc':    lambda m: m.erscheinungsjahr,
                    'rating_desc': lambda m: -m.bewertung,
                    'dauer_asc':   lambda m: m.dauer,
                    'dauer_desc':  lambda m: -m.dauer,
                }
                movies.sort(
                    key=sort_map.get(sort_key, lambda m: m.titel.lower()),
                    reverse=(sort_key == 'titel_desc')
                )

                result_label.set_text(f'{len(movies)} Film(e) gefunden')
                table_container.clear()

                with table_container:
                    if not movies:
                        with ui.column().classes('w-full items-center py-16 gap-3'):
                            ui.icon('search_off').classes('text-gray-600 text-6xl')
                            ui.label('Keine Filme gefunden.').classes('text-gray-400 text-lg')
                        return

                    with ui.row().classes(
                        'w-full items-center gap-2 px-4 py-2 text-gray-400 text-xs '
                        'font-bold uppercase tracking-wider'
                    ).style('border-bottom:1px solid #333;'):
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
                        self._render_movie_row(movie, refresh_table, is_admin)

            search_input.on('input', lambda: refresh_table())
            search_input.on('keyup', lambda: refresh_table())
            genre_filter.on('update:model-value', lambda: refresh_table())
            fsk_filter.on('update:model-value', lambda: refresh_table())
            sort_select.on('update:model-value', lambda: refresh_table())
            ui.timer(0.05, refresh_table, once=True)

    # ── OMDb Import Dialog (nur Admin) ────────────────────────────────────────
    def _open_omdb_dialog(self):
        with ui.dialog() as dialog, ui.card().classes('rounded-xl w-full').style(
            'background-color:#1f1f1f; max-width:620px;'
        ):
            ui.label('Film via OMDb importieren').classes('text-white text-2xl font-bold mb-1')
            ui.label('Suche nach einem Filmtitel und importiere ihn direkt in die Datenbank.').classes(
                'text-gray-400 text-sm mb-4'
            )

            omdb_key = os.environ.get('OMDB_API_KEY', '')
            if not omdb_key:
                with ui.row().classes('w-full items-start gap-2 p-3 rounded-lg mb-4').style(
                    'background-color:#2a1a0a; border:1px solid #f59e0b;'
                ):
                    ui.icon('warning').classes('text-yellow-500 text-base mt-0.5')
                    with ui.column().classes('gap-0'):
                        ui.label('OMDB_API_KEY nicht gesetzt').classes('text-yellow-400 text-sm font-bold')
                        ui.label(
                            'Trage OMDB_API_KEY=deinkeyhere in der .env Datei ein. '
                            'Kostenloser Key: omdbapi.com/apikey.aspx'
                        ).classes('text-yellow-600 text-xs')

            with ui.row().classes('w-full gap-3 items-end mb-4'):
                omdb_input = ui.input(
                    label='Filmtitel', placeholder='z.B. Inception, The Dark Knight...'
                ).props('dark outlined').classes('flex-1')
                search_btn = ui.button('Suchen').props('no-caps unelevated').classes(
                    'text-white font-bold rounded px-4'
                ).style('background-color:#e50914 !important; height:44px;')

            result_container = ui.column().classes('w-full gap-3')
            error_label = ui.label('').classes('text-red-500 text-sm')

            async def do_search():
                title = omdb_input.value.strip()
                if not title:
                    error_label.set_text('Bitte einen Filmtitel eingeben.')
                    return
                key = os.environ.get('OMDB_API_KEY', '')
                if not key:
                    error_label.set_text('OMDB_API_KEY fehlt in der .env Datei.')
                    return
                error_label.set_text('')
                result_container.clear()
                with result_container:
                    ui.spinner(size='md').classes('text-red-500')
                try:
                    import httpx
                    resp = httpx.get(
                        'http://www.omdbapi.com/',
                        params={'t': title, 'apikey': key, 'plot': 'short'},
                        timeout=6.0
                    )
                    data = resp.json()
                except Exception as e:
                    result_container.clear()
                    error_label.set_text(f'Netzwerkfehler: {e}')
                    return

                result_container.clear()
                if data.get('Response') != 'True':
                    error_label.set_text(f'OMDb: {data.get("Error", "Kein Ergebnis gefunden.")}')
                    return

                self._render_omdb_result(data, result_container, dialog)

            search_btn.on('click', do_search)
            omdb_input.on('keydown.enter', do_search)

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Schliessen', on_click=dialog.close).props('flat no-caps').classes('text-gray-300')

        dialog.open()

    def _render_omdb_result(self, data: dict, container, parent_dialog):
        """Zeigt das OMDb-Ergebnis mit Import-Möglichkeit."""
        with container:
            with ui.card().classes('w-full rounded-xl').style('background-color:#2a2a2a;'):
                with ui.row().classes('gap-4 items-start p-4'):
                    poster = data.get('Poster', '')
                    if poster and poster != 'N/A':
                        ui.image(poster).classes('rounded-lg shadow-lg').style(
                            'width:100px; height:150px; object-fit:cover; flex-shrink:0;'
                        )
                    else:
                        with ui.element('div').classes('rounded-lg flex items-center justify-center').style(
                            'width:100px; height:150px; background:#333; flex-shrink:0;'
                        ):
                            ui.icon('movie').classes('text-gray-500 text-4xl')

                    with ui.column().classes('flex-1 gap-1 min-w-0'):
                        ui.label(data.get('Title', '')).classes('text-white font-black text-xl leading-tight')
                        with ui.row().classes('gap-2 flex-wrap items-center'):
                            ui.label(data.get('Year', '')).classes('text-gray-400 text-sm')
                            ui.label('·').classes('text-gray-600')
                            ui.label(data.get('Runtime', '')).classes('text-gray-400 text-sm')
                            ui.label('·').classes('text-gray-600')
                            ui.label(data.get('Rated', '')).classes('text-gray-400 text-sm')
                        ui.label(f'Genre: {data.get("Genre", "")}').classes('text-green-500 text-sm font-semibold')
                        ui.label(f'Regie: {data.get("Director", "")}').classes('text-gray-400 text-sm')
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('star').classes('text-yellow-400 text-sm')
                            ui.label(f'IMDb: {data.get("imdbRating","N/A")}').classes('text-yellow-400 text-sm font-bold')
                        if data.get('Plot') and data.get('Plot') != 'N/A':
                            ui.label(data['Plot']).classes('text-gray-300 text-xs mt-1').style('line-height:1.5;')

                ui.separator().style('background-color:#333;').classes('mx-4')

                mapped = self._map_omdb_to_movie(data)
                with ui.row().classes('gap-4 flex-wrap px-4 py-3'):
                    ui.label('Wird importiert als:').classes('text-gray-500 text-xs w-full mb-1')
                    for lbl, val in [
                        ('Genre', mapped['genre'].value),
                        ('FSK', f'FSK {mapped["altersfreigabe"].value}'),
                        ('Jahr', str(mapped['erscheinungsjahr'])),
                        ('Dauer', f'{mapped["dauer"]} Min'),
                        ('Bewertung', f'★ {mapped["bewertung"]:.1f}'),
                    ]:
                        with ui.element('div').classes('px-3 py-1 rounded-lg').style('background-color:#333;'):
                            ui.label(f'{lbl}: {val}').classes('text-gray-300 text-xs font-semibold')

                with ui.row().classes('w-full justify-end gap-3 px-4 pb-4'):
                    status_label = ui.label('').classes('text-green-500 text-sm flex-1 self-center')

                    def do_import():
                        from kinoverwaltungssystem.model.movie_model import Movie
                        m = self._map_omdb_to_movie(data)
                        new_movie = Movie(
                            titel=data.get('Title', 'Unbekannt'),
                            genre=m['genre'],
                            dauer=m['dauer'],
                            erscheinungsjahr=m['erscheinungsjahr'],
                            altersfreigabe=m['altersfreigabe'],
                            regisseur=data.get('Director') or None,
                            produktionsfirma=data.get('Production') or None,
                            beschreibung=data.get('Plot') if data.get('Plot') != 'N/A' else None,
                            bewertung=m['bewertung'],
                            imageUrl=data.get('Poster', '') if data.get('Poster', '') != 'N/A' else '',
                        )
                        self.db.save_movie(new_movie)
                        status_label.set_text(f'✅ "{new_movie.titel}" wurde importiert!')
                        import_btn.props('disable')
                        ui.notify(f'"{new_movie.titel}" erfolgreich importiert!', color='positive')

                    import_btn = ui.button(
                        '⬇ In Datenbank importieren', on_click=do_import
                    ).props('no-caps unelevated').classes(
                        'text-white font-bold rounded px-4'
                    ).style('background-color:#e50914 !important;')

    @staticmethod
    def _map_omdb_to_movie(data: dict) -> dict:
        """Mappt OMDb-Felder auf interne Modell-Werte."""
        from kinoverwaltungssystem.constants import Genre, Altersfreigabe

        try:
            bewertung = float(data.get('imdbRating', 0))
        except (ValueError, TypeError):
            bewertung = 0.0

        try:
            jahr = int(str(data.get('Year', '2000'))[:4])
        except (ValueError, TypeError):
            jahr = 2000

        runtime_str = data.get('Runtime', '90 min').replace(' min', '').strip()
        try:
            dauer = int(runtime_str)
        except (ValueError, TypeError):
            dauer = 90

        genre_str = data.get('Genre', '').split(',')[0].strip().lower()
        genre_map = {
            'action': Genre.ACTION,
            'adventure': Genre.ABENTEUER,
            'thriller': Genre.THRILLER,
            'documentary': Genre.DOKU,
            'drama': Genre.DRAMA,
            'fantasy': Genre.FANTASY,
            'horror': Genre.HORROR,
            'comedy': Genre.KOMÖDIE,
            'crime': Genre.KRIMI,
            'romance': Genre.ROMANTIK,
            'sci-fi': Genre.SCIENCE_FICTION,
            'science fiction': Genre.SCIENCE_FICTION,
            'western': Genre.WESTERN,
            'animation': Genre.SONSTIGE,
            'biography': Genre.DRAMA,
            'history': Genre.DOKU,
            'music': Genre.SONSTIGE,
            'sport': Genre.SONSTIGE,
            'war': Genre.ACTION,
        }
        genre = genre_map.get(genre_str, Genre.SONSTIGE)

        rated = data.get('Rated', 'NR').upper()
        rated_map = {
            'G': Altersfreigabe.FSK0,
            'PG': Altersfreigabe.FSK6,
            'PG-13': Altersfreigabe.FSK12,
            'R': Altersfreigabe.FSK16,
            'NC-17': Altersfreigabe.FSK18,
        }
        altersfreigabe = rated_map.get(rated, Altersfreigabe.FSK0)

        return {
            'genre': genre,
            'altersfreigabe': altersfreigabe,
            'erscheinungsjahr': jahr,
            'dauer': dauer,
            'bewertung': bewertung,
        }

    # ── Film-Tabelle ──────────────────────────────────────────────────────────
    def _render_movie_row(self, movie: Movie, refresh_fn, is_admin: bool):
        with ui.row().classes(
            'w-full items-center gap-2 px-4 py-3 rounded-lg hover:bg-white/5 transition-colors cursor-pointer'
        ).style('border-bottom:1px solid #222;').on('click', lambda m=movie: ui.navigate.to(f'/tickets?movie_id={m.id}')):
            if movie.imageUrl:
                ui.image(movie.imageUrl).classes('w-12 h-16 object-cover rounded shadow-md').style('flex-shrink:0;')
            else:
                with ui.element('div').classes(
                    'w-12 h-16 rounded flex items-center justify-center'
                ).style('background-color:#333; flex-shrink:0;'):
                    ui.icon('movie').classes('text-gray-500 text-2xl')

            with ui.column().classes('flex-1 min-w-0'):
                ui.label(movie.titel).classes('text-white font-bold text-sm truncate')
                if movie.beschreibung:
                    ui.label(
                        movie.beschreibung[:80] + ('...' if len(movie.beschreibung or '') > 80 else '')
                    ).classes('text-gray-500 text-xs truncate hidden sm:block')

            ui.label(movie.genre.value).classes('w-28 text-green-500 text-xs font-semibold hidden sm:block')
            ui.label(str(movie.erscheinungsjahr)).classes('w-16 text-gray-400 text-xs text-center hidden sm:block')
            ui.label(f'{movie.dauer} Min').classes('w-20 text-gray-400 text-xs text-center hidden md:block')

            fsk_colors = {0:'bg-green-600', 6:'bg-yellow-500', 12:'bg-orange-500', 16:'bg-red-600', 18:'bg-red-800'}
            fsk_val = movie.altersfreigabe.value
            with ui.element('div').classes('w-14 flex justify-center hidden md:flex'):
                ui.label(f'FSK {fsk_val}').classes(
                    f'text-white text-[10px] font-bold px-2 py-0.5 rounded {fsk_colors.get(fsk_val,"bg-gray-600")}'
                )

            with ui.element('div').classes('w-16 text-center hidden lg:flex items-center justify-center gap-1'):
                ui.icon('star').classes('text-yellow-400 text-sm')
                ui.label(f'{movie.bewertung:.1f}').classes('text-gray-300 text-xs')

            if is_admin:
                with ui.row().classes('w-28 gap-1 justify-center').on('click.stop', lambda: None):
                    ui.button(icon='edit', on_click=lambda m=movie: self._open_movie_dialog(m)).props(
                        'flat round size=sm').classes('text-blue-400')
                    ui.button(icon='delete', on_click=lambda m=movie: self._confirm_delete(m, refresh_fn)).props(
                        'flat round size=sm').classes('text-red-500')

    def _confirm_delete(self, movie: Movie, refresh_fn):
        with ui.dialog() as dialog, ui.card().classes('rounded-xl').style(
            'background-color:#1f1f1f; min-width:360px;'
        ):
            ui.label('Film löschen').classes('text-white text-xl font-bold mb-2')
            ui.label(f'Soll "{movie.titel}" wirklich gelöscht werden?').classes('text-gray-300 mb-6')
            with ui.row().classes('w-full gap-3 justify-end'):
                ui.button('Abbrechen', on_click=dialog.close).props('flat no-caps').classes('text-gray-300')
                def do_delete():
                    self.db.delete_movie_by_id(movie.id)
                    dialog.close()
                    ui.notify(f'"{movie.titel}" gelöscht.', color='positive')
                    refresh_fn()
                ui.button('Löschen', on_click=do_delete).props('no-caps unelevated').classes(
                    'text-white font-bold rounded px-4').style('background-color:#e50914 !important;')
        dialog.open()

    def _open_movie_dialog(self, movie: Movie | None):
        is_edit = movie is not None
        with ui.dialog() as dialog, ui.card().classes('rounded-xl w-full').style(
            'background-color:#1f1f1f; max-width:640px; max-height:90vh; overflow-y:auto;'
        ):
            ui.label('Film bearbeiten' if is_edit else 'Film manuell hinzufügen').classes(
                'text-white text-2xl font-bold mb-4'
            )
            titel_input = ui.input(
                label='Titel *', value=movie.titel if is_edit else ''
            ).props('dark outlined').classes('w-full mb-3')

            genre_opts = [g.value for g in Genre]
            genre_select = ui.select(
                options=genre_opts, label='Genre *',
                value=movie.genre.value if is_edit else genre_opts[0]
            ).props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                dauer_input = ui.number(
                    label='Dauer (Min) *', value=movie.dauer if is_edit else 90, min=1, max=600
                ).props('dark outlined').classes('flex-1')
                jahr_input = ui.number(
                    label='Erscheinungsjahr *', value=movie.erscheinungsjahr if is_edit else CURRENT_YEAR,
                    min=1900, max=CURRENT_YEAR+2
                ).props('dark outlined').classes('flex-1')

            fsk_select = ui.select(
                options=[str(a.value) for a in Altersfreigabe], label='FSK *',
                value=str(movie.altersfreigabe.value) if is_edit else '0'
            ).props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                reg_input = ui.input(
                    label='Regisseur', value=movie.regisseur or '' if is_edit else ''
                ).props('dark outlined').classes('flex-1')
                prod_input = ui.input(
                    label='Produktionsfirma', value=movie.produktionsfirma or '' if is_edit else ''
                ).props('dark outlined').classes('flex-1')

            desc_input = ui.textarea(
                label='Beschreibung', value=movie.beschreibung or '' if is_edit else ''
            ).props('dark outlined').classes('w-full mb-3')

            with ui.row().classes('w-full gap-3 mb-3'):
                rating_input = ui.number(
                    label='Bewertung (0–10)', value=movie.bewertung if is_edit else 0.0,
                    min=0.0, max=10.0, step=0.1, format='%.1f'
                ).props('dark outlined').classes('flex-1')
                img_input = ui.input(
                    label='Bild-URL', value=movie.imageUrl or '' if is_edit else ''
                ).props('dark outlined').classes('flex-1')

            error_label = ui.label('').classes('text-red-500 text-sm mb-2')

            def save():
                if not titel_input.value.strip():
                    error_label.set_text('Bitte Titel eingeben.')
                    return
                try:
                    new_dauer = int(dauer_input.value)
                    new_jahr = int(jahr_input.value)
                    new_rating = float(rating_input.value)
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
                    movie.regisseur = reg_input.value.strip() or None
                    movie.produktionsfirma = prod_input.value.strip() or None
                    movie.beschreibung = desc_input.value.strip() or None
                    movie.bewertung = new_rating
                    movie.imageUrl = img_input.value.strip()
                    self.db._session.add(movie)
                    self.db._session.commit()
                    ui.notify(f'"{movie.titel}" aktualisiert.', color='positive')
                else:
                    new_movie = Movie(
                        titel=titel_input.value.strip(), genre=genre_enum,
                        dauer=new_dauer, erscheinungsjahr=new_jahr, altersfreigabe=fsk_enum,
                        regisseur=reg_input.value.strip() or None,
                        produktionsfirma=prod_input.value.strip() or None,
                        beschreibung=desc_input.value.strip() or None,
                        bewertung=new_rating, imageUrl=img_input.value.strip(),
                    )
                    self.db.save_movie(new_movie)
                    ui.notify(f'"{new_movie.titel}" hinzugefügt.', color='positive')
                dialog.close()
                ui.navigate.to('/movies')

            with ui.row().classes('w-full gap-3 justify-end mt-2'):
                ui.button('Abbrechen', on_click=dialog.close).props('flat no-caps').classes('text-gray-300')
                ui.button('Speichern', on_click=save).props('no-caps unelevated').classes(
                    'text-white font-bold rounded px-6'
                ).style('background-color:#e50914 !important;')
        dialog.open()