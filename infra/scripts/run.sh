#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/../.." && pwd)"
cd "$repo_dir"

readonly COMPOSE_WAIT_TIMEOUT_SECONDS=180
readonly DEPLOY_DRAIN_SECONDS=10
readonly DEPLOY_STATE_DIR="${repo_dir}/.deploy-state"
readonly ACTIVE_SLOT_FILE="${DEPLOY_STATE_DIR}/active-slot"

require_command() {
    local command_name="$1"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "${command_name} could not be found. Install it." >&2
        exit 1
    fi
}

require_env() {
    local variable_name="$1"
    local message="${2:-${variable_name} must be set in .env.}"

    if [ -z "${!variable_name:-}" ]; then
        echo "$message" >&2
        exit 1
    fi
}

require_environment() {
    local required_variables=(
        "VPN_BIND_ADDRESS"
        "APP_URL_SCHEMA"
        "APP_DEBUG"
        "APP_DOMAIN"
        "APP_SECRET_KEY"
        "APP_USE_CACHE"
        "APP_CONTACT_REQUESTS_ENABLED"
        "OWNER_INIT_LOGIN"
        "OWNER_INIT_PASSWORD"
        "DB_USER"
        "DB_PASSWORD"
        "DB_DRIVER"
        "DB_HOST"
        "DB_PORT"
        "DB_NAME"
        "DB_POOL_PRE_PING"
        "DB_POOL_SIZE"
        "DB_MAX_OVERFLOW"
        "DB_EXPIRE_ON_COMMIT"
        "DB_LOG_QUERY_METRICS"
        "DB_SLOW_QUERY_LOG_THRESHOLD_MS"
        "DB_SLOW_QUERY_LOG_STATEMENT_MAX_LENGTH"
        "AUTH_TOKEN_EXPIRE_SECONDS"
        "AUTH_TOKEN_HEADER_NAME"
        "AUTH_TOKEN_PREFIX"
        "AUTH_PUBLIC_KEY"
        "AUTH_PRIVATE_KEY"
        "MINIO_HOST"
        "MINIO_PORT"
        "MINIO_REGION"
        "MINIO_SECRET_KEY"
        "MINIO_ACCESS_KEY"
        "MINIO_SECURE"
        "MINIO_PUBLIC_URL"
        "MINIO_CORS_MAX_AGE_SECONDS"
        "SENTRY_USE"
        "SENTRY_DSN"
        "VALKEY_HOST"
        "VALKEY_PORT"
        "I18N_DEFAULT_LANGUAGE"
        "COMPETENCY_MATRIX_QUESTION_SUGGESTION_ANONYMOUS_DAILY_LIMIT"
        "TASKIQ_CACHE_WARM_INTERVAL_SECONDS"
        "TASKIQ_RESULT_EXPIRE_SECONDS"
        "CACHE_WARM_ARTICLES_PAGE_SIZE"
        "LE_EMAIL"
        "SSL_CERT"
        "SSL_KEY"
        "IMAGE_TAG"
    )

    for variable_name in "${required_variables[@]}"; do
        if [ "$variable_name" = "VPN_BIND_ADDRESS" ]; then
            require_env "$variable_name" "VPN_BIND_ADDRESS must be set in .env."
            continue
        fi
        require_env "$variable_name"
    done
}

other_slot() {
    local slot="$1"

    case "$slot" in
        blue)
            printf '%s\n' "green"
            ;;
        green)
            printf '%s\n' "blue"
            ;;
        *)
            echo "Unknown deploy slot: ${slot}" >&2
            exit 1
            ;;
    esac
}

read_active_slot() {
    if [ -f "$ACTIVE_SLOT_FILE" ]; then
        cat "$ACTIVE_SLOT_FILE"
        return
    fi

    printf '%s\n' "${ACTIVE_DEPLOY_SLOT:-}"
}

service_is_running() {
    local service_name="$1"

    docker compose ps --services --status running | grep -Fxq "$service_name"
}

compose_up_wait() {
    docker compose up --wait --build -d --wait-timeout "$COMPOSE_WAIT_TIMEOUT_SECONDS" "$@"
}

run_backend_init() {
    docker compose build backend-init
    docker compose run --rm backend-init
}

sync_certificates() {
    docker compose run --rm cert-sync
}

render_and_reload_nginx() {
    docker compose exec \
        -T \
        -e "ACTIVE_BACKEND_SLOT=${ACTIVE_BACKEND_SLOT}" \
        -e "ACTIVE_FRONTEND_SLOT=${ACTIVE_FRONTEND_SLOT}" \
        -e "MINIO_PUBLIC_URL=${MINIO_PUBLIC_URL}" \
        nginx \
        sh -c 'mkdir -p /tmp/nginx-conf.d && cat > /tmp/site.conf.template && envsubst "\$APP_DOMAIN \$SSL_CERT \$SSL_KEY \$ACTIVE_BACKEND_SLOT \$ACTIVE_FRONTEND_SLOT \$MINIO_PUBLIC_URL" < /tmp/site.conf.template > /tmp/nginx-conf.d/site.conf && nginx -s reload' \
        <infra/nginx/templates/site.conf.template
}

switch_nginx() {
    if service_is_running nginx \
        && docker compose exec -T nginx sh -c "grep -q ACTIVE_BACKEND_SLOT /etc/nginx/runtime-templates/site.conf.template"; then
        render_and_reload_nginx
        return
    fi

    compose_up_wait nginx
}

smoke_edge() {
    local edge_health_urls=(
        "https://${APP_DOMAIN}/api/healthcheck"
        "https://${APP_DOMAIN}/healthz"
    )
    local attempt
    local edge_health_url

    for edge_health_url in "${edge_health_urls[@]}"; do
        for attempt in {1..30}; do
            if curl -k -fsS -o /dev/null --max-time 5 "$edge_health_url"; then
                break
            fi
            if [ "$attempt" -eq 30 ]; then
                echo "Edge healthcheck failed: ${edge_health_url}" >&2
                exit 1
            fi
            sleep 1
        done
    done
}

save_active_slot() {
    local slot="$1"

    mkdir -p "$DEPLOY_STATE_DIR"
    printf '%s\n' "$slot" >"$ACTIVE_SLOT_FILE"
}

stop_previous_slot() {
    local previous_slot="$1"

    if [ -z "$previous_slot" ]; then
        return
    fi

    sleep "$DEPLOY_DRAIN_SECONDS"
    docker compose stop "backend-${previous_slot}" "frontend-${previous_slot}" || true
}

if [ ! -f .env ]; then
    echo ".env file could not be found" >&2
    echo "Please create a .env file in the root directory" >&2
    exit 1
fi

require_command docker
require_command curl

if ! docker compose version >/dev/null 2>&1; then
    echo "docker compose plugin could not be found. Install it." >&2
    exit 1
fi

set -a
. .env
set +a

require_environment

previous_slot="$(read_active_slot)"
if [ -z "$previous_slot" ]; then
    target_slot="blue"
else
    target_slot="$(other_slot "$previous_slot")"
fi

export ACTIVE_DEPLOY_SLOT="$target_slot"
export ACTIVE_BACKEND_SLOT="backend-${target_slot}"
export ACTIVE_FRONTEND_SLOT="frontend-${target_slot}"

compose_up_wait postgres valkey minio databasus
run_backend_init
compose_up_wait "$ACTIVE_BACKEND_SLOT" "$ACTIVE_FRONTEND_SLOT" taskiq-worker taskiq-scheduler
sync_certificates
switch_nginx
smoke_edge
save_active_slot "$target_slot"
stop_previous_slot "$previous_slot"

echo "Deployment slot ${target_slot} is active."
