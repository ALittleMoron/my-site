#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/../.." && pwd)"
cd "$repo_dir"

require_command() {
    local command_name="$1"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "${command_name} could not be found. Install it." >&2
        exit 1
    fi
}

require_env() {
    local variable_name="$1"

    if [ -z "${!variable_name:-}" ]; then
        echo "${variable_name} must be set in .env." >&2
        exit 1
    fi
}

load_environment() {
    if [ ! -f .env ]; then
        echo ".env file could not be found" >&2
        echo "Please create a .env file in the root directory" >&2
        exit 1
    fi

    set -a
    . .env
    set +a

    require_env APP_DOMAIN
    require_env LE_EMAIL
}

sync_certificates() {
    docker compose run --rm cert-sync
}

reload_nginx_if_running() {
    if docker compose ps --services --status running | grep -Fxq nginx; then
        docker compose exec -T nginx nginx -s reload
    fi
}

issue_certificates() {
    docker compose run --rm --service-ports certbot \
        certonly \
        --standalone \
        --preferred-challenges http \
        --email "$LE_EMAIL" \
        --agree-tos \
        --no-eff-email \
        --keep-until-expiring \
        -d "$APP_DOMAIN" \
        -d "s3.${APP_DOMAIN}"
    sync_certificates
}

renew_certificates() {
    docker compose run --rm certbot \
        renew \
        --webroot \
        --webroot-path=/var/www/certbot
    sync_certificates
    reload_nginx_if_running
}

action="${1:?action is required}"

require_command docker
if ! docker compose version >/dev/null 2>&1; then
    echo "docker compose plugin could not be found. Install it." >&2
    exit 1
fi
load_environment

case "$action" in
    issue)
        issue_certificates
        ;;
    renew)
        renew_certificates
        ;;
    sync)
        sync_certificates
        ;;
    *)
        echo "Unknown TLS action: ${action}" >&2
        exit 2
        ;;
esac
