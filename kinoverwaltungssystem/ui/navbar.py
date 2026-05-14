from nicegui import ui, app as nicegui_app


class Navbar:
    def __init__(self, active: str = ''):
        self.active = active

    def render(self) -> None:
        authenticated = nicegui_app.storage.user.get('authenticated', False)
        username = nicegui_app.storage.user.get('username', 'Gast')
        is_guest = nicegui_app.storage.user.get('is_guest', True)
        is_admin = nicegui_app.storage.user.get('is_admin', False)

        def logout():
            nicegui_app.storage.user.clear()
            ui.navigate.to('/')

        with ui.header().classes(
            'bg-black/80 backdrop-blur-md border-none p-4 justify-between items-center fixed top-0 w-full z-50'
        ):
            ui.label('Kinoverwaltungssystem').classes(
                'text-red-600 text-3xl font-black tracking-tighter cursor-pointer'
            ).on('click', lambda: ui.navigate.to('/'))
            with ui.row().classes('items-center gap-6'):
                ui.link('Home', '/').classes(self._link_classes('home'))
                ui.link('Filme', '/movies').classes(self._link_classes('movies'))
                ui.link('Tickets', '/tickets').classes(self._link_classes('tickets'))
                if authenticated:
                    ui.label(f'{"Gast" if is_guest else username}').classes('text-gray-300 text-sm')
                    if is_admin:
                        ui.label('Admin').classes('text-xs font-bold px-2 py-0.5 rounded').style(
                            'background-color: #e50914; color: white;')
                    ui.button('Abmelden', on_click=logout).props('no-caps unelevated').classes(
                        'text-white text-sm font-bold rounded px-3 py-1'
                    ).style('background-color: #e50914 !important;')
                else:
                    ui.button('Anmelden', on_click=lambda: ui.navigate.to('/login')).props('no-caps unelevated').classes(
                        'text-white text-sm font-bold rounded px-3 py-1'
                    ).style('background-color: #e50914 !important;')

    def _link_classes(self, page: str) -> str:
        return 'no-underline ' + ('text-white font-bold' if self.active == page else 'text-gray-300 hover:text-white')
