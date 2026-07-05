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

require_file_exists() {
    local file_path="$1"
    local description="$2"

    if [ ! -f "$file_path" ]; then
        echo "Missing ${description}: ${file_path}" >&2
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

run_deploy_env_configuration_check() {
    local compose_file="${repo_dir}/docker-compose.yml"
    local ci_workflow="${repo_dir}/.github/workflows/ci.yaml"
    local legacy_deploy_workflow="${repo_dir}/.github/workflows/deploy.yaml"
    local env_example="${repo_dir}/.env.example"
    local manifest_file="${repo_dir}/infra/deploy/runtime-env.manifest.json"
    local renderer="${repo_dir}/infra/scripts/render_deploy_env.py"
    local rendered_env

    require_command python3
    require_file_exists "$ci_workflow" "CI workflow"
    require_file_not_exists "$legacy_deploy_workflow" "standalone deploy workflow"
    require_file_exists "$manifest_file" "runtime environment manifest"
    require_file_exists "$renderer" "runtime environment renderer"

    require_file_contains "$ci_workflow" "post-smoke-security:" "post-smoke security job"
    require_file_contains "$ci_workflow" "run-infra-security: true" "post-smoke infrastructure security scan"
    require_file_contains "$ci_workflow" "deploy:" "CI deploy job"
    require_file_contains "$ci_workflow" "if: github.ref == 'refs/heads/main'" "main-only deploy gate"
    require_file_contains "$ci_workflow" "- post-smoke-security" "deploy dependency on post-smoke security"
    require_file_contains "$ci_workflow" "environment: production" "production deployment environment approval"
    require_file_contains "$ci_workflow" "vars.REMOTE_HOST" "remote host GitHub variable"
    require_file_contains "$ci_workflow" "vars.REMOTE_USER" "remote user GitHub variable"
    require_file_contains "$ci_workflow" "vars.REMOTE_PATH" "remote path GitHub variable"
    require_file_contains "$ci_workflow" "secrets.SSH_PRIVATE_KEY" "SSH private key deploy secret"
    require_file_contains "$ci_workflow" "cp -a Makefile docker-compose.yml backend/ frontend/ infra/ .env .deploy-payload/" "runtime file deploy sync"
    require_file_contains "$ci_workflow" "make run" "remote stack restart"
    require_file_not_contains "$ci_workflow" "Create .env file from secrets" "manual secret echo env generation"
    require_file_not_contains "$ci_workflow" "REMOTE_HOST=\${{ secrets.REMOTE_HOST }}" "remote host runtime env entry"
    require_file_not_contains "$ci_workflow" "SSH_PRIVATE_KEY=" "SSH private key runtime env entry"
    require_file_not_contains "$ci_workflow" "DOCKER_PASSWORD=" "Docker password runtime env entry"
    require_file_not_contains "$ci_workflow" "CACHE_WARM_NOTES_PAGE_SIZE" "stale cache warm env name"
    require_file_not_contains "$ci_workflow" "issue_certificates" "deploy-time certificate issue input"
    require_file_not_contains "$ci_workflow" "make certbot-issue" "deploy-time certificate issue step"

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
    local ci_workflow="${repo_dir}/.github/workflows/ci.yaml"
    local nginx_template="${repo_dir}/infra/nginx/templates/site.conf.template"
    local run_script="${repo_dir}/infra/scripts/run.sh"
    local frontend_server="${repo_dir}/frontend/src/server-app.ts"

    require_file_contains "$compose_file" "backend-blue:" "blue backend service"
    require_file_contains "$compose_file" "backend-green:" "green backend service"
    require_file_contains "$compose_file" "frontend-blue:" "blue frontend service"
    require_file_contains "$compose_file" "frontend-green:" "green frontend service"
    require_file_contains "$compose_file" "backend-init:" "one-shot backend init service"
    require_file_contains "$compose_file" "/api/healthcheck/ready" "backend readiness healthcheck"
    require_file_contains "$compose_file" "/healthz" "frontend healthcheck"
    require_file_contains "$compose_file" "/nginx-healthz" "nginx healthcheck"
    require_file_contains "$compose_file" "MINIO_API_CORS_ALLOW_ORIGIN: \${APP_URL_SCHEMA}://\${APP_DOMAIN}" "MinIO public file CORS origin"

    require_file_contains "$nginx_template" "resolver 127.0.0.11" "Docker DNS resolver"
    require_file_contains "$nginx_template" "server \${ACTIVE_BACKEND_SLOT}:8080 resolve;" "active backend slot"
    require_file_contains "$nginx_template" "server \${ACTIVE_FRONTEND_SLOT}:4000 resolve;" "active frontend slot"
    require_file_contains "$nginx_template" "connect-src 'self' \${MINIO_PUBLIC_URL}" "public MinIO file CSP"
    require_file_contains "$nginx_template" "location = /nginx-healthz" "nginx health endpoint"

    require_file_contains "$run_script" "ACTIVE_DEPLOY_SLOT" "active deploy slot tracking"
    require_file_contains "$run_script" "nginx -s reload" "graceful nginx reload"
    require_file_contains "$run_script" "docker compose up --wait" "health-gated compose startup"
    require_file_contains "$run_script" "backend-init" "backend init deploy step"

    require_file_contains "$frontend_server" "app.get('/healthz'" "frontend health endpoint"
    require_file_contains "$ci_workflow" "frontend/" "frontend deploy sync"
}

run_certbot_configuration_check() {
    local compose_file="${repo_dir}/docker-compose.yml"
    local ci_workflow="${repo_dir}/.github/workflows/ci.yaml"
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
        nginx -t
}

run_deploy_env_configuration_check
run_private_panel_configuration_check
run_healthcheck_configuration_check
run_certbot_configuration_check
run_nginx_syntax_check
