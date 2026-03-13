class Movie:
    def __init__(self, titel: str, genre: str, dauer: int, altersfreigabe: int,
                 erscheinungsjahr: int, beschreibung: str, produktionsfirma: str,
                 regisseur: str, bewertung: float, imageUrl: str = ""):  # ← hinzufügen
        self.titel = titel
        self.altersfreigabe = altersfreigabe
        self.dauer = dauer
        self.genre = genre
        self.erscheinungsjahr = erscheinungsjahr
        self.beschreibung = beschreibung
        self.produktionsfirma = produktionsfirma
        self.regisseur = regisseur
        self.bewertung = bewertung
        self.imageUrl = imageUrl

    def get_titel(self):
        return self.titel
    def set_titel(self, titel: str):
        self.titel = titel

    def get_altersfreigabe(self):
        return self.altersfreigabe
    def set_altersfreigabe(self, altersfreigabe: float):
        self.altersfreigabe = altersfreigabe

    def get_dauer(self):
        return self.dauer
    def set_dauer(self, dauer: float):
        self.dauer = dauer

    def get_genre(self):
        return self.genre
    def set_genre(self, genre: str):
        self.genre = genre

    def get_erscheinungsjahr(self):
        return self.erscheinungsjahr
    def set_erscheinungsjahr(self, erscheinungsjahr: float):
        self.erscheinungsjahr = erscheinungsjahr

    def get_beschreibung(self):
        return self.beschreibung
    def set_beschreibung(self, beschreibung: str):
        self.beschreibung = beschreibung

    def get_produktionsfirma(self):
        return self.produktionsfirma
    def set_produktionsfirma(self, produktionsfirma: str):
        self.produktionsfirma = produktionsfirma

    def get_regisseur(self):
        return self.regisseur
    def set_regisseur(self, regisseur: str):
        self.regisseur = regisseur

    def get_bewertung(self):
        return self.bewertung
    def set_bewertung(self, bewertung: float):
        self.bewertung = bewertung


