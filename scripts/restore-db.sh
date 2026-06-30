#!/usr/bin/env bash
set -euo pipefail

DB_SERVICE="db"
API_SERVICE="api"
DB_NAME="agua_sales"
DB_USER="agua_user"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

usage() {
  printf 'Usage: %s path/to/backup.dump\n' "$0" >&2
}

service_exists() {
  local service_name="$1"
  local services
  services="$(docker compose config --services 2>/dev/null || true)"
  printf '%s\n' "$services" | grep -qx "$service_name"
}

service_running() {
  local service_name="$1"
  local running_service
  running_service="$(docker compose ps --status running --services "$service_name" 2>/dev/null || true)"
  [[ "$running_service" == "$service_name" ]]
}

if [[ $# -ne 1 ]]; then
  usage
  fail "A backup file path is required."
fi

INPUT_BACKUP_PATH="$1"
if [[ ! -f "$INPUT_BACKUP_PATH" ]]; then
  fail "Backup file not found: ${INPUT_BACKUP_PATH}"
fi

BACKUP_DIR="$(cd "$(dirname "$INPUT_BACKUP_PATH")" && pwd)"
BACKUP_FILE="${BACKUP_DIR}/$(basename "$INPUT_BACKUP_PATH")"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONTAINER_RESTORE_PATH="/tmp/agente_activa_restore_$(date +%Y%m%d_%H%M%S).dump"

cd "$REPO_ROOT"

command -v docker >/dev/null 2>&1 || fail "Docker is not installed or not in PATH."
docker compose version >/dev/null 2>&1 || fail "Docker Compose is not available."
docker info >/dev/null 2>&1 || fail "Docker is not running."
service_exists "$DB_SERVICE" || fail "Docker Compose service '${DB_SERVICE}' does not exist."
service_exists "$API_SERVICE" || fail "Docker Compose service '${API_SERVICE}' does not exist."
service_running "$DB_SERVICE" || fail "Docker Compose service '${DB_SERVICE}' is not running."
service_running "$API_SERVICE" || fail "Docker Compose service '${API_SERVICE}' is not running."

cat <<'WARNING'
WARNING: Database restore can be destructive.

- Do not use this in production without a previous backup.
- Test restore first in a local/test environment.
- pg_restore --clean --if-exists can delete or replace existing database objects.

Type RESTORE exactly to continue.
WARNING

if ! read -r CONFIRMATION; then
  fail "Restore aborted. Could not read confirmation."
fi
if [[ "$CONFIRMATION" != "RESTORE" ]]; then
  fail "Restore aborted. Confirmation did not match RESTORE."
fi

printf 'Copying backup into PostgreSQL container...\n'
docker compose cp "$BACKUP_FILE" "${DB_SERVICE}:${CONTAINER_RESTORE_PATH}"

cleanup() {
  docker compose exec -T "$DB_SERVICE" rm -f "$CONTAINER_RESTORE_PATH" >/dev/null 2>&1 || true
}
trap cleanup EXIT

printf 'Restoring database "%s"...\n' "$DB_NAME"
docker compose exec -T "$DB_SERVICE" pg_restore \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --clean \
  --if-exists \
  "$CONTAINER_RESTORE_PATH"

printf 'Applying migrations...\n'
docker compose exec -T "$API_SERVICE" alembic upgrade head

printf 'Running idempotent order status seed...\n'
docker compose exec -T "$API_SERVICE" python -m app.seeds.order_statuses

printf 'Restore completed. Run ./scripts/check-health.sh to verify the system.\n'
