# FWWO Einsatzleiter-Hilfswerkzeug

**Digitales Einsatzleiter-Werkzeug für Feuerwehren** — Multi-User, Multi-Organisations-fähig, Echtzeit.

Entwickelt für die Freiwillige Feuerwehr Wolfurt (Vorarlberg), verfügbar für alle österreichischen Feuerwehren.

[![CI](https://github.com/BattloXX/FWWO-Einsatzleiter-Hilfswerkzeug/actions/workflows/ci.yml/badge.svg)](https://github.com/BattloXX/FWWO-Einsatzleiter-Hilfswerkzeug/actions)
![Python](https://img.shields.io/badge/python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![Version](https://img.shields.io/badge/version-2.0.0-orange)

---

## Überblick

Das Werkzeug ersetzt ein Single-File-HTML-Tool durch eine vollwertige Webapp mit:

- **Echtzeit-Kanban-Board** für mehrere Geräte gleichzeitig (WebSockets)
- **REST-API** für automatische Einsatzanlage aus dem Alarmierungssystem
- **Atemschutzüberwachung** mit Rückzugsdruckberechnung (gesetzlich verpflichtend)
- **Multi-Organisationsunterstützung** — mehrere Wehren arbeiten gemeinsam an einem Einsatz
- **Mannschaftsregister** mit Qualifikationen und AGT-Ablaufdaten
- **Archiv & PDF-Export** mit vollständigem Audit-Log und Zeitreise-Funktion
- **PWA** mit Offline-Support und Web-Push-Benachrichtigungen
- **In-App ZIP-Update** — neue Versionen per Upload einspielen, ohne SSH

---

## Autoren

| Name | Rolle |
|------|-------|
| **Johannes Battlogg** ([@BattloXX](https://github.com/BattloXX)) | Lead-Entwicklung, Konzept & Design |
| **Roman Reiter** | Fachberatung Einsatzleitung & Atemschutz |

---

## Versionshistorie

| Version | Datum | Highlights |
|---------|-------|------------|
| **2.0.0** | 2026-05-22 | Multi-Org, System-Admin-Rolle, Settings-Page (Logo/Name), ZIP-Update, Python 3.14, Port 8092 |
| **1.0.0** | 2026-05-22 | Initiale Webapp (FastAPI + HTMX, WebSocket, Atemschutz, PWA, QR-Code, Sprachdiktat) |

---

## Tech-Stack

| Schicht | Technologie |
|---------|-------------|
| Backend | FastAPI (Python 3.14) |
| ORM / Migrationen | SQLAlchemy 2.x + Alembic |
| Datenbank | MariaDB 10.11+ |
| Templates | Jinja2 (Server-rendered) |
| Frontend-Interaktivität | HTMX + Alpine.js |
| Realtime | FastAPI WebSockets (Pub/Sub pro Einsatz) |
| Drag & Drop | SortableJS |
| Auth | Session-Cookies + bcrypt + itsdangerous |
| PDF | WeasyPrint |
| Push | pywebpush (VAPID) |
| QR-Code | qrcode[pil] |
| PWA | Service Worker |
| Deployment | Gunicorn + UvicornWorker, Port **8092**, NGINX, systemd |

---

## Schnellstart (Lokale Entwicklung)

```bash
# 1. Klonen
git clone https://github.com/BattloXX/FWWO-Einsatzleiter-Hilfswerkzeug.git
cd FWWO-Einsatzleiter-Hilfswerkzeug

# 2. Python 3.14 venv
python3.14 -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows

# 3. Abhängigkeiten
pip install -e ".[dev]"

# 4. MariaDB (Docker)
docker run -d --name fwwo-db \
  -e MARIADB_ROOT_PASSWORD=root \
  -e MARIADB_DATABASE=einsatzleiter \
  -e MARIADB_USER=einsatzleiter \
  -e MARIADB_PASSWORD=devpassword \
  -p 3306:3306 mariadb:10.11

# 5. Konfiguration
cp .env.example .env
# DATABASE_URL und SECRET_KEY anpassen

# 6. Datenbank + Seed
alembic upgrade head
python -m app.seed_data

# 7. Server starten
uvicorn app.main:app --reload --port 8092

# Browser: http://localhost:8092  (admin / admin)
```

---

## Produktion (Debian 12 + CloudPanel)

Vollständige Anleitung: [`deploy/README-Deployment.md`](deploy/README-Deployment.md)

```bash
# Systempakete
sudo apt-get install -y python3.14 python3.14-venv python3.14-dev \
    libmariadb-dev libpango-1.0-0 libpangoft2-1.0-0 build-essential

# App installieren
git clone https://github.com/BattloXX/FWWO-Einsatzleiter-Hilfswerkzeug.git \
    /home/clp-einsatz/htdocs/einsatzleiter
cd /home/clp-einsatz/htdocs/einsatzleiter
python3.14 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env && nano .env

alembic upgrade head
python -m app.seed_data

# Systemd-Service
sudo cp deploy/einsatzleiter.service /etc/systemd/system/
sudo systemctl enable --now einsatzleiter
# → App läuft auf Port 8092
```

### NGINX (CloudPanel) — Port 8092 + WebSocket

```nginx
# Statische Dateien direkt ausliefern
location /static/ {
    alias /home/clp-einsatz/htdocs/einsatzleiter/app/static/;
    expires 7d;
}

# WebSocket-Upgrade (zwingend!)
location /ws/ {
    proxy_pass http://127.0.0.1:8092;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
}

# Alle anderen Anfragen
location / {
    proxy_pass http://127.0.0.1:8092;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## Rollen-System

| Rolle | Code | Bereich | Beschreibung |
|-------|------|---------|-------------|
| **Systemadmin** | `system_admin` | Systemweit | Organisationsübergreifender Vollzugriff |
| **Org-Admin** | `org_admin` / `admin` | Eigene Org | Vollzugriff innerhalb der eigenen Organisation |
| **Einsatzleiter** | `incident_leader` | Eigene + kollaborierende Orgs | Einsatz und Atemschutz steuern |
| **AS-Überwacher** | `breathing_supervisor` | Eigene + kollaborierende Orgs | Nur Atemschutzüberwachung |
| **Schriftführer** | `recorder` | Eigene + kollaborierende Orgs | Journal und Meldungen |
| **Beobachter** | `readonly` | Eigene + kollaborierende Orgs | Nur Lesen |

---

## Multi-Organisations-Architektur (v2.0.0)

Mehrere Feuerwehren können in einer Instanz verwaltet werden und gemeinsam an Einsätzen arbeiten.

```
System-Admin (organisationsübergreifend)
    │
    ├── Organisation A (z.B. FF Wolfurt) — Org-Admin A
    │   ├── Benutzer von Org A
    │   ├── Mitglieder von Org A
    │   └── Fahrzeuge von Org A
    │
    └── Organisation B (z.B. FF Lauterach) — Org-Admin B
        ├── Benutzer von Org B
        ├── Mitglieder von Org B
        └── Fahrzeuge von Org B

Gemeinsamer Einsatz:
    Org A erstellt Einsatz → fügt Org B als Kollaborator hinzu
    → Benutzer beider Orgs sehen/bearbeiten den Einsatz
    → Fahrzeuge beider Orgs erscheinen auf dem Board
```

### Org-Verwaltung

- **System-Admin**: `/admin/organisations` — Organisationen anlegen, aktivieren/deaktivieren
- **Org-Admin**: `/admin/settings` — eigene Org bearbeiten (Name, Logo, Farbe, Kontakt)

---

## REST-API

### Einsatz anlegen (Alarmierungssystem)

```http
POST /api/v1/einsatz
X-API-Key: fwwo_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Type: application/json
```

```json
{
  "Key": "426747e9-0126-45bc-a0c1-b51a182de14b",
  "Nummer": 1978,
  "AlarmDatumZeit": "2026-05-19T21:11:11.323",
  "Stufe": "t3",
  "Art": "T",
  "Meldung": "Wolfurt Senderstraße 34 Heizraum überflutet",
  "Einsatzgrund": "Heizraum überflutet",
  "Ort": "Wolfurt",
  "Strasse": "Senderstraße",
  "HausNr": "34",
  "Uebung": false
}
```

**Idempotenz:** Doppelter `Key` → `created: false`, vorhandene ID wird zurückgegeben.

API-Key erstellen:
```bash
python -m app.cli create-api-key --label "Alarmierungssystem"
```

---

## In-App ZIP-Update (v2.0.0)

Updates können über die Weboberfläche eingespielt werden — kein SSH erforderlich.

### Vorgang

1. **Aufruf**: `/admin/system/update` (nur `system_admin`)
2. **Release-ZIP hochladen** (muss `app/` und `pyproject.toml` enthalten)
3. **Automatischer Ablauf:**
   - Validierung des ZIPs
   - Extraktion in temporäres Verzeichnis
   - Kopieren aller Dateien (geschützte Pfade werden übersprungen)
   - `alembic upgrade head`
   - Gunicorn `SIGHUP` (graceful reload)

### Geschützte Dateien (werden nie überschrieben)

| Pfad | Grund |
|------|-------|
| `.env` | Secrets und Konfiguration |
| `alembic/versions/` | Eigene Datenbank-Migrationen |
| `app/static/img/uploads/` | Hochgeladene Logos und Bilder |

### Release-ZIP erstellen

```bash
# Aus Git-Archiv:
git archive --format=zip --prefix=release-2.0.0/ HEAD > release-2.0.0.zip
```

### Sudoers für automatischen Restart (optional)

```sudoers
clp-einsatz ALL=(ALL) NOPASSWD: /bin/systemctl restart einsatzleiter
```

---

## Zentrale Einstellungsseite

`/admin/settings` (für Org-Admin und System-Admin)

- **Logo hochladen** (PNG/JPG/SVG) — erscheint im Header und auf PDF-Berichten
- **Organisationsname** ändern
- **Primärfarbe** (Akzentfarbe, Fahrzeugkarten-Streifen)
- **Kontaktdaten** (E-Mail, Telefon, Adresse)
- **Footer-Text** für PDF-Berichte

---

## Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

CI (GitHub Actions): Lint (ruff) + Typecheck (mypy) + pytest mit MariaDB-Service-Container (Python 3.14)

---

## Dokumentation

29 Seiten Dokumentation auf Deutsch in `docs/wiki/` und im GitHub-Wiki:

**Installation** — Server, Datenbank, App, systemd, NGINX, Erst-Setup, Backups, Updates, Troubleshooting  
**Anwender** — Board, Atemschutz, Personen, PWA, Push, QR-Code, Übungsmodus  
**Administration** — Benutzer/Rollen, Stammdaten, API-Keys, Audit-Log, Statistik  
**Entwickler** — Architektur, Datenmodell, REST-API, WebSocket-Events, Tests, Beitragen

---

## Projektstruktur

```
app/
├── main.py            FastAPI-App v2.0.0, Port 8092
├── config.py          Einstellungen (pydantic-settings)
├── models/            SQLAlchemy-Models (user, master, incident, breathing)
├── routers/           HTTP-Endpunkte (auth, api_v1, ui_*, ws)
│   └── ui_settings.py Einstellungen, Org-Verwaltung, ZIP-Update, About
├── services/
│   └── update_service.py ZIP-Update-Mechanismus
├── core/              security, permissions (system_admin), audit
└── templates/admin/   settings, organisations, system_update, about
alembic/versions/
├── 0001_initial.py    Vollständiges Schema v1.0.0
└── 0002_multiorg_settings_update.py Multi-Org, Settings v2.0.0
deploy/
├── einsatzleiter.service  Port 8092
└── nginx-snippet.conf     Port 8092 + WebSocket
docs/wiki/             29 Wiki-Seiten (Deutsch)
```

---

## Lizenz

MIT License — Freiwillige Feuerwehr Wolfurt  
Nutzung für alle österreichischen Feuerwehren ausdrücklich erwünscht.
