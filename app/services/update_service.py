"""In-app ZIP-Update-Mechanismus.

Ablauf:
1. system_admin lädt ein Release-ZIP hoch (POST /admin/system/update)
2. ZIP wird validiert (muss app/, pyproject.toml enthalten)
3. Inhalt wird in ein temporäres Verzeichnis extrahiert
4. Kritische Dateien (.env, alembic/versions/, static/img/uploads/) werden nie überschrieben
5. Neue Dateien werden über die bestehende Installation kopiert
6. alembic upgrade head wird ausgeführt
7. Gunicorn erhält SIGHUP (graceful reload) oder systemctl restart
8. Ergebnis wird zurückgegeben
"""

import os
import shutil
import signal
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

APP_ROOT = Path(__file__).parent.parent.parent  # Projektverzeichnis

# Dateien und Verzeichnisse, die beim Update NIEMALS überschrieben werden
PROTECTED_PATHS = {
    ".env",
    ".env.local",
    "alembic/versions",     # eigene Migrationen bleiben
    "app/static/img/uploads",  # hochgeladene Logos etc.
}


def _is_protected(rel_path: str) -> bool:
    for p in PROTECTED_PATHS:
        if rel_path == p or rel_path.startswith(p + "/") or rel_path.startswith(p + os.sep):
            return True
    return False


def validate_zip(zip_path: Path) -> tuple[bool, str]:
    """Prüft ob das ZIP eine gültige App-Struktur enthält."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
        has_app = any(n.startswith("app/") or n.startswith("app\\") for n in names)
        has_pyproject = any(n == "pyproject.toml" or n.endswith("/pyproject.toml") for n in names)
        if not has_app:
            return False, "ZIP enthält kein app/-Verzeichnis"
        if not has_pyproject:
            return False, "ZIP enthält keine pyproject.toml"
        return True, "OK"
    except zipfile.BadZipFile:
        return False, "Ungültige ZIP-Datei"


def apply_update(zip_path: Path) -> dict:
    """
    Extrahiert das ZIP und kopiert Dateien über die bestehende Installation.
    Gibt ein Dict mit {success, message, files_updated, migrations_applied} zurück.
    """
    valid, msg = validate_zip(zip_path)
    if not valid:
        return {"success": False, "message": msg}

    files_updated: list[str] = []
    skipped: list[str] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # ZIP extrahieren
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp)

        # Falls das ZIP einen Root-Ordner hat (z.B. release-2.0.0/), diesen als Basis nehmen
        entries = list(tmp.iterdir())
        if len(entries) == 1 and entries[0].is_dir():
            src_root = entries[0]
        else:
            src_root = tmp

        # Dateien kopieren
        for src_file in src_root.rglob("*"):
            if src_file.is_dir():
                continue
            rel = src_file.relative_to(src_root).as_posix()
            if _is_protected(rel):
                skipped.append(rel)
                continue
            dst = APP_ROOT / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst)
            files_updated.append(rel)

    # Migrationen ausführen
    migrations_applied = _run_migrations()

    # Gunicorn graceful reload (SIGHUP)
    reloaded = _reload_server()

    return {
        "success": True,
        "message": "Update erfolgreich eingespielt",
        "files_updated": len(files_updated),
        "files_skipped": len(skipped),
        "migrations_applied": migrations_applied,
        "server_reloaded": reloaded,
    }


def _run_migrations() -> str:
    """Führt alembic upgrade head aus. Gibt Ausgabe oder Fehlermeldung zurück."""
    python = APP_ROOT / ".venv" / "bin" / "python"
    if not python.exists():
        python = Path("python")  # Fallback: System-Python
    try:
        result = subprocess.run(
            [str(python), "-m", "alembic", "upgrade", "head"],
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return "OK"
        return f"Fehler: {result.stderr[:500]}"
    except Exception as e:
        return f"Fehler: {e}"


def _reload_server() -> bool:
    """Sendet SIGHUP an den Gunicorn-Master-Prozess (graceful reload)."""
    pidfile = APP_ROOT / "gunicorn.pid"
    if pidfile.exists():
        try:
            pid = int(pidfile.read_text().strip())
            os.kill(pid, signal.SIGHUP)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    # Fallback: systemctl restart (benötigt sudo-Rechte via sudoers)
    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "einsatzleiter"],
            timeout=10,
            capture_output=True,
        )
        return True
    except Exception:
        return False


def get_current_version() -> str:
    """Liest die aktuelle Version aus pyproject.toml."""
    try:
        content = (APP_ROOT / "pyproject.toml").read_text()
        for line in content.splitlines():
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "unbekannt"
