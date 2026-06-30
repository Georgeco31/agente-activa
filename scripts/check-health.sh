#!/usr/bin/env bash
set -euo pipefail

API_HEALTH_URL="http://localhost:8000/api/v1/health"
FRONTEND_URL_PRIMARY="http://localhost:3000"
FRONTEND_URL_FALLBACK="http://localhost:3001"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "$REPO_ROOT"

OVERALL_STATUS=0

print_section() {
  printf '\n== %s ==\n' "$1"
}

check_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    if lsof -nP -i ":${port}" -sTCP:LISTEN >/dev/null 2>&1; then
      printf 'Port %s: in use\n' "$port"
      lsof -nP -i ":${port}" -sTCP:LISTEN || true
    else
      printf 'Port %s: not listening\n' "$port"
    fi
  else
    printf 'Port %s: skipped because lsof is not available\n' "$port"
  fi
}

print_section "Docker Compose"
if ! command -v docker >/dev/null 2>&1; then
  printf 'Docker: not installed or not in PATH\n'
  OVERALL_STATUS=1
elif ! docker compose version >/dev/null 2>&1; then
  printf 'Docker Compose: not available\n'
  OVERALL_STATUS=1
elif ! docker info >/dev/null 2>&1; then
  printf 'Docker: not running\n'
  OVERALL_STATUS=1
else
  docker compose ps || OVERALL_STATUS=1
fi

print_section "Backend"
if command -v curl >/dev/null 2>&1; then
  if API_RESPONSE="$(curl -fsS --max-time 5 "$API_HEALTH_URL" 2>/dev/null)"; then
    printf 'Backend health OK: %s\n' "$API_RESPONSE"
  else
    printf 'Backend health failed or API is off: %s\n' "$API_HEALTH_URL"
    OVERALL_STATUS=1
  fi
else
  printf 'curl is not available; cannot check backend health.\n'
  OVERALL_STATUS=1
fi

print_section "Frontend"
if command -v curl >/dev/null 2>&1; then
  if curl -fsS --max-time 5 -o /dev/null "$FRONTEND_URL_PRIMARY" 2>/dev/null; then
    printf 'Frontend OK: %s\n' "$FRONTEND_URL_PRIMARY"
  elif curl -fsS --max-time 5 -o /dev/null "$FRONTEND_URL_FALLBACK" 2>/dev/null; then
    printf 'Frontend OK: %s\n' "$FRONTEND_URL_FALLBACK"
  else
    printf 'Frontend appears to be off on ports 3000 and 3001.\n'
    printf 'This is not fatal if the admin dev server is intentionally stopped.\n'
  fi
else
  printf 'curl is not available; cannot check frontend.\n'
fi

print_section "Ports"
check_port "3000"
check_port "3001"
check_port "8000"
check_port "5432"

exit "$OVERALL_STATUS"
