#!/usr/bin/env bash
# Frontend-Build (Tailwind CSS).
#
# Verwendung:
#   ./deploy/build-frontend.sh
#
# Voraussetzung: Node.js >= 18, npm.
# Erzeugt das gebuendelte CSS unter app/static/css/app.css und checkt
# es ins Repo ein, damit Deploy-Server ohne Node auskommen.

set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v npm > /dev/null 2>&1; then
  echo "FEHLER: npm nicht gefunden. Installiere Node.js >= 18." >&2
  exit 1
fi

echo ">>> npm install ..."
npm ci --silent || npm install --silent

echo ">>> Tailwind build ..."
npm run build

echo ">>> Fertig. Output: app/static/css/app.css"
ls -la app/static/css/app.css
