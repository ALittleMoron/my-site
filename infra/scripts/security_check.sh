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

run_nginx_syntax_check
