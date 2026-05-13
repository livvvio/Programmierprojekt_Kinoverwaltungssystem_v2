import html as html_lib
from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.model.movie_model import Movie


class Home_UI:
    def __init__(self, movies: list[Movie]):
        self.movies = movies

    def render(self):
        ui.query('body').style(
            'background-color: #141414; color: white; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;')

        ui.add_head_html('''<style>
            .kino-card {
                position: relative;
                border-radius: 10px;
                overflow: hidden;
                cursor: pointer;
                background-color: #1a1a1a;
                transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94),
                            box-shadow 0.3s ease;
            }
            .kino-card:hover {
                transform: scale(1.05) translateY(-5px);
                box-shadow: 0 24px 48px rgba(0,0,0,0.9),
                            0 0 0 2px rgba(229,9,20,0.8);
                z-index: 20;
            }
            .kino-card img {
                width: 100%;
                aspect-ratio: 2/3;
                object-fit: cover;
                display: block;
            }
            .kino-card-overlay {
                position: absolute;
                inset: 0;
                background: linear-gradient(to top,
                    rgba(0,0,0,0.95) 0%,
                    rgba(0,0,0,0.4) 50%,
                    transparent 100%);
                opacity: 0;
                transition: opacity 0.3s ease;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding: 14px;
                gap: 4px;
            }
            .kino-card:hover .kino-card-overlay {
                opacity: 1;
            }
            .kino-card-title {
                color: white;
                font-weight: 800;
                font-size: 15px;
                line-height: 1.25;
            }
            .kino-card-meta {
                display: flex;
                gap: 8px;
                align-items: center;
            }
        </style>''')

        authenticated = nicegui_app.storage.user.get('authenticated', False)
        username = nicegui_app.storage.user.get('username', 'Gast')
        is_guest = nicegui_app.storage.user.get('is_guest', True)
        is_admin = nicegui_app.storage.user.get('is_admin', False)

        def logout():
            nicegui_app.storage.user.clear()
            ui.navigate.to('/')

        def go_to_login():
            ui.navigate.to('/login')

        # ── Navbar ───────────────────────────────────────────────────────────
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
                            'background-color: #e50914; color: white;')
                    ui.button('Abmelden', on_click=logout).props('no-caps unelevated').classes(
                        'text-white text-sm font-bold rounded px-3 py-1'
                    ).style('background-color: #e50914 !important;')
                else:
                    ui.button('Anmelden', on_click=go_to_login).props('no-caps unelevated').classes(
                        'text-white text-sm font-bold rounded px-3 py-1'
                    ).style('background-color: #e50914 !important;')

        # ── Main Content ─────────────────────────────────────────────────────
        with ui.column().classes('w-full px-10 pt-24 pb-16'):

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

            # ── Grid ─────────────────────────────────────────────────────
            with ui.element('div').style(
                'display: grid;'
                'grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));'
                'gap: 20px; width: 100%;'
            ):
                for movie in self.movies:
                    self._render_card(movie)

    def _render_card(self, movie: Movie):
        title   = html_lib.escape(movie.titel)
        genre   = html_lib.escape(movie.genre.value)
        image   = html_lib.escape(movie.imageUrl or '')
        rating  = f'{movie.bewertung:.1f}'
        year    = movie.erscheinungsjahr
        fsk     = movie.altersfreigabe.value
        duration = movie.dauer

        placeholder = (
            '<div style="width:100%;aspect-ratio:2/3;background:#2a2a2a;'
            'display:flex;align-items:center;justify-content:center;">'
            '<span style="color:#4b5563;font-size:48px;">🎬</span></div>'
        )
        img_html = f'<img src="{image}" alt="{title}">' if image else placeholder

        ui.html(f'''
        <div class="kino-card" onclick="window.location='/tickets'">
            {img_html}
            <div class="kino-card-overlay">
                <div class="kino-card-title">{title}</div>
                <div class="kino-card-meta">
                    <span style="color:#22c55e;font-size:11px;font-weight:600;">{genre}</span>
                    <span style="color:#6b7280;font-size:11px;">{year}</span>
                    <span style="color:#6b7280;font-size:11px;">{duration} Min</span>
                </div>
                <div style="color:#f59e0b;font-size:11px;font-weight:700;">★ {rating} &nbsp;·&nbsp; FSK {fsk}</div>
            </div>
        </div>
        ''')
