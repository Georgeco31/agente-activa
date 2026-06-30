#!/usr/bin/env bash
set -euo pipefail

DB_SERVICE="db"
DB_NAME="agua_sales"
DB_USER="agua_user"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${REPO_ROOT}/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_NAME="${DB_NAME}_${TIMESTAMP}.dump"
CONTAINER_BACKUP_PATH="/tmp/${BACKUP_NAME}"
LOCAL_BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
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

cd "$REPO_ROOT"

command -v docker >/dev/null 2>&1 || fail "Docker is not installed or not in PATH."
docker compose version >/dev/null 2>&1 || fail "Docker Compose is not available."
docker info >/dev/null 2>&1 || fail "Docker is not running."
service_exists "$DB_SERVICE" || fail "Docker Compose service '${DB_SERVICE}' does not exist."
service_running "$DB_SERVICE" || fail "Docker Compose service '${DB_SERVICE}' is not running."

mkdir -p "$BACKUP_DIR"

printf 'Creating PostgreSQL backup from service "%s"...\n' "$DB_SERVICE"
docker compose exec -T "$DB_SERVICE" pg_dump \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -Fc \
  -f "$CONTAINER_BACKUP_PATH"

docker compose cp "${DB_SERVICE}:${CONTAINER_BACKUP_PATH}" "$LOCAL_BACKUP_PATH"
docker compose exec -T "$DB_SERVICE" rm -f "$CONTAINER_BACKUP_PATH" >/dev/null 2>&1 || true

printf 'Backup created: %s\n' "$LOCAL_BACKUP_PATH"
printf 'Do not commit files from backups/ to Git.\n'
