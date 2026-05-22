from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.model.movie_model import Movie
from kinoverwaltungssystem.ui.navbar import Navbar


class Home_UI:
    def __init__(self, movies: list[Movie]):
        self.movies = movies
        self._featured_idx = 0
        self._refresh_hero = None

    def render(self):
        ui.query('body').style(
            'background-color: #0a0a0a; color: white; '
            'font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; '
            'overflow: hidden; height: 100vh; margin: 0;'
        )
        ui.add_head_html('''<style>
            ::-webkit-scrollbar { display: none; }
            * { scrollbar-width: none; -ms-overflow-style: none; }
            @keyframes heroFade { from { opacity: 0; } to { opacity: 1; } }
            .hero-fade { animation: heroFade 0.7s ease; }
            .carousel-card:hover { transform: scale(1.06); z-index: 10; }
            .carousel-card { transition: transform 0.2s ease; }
            .card-overlay { opacity: 0; transition: opacity 0.2s ease; }
            .carousel-card:hover .card-overlay { opacity: 1; }
        </style>''')

        Navbar('home').render()

        if not self.movies:
            self._render_empty()
            return

        top_rated = sorted(self.movies, key=lambda m: m.bewertung, reverse=True)

        @ui.refreshable
        def hero_section():
            movie = self.movies[self._featured_idx]
            with ui.element('div').classes('hero-fade').style('height: 100%; position: relative; overflow: hidden;'):
                self._render_hero(movie)

        self._refresh_hero = hero_section.refresh

        with ui.element('div').style(
            'position: fixed; top: 64px; left: 0; right: 0; bottom: 0; '
            'display: flex; flex-direction: column;'
        ):
            with ui.element('div').style('flex: 0 0 56%; position: relative; overflow: hidden;'):
                hero_section()

            with ui.element('div').style(
                'flex: 1; display: flex; flex-direction: column; '
                'padding: 10px 36px 8px 36px; background: #0a0a0a; overflow: hidden; gap: 0;'
            ):
                self._render_carousel('Alle Filme', self.movies, 'c-all')
                ui.separator().style('background: #1a1a1a; margin: 4px 0; flex-shrink: 0;')
                self._render_carousel('Top Bewertet', top_rated, 'c-top')

        def _rotate():
            self._featured_idx = (self._featured_idx + 1) % len(self.movies)
            hero_section.refresh()

        ui.timer(6.0, _rotate)

    def _render_hero(self, movie: Movie):
        # Blurred background image
        if movie.imageUrl:
            with ui.element('div').style(
                f'position: absolute; inset: 0; '
                f'background-image: url("{movie.imageUrl}"); '
                f'background-size: cover; background-position: center 20%; '
                f'filter: blur(4px) brightness(0.3); transform: scale(1.07);'
            ):
                pass

        # Gradient overlay
        with ui.element('div').style(
            'position: absolute; inset: 0; '
            'background: linear-gradient(100deg, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.5) 55%, transparent 100%);'
        ):
            pass

        # Hero content
        with ui.element('div').style(
            'position: relative; z-index: 1; height: 100%; '
            'display: flex; align-items: flex-end; padding: 32px 48px;'
        ):
            # Left: movie info
            with ui.element('div').style('max-width: 500px; flex: 1;'):
                ui.label('IM KINO').style(
                    'color: #e50914; font-size: 10px; font-weight: 800; '
                    'letter-spacing: 4px; margin-bottom: 10px; display: block;'
                )
                ui.label(movie.titel).style(
                    'font-size: clamp(20px, 2.6vw, 38px); font-weight: 900; '
                    'line-height: 1.1; color: white; margin-bottom: 12px; display: block;'
                )
                with ui.row().style('gap: 10px; align-items: center; margin-bottom: 14px; flex-wrap: wrap;'):
                    ui.label(f'★ {movie.bewertung:.1f}').style(
                        'color: #f5c518; font-weight: 800; font-size: 13px;'
                    )
                    ui.label('·').style('color: #333; font-size: 16px;')
                    ui.label(movie.genre.value).style('color: #999; font-size: 12px;')
                    ui.label('·').style('color: #333; font-size: 16px;')
                    ui.label(str(movie.erscheinungsjahr)).style('color: #999; font-size: 12px;')
                    ui.label('·').style('color: #333; font-size: 16px;')
                    ui.label(f'{movie.dauer} Min').style('color: #999; font-size: 12px;')
                    ui.label('·').style('color: #333; font-size: 16px;')
                    ui.label(f'FSK {movie.altersfreigabe.value}').style('color: #999; font-size: 12px;')

                if movie.beschreibung:
                    desc = (movie.beschreibung[:130] + '…') if len(movie.beschreibung) > 130 else movie.beschreibung
                    ui.label(desc).style(
                        'color: #bbb; font-size: 12px; line-height: 1.65; '
                        'margin-bottom: 20px; display: block; max-width: 420px;'
                    )
                else:
                    ui.element('div').style('margin-bottom: 20px;')

                with ui.row().style('gap: 10px; align-items: center;'):
                    ui.button('Ticket kaufen',
                        on_click=lambda m=movie: ui.navigate.to(f'/tickets?movie_id={m.id}')
                    ).props('no-caps unelevated').style(
                        'background: #e50914 !important; color: white; '
                        'font-weight: 700; padding: 9px 26px; border-radius: 3px; '
                        'font-size: 13px; letter-spacing: 0.3px;'
                    )
                    ui.button('Alle Filme',
                        on_click=lambda: ui.navigate.to('/movies')
                    ).props('no-caps unelevated').style(
                        'background: rgba(255,255,255,0.1) !important; color: #ccc; '
                        'font-weight: 600; padding: 9px 20px; border-radius: 3px; '
                        'font-size: 13px; border: 1px solid rgba(255,255,255,0.15);'
                    )

            # Right: poster
            if movie.imageUrl:
                with ui.element('div').style(
                    'flex: 0 0 auto; margin-left: 40px; '
                    'width: min(130px, 13vw); align-self: flex-end; '
                    'border-radius: 6px; overflow: hidden; '
                    'box-shadow: 0 12px 40px rgba(0,0,0,0.8);'
                ):
                    ui.image(movie.imageUrl).style('width: 100%; display: block;')

        # Prev/next arrows on hero
        with ui.element('div').style(
            'position: absolute; top: 50%; left: 12px; transform: translateY(-50%); z-index: 2;'
        ):
            ui.button('', icon='chevron_left').props('flat dense round').style(
                'color: white; background: rgba(0,0,0,0.4) !important; width: 36px; height: 36px;'
            ).on('click', lambda: self._hero_prev())

        with ui.element('div').style(
            'position: absolute; top: 50%; right: 12px; transform: translateY(-50%); z-index: 2;'
        ):
            ui.button('', icon='chevron_right').props('flat dense round').style(
                'color: white; background: rgba(0,0,0,0.4) !important; width: 36px; height: 36px;'
            ).on('click', lambda: self._hero_next())

        # Progress dots (max 8 shown)
        visible = min(len(self.movies), 8)
        with ui.element('div').style(
            'position: absolute; bottom: 14px; left: 48px; '
            'display: flex; gap: 5px; z-index: 2; align-items: center;'
        ):
            for i in range(visible):
                is_active = i == (self._featured_idx % visible)
                ui.element('div').style(
                    f'height: 3px; border-radius: 2px; '
                    f'width: {"22px" if is_active else "8px"}; '
                    f'background: {"#e50914" if is_active else "#444"}; '
                    f'transition: all 0.3s ease;'
                )

    def _hero_prev(self):
        self._featured_idx = (self._featured_idx - 1) % len(self.movies)
        if self._refresh_hero:
            self._refresh_hero()

    def _hero_next(self):
        self._featured_idx = (self._featured_idx + 1) % len(self.movies)
        if self._refresh_hero:
            self._refresh_hero()

    def _render_carousel(self, title: str, movies: list[Movie], carousel_id: str):
        with ui.element('div').style('flex: 1; display: flex; flex-direction: column; min-height: 0; padding: 6px 0;'):
            with ui.row().style(
                'align-items: center; justify-content: space-between; '
                'margin-bottom: 6px; flex-shrink: 0;'
            ):
                ui.label(title).style(
                    'font-size: 11px; font-weight: 700; color: #aaa; '
                    'text-transform: uppercase; letter-spacing: 2.5px;'
                )
                with ui.row().style('gap: 2px;'):
                    (ui.button('', icon='chevron_left')
                        .props('flat dense')
                        .style('color: #555; width: 26px; height: 26px; min-width: 0;')
                        .on('click', lambda cid=carousel_id: ui.run_javascript(
                            f'document.getElementById("{cid}").scrollBy({{left:-560,behavior:"smooth"}})'
                        )))
                    (ui.button('', icon='chevron_right')
                        .props('flat dense')
                        .style('color: #555; width: 26px; height: 26px; min-width: 0;')
                        .on('click', lambda cid=carousel_id: ui.run_javascript(
                            f'document.getElementById("{cid}").scrollBy({{left:560,behavior:"smooth"}})'
                        )))

            with ui.element('div').props(f'id={carousel_id}').style(
                'display: flex; gap: 8px; overflow-x: auto; overflow-y: hidden; '
                'flex: 1; align-items: stretch; padding-bottom: 2px;'
            ):
                for movie in movies:
                    self._render_card(movie)

    def _render_card(self, movie: Movie):
        with ui.element('div').classes('carousel-card').style(
            'flex: 0 0 auto; width: 80px; cursor: pointer; position: relative; '
            'border-radius: 5px; overflow: hidden;'
        ).on('click', lambda m=movie: ui.navigate.to(f'/tickets?movie_id={m.id}')):

            if movie.imageUrl:
                ui.image(movie.imageUrl).style(
                    'width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block;'
                )
            else:
                with ui.element('div').style(
                    'width: 100%; aspect-ratio: 2/3; background: #1c1c1c; '
                    'display: flex; align-items: center; justify-content: center;'
                ):
                    ui.icon('movie').style('color: #383838; font-size: 26px;')

            with ui.element('div').classes('card-overlay').style(
                'position: absolute; inset: 0; '
                'background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, transparent 55%); '
                'display: flex; flex-direction: column; justify-content: flex-end; padding: 5px;'
            ):
                ui.label(movie.titel).style(
                    'color: white; font-size: 8px; font-weight: 700; line-height: 1.25; '
                    'display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;'
                )
                ui.label(f'★ {movie.bewertung:.1f}').style(
                    'color: #f5c518; font-size: 8px; font-weight: 700; margin-top: 2px;'
                )

    def _render_empty(self):
        is_admin = nicegui_app.storage.user.get('is_admin', False)
        with ui.element('div').style(
            'display: flex; flex-direction: column; align-items: center; '
            'justify-content: center; height: calc(100vh - 64px); gap: 16px;'
        ):
            ui.icon('movie').style('color: #222; font-size: 72px;')
            ui.label('Noch keine Filme vorhanden.').style('color: #555; font-size: 17px;')
            if is_admin:
                ui.button('Ersten Film hinzufügen',
                    on_click=lambda: ui.navigate.to('/movies')
                ).props('no-caps unelevated').style(
                    'background: #e50914 !important; color: white; '
                    'font-weight: 700; padding: 10px 24px; border-radius: 3px;'
                )