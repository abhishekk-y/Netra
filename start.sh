#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ "${1:-}" == "--local" ]]; then
    shift
    [[ -x .venv/bin/python ]] || python3 -m venv .venv
    exec .venv/bin/python scripts/run_local.py "$@"
fi
command -v docker >/dev/null || { echo 'Install Docker, or use bash start.sh --local --install.' >&2; exit 1; }
docker compose version
docker info --format '{{.ServerVersion}}'
[[ -f .env ]] || cp .env.example .env
docker compose up --build --detach --wait --wait-timeout 180
echo 'Netra: http://localhost:3000'
echo 'API reference: http://localhost:8000/docs'
