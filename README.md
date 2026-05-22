# Einsatzleiter-Hilfswerkzeug – Feuerwehr Wolfurt

Digitales Kanban-basiertes Einsatzführungswerkzeug für die Freiwillige Feuerwehr Wolfurt.  
Multi-User, Echtzeit-Synchronisation, Atemschutzüberwachung, REST-API für automatische Alarmierung.

## Kurzübersicht

| Merkmal | Details |
|---------|---------|
| Backend | FastAPI + SQLAlchemy + MariaDB |
| Frontend | HTMX + Alpine.js + Jinja2 |
| Echtzeit | WebSockets |
| Deployment | Debian + CloudPanel + systemd |
| Offline | PWA + Service Worker |

## Schnellstart (lokal)

```bash
git clone https://github.com/BattloXX/FWWO-Einsatzleiter-Hilfswerkzeug.git
cd FWWO-Einsatzleiter-Hilfswerkzeug
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env        # .env anpassen
alembic upgrade head
python -m app.seed_data
python -m app.cli create-admin --username admin --password geheim
uvicorn app.main:app --reload
```

Dann: http://localhost:8000

## Dokumentation

Vollständige Installations-, Anwender- und Entwicklerdokumentation im **[GitHub Wiki](../../wiki)**.

## Lizenz

Intern – Freiwillige Feuerwehr Wolfurt
