from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.model.movie_model import Movie


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

        def logout():
            nicegui_app.storage.user.clear()
            ui.navigate.to('/')

        def go_to_login():
            ui.navigate.to('/login')

        with ui.header().classes(
                'bg-black/80 backdrop-blur-md border-none p-4 justify-between items-center fixed top-0 w-full z-50'):
            ui.label('Kinoverwaltungssystem').classes('text-red-600 text-3xl font-black tracking-tighter')
            with ui.row().classes('items-center gap-6'):
                ui.link('Home', '/').classes('text-white font-bold no-underline')
                ui.link('Filme', '/movies').classes('text-gray-300 no-underline hover:text-white')
                ui.link('Tickets', '/tickets').classes('text-gray-300 no-underline hover:text-white')
                if authenticated:
                    ui.label(f'{"Gast" if is_guest else username}').classes('text-gray-300 text-sm')
                    if is_admin:
                        ui.label('Admin').classes('text-xs font-bold px-2 py-0.5 rounded').style(
                            'background-color: #e50914; color: white;'
                        )
                    ui.button('Abmelden', on_click=logout).props('no-caps unelevated').classes(
                        'text-white text-sm font-bold rounded px-3 py-1'
                    ).style('background-color: #e50914 !important;')
                else:
                    ui.button('Anmelden', on_click=go_to_login).props('no-caps unelevated').classes(
                        'text-white text-sm font-bold rounded px-3 py-1'
                    ).style('background-color: #e50914 !important;')

        with ui.column().classes('w-full px-12 pt-24 pb-12'):
            if authenticated and not is_guest:
                ui.label(f"Willkommen zurück, {username}!").classes('text-2xl font-bold mb-4 ml-2 text-white')
            else:
                ui.label("Willkommen!").classes('text-2xl font-bold mb-4 ml-2 text-white')
            ui.label('Derzeit beliebt').classes('text-2xl font-bold mb-4 ml-2 text-white')

            if not self.movies:
                with ui.column().classes('items-center w-full mt-12 gap-4'):
                    ui.icon('movie').classes('text-gray-600 text-8xl')
                    ui.label('Noch keine Filme vorhanden.').classes('text-gray-500 text-xl')
                    if is_admin:
                        ui.button('Ersten Film hinzufügen', on_click=lambda: ui.navigate.to('/movies')).props(
                            'no-caps unelevated'
                        ).classes('text-white font-bold rounded px-6 py-2').style('background-color: #e50914 !important;')
            else:
                with ui.row().classes('w-full gap-4 no-wrap overflow-x-auto pb-8'):
                    for movie in self.movies:
                        self.create_movie_card(movie)

    def create_movie_card(self, movie: Movie):
        with ui.card().tight().classes(
                'w-64 bg-transparent border-none cursor-pointer transition-transform duration-300 hover:scale-110 hover:z-10').on(
                'click', lambda m=movie: ui.navigate.to('/tickets')):
            ui.image(movie.imageUrl).classes('w-full aspect-[2/3] object-cover rounded-md shadow-2xl')

            with ui.column().classes('p-2'):
                ui.label(movie.titel).classes('text-sm font-bold truncate text-white')
                with ui.row().classes('items-center gap-2'):
                    ui.label(f"{movie.erscheinungsjahr}").classes('text-[10px] text-gray-400')
                    ui.label(f"FSK {movie.altersfreigabe.value}+").classes(
                        'border border-gray-500 px-1 text-[8px] text-gray-400 rounded')
                    ui.label(movie.genre.value).classes('text-[10px] text-green-500 font-bold')
