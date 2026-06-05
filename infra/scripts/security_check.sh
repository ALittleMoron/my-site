#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/../.." && pwd)"
template_path="${repo_dir}/infra/nginx/templates/site.conf.template"
nginx_config_path="${repo_dir}/infra/nginx/nginx.conf"
nginx_dockerfile_path="${repo_dir}/infra/nginx/Dockerfile"
compose_path="${repo_dir}/docker-compose.yml"
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

require_file_text() {
    local file_path="$1"
    local expected="$2"

    if ! grep -Fq -- "$expected" "$file_path"; then
        echo "Missing nginx security baseline text in ${file_path}: ${expected}" >&2
        exit 1
    fi
}

reject_file_text() {
    local file_path="$1"
    local expected="$2"

    if grep -Fq -- "$expected" "$file_path"; then
        echo "Unexpected nginx security baseline text in ${file_path}: ${expected}" >&2
        exit 1
    fi
}

require_nginx_unprivileged_alpine_image() {
    local file_path="$1"
    local image_reference
    local image_tag

    image_reference="$(
        awk '
            toupper($1) == "FROM" {
                for (field_index = 2; field_index <= NF; field_index++) {
                    if ($field_index ~ /^--/) {
                        next
                    }
                    print $field_index
                    exit
                }
            }
        ' "$file_path"
    )"

    if [ -z "$image_reference" ]; then
        echo "Missing nginx Dockerfile FROM image in ${file_path}." >&2
        exit 1
    fi

    case "$image_reference" in
        nginxinc/nginx-unprivileged:*)
            image_tag="${image_reference#nginxinc/nginx-unprivileged:}"
            ;;
        *)
            echo "Nginx security baseline requires nginxinc/nginx-unprivileged in ${file_path}: ${image_reference}" >&2
            exit 1
            ;;
    esac

    if [[ ! "$image_tag" =~ (^|-)alpine([0-9.]+)?($|-) ]]; then
        echo "Nginx security baseline requires an Alpine nginx image tag in ${file_path}: ${image_reference}" >&2
        exit 1
    fi
}

run_static_checks() {
    require_nginx_unprivileged_alpine_image "$nginx_dockerfile_path"
    require_file_text "$nginx_dockerfile_path" "USER nginx"
    require_file_text "$nginx_config_path" "pid /tmp/nginx.pid;"
    require_file_text "$nginx_config_path" "proxy_temp_path /tmp/proxy_temp;"
    require_file_text "$nginx_config_path" "client_body_temp_path /tmp/client_temp;"
    require_file_text "$nginx_config_path" "fastcgi_temp_path /tmp/fastcgi_temp;"
    require_file_text "$nginx_config_path" "uwsgi_temp_path /tmp/uwsgi_temp;"
    require_file_text "$nginx_config_path" "scgi_temp_path /tmp/scgi_temp;"
    require_file_text "$template_path" "listen 8080;"
    require_file_text "$template_path" "listen 8443 ssl;"
    reject_file_text "$template_path" "listen 80;"
    reject_file_text "$template_path" "listen 443 ssl;"
    require_file_text "$compose_path" "\"80:8080\""
    require_file_text "$compose_path" "\"443:8443\""
    require_file_text "$template_path" "limit_req_status 429;"
    require_file_text "$template_path" "limit_req_zone \$binary_remote_addr zone=api_per_ip:20m rate=120r/m;"
    require_file_text "$template_path" "limit_req_zone \$binary_remote_addr zone=login_per_ip:10m rate=5r/m;"
    require_file_text "$template_path" "limit_req_zone \$binary_remote_addr zone=contact_per_ip:10m rate=3r/m;"
    require_file_text "$template_path" "limit_req_zone \$binary_remote_addr zone=heavy_read_per_ip:10m rate=30r/m;"
    require_file_text "$template_path" "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
    require_file_text "$template_path" "add_header X-Content-Type-Options \"nosniff\" always;"
    require_file_text "$template_path" "add_header X-Frame-Options \"DENY\" always;"
    require_file_text "$template_path" "add_header Referrer-Policy \"no-referrer\" always;"
    require_file_text "$template_path" "add_header Content-Security-Policy"
    require_file_text "$template_path" "location = /api/auth/login"
    require_file_text "$template_path" "location = /api/contacts"
    require_file_text "$template_path" "location = /api/notes"
    require_file_text "$template_path" "location = /api/notes/tags/search"
    require_file_text "$template_path" "location = /api/competency-matrix/resources/search"
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

run_static_checks
run_nginx_syntax_check
