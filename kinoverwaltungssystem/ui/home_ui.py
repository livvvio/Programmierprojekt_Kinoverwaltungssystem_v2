from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.ui.navbar import Navbar


class Home_UI:
    def __init__(self, movies: list[Movie]):
        self.movies = movies

    def render(self):
        ui.query('body').style(
            'background-color: #141414; color: white; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;')

        authenticated = nicegui_app.storage.user.get('authenticated', False)
        username = nicegui_app.storage.user.get('username', 'Gast')
        is_guest = nicegui_app.storage.user.get('is_guest', True)
        is_admin = nicegui_app.storage.user.get('is_admin', False)

        Navbar('home').render()

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
                ui.label(f'{len(self.movies)} Titel').classes('text-gray-500 text-sm')

            with ui.element('div').style(
                'display: grid;'
                'grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));'
                'gap: 20px; width: 100%;'
            ):
                for movie in self.movies:
                    self._render_card(movie)

    def _render_card(self, movie: Movie):
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
                ui.label(movie.titel).classes('text-white font-extrabold text-sm leading-tight')
                with ui.row().classes('gap-2 items-center'):
                    ui.label(movie.genre.value).classes('text-green-500 text-xs font-semibold')
                    ui.label(str(movie.erscheinungsjahr)).classes('text-gray-400 text-xs')
                    ui.label(f'{movie.dauer} Min').classes('text-gray-400 text-xs')
                ui.label(f'★ {movie.bewertung:.1f}  ·  FSK {movie.altersfreigabe.value}').classes(
                    'text-yellow-400 text-xs font-bold')
