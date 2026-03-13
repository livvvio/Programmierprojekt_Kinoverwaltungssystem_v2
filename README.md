# 🎬 Kinoverwaltungssystem

Diese Anwendung ermöglicht es dem Kunden oder dem Empfangsmitarbeiter im Kino, Filme hinzuzufügen, zu bearbeiten und zu
löschen und Ticketpreise/Tickets für Kunden auszugeben. Das Programm speichert die Filme mit deren dazugehörigen
Attributen in einer Datei.

---
## 📥 Installation und Ausführung
 
### Voraussetzungen

- Git installiert
- Geeignete IDE (z. B. VS Code / PyCharm)
- Aktuelle Python Version (3.x)

Es gibt zwei Möglichkeiten, das Projekt herunterzuladen:
- Zum einen über Git
- Zum anderen als ZIP-Datei


### Git: Repository klonen
- Ordner wählen, in dem das Projekt liegen soll (z. B. Dokumente/Projekte)
- Terminal/Eingabeaufforderung im gewünschten Ordner öffnen
- Befehl ausführen:

```bash
    git clone https://github.com/livvvio/Programmierprojekt_Kinoverwaltungssystem.git
    cd Programmierprojekt_Kinoverwaltungssystem
    python app.py
```
### ZipFile
- Zipfile herunterladen
- Zipfile entpacken 

### Ausführung mit einer Entwicklungsumgebung
- VS Code / PyCharm starten
- Ordner in der IDE öffnen und Programmierprojekt_Kinoverwaltungssystem auswählen
- app.py öffnen
- File starten
  
### Ausführung über das Terminal

Alternativ zur Ausführung in einer IDE (VS Code / PyCharm) kann das Programm auch direkt über das Terminal gestartet werden.

1. **Terminal öffnen**  
   - Windows: z. B. *Eingabeaufforderung* oder *PowerShell*  
   - macOS / Linux: *Terminal*

2. **In den Projektordner wechseln**  
   Falls die Repository z. B. in `Dokumente/Projekte` geklont wurde:

   ```bash
   cd Pfad/zum/Ordner/Programmierprojekt_Kinoverwaltungssystem
3. **Starten**
   ```bash
   python app.py
   ```
    
   ins Terminal eingeben
---

## 🚀 Features & Funktionen

### Admin

- **Filmliste ansehen** – Der Benutzer wählt die Funktion «Filme anschauen» und wird nun gefragt, ob er nach einem
  gewissen Film suchen möchte. Mittels Ja/Nein kann der Benutzer jetzt die Suchfunktion ein- oder ausschalten. Falls die
  Suchfunktion eingeschaltet wurde, wird jetzt gefragt, wonach der Benutzer suchen möchte. Gleiches Spiel für die
  Sortierfunktion. Hier kann der Benutzer nach einem Attribut der Klasse Film sortieren. Nach der Eingabe werden die
  einzelnen Filme gefiltert/ungefiltert, sortiert/unsortiert untereinander in der Konsole ausgegeben.


- **Film hinzufügen** – Wird die Funktion «Film bearbeiten» gewählt, so kann der Benutzer die Attribute eines Filmes
  bearbeiten. Die eingegebenen Werte werden dann gespeichert.


- **Film löschen** – Wird die Funktion «Film löschen» ausgewählt, so wird der Benutzer nach dem Filmtitel gefragt, um
  den dazugehörigen Film zu löschen.
 

- **Benutzer wechseln** – Wird die Funktion «Benutzer wechseln» gewählt, so kann man zwischen dem Benutzer Admin und
  dem Benutzer Kunde wechseln.


- **Programm beenden** – Wenn der Benutzer die Funktion «Programm beenden» drückt, endet das Programm.

### Demo der Adminansicht
[![Demo Adminansicht ](https://img.youtube.com/vi/Wfg52nPl4uA/0.jpg)](https://youtu.be/Wfg52nPl4uA)

---

### Kunde

- **Filmliste ansehen** – Der Benutzer wählt die Funktion «Filme anschauen» und wird nun gefragt, ob er nach einem
  gewissen Film suchen möchte. Mittels Ja/Nein kann der Benutzer jetzt die Suchfunktion ein- oder ausschalten. Falls die
  Suchfunktion eingeschaltet wurde, wird jetzt gefragt, wonach der Benutzer suchen möchte. Gleiches Spiel für die
  Sortierfunktion. Hier kann der Benutzer nach einem Attribut der Klasse Film sortieren. Nach der Eingabe werden die
  einzelnen Filme gefiltert/ungefiltert, sortiert/unsortiert untereinander in der Konsole ausgegeben.


- **Ticketpreis berechnen** – Wird die Funktion «Ticketpreis berechnen» ausgewählt, so wird der Benutzer nach:
    - Vorstellungszeit
    - Ist Wochenende
    - Namen der Personen
    - Alter der Personen (Altersfreigabe/Kinderrabatt/Rentnerrabatt)
    - Student -> Ja/Nein

  gefragt. Danach wird dem Kunden eine Übersicht über alle Kostenpunkte aufgelistet und die entsprechenden Abzüge werden
  dargestellt.


- **Benutzer wechseln** – Wird die Funktion «Benutzer wechseln» gewählt, so kann man zwischen dem Benutzer Admin und
  dem Benutzer Kunde wechseln.


- **Programm beenden** – Wenn der Benutzer die Funktion «Programm beenden» drückt, endet das Programm.

### Demo der Kundensicht

[![Demo Kundenansicht](https://img.youtube.com/vi/W09TTs6hkb0/0.jpg)](https://youtu.be/W09TTs6hkb0)

---

## 🧩 Projektstruktur

```
Programmierprojekt_Kinoverwaltungssystem
│
├── kinoverwaltungssystem/
│   ├── file_operations.py  # Lädt, speichert die Filmdaten: Enthält die Klasse 'Movie' für Filmdaten
│   ├── login.py            # Login Teil im Programm
│   ├── menu_options.py     # Enthält die Funktionalität der Menu-Optionen
│   ├── movies.json         # Datei, wo die Filme gespeichert werden
│   └── utility.py          # Enthält Hilfsmethoden für das UI
├── app.py                  # Hauptprogramm: Startpunkt des Systems
└── README.md               # Informationen zum Programm
```
---

## 👤 Autoren

- Lukas Folch
- Simon Moor
- Livio Fritz
---

## ©️ Lizenz

Dieses Projekt wurde für Bildungszwecke erstellt.


