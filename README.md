# 🎬 Kinoverwaltungssystem – Cinema Management System (Browser App)

> UI Showcase

Dieses Projekt demonstriert die Entwicklung einer browserbasierten Anwendung mit NiceGUI, mit Fokus auf saubere
Architektur, Datenvalidierung und Datenbankintegration via ORM.

Ziele des Projekts:

- Den vollständigen Prozess von der Anforderungsanalyse bis zur Implementierung abdecken
- Fortgeschrittene Python-Konzepte in einer Webanwendung anwenden
- Datenvalidierung, Schichtenarchitektur und ORM-Einsatz demonstrieren
- Sauberen, wartbaren und gut getesteten Code produzieren
- Teamarbeit und professionelle Dokumentation fördern

---

## Inhaltsverzeichnis

- [📝 Anwendungsanforderungen](#-anwendungsanforderungen)
- [📖 User Stories](#-user-stories)
- [🧩 Use Cases](#-use-cases)
- [🏛️ Architektur](#architektur)
- [🗄️ Datenbank und ORM](#-datenbank-und-orm)
- [✅ Projektanforderungen](#-projektanforderungen)
- [⚙️ Implementierung](#-implementierung)
- [📂 Repository-Struktur](#-repository-struktur)
- [🚀 Ausführung](#-ausführung)
- [🧪 Tests](#-tests)
- [👥 Team & Beiträge](#-team--beiträge)
- [📝 Lizenz](#-lizenz)

---

## 📝 Anwendungsanforderungen

### Problem

In kleineren Kinos werden Ticketverkäufe und Preisberechnungen oft manuell abgewickelt. Dies führt zu Fehlern bei der
Altersfreigabe-Prüfung, falschen Rabattberechnungen und fehlenden Aufzeichnungen von Transaktionen.

### Szenario

Die Anwendung ermöglicht es Benutzern:

- Einen Filmkatalog im Browser zu durchsuchen
- Tickets für eine oder mehrere Personen zu buchen
- Preise automatisch zu berechnen (inkl. Altersrabatte, Studentenrabatt, Wochenend- und Spätvorstellungszuschlag)
- Ein generiertes PDF-Ticket herunterzuladen
- Den Filmkatalog zu verwalten (nur Admin)

---

## 📖 User Stories

### 1. Filmkatalog ansehen

Als Benutzer möchte ich alle verfügbaren Filme in der Browser-App sehen.

- **Eingaben:** keine
- **Ausgaben:** Liste der Filme (`list[Movie]`)

### 2. Tickets buchen und Gesamtpreis berechnen

Als Kunde möchte ich Personen zu einer Buchung hinzufügen und den automatisch berechneten Gesamtpreis sehen.

- **Eingaben:** Film-ID (`int`), Personendaten (Name, Alter, Student-Flag), Vorstellungszeit (`int`), Wochenende (
  `bool`)
- **Ausgaben:** Preis pro Person, angewandte Rabatte, Gesamtbetrag (`float`)

### 3. Automatische Rabatt- und Zuschlagsregeln

Als Kunde möchte ich, dass Rabatte und Zuschläge automatisch anhand von Alter, Studentenstatus, Uhrzeit und Wochentag
berechnet werden.

- **Eingaben:** Alter der Person (`int`), ist Student (`bool`), Vorstellungszeit (`int`), ist Wochenende (`bool`)
- **Ausgaben:** Rabattzeilen, angepasster Preis pro Person

### 4. PDF-Ticket generieren

Als Kunde möchte ich nach dem Checkout automatisch ein PDF-Ticket herunterladen können.

- **Eingaben:** abgeschlossene Buchung (Film, Personen, Gesamtpreis, Vorstellungsdetails)
- **Ausgaben:** PDF-Ticket-Datei (Download im Browser)

### 5. Filmkatalog verwalten (Admin)

Als Admin möchte ich Filme im Katalog hinzufügen, bearbeiten und löschen können.

- **Eingaben:** Filmattribute (Titel, Genre, Dauer, Altersfreigabe, Erscheinungsjahr, Regisseur, etc.)
- **Ausgaben:** aktualisierter Filmkatalog

---

## 🧩 Use Cases

### UML Use Case Diagramm

<img width="684" height="772" alt="Diagram-drawio" src="https://github.com/user-attachments/assets/271b00a9-babb-4686-acbe-a9598f978ef8" />

### Hauptanwendungsfälle

- Filmkatalog anzeigen (Kunde)
- Ticket buchen (Kunde)
- Preisaufschlüsselung anzeigen (Kunde)
- Checkout & PDF-Ticket herunterladen (Kunde)
- Anmelden (Admin / Kunde)
- Filme verwalten — Hinzufügen / Bearbeiten / Löschen (Admin)

### Akteure

- **Kunde** – durchsucht Filme, bucht Tickets, lädt PDF herunter
- **Admin** – verwaltet den Filmkatalog, hat alle Kundenrechte

---
<a id="-architektur"></a>

## 🏛️ Architektur

<img width="631" height="461" alt="Architektur drawio" src="https://github.com/user-attachments/assets/f0c81eb0-17a1-4284-afd6-554b7f948d26" />

### UML Klassendiagramm

> Siehe `Documentation/klassendiagramm.jpg` für das vollständige Klassendiagramm.

### Schichten

| Schicht         | Technologie                             |
|-----------------|-----------------------------------------|
| UI              | NiceGUI (browserbasierte Seiten)        |
| Anwendungslogik | Service-Klassen, Seitencontroller       |
| Persistenz      | SQLite + SQLModel ORM + Database-Facade |

### Designentscheidungen

- **MVC-Struktur (Model–View–Controller):** Trennt UI-Seiten (`ui/`), Domänenmodelle (`model/`) und Geschäftslogik (
  `service/`, `db/`), was das Projekt einfacher testbar und erweiterbar macht.
- **Facade Pattern:** Die Klasse `Database` kapselt das gesamte SQLite/SQLModel-Setup, Session-Management und
  Migrationen — der Rest der Anwendung ruft nur ihre öffentlichen Methoden auf.

### Verwendete Entwurfsmuster

- **Model-View-Controller / geschichtete MVC-Variante:** MVC ist hier sinnvoll, weil die Anwendung eine grafische
  Browser-Oberfläche, Benutzerinteraktionen, Geschäftsobjekte und Datenbankzugriff hat. Die Trennung dieser
  Verantwortlichkeiten macht das Projekt einfacher zu verstehen, zu testen und zu erweitern.
- **Facade Pattern:** Facade ist sinnvoll, weil die Datenbankeinrichtung mehrere technische Details umfasst (
  Engine-Erstellung, Schema-Migration, Session-Lifecycle). Der Rest der Anwendung muss nicht wissen, wie der
  Datenbankmotor, Tabellen und Sessions verwaltet werden.

---
<a id="-datenbank-und-orm"></a>

## 🗄️ Datenbank und ORM

Die Anwendung verwendet **SQLModel**, um Domänenobjekte auf eine SQLite-Datenbank (`movies.db`) abzubilden.

### Entitäten

| Entität | Beschreibung                                                                             |
|---------|------------------------------------------------------------------------------------------|
| `Movie` | Film im Katalog (Titel, Genre, Dauer, Altersfreigabe, Erscheinungsjahr, Regisseur, etc.) |
| `User`  | Registrierter Benutzer mit Rollen-Flag (`is_admin`)                                      |

### Beziehungen

- Ein `User` (Admin) kann viele `Movie`-Datensätze verwalten
- Jede Buchung verknüpft einen `Movie` mit einer oder mehreren Personen (in-memory berechnet, Ausgabe als PDF)

---

## ✅ Projektanforderungen

### 1. Browserbasierte App (NiceGUI)

Die Anwendung läuft vollständig im Browser via NiceGUI. Benutzer können:

- Den Filmkatalog auf der Startseite durchsuchen
- Sich als Admin oder Kunde anmelden
- Einen Film auswählen und eine Ticketbuchung konfigurieren
- Eine Live-Preisaufschlüsselung pro Person sehen
- Das generierte PDF-Ticket herunterladen

Architekturhinweis (gemäss SS26-Richtlinien): Der Browser ist ein Thin Client; UI-Zustand und Geschäftslogik liegen auf
der serverseitigen NiceGUI-App.

### 2. Datenvalidierung

Die Anwendung validiert alle Benutzereingaben, um Datenintegrität und eine reibungslose Benutzererfahrung
sicherzustellen. Diese Prüfungen verhindern Abstürze und leiten den Benutzer zur korrekten Eingabe, entsprechend den
Validierungsanforderungen der Projektrichtlinien.

- Alterswerte müssen nicht-negative Ganzzahlen sein
- Personennamen dürfen nicht leer sein
- Die Vorstellungszeit muss eine gültige Stunde (0–23) sein
- Filmattribute (Titel, Genre, Dauer, Altersfreigabe, Erscheinungsjahr) werden bei der Erstellung validiert
- Altersfreigabe-Prüfungen verhindern Buchungen für minderjährige Personen

### 3. Datenbankmanagement

Alle persistenten Daten werden via **SQLModel** (ORM auf Basis von SQLAlchemy) verwaltet:

- `Movie`-Datensätze werden über die `Database`-Facade erstellt, gelesen, aktualisiert und gelöscht
- `User`-Datensätze (inkl. Standard-Admin) werden über dieselbe Facade verwaltet
- Schema-Migrationen (z. B. Hinzufügen der Spalte `isAdmin`) werden beim Start automatisch ausgeführt

---
<a id="-implementierung"></a>

## ⚙️ Implementierung

### Technologie

- Python 3.x
- NiceGUI
- SQLModel / SQLAlchemy
- ReportLab
- Stripe
- pytest

### 📚 Verwendete Bibliotheken

| Bibliothek        | Zweck                                         |
|-------------------|-----------------------------------------------|
| `nicegui`         | Browserbasiertes UI-Framework                 |
| `sqlmodel`        | ORM für Datenmodelle und Datenbankzugriff     |
| `sqlalchemy`      | Datenbank-Toolkit (wird von SQLModel genutzt) |
| `reportlab`       | PDF-Ticket-Generierung                        |
| `python-dotenv`   | Konfiguration via Umgebungsvariablen          |
| `stripe`          | Zahlungsabwicklung via Stripe Checkout        |   
| `omdb / requests` | Filmdaten und Poster via OMDb API             |   
| `pytest`          | Testing                                       |
| `pytest-cov`      | Test-Coverage-Auswertung                      |   

---

## 📂 Repository-Struktur

```
kinoverwaltungssystem/
├── __main__.py
├── application.py
├── constants.py
├── movies.db
├── db/
│   └── database.py
├── model/
│   ├── auth.py
│   ├── movie_model.py
│   └── user_model.py
├── service/
│   ├── __init__.py
│   └── ticket_service.py
└── ui/
    ├── home_ui.py
    ├── login_ui.py
    ├── movie_ui.py
    ├── navbar.py
    ├── ticket_success_ui.py
    └── ticket_ui.py
tests/
├── test_unit.py
├── test_database.py
└── test_integration.py
```

---

## 🚀 Ausführung

### 1. Projekteinrichtung

Python 3.13 (oder die Kursversion) wird benötigt.

Virtuelle Umgebung erstellen und aktivieren:

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\Activate
```

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

### 2. Konfiguration

Das Projekt benötigt eine `.env`-Datei im Projekt-Root. Kopiere die Vorlage und fülle die Werte aus:

```bash
cp .env.example .env
```

Du brauchst Keys von [Stripe](https://dashboard.stripe.com/apikeys) und [OMDb](https://www.omdbapi.com/apikey.aspx) (
beide kostenlos).

> ⚠️ Die `.env`-Datei enthält Secrets und darf **nicht** committet werden – sie steht bereits in der `.gitignore`.

### Stripe-Zahlungsintegration

Die App unterstützt echte Kartenzahlungen via Stripe Checkout.  
Ohne `STRIPE_SECRET_KEY` läuft die App im **Demo-Modus** (kein echter Zahlungsfluss, PDF-Download direkt).

**So richtest du Stripe ein:**

1. Kostenlosen Account auf [stripe.com](https://stripe.com) erstellen
2. Im Dashboard unter **Developers → API keys** den **Secret key** (`sk_test_...`) kopieren
3. In die `.env`-Datei eintragen (Kommentare für Windows / macOS beachten):

- STRIPE_SECRET_KEY=sk_test_...
- APP_URL=http://localhost:8080

```bash
pip install stripe
```

**Testzahlung durchführen (Stripe Test-Modus):**

| Karte               | Nummer                | Ablauf                   | CVC                    |
|---------------------|-----------------------|--------------------------|------------------------|
| Visa (Erfolg)       | `4242 4242 4242 4242` | Beliebig (z. B. `12/34`) | Beliebig (z. B. `123`) |
| Mastercard (Erfolg) | `5555 5555 5555 4444` | Beliebig                 | Beliebig               |
| Karte abgelehnt     | `4000 0000 0000 0002` | Beliebig                 | Beliebig               |

> ⚠️ Im Test-Modus werden **keine echten Zahlungen** verarbeitet. Für Produktion den `sk_live_...`-Key verwenden.

### Omdb-API

> OMDb wird für das automatische Laden von Filmpostern und Metadaten verwendet.
<br>
<br>

Für die Datenbank ist keine manuelle Konfiguration erforderlich. Beim ersten Start erstellt die Anwendung automatisch:

- Die SQLite-Datenbank (`kinoverwaltungssystem/movies.db`)
- Einen Standard-Admin-Account:
    - **E-Mail:** `admin@kinoverwaltung.ch`
    - **Passwort:** `admin123`

### 3. Starten

```bash
python -m kinoverwaltungssystem
```

Die im Terminal angezeigte URL öffnen (Standard: `http://localhost:8080`).

### 4. Benutzung

**Filme durchsuchen (Kunde):**

1. Startseite öffnen — der Filmkatalog wird automatisch angezeigt.
2. Auf einen Film klicken, um die Ticketbuchungsseite zu öffnen.

**Ticket buchen:**

1. Vorstellungszeit eingeben und auswählen, ob es ein Wochenende ist.
2. Eine oder mehrere Personen hinzufügen (Name, Alter, Student-Flag).
3. Die Preisaufschlüsselung (inkl. aller Rabatte und Zuschläge) aktualisiert sich live.
4. Auf **Checkout** klicken, um das PDF-Ticket zu generieren und herunterzuladen.

**Filme verwalten (Admin):**

1. Unter `/login` mit den Admin-Zugangsdaten anmelden.
2. Zu `/movies` navigieren, um Filme hinzuzufügen, zu bearbeiten oder zu löschen.

> Screenshots der Hauptseiten hier einfügen (oder Link zu einem kurzen Video):

---

## 🧪 Tests

> Erkläre, was getestet wird und wie die Tests ausgeführt werden.

Alle Tests ausführen:

```bash
pytest tests/
```

Mit Coverage-Auswertung:

```bash
pytest --cov=kinoverwaltungssystem tests/
```

### Test-Mix

- **Unit-Tests** (`test_unit.py`): z. B. Preisberechnung pro Altersgruppe, Rabattlogik für Studenten, Wochenendzuschlag,
  Spätvorstellungszuschlag, kein Rabatt bei nicht zutreffenden Kriterien
- **DB-Tests** (`test_database.py`): z. B. Filmkatalog-Abfrage gibt geseedete Daten zurück, User-Speicherung persistiert
  korrekt, Admin-Erstellung beim ersten Start
- **Integrationstests** (`test_integration.py`): z. B. vollständiger Ticketbuchungsfluss generiert ein herunterladbares
  PDF, Altersfreigabe-Prüfung blockiert Buchung für Minderjährige

### Vorlage für Testfälle

| Feld                   | Beschreibung                               |
|------------------------|--------------------------------------------|
| Test-ID                | Eindeutiger Bezeichner (z. B. TC_001)      |
| Titel                  | Worum geht es im Test?                     |
| Vorbedingungen         | Anforderungen vor der Testausführung       |
| Testschritte           | Auszuführende Aktionen                     |
| Testdaten / Eingabe    | Konkrete Eingabewerte                      |
| Erwartetes Ergebnis    | Was sollte passieren                       |
| Tatsächliches Ergebnis | Was tatsächlich passiert ist               |
| Status                 | Bestanden / Fehlgeschlagen                 |
| Kommentare             | Zusätzliche Hinweise oder gefundene Fehler |

---

## 👥 Team & Beiträge

> Trage die individuellen Beiträge der Teammitglieder ein.

| Name        | Beitrag                             |
|-------------|-------------------------------------|
| Lukas Folch | NiceGUI + documentation             |
| Simon Moor  | Database + documentation            |
| Livio Fritz | Business logic + UI + documentation |

---

## 📝 Lizenz

Dieses Projekt wurde ausschliesslich für Bildungszwecke im Rahmen des Moduls «Advanced Programming» an der FHNW
erstellt.

MIT License
