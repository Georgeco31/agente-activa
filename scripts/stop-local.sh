#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "$REPO_ROOT"

if ! command -v docker >/dev/null 2>&1; then
  printf 'ERROR: Docker is not installed or not in PATH.\n' >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  printf 'ERROR: Docker Compose is not available.\n' >&2
  exit 1
fi

printf 'Stopping local Docker services with docker compose down...\n'
printf 'This does NOT remove volumes, backups, .env files or database data.\n'
printf 'This script does NOT run docker compose down -v.\n'

docker compose down

printf 'Local Docker services stopped.\n'
