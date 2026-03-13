class User:
    def __init__(self, username: str, email: str, password_hash: str, display_name: str = ""):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.display_name = display_name

    def get_username(self): return self.username
    def set_username(self, username: str): self.username = username

    def get_email(self): return self.email
    def set_email(self, email: str): self.email = email

    def get_password_hash(self): return self.password_hash
    def set_password_hash(self, password_hash: str): self.password_hash = password_hash

    def get_display_name(self): return self.display_name
    def set_display_name(self, display_name: str): self.display_name = display_name

    def __repr__(self):
        return f"User(username={self.username}, email={self.email}, display_name={self.display_name})"