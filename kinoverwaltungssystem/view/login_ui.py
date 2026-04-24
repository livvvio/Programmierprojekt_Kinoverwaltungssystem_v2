from nicegui import ui, app as nicegui_app
from kinoverwaltungssystem.db.database import Database
from kinoverwaltungssystem.model.auth import hash_password


class Login_UI:
    def __init__(self, db: Database):
        self.db = db

    def render(self):
        ui.query('body').style(
            'background-color: #141414; color: white; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;'
        )

        with ui.column().classes('absolute-center items-center w-full').style('max-width: 400px'):
            ui.label('Kinoverwaltungssystem').classes('text-red-600 text-4xl font-black tracking-tighter mb-6')

            with ui.card().classes('w-full rounded-lg').style('background-color: #1f1f1f; padding: 2rem;'):
                ui.label('Anmelden').classes('text-white text-2xl font-bold mb-6')

                email_input = ui.input(label='E-Mail').props('dark outlined').classes('w-full mb-2')
                password_input = (
                    ui.input(label='Passwort', password=True, password_toggle_button=True)
                    .props('dark outlined')
                    .classes('w-full mb-2')
                )

                error_label = ui.label('').classes('text-red-500 text-sm mb-3')

                def try_login():
                    error_label.set_text('')
                    user = self.db.get_user_by_email(email_input.value.strip())
                    if user and user.password_hash == hash_password(password_input.value):
                        nicegui_app.storage.user['authenticated'] = True
                        nicegui_app.storage.user['username'] = user.username
                        nicegui_app.storage.user['is_guest'] = False
                        nicegui_app.storage.user['is_admin'] = bool(user.is_admin)
                        ui.navigate.to('/')
                    else:
                        error_label.set_text('Ungültige E-Mail oder Passwort.')

                ui.button('Anmelden', on_click=try_login).props('no-caps unelevated').classes(
                    'w-full text-white font-bold rounded mb-4'
                ).style('background-color: #e50914 !important; padding: 0.6rem;')

                with ui.row().classes('w-full items-center gap-2 mb-4'):
                    ui.separator().classes('flex-1').style('background-color: #444;')
                    ui.label('oder').classes('text-gray-500 text-sm')
                    ui.separator().classes('flex-1').style('background-color: #444;')

                def continue_as_guest():
                    nicegui_app.storage.user['authenticated'] = True
                    nicegui_app.storage.user['username'] = 'Gast'
                    nicegui_app.storage.user['is_guest'] = True
                    nicegui_app.storage.user['is_admin'] = False
                    ui.navigate.to('/')

                ui.button('Als Gast fortfahren', on_click=continue_as_guest).props('no-caps flat').classes(
                    'w-full font-bold rounded'
                ).style('background-color: transparent !important; border: 1px solid #555; color: white !important; padding: 0.6rem;')