#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/../.." && pwd)"
minio_check_image_tag=""
minio_check_temp_dir=""
nginx_check_temp_dir=""
nginx_check_image_tag=""

cleanup_security_check_images() {
    if [ -n "$minio_check_image_tag" ]; then
        docker image rm "$minio_check_image_tag" >/dev/null 2>&1 || true
    fi
    if [ -n "$minio_check_temp_dir" ]; then
        rm -rf "$minio_check_temp_dir"
    fi
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

require_file_exists() {
    local file_path="$1"
    local description="$2"

    if [ ! -f "$file_path" ]; then
        echo "Missing ${description}: ${file_path}" >&2
        exit 1
    fi
}

require_frontend_location_has_no_proxy_headers() {
    local file_path="$1"

    if awk '
        $0 ~ /^[[:space:]]*location \/ \{/ {
            in_frontend_location = 1
            next
        }
        in_frontend_location && $0 ~ /^[[:space:]]*\}/ {
            in_frontend_location = 0
            next
        }
        in_frontend_location && $0 ~ /proxy_set_header/ {
            found = 1
        }
        END { exit found ? 0 : 1 }
    ' "$file_path"; then
        echo "Frontend location must inherit server-level proxy headers; move location-level proxy_set_header directives to the server block." >&2
        exit 1
    fi
}

require_file_not_exists() {
    local file_path="$1"
    local description="$2"

    if [ -f "$file_path" ]; then
        echo "Unexpected ${description}: ${file_path}" >&2
        exit 1
    fi
}

require_no_unapproved_network_literals() {
    local description="$1"
    local pattern="$2"
    shift 2

    local file_path
    local line
    local failed=0

    for file_path in "$@"; do
        while IFS= read -r line; do
            case "$line" in
                *"127.0.0.11"*) ;;
                *"127.0.0.1:8080/api/healthcheck/ready"*) ;;
                *"127.0.0.1:4000/healthz"*) ;;
                *"127.0.0.1:8080/nginx-healthz"*) ;;
                *"localhost:9000/minio/health/live"*) ;;
                *)
                    echo "Unexpected ${description} in ${line}" >&2
                    failed=1
                    ;;
            esac
        done < <(grep -En "$pattern" "$file_path" || true)
    done

    if [ "$failed" -ne 0 ]; then
        exit 1
    fi
}

require_no_inspect_visible_secret_environment() {
    local compose_file="$1"
    local secret_patterns=(
        "APP_SECRET_KEY:"
        "AUTH_PRIVATE_KEY:"
        "DB_PASSWORD:"
        "MINIO_ACCESS_KEY:"
        "MINIO_SECRET_KEY:"
        "MINIO_ROOT_PASSWORD:"
        "MINIO_ROOT_USER:"
        "OWNER_INIT_PASSWORD:"
        "POSTGRES_PASSWORD:"
        "SENTRY_DSN:"
    )
    local pattern

    require_file_not_contains "$compose_file" "env_file:" "inspect-visible environment file"

    for pattern in "${secret_patterns[@]}"; do
        require_file_not_contains "$compose_file" "$pattern" "inspect-visible secret environment"
    done
}

require_no_container_file_logs() {
    local file_path
    local line
    local failed=0

    for file_path in "$@"; do
        while IFS= read -r line; do
            case "$line" in
                *"access_log off;"*) ;;
                *"access_log /dev/stdout;"*) ;;
                *"error_log /dev/stderr"*) ;;
                *)
                    echo "Unexpected container file logging directive in ${line}" >&2
                    failed=1
                    ;;
            esac
        done < <(grep -En "(access_log|error_log|/var/log|FileHandler|RotatingFileHandler|--log-file|log_file)" "$file_path" || true)
    done

    if [ "$failed" -ne 0 ]; then
        exit 1
    fi
}

run_deploy_env_configuration_check() {
    local compose_file="${repo_dir}/docker-compose.yml"
    local ci_workflow="${repo_dir}/.github/workflows/ci.yaml"
    local deploy_workflow="${repo_dir}/.github/workflows/_deploy.yaml"
    local backend_image_workflow="${repo_dir}/.github/workflows/_backend_docker_image_security.yaml"
    local frontend_image_workflow="${repo_dir}/.github/workflows/_frontend_docker_image_security.yaml"
    local nginx_image_workflow="${repo_dir}/.github/workflows/_nginx_docker_image_security.yaml"
    local manual_deploy_workflow="${repo_dir}/.github/workflows/deploy.yaml"
    local env_example="${repo_dir}/.env.example"
    local manifest_file="${repo_dir}/infra/deploy/runtime-env.manifest.json"
    local renderer="${repo_dir}/infra/scripts/render_deploy_env.py"
    local rendered_env

    require_command python3
    require_file_exists "$ci_workflow" "CI workflow"
    require_file_exists "$deploy_workflow" "private deploy workflow"
    require_file_exists "$backend_image_workflow" "private backend image security workflow"
    require_file_exists "$frontend_image_workflow" "private frontend image security workflow"
    require_file_exists "$nginx_image_workflow" "private nginx image security workflow"
    require_file_exists "$manual_deploy_workflow" "manual deploy workflow"
    require_file_exists "$manifest_file" "runtime environment manifest"
    require_file_exists "$renderer" "runtime environment renderer"

    require_file_not_contains "$ci_workflow" "runs-on:" "inline CI job runner"
    require_file_not_contains "$ci_workflow" "steps:" "inline CI job steps"
    require_file_contains "$ci_workflow" "dockerfile-lint:" "post-smoke Dockerfile lint job"
    require_file_contains "$ci_workflow" "trivy-config-scan:" "post-smoke Trivy config scan job"
    require_file_contains "$ci_workflow" "backend-docker-image-security:" "backend image security job"
    require_file_contains "$ci_workflow" "frontend-docker-image-security:" "frontend image security job"
    require_file_contains "$ci_workflow" "nginx-docker-image-security:" "nginx image security job"
    require_file_contains "$ci_workflow" "infra-security:" "post-smoke infrastructure security job"
    require_file_contains "$ci_workflow" "_backend_docker_image_security.yaml" "backend image security workflow"
    require_file_contains "$ci_workflow" "_frontend_docker_image_security.yaml" "frontend image security workflow"
    require_file_contains "$ci_workflow" "_nginx_docker_image_security.yaml" "nginx image security workflow"
    require_file_not_contains "$ci_workflow" "_deploy.yaml" "private deploy workflow call"
    require_file_not_contains "$ci_workflow" "uses: ./.github/workflows/_docker_image_security.yaml" "generic image security workflow"
    require_file_not_contains "$ci_workflow" "post-smoke-security:" "combined post-smoke security job"
    require_file_not_contains "$ci_workflow" "run-infra-security: true" "combined Docker security input"
    require_file_not_contains "$ci_workflow" "deploy:" "CI deploy job"
    require_file_contains "$manual_deploy_workflow" "workflow_dispatch:" "manual deploy trigger"
    require_file_not_contains "$manual_deploy_workflow" "push:" "automatic deploy trigger"
    require_file_not_contains "$manual_deploy_workflow" "needs:" "manual deploy CI needs graph"
    require_file_not_contains "$manual_deploy_workflow" "runs-on:" "inline manual deploy job runner"
    require_file_not_contains "$manual_deploy_workflow" "steps:" "inline manual deploy job steps"
    require_file_contains "$manual_deploy_workflow" "deploy:" "manual deploy job"
    require_file_contains "$manual_deploy_workflow" "if: github.ref == 'refs/heads/main'" "main-only deploy gate"
    require_file_contains "$manual_deploy_workflow" "uses: ./.github/workflows/_deploy.yaml" "private deploy workflow call"
    require_file_contains "$manual_deploy_workflow" "secrets: inherit" "deploy reusable workflow secrets pass-through"
    require_file_contains "$deploy_workflow" "environment: production" "production deployment environment approval"
    require_file_contains "$deploy_workflow" "vars.REMOTE_HOST" "remote host GitHub variable"
    require_file_contains "$deploy_workflow" "vars.REMOTE_USER" "remote user GitHub variable"
    require_file_contains "$deploy_workflow" "vars.REMOTE_PATH" "remote path GitHub variable"
    require_file_contains "$deploy_workflow" "secrets.SSH_PRIVATE_KEY" "SSH private key deploy secret"
    require_file_contains "$deploy_workflow" "cp -a Makefile docker-compose.yml backend/ frontend/ infra/ .env .deploy-payload/" "runtime file deploy sync"
    require_file_contains "$deploy_workflow" "make run" "remote stack restart"
    require_file_not_contains "$ci_workflow" "Create .env file from secrets" "manual secret echo env generation"
    require_file_not_contains "$ci_workflow" "REMOTE_HOST=\${{ secrets.REMOTE_HOST }}" "remote host runtime env entry"
    require_file_not_contains "$ci_workflow" "SSH_PRIVATE_KEY=" "SSH private key runtime env entry"
    require_file_not_contains "$ci_workflow" "DOCKER_PASSWORD=" "Docker password runtime env entry"
    require_file_not_contains "$ci_workflow" "CACHE_WARM_NOTES_PAGE_SIZE" "stale cache warm env name"
    require_file_not_contains "$ci_workflow" "issue_certificates" "deploy-time certificate issue input"
    require_file_not_contains "$ci_workflow" "make certbot-issue" "deploy-time certificate issue step"
    require_file_not_contains "$manual_deploy_workflow" "Create .env file from secrets" "manual secret echo env generation"
    require_file_not_contains "$manual_deploy_workflow" "REMOTE_HOST=\${{ secrets.REMOTE_HOST }}" "remote host runtime env entry"
    require_file_not_contains "$manual_deploy_workflow" "SSH_PRIVATE_KEY=" "SSH private key runtime env entry"
    require_file_not_contains "$manual_deploy_workflow" "DOCKER_PASSWORD=" "Docker password runtime env entry"
    require_file_not_contains "$manual_deploy_workflow" "CACHE_WARM_NOTES_PAGE_SIZE" "stale cache warm env name"
    require_file_not_contains "$manual_deploy_workflow" "issue_certificates" "deploy-time certificate issue input"
    require_file_not_contains "$manual_deploy_workflow" "make certbot-issue" "deploy-time certificate issue step"
    require_file_not_contains "$deploy_workflow" "Create .env file from secrets" "manual secret echo env generation"
    require_file_not_contains "$deploy_workflow" "REMOTE_HOST=\${{ secrets.REMOTE_HOST }}" "remote host runtime env entry"
    require_file_not_contains "$deploy_workflow" "SSH_PRIVATE_KEY=" "SSH private key runtime env entry"
    require_file_not_contains "$deploy_workflow" "DOCKER_PASSWORD=" "Docker password runtime env entry"
    require_file_not_contains "$deploy_workflow" "CACHE_WARM_NOTES_PAGE_SIZE" "stale cache warm env name"
    require_file_not_contains "$deploy_workflow" "issue_certificates" "deploy-time certificate issue input"
    require_file_not_contains "$deploy_workflow" "make certbot-issue" "deploy-time certificate issue step"

    require_file_contains "$manifest_file" '"CACHE_WARM_ARTICLES_PAGE_SIZE"' "cache warm articles page size manifest entry"
    require_file_not_contains "$manifest_file" "CACHE_WARM_NOTES_PAGE_SIZE" "stale cache warm manifest entry"
    require_file_not_contains "$manifest_file" "REMOTE_HOST" "deploy remote host manifest entry"
    require_file_not_contains "$manifest_file" "SSH_PRIVATE_KEY" "deploy SSH key manifest entry"
    require_file_not_contains "$manifest_file" "DOCKER_PASSWORD" "Docker password manifest entry"

    require_file_not_contains "$env_example" "REMOTE_HOST=" "remote host local env example entry"
    require_file_not_contains "$env_example" "SSH_PRIVATE_KEY=" "SSH private key local env example entry"
    require_file_not_contains "$env_example" "DOCKER_PASSWORD=" "Docker password local env example entry"
    require_file_not_contains "$env_example" "DOCKER_REGISTRY=" "Docker registry local env example entry"
    require_file_not_contains "$env_example" "DOCKER_USERNAME=" "Docker username local env example entry"

    require_file_not_contains "$compose_file" "\${DOCKER_REGISTRY}" "runtime Docker registry interpolation"
    require_file_not_contains "$compose_file" "\${DOCKER_USERNAME}" "runtime Docker username interpolation"
    require_file_contains "$compose_file" "image: my_site_application:\${IMAGE_TAG:-latest}" "local backend image tag"

    rendered_env="$(mktemp)"
    (
        export IMAGE_TAG="security-check-sha"
        export GITHUB_ENV_VARS_JSON='{"OWNER_INIT_LOGIN":"owner","APP_CONTACT_REQUESTS_ENABLED":"false","APP_DEBUG":"false","APP_DOMAIN":"example.test","APP_URL_SCHEMA":"https","APP_USE_CACHE":"true","AUTH_PUBLIC_KEY":"-----BEGIN PUBLIC KEY-----\npublic\n-----END PUBLIC KEY-----","AUTH_TOKEN_EXPIRE_SECONDS":"172800","AUTH_TOKEN_HEADER_NAME":"Authorization","AUTH_TOKEN_PREFIX":"Bearer","CACHE_WARM_ARTICLES_PAGE_SIZE":"10","COMPETENCY_MATRIX_QUESTION_SUGGESTION_ANONYMOUS_DAILY_LIMIT":"10","DB_DRIVER":"postgresql+psycopg","DB_EXPIRE_ON_COMMIT":"false","DB_HOST":"postgres","DB_LOG_QUERY_METRICS":"false","DB_MAX_OVERFLOW":"20","DB_NAME":"my_site_database","DB_POOL_PRE_PING":"true","DB_POOL_SIZE":"10","DB_PORT":"5432","DB_SLOW_QUERY_LOG_STATEMENT_MAX_LENGTH":"1000","DB_SLOW_QUERY_LOG_THRESHOLD_MS":"250","DB_USER":"postgres","I18N_DEFAULT_LANGUAGE":"ru","LE_EMAIL":"ops@example.test","MINIO_CORS_MAX_AGE_SECONDS":"300","MINIO_HOST":"minio","MINIO_PORT":"9000","MINIO_REGION":"us-east-1","MINIO_PUBLIC_URL":"https://s3.example.test","MINIO_SECURE":"false","SENTRY_USE":"false","SSL_CERT":"/certs/fullchain.pem","SSL_KEY":"/certs/privkey.pem","TASKIQ_CACHE_WARM_INTERVAL_SECONDS":"3600","TASKIQ_RESULT_EXPIRE_SECONDS":"3600","VALKEY_HOST":"valkey","VALKEY_PORT":"6379","VPN_BIND_ADDRESS":"10.77.0.1"}'
        export GITHUB_SECRETS_JSON='{"OWNER_INIT_PASSWORD":"owner-password","APP_SECRET_KEY":"app-secret","AUTH_PRIVATE_KEY":"-----BEGIN PRIVATE KEY-----\nprivate\n-----END PRIVATE KEY-----","DB_PASSWORD":"postgres-password","MINIO_ACCESS_KEY":"minio-access","MINIO_SECRET_KEY":"minio-secret","SENTRY_DSN":""}'
        python3 "$renderer" --manifest "$manifest_file" --output "$rendered_env"
    )
    require_file_contains "$rendered_env" 'CACHE_WARM_ARTICLES_PAGE_SIZE="10"' "rendered cache warm articles page size"
    require_file_contains "$rendered_env" 'MINIO_REGION="us-east-1"' "rendered MinIO region"
    require_file_contains "$rendered_env" 'MINIO_PUBLIC_URL="https://s3.example.test"' "rendered public MinIO URL"
    require_file_contains "$rendered_env" 'AUTH_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nprivate\n-----END PRIVATE KEY-----"' "rendered escaped multiline private key"
    require_file_not_contains "$rendered_env" "CACHE_WARM_NOTES_PAGE_SIZE" "stale cache warm rendered env entry"
    require_file_not_contains "$rendered_env" "REMOTE_HOST" "deploy remote host rendered env entry"
    require_file_not_contains "$rendered_env" "SSH_PRIVATE_KEY" "deploy SSH key rendered env entry"
    require_file_not_contains "$rendered_env" "DOCKER_PASSWORD" "Docker password rendered env entry"
    rm -f "$rendered_env"

    if (
        export IMAGE_TAG="security-check-sha"
        export GITHUB_ENV_VARS_JSON='{}'
        export GITHUB_SECRETS_JSON='{}'
        python3 "$renderer" --manifest "$manifest_file" --output "$rendered_env"
    ) >/dev/null 2>&1; then
        echo "Renderer accepted missing required deployment values." >&2
        rm -f "$rendered_env"
        exit 1
    fi
    rm -f "$rendered_env"
}

run_private_panel_configuration_check() {
    local compose_file="${repo_dir}/docker-compose.yml"
    local env_example="${repo_dir}/.env.example"
    local manifest_file="${repo_dir}/infra/deploy/runtime-env.manifest.json"
    local nginx_template="${repo_dir}/infra/nginx/templates/site.conf.template"
    local run_script="${repo_dir}/infra/scripts/run.sh"

    require_file_contains "$env_example" "VPN_BIND_ADDRESS=" "VPN bind address example"
    require_file_contains "$manifest_file" "VPN_BIND_ADDRESS" "VPN bind address deployment variable"
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

run_healthcheck_configuration_check() {
    local compose_file="${repo_dir}/docker-compose.yml"
    local deploy_workflow="${repo_dir}/.github/workflows/_deploy.yaml"
    local nginx_template="${repo_dir}/infra/nginx/templates/site.conf.template"
    local run_script="${repo_dir}/infra/scripts/run.sh"
    local backend_start_script="${repo_dir}/backend/start_application.sh"
    local frontend_server="${repo_dir}/frontend/src/server-app.ts"
    local compose_secret_script="${repo_dir}/infra/scripts/compose_secrets.sh"

    require_command docker
    if ! docker compose version >/dev/null 2>&1; then
        echo "docker compose plugin could not be found." >&2
        exit 2
    fi

    (
        export APP_CONTACT_REQUESTS_ENABLED="false"
        export APP_DEBUG="false"
        export APP_DOMAIN="example.test"
        export APP_SECRET_KEY="app-secret"
        export APP_URL_SCHEMA="https"
        export APP_USE_CACHE="true"
        export AUTH_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nprivate\n-----END PRIVATE KEY-----"
        export AUTH_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\npublic\n-----END PUBLIC KEY-----"
        export AUTH_TOKEN_EXPIRE_SECONDS="172800"
        export AUTH_TOKEN_HEADER_NAME="Authorization"
        export AUTH_TOKEN_PREFIX="Bearer"
        export CACHE_WARM_ARTICLES_PAGE_SIZE="10"
        export COMPETENCY_MATRIX_QUESTION_SUGGESTION_ANONYMOUS_DAILY_LIMIT="10"
        export DB_DRIVER="postgresql+psycopg"
        export DB_EXPIRE_ON_COMMIT="false"
        export DB_HOST="postgres"
        export DB_LOG_QUERY_METRICS="false"
        export DB_MAX_OVERFLOW="20"
        export DB_NAME="my_site_database"
        export DB_PASSWORD="postgres-password"
        export DB_POOL_PRE_PING="true"
        export DB_POOL_SIZE="10"
        export DB_PORT="5432"
        export DB_SLOW_QUERY_LOG_STATEMENT_MAX_LENGTH="1000"
        export DB_SLOW_QUERY_LOG_THRESHOLD_MS="250"
        export DB_USER="my_site"
        export IMAGE_TAG="security-check-sha"
        export I18N_DEFAULT_LANGUAGE="ru"
        export LE_EMAIL="ops@example.test"
        export MINIO_ACCESS_KEY="minio-access"
        export MINIO_CORS_MAX_AGE_SECONDS="300"
        export MINIO_HOST="minio"
        export MINIO_PORT="9000"
        export MINIO_PUBLIC_URL="https://s3.example.test"
        export MINIO_REGION="us-east-1"
        export MINIO_SECURE="false"
        export MINIO_SECRET_KEY="minio-secret"
        export OWNER_INIT_LOGIN="owner"
        export OWNER_INIT_PASSWORD="owner-password"
        export SENTRY_DSN=""
        export SENTRY_USE="false"
        export SSL_CERT="/certs/fullchain.pem"
        export SSL_KEY="/certs/privkey.pem"
        export TASKIQ_CACHE_WARM_INTERVAL_SECONDS="3600"
        export TASKIQ_RESULT_EXPIRE_SECONDS="3600"
        export VALKEY_HOST="valkey"
        export VALKEY_PORT="6379"
        export VPN_BIND_ADDRESS="10.77.0.1"
        export COMPOSE_SECRETS_DIR
        COMPOSE_SECRETS_DIR="$(mktemp -d)"
        trap 'rm -rf "$COMPOSE_SECRETS_DIR"' EXIT
        # shellcheck source=compose_secrets.sh
        . "$compose_secret_script"
        prepare_compose_secret_files
        docker compose -f "$compose_file" config >/dev/null
    )

    require_file_contains "$compose_file" "backend-blue:" "blue backend service"
    require_file_contains "$compose_file" "backend-green:" "green backend service"
    require_file_contains "$compose_file" "frontend-blue:" "blue frontend service"
    require_file_contains "$compose_file" "frontend-green:" "green frontend service"
    require_file_contains "$compose_file" "backend-init:" "one-shot backend init service"
    require_file_contains "$compose_file" "/api/healthcheck/ready" "backend readiness healthcheck"
    require_file_contains "$compose_file" "/healthz" "frontend healthcheck"
    require_file_contains "$compose_file" "/nginx-healthz" "nginx healthcheck"
    require_file_contains "$compose_file" "MINIO_API_CORS_ALLOW_ORIGIN: \${APP_URL_SCHEMA}://\${APP_DOMAIN}" "MinIO public file CORS origin"
    require_file_contains "$compose_file" 'user: "10001:10001"' "backend explicit non-root UID/GID"
    require_file_contains "$compose_file" 'user: "1000:1000"' "frontend explicit non-root UID/GID"
    require_file_contains "$compose_file" 'user: "101:101"' "nginx explicit non-root UID/GID"
    require_file_contains "$compose_file" 'user: "70:70"' "Postgres explicit non-root UID/GID"
    require_file_contains "$compose_file" 'user: "999:999"' "Valkey explicit non-root UID/GID"
    require_file_contains "$compose_file" 'user: "10002:10002"' "MinIO explicit non-root UID/GID"
    require_file_contains "$compose_file" "dockerfile: infra/minio/Dockerfile" "MinIO non-root wrapper Dockerfile"
    require_file_contains "$compose_file" 'command: ["server", "/data", "--console-address", ":9001"]' "MinIO exec-form command"
    require_file_contains "$compose_file" "read_only: true" "app-owned read-only root filesystems"
    require_file_contains "$compose_file" "cap_drop:" "runtime Linux capability drop"
    require_file_contains "$compose_file" "no-new-privileges:true" "runtime no-new-privileges"
    require_file_contains "$compose_file" "/tmp:mode=1777,uid=10001,gid=10001" "backend writable tmpfs"
    require_file_contains "$compose_file" "/tmp:mode=1777,uid=1000,gid=1000" "frontend writable tmpfs"
    require_file_contains "$compose_file" "/tmp:mode=1777,uid=101,gid=101" "nginx writable tmpfs"
    require_file_contains "$compose_file" "command: bash start_application.sh taskiq-worker" "TaskIQ worker read-only-compatible entrypoint"
    require_file_contains "$compose_file" "command: bash start_application.sh taskiq-scheduler" "TaskIQ scheduler read-only-compatible entrypoint"
    require_file_contains "$compose_file" "./infra/nginx/certs:/certs:ro" "nginx read-only certificate volume"
    require_file_contains "$compose_file" "APP_SECRET_KEY_FILE: /run/secrets/app_secret_key" "backend app secret file"
    require_file_contains "$compose_file" "AUTH_PRIVATE_KEY_FILE: /run/secrets/auth_private_key" "backend private key secret file"
    require_file_contains "$compose_file" "DB_PASSWORD_FILE: /run/secrets/db_password" "backend database secret file"
    require_file_contains "$compose_file" "POSTGRES_PASSWORD_FILE: /run/secrets/db_password" "Postgres password secret file"
    require_file_contains "$compose_file" "MINIO_ACCESS_KEY_FILE: /run/secrets/minio_access_key" "backend MinIO access key secret file"
    require_file_contains "$compose_file" "MINIO_SECRET_KEY_FILE: /run/secrets/minio_secret_key" "backend MinIO secret key secret file"
    require_file_contains "$compose_file" "OWNER_INIT_PASSWORD_FILE: /run/secrets/owner_init_password" "backend owner password secret file"
    require_file_contains "$compose_file" "SENTRY_DSN_FILE: /run/secrets/sentry_dsn" "backend Sentry DSN secret file"
    require_file_contains "$compose_file" "file: \${COMPOSE_APP_SECRET_KEY_FILE:?" "Compose app secret file source"
    require_file_contains "$compose_file" "file: \${COMPOSE_AUTH_PRIVATE_KEY_FILE:?" "Compose private key secret file source"
    require_file_contains "$compose_file" "file: \${COMPOSE_DB_PASSWORD_FILE:?" "Compose database password secret file source"
    require_file_contains "$compose_file" "file: \${COMPOSE_MINIO_ACCESS_KEY_FILE:?" "Compose MinIO access key secret file source"
    require_file_contains "$compose_file" "file: \${COMPOSE_MINIO_SECRET_KEY_FILE:?" "Compose MinIO secret key secret file source"
    require_file_contains "$compose_file" "file: \${COMPOSE_OWNER_INIT_PASSWORD_FILE:?" "Compose owner password secret file source"
    require_file_contains "$compose_file" "file: \${COMPOSE_SENTRY_DSN_FILE:?" "Compose Sentry DSN secret file source"

    require_file_contains "$nginx_template" "resolver 127.0.0.11" "Docker DNS resolver"
    require_file_contains "$nginx_template" "server \${ACTIVE_BACKEND_SLOT}:8080 resolve;" "active backend slot"
    require_file_contains "$nginx_template" "server \${ACTIVE_FRONTEND_SLOT}:4000 resolve;" "active frontend slot"
    require_file_contains "$nginx_template" "connect-src 'self' \${MINIO_PUBLIC_URL}" "public MinIO file CSP"
    require_file_contains "$nginx_template" "img-src 'self' data: \${MINIO_PUBLIC_URL}; font-src 'self' data:;" "main site CSP without Swagger CDN origins"
    require_file_contains "$nginx_template" "style-src 'self' 'nonce-\$request_id'; script-src 'self' 'nonce-\$request_id'; script-src-attr 'none'" "main site nonce CSP without inline style attributes"
    require_file_contains "$nginx_template" "proxy_set_header X-CSP-Nonce" "frontend CSP nonce proxy header"
    require_frontend_location_has_no_proxy_headers "$nginx_template"
    require_file_contains "$nginx_template" "location ^~ /api/docs" "public API docs CSP location"
    require_file_contains "$nginx_template" "img-src 'self' data: \${MINIO_PUBLIC_URL} https://cdn.jsdelivr.net" "Swagger UI image CSP"
    require_file_contains "$nginx_template" "font-src 'self' data: https://cdn.jsdelivr.net" "Swagger UI font CSP"
    require_file_contains "$nginx_template" "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" "Swagger UI script CSP"
    require_file_contains "$nginx_template" "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" "Swagger UI style CSP"
    require_file_contains "$nginx_template" "location = /nginx-healthz" "nginx health endpoint"

    require_file_contains "$run_script" "ACTIVE_DEPLOY_SLOT" "active deploy slot tracking"
    require_file_contains "$run_script" "infra/nginx/templates/site.conf.template" "host nginx template render"
    require_file_contains "$run_script" "/tmp/nginx-conf.d/site.conf" "read-only-compatible nginx runtime config"
    require_file_contains "$run_script" "nginx -s reload" "graceful nginx reload"
    require_file_contains "$run_script" "docker compose up --wait" "health-gated compose startup"
    require_file_contains "$run_script" "backend-init" "backend init deploy step"
    require_file_contains "$run_script" "prepare_minio_volume_permissions" "MinIO non-root volume ownership preparation"
    require_file_contains "$run_script" "chown -R 10002:10002 /data" "MinIO volume ownership repair"
    require_file_contains "$run_script" "prepare_compose_secret_files" "host-side Compose secret file preparation"
    require_file_contains "$compose_secret_script" "COMPOSE_SENTRY_DSN_FILE allow-empty" "empty Sentry DSN secret file support"
    require_file_contains "$compose_secret_script" "chmod 444 \"\$secret_file_path\"" "non-root-readable Compose secret files"
    require_file_contains "$backend_start_script" "AUTH_PRIVATE_KEY AUTH_PUBLIC_KEY" "runtime key newline normalization"

    require_file_contains "$frontend_server" "app.get('/healthz'" "frontend health endpoint"
    require_file_contains "$deploy_workflow" "frontend/" "frontend deploy sync"
}

run_runtime_container_security_check() {
    local compose_file="${repo_dir}/docker-compose.yml"
    local docker_lint_script="${repo_dir}/infra/scripts/docker_lint.sh"
    local nginx_conf="${repo_dir}/infra/nginx/nginx.conf"
    local nginx_template="${repo_dir}/infra/nginx/templates/site.conf.template"

    require_file_contains "$docker_lint_script" "infra/minio/Dockerfile" "MinIO Dockerfile lint coverage"
    require_no_inspect_visible_secret_environment "$compose_file"
    require_no_unapproved_network_literals \
        "hardcoded IP literal outside Docker resolver or self-healthchecks" \
        "([0-9]{1,3}\.){3}[0-9]{1,3}" \
        "$compose_file" \
        "$nginx_template"
    require_no_unapproved_network_literals \
        "localhost reference outside self-healthchecks" \
        "localhost" \
        "$compose_file" \
        "$nginx_template"
    require_no_container_file_logs \
        "$compose_file" \
        "$nginx_conf" \
        "$nginx_template" \
        "${repo_dir}/backend/Dockerfile" \
        "${repo_dir}/backend/start_application.sh" \
        "${repo_dir}/frontend/Dockerfile" \
        "${repo_dir}/infra/minio/Dockerfile" \
        "${repo_dir}/infra/nginx/Dockerfile"
}

run_certbot_configuration_check() {
    local compose_file="${repo_dir}/docker-compose.yml"
    local ci_workflow="${repo_dir}/.github/workflows/ci.yaml"
    local deploy_workflow="${repo_dir}/.github/workflows/_deploy.yaml"
    local makefile="${repo_dir}/Makefile"
    local nginx_template="${repo_dir}/infra/nginx/templates/site.conf.template"
    local run_script="${repo_dir}/infra/scripts/run.sh"
    local tls_script="${repo_dir}/infra/scripts/tls.sh"

    require_file_exists "$tls_script" "TLS helper script"
    require_file_contains "$compose_file" "cert-sync:" "certificate sync service"
    require_file_contains "$compose_file" "certbot-www:/var/www/certbot:ro" "nginx read-only certbot challenge volume"
    require_file_contains "$compose_file" "certbot-www:/var/www/certbot" "certbot challenge volume"
    require_file_contains "$compose_file" "./infra/nginx/certs:/certs" "nginx certificate volume"
    require_file_contains "$compose_file" "letsencrypt:/etc/letsencrypt" "certbot certificate volume"
    require_file_contains "$nginx_template" "root /var/www/certbot;" "HTTP-01 challenge webroot"
    require_file_contains "$run_script" "sync_certificates" "deploy certificate sync step"
    require_file_contains "$makefile" "certbot-issue" "certbot issue target"
    require_file_contains "$makefile" "certbot-renew" "certbot renew target"
    require_file_contains "$makefile" "certbot-sync" "certbot sync target"
    require_file_not_contains "$ci_workflow" "issue_certificates" "deploy-time certificate issue input"
    require_file_not_contains "$ci_workflow" "make certbot-issue" "deploy-time certificate issue step"
    require_file_not_contains "$deploy_workflow" "issue_certificates" "deploy-time certificate issue input"
    require_file_not_contains "$deploy_workflow" "make certbot-issue" "deploy-time certificate issue step"
}

run_minio_image_check() {
    require_command docker

    minio_check_image_tag="my-site-minio-security-check:$(date +%s)-$$"
    minio_check_temp_dir="$(mktemp -d)"
    trap cleanup_security_check_images EXIT

    mkdir -p "${minio_check_temp_dir}/secrets"
    printf '%s' "minioadmin" >"${minio_check_temp_dir}/secrets/minio_access_key"
    printf '%s' "minioadminsecret" >"${minio_check_temp_dir}/secrets/minio_secret_key"

    docker build \
        -f "${repo_dir}/infra/minio/Dockerfile" \
        -t "$minio_check_image_tag" \
        "$repo_dir"

    docker run --rm \
        --user 10002:10002 \
        -v "${minio_check_temp_dir}/secrets:/run/secrets:ro" \
        "$minio_check_image_tag" \
        server --help >"${minio_check_temp_dir}/minio-help.txt"

    require_file_contains "${minio_check_temp_dir}/minio-help.txt" "NAME:" "MinIO server help output"

    docker run --rm \
        --user 10002:10002 \
        --entrypoint sh \
        "$minio_check_image_tag" \
        -c 'test "$(id -u):$(id -g)" = "10002:10002" && test -w /data'
}

run_nginx_syntax_check() {
    local cert_dir

    require_command docker
    require_command openssl

    nginx_check_temp_dir="$(mktemp -d)"
    cert_dir="${nginx_check_temp_dir}/certs"
    nginx_check_image_tag="my-site-nginx-security-check:$(date +%s)-$$"
    mkdir -p "$cert_dir"
    trap cleanup_security_check_images EXIT

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
        --read-only \
        --cap-drop ALL \
        --security-opt no-new-privileges \
        --tmpfs /tmp:mode=1777,uid=101,gid=101 \
        --user 101:101 \
        --add-host backend:127.0.0.1 \
        --add-host backend-blue:127.0.0.1 \
        --add-host backend-green:127.0.0.1 \
        --add-host frontend:127.0.0.1 \
        --add-host frontend-blue:127.0.0.1 \
        --add-host frontend-green:127.0.0.1 \
        --add-host minio:127.0.0.1 \
        --add-host databasus:127.0.0.1 \
        -e APP_DOMAIN=example.test \
        -e SSL_CERT=/certs/test.crt \
        -e SSL_KEY=/certs/test.key \
        -e ACTIVE_BACKEND_SLOT=backend-blue \
        -e ACTIVE_FRONTEND_SLOT=frontend-blue \
        -e MINIO_PUBLIC_URL=https://s3.example.test \
        -v "${cert_dir}:/certs:ro" \
        "$nginx_check_image_tag" \
        sh -ec 'mkdir -p /tmp/nginx-conf.d && envsubst "\$APP_DOMAIN \$SSL_CERT \$SSL_KEY \$ACTIVE_BACKEND_SLOT \$ACTIVE_FRONTEND_SLOT \$MINIO_PUBLIC_URL" < /etc/nginx/runtime-templates/site.conf.template > /tmp/nginx-conf.d/site.conf && nginx -t'
}

run_deploy_env_configuration_check
run_private_panel_configuration_check
run_healthcheck_configuration_check
run_runtime_container_security_check
run_certbot_configuration_check
run_minio_image_check
run_nginx_syntax_check
