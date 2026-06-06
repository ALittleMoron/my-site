#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/../.." && pwd)"
nginx_check_temp_dir=""
nginx_check_image_tag=""

cleanup_nginx_syntax_check() {
    if [ -n "$nginx_check_image_tag" ]; then
        docker image rm "$nginx_check_image_tag" >/dev/null 2>&1 || true
    fi
    if [ -n "$nginx_check_temp_dir" ]; then
        rm -rf "$nginx_check_temp_dir"
    fi
}

require_command() {
    local command_name="$1"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "${command_name} could not be found." >&2
        exit 2
    fi
}

require_file_contains() {
    local file_path="$1"
    local pattern="$2"
    local description="$3"

    if ! grep -Fq -- "$pattern" "$file_path"; then
        echo "Missing ${description} in ${file_path}: ${pattern}" >&2
        exit 1
    fi
}

require_file_not_contains() {
    local file_path="$1"
    local pattern="$2"
    local description="$3"

    if grep -Fq -- "$pattern" "$file_path"; then
        echo "Unexpected ${description} in ${file_path}: ${pattern}" >&2
        exit 1
    fi
}

run_private_panel_configuration_check() {
    local compose_file="${repo_dir}/docker-compose.yml"
    local deploy_workflow="${repo_dir}/.github/workflows/_infrastructure.yaml"
    local env_example="${repo_dir}/.env.example"
    local nginx_template="${repo_dir}/infra/nginx/templates/site.conf.template"
    local run_script="${repo_dir}/infra/scripts/run.sh"

    require_file_contains "$env_example" "VPN_BIND_ADDRESS=" "VPN bind address example"
    require_file_contains "$deploy_workflow" "VPN_BIND_ADDRESS" "VPN bind address deployment secret"
    require_file_contains "$run_script" "VPN_BIND_ADDRESS must be set" "VPN bind address startup guard"

    require_file_contains "$compose_file" '"${VPN_BIND_ADDRESS}:18081:18081"' "MinIO Console VPN-only port binding"
    require_file_contains "$compose_file" '"${VPN_BIND_ADDRESS}:18082:18082"' "Databasus VPN-only port binding"
    require_file_not_contains "$compose_file" "-d s3-panel.\${APP_DOMAIN}" "public MinIO Console certificate domain"
    require_file_not_contains "$compose_file" "-d backup.\${APP_DOMAIN}" "public Databasus certificate domain"

    require_file_not_contains "$nginx_template" "server_name s3-panel.\${APP_DOMAIN};" "public MinIO Console virtual host"
    require_file_not_contains "$nginx_template" "server_name backup.\${APP_DOMAIN};" "public Databasus virtual host"
    require_file_contains "$nginx_template" "listen 18081;" "private MinIO Console listener"
    require_file_contains "$nginx_template" "listen 18082;" "private Databasus listener"
}

run_nginx_syntax_check() {
    local cert_dir

    require_command docker
    require_command openssl

    nginx_check_temp_dir="$(mktemp -d)"
    cert_dir="${nginx_check_temp_dir}/certs"
    nginx_check_image_tag="my-site-nginx-security-check:$(date +%s)-$$"
    mkdir -p "$cert_dir"
    trap cleanup_nginx_syntax_check EXIT

    openssl req \
        -x509 \
        -nodes \
        -newkey rsa:2048 \
        -keyout "${cert_dir}/test.key" \
        -out "${cert_dir}/test.crt" \
        -days 1 \
        -subj "/CN=example.test" >/dev/null 2>&1
    chmod 644 "${cert_dir}/test.key" "${cert_dir}/test.crt"

    docker build \
        -f "${repo_dir}/infra/nginx/Dockerfile" \
        -t "$nginx_check_image_tag" \
        "$repo_dir"

    docker run --rm \
        --add-host backend:127.0.0.1 \
        --add-host frontend:127.0.0.1 \
        --add-host minio:127.0.0.1 \
        --add-host databasus:127.0.0.1 \
        -e APP_DOMAIN=example.test \
        -e SSL_CERT=/certs/test.crt \
        -e SSL_KEY=/certs/test.key \
        -v "${cert_dir}:/certs:ro" \
        "$nginx_check_image_tag" \
        nginx -t
}

run_private_panel_configuration_check
run_nginx_syntax_check
