#!/usr/bin/env bash

readonly COMPOSE_SECRET_SPECS=(
    "APP_SECRET_KEY app_secret_key COMPOSE_APP_SECRET_KEY_FILE required literal"
    "AUTH_PRIVATE_KEY auth_private_key COMPOSE_AUTH_PRIVATE_KEY_FILE required pem"
    "DB_PASSWORD db_password COMPOSE_DB_PASSWORD_FILE required literal"
    "MINIO_ACCESS_KEY minio_access_key COMPOSE_MINIO_ACCESS_KEY_FILE required literal"
    "MINIO_SECRET_KEY minio_secret_key COMPOSE_MINIO_SECRET_KEY_FILE required literal"
    "OWNER_INIT_PASSWORD owner_init_password COMPOSE_OWNER_INIT_PASSWORD_FILE required literal"
    "SENTRY_DSN sentry_dsn COMPOSE_SENTRY_DSN_FILE allow-empty literal"
    "AGENT_ACCESS_ISSUING_CERTIFICATE agent_issuing_certificate COMPOSE_AGENT_ISSUING_CERTIFICATE_FILE required pem"
    "AGENT_ACCESS_ISSUING_PRIVATE_KEY agent_issuing_private_key COMPOSE_AGENT_ISSUING_PRIVATE_KEY_FILE required pem"
    "AGENT_ACCESS_CERTIFICATE_CHAIN agent_certificate_chain COMPOSE_AGENT_CERTIFICATE_CHAIN_FILE required pem"
)

fail_invalid_secret() {
    local secret_name="$1"

    echo "${secret_name} is not valid deployment PKI material." >&2
    return 1
}

extract_chain_certificate() {
    local chain_file="$1"
    local certificate_number="$2"
    local output_file="$3"

    awk -v wanted="$certificate_number" '
        /-----BEGIN CERTIFICATE-----/ {
            current += 1
        }
        current == wanted {
            print
        }
        current == wanted && /-----END CERTIFICATE-----/ {
            exit
        }
    ' "$chain_file" >"$output_file"
}

validate_compose_pki() {
    local secrets_dir="$1"
    local auth_key="${secrets_dir}/auth_private_key"
    local issuing_certificate="${secrets_dir}/agent_issuing_certificate"
    local issuing_key="${secrets_dir}/agent_issuing_private_key"
    local chain="${secrets_dir}/agent_certificate_chain"
    local chain_issuing="${secrets_dir}/.agent-chain-issuing.pem"
    local chain_root="${secrets_dir}/.agent-chain-root.pem"
    local certificate_public_key="${secrets_dir}/.agent-certificate-public.der"
    local private_public_key="${secrets_dir}/.agent-private-public.der"
    local certificate_count

    if ! command -v openssl >/dev/null 2>&1; then
        echo "openssl is required to validate deployment PKI material." >&2
        return 1
    fi
    openssl pkey -in "$auth_key" -noout >/dev/null 2>&1 \
        || fail_invalid_secret "AUTH_PRIVATE_KEY"
    openssl x509 -in "$issuing_certificate" -noout >/dev/null 2>&1 \
        || fail_invalid_secret "AGENT_ACCESS_ISSUING_CERTIFICATE"
    openssl pkey -in "$issuing_key" -noout >/dev/null 2>&1 \
        || fail_invalid_secret "AGENT_ACCESS_ISSUING_PRIVATE_KEY"

    certificate_count="$(grep -c '^-----BEGIN CERTIFICATE-----$' "$chain" || true)"
    if [ "$certificate_count" -ne 2 ]; then
        fail_invalid_secret "AGENT_ACCESS_CERTIFICATE_CHAIN"
        return 1
    fi
    extract_chain_certificate "$chain" 1 "$chain_issuing"
    extract_chain_certificate "$chain" 2 "$chain_root"
    openssl x509 -in "$chain_issuing" -noout >/dev/null 2>&1 \
        || fail_invalid_secret "AGENT_ACCESS_CERTIFICATE_CHAIN"
    openssl x509 -in "$chain_root" -noout >/dev/null 2>&1 \
        || fail_invalid_secret "AGENT_ACCESS_CERTIFICATE_CHAIN"
    if [ "$(openssl x509 -in "$issuing_certificate" -noout -fingerprint -sha256)" \
        != "$(openssl x509 -in "$chain_issuing" -noout -fingerprint -sha256)" ]; then
        fail_invalid_secret "AGENT_ACCESS_CERTIFICATE_CHAIN"
        return 1
    fi
    openssl verify -CAfile "$chain_root" "$chain_root" >/dev/null 2>&1 \
        || fail_invalid_secret "AGENT_ACCESS_CERTIFICATE_CHAIN"
    openssl verify -CAfile "$chain_root" "$chain_issuing" >/dev/null 2>&1 \
        || fail_invalid_secret "AGENT_ACCESS_CERTIFICATE_CHAIN"
    openssl x509 -in "$issuing_certificate" -pubkey -noout \
        | openssl pkey -pubin -outform DER >"$certificate_public_key" 2>/dev/null \
        || fail_invalid_secret "AGENT_ACCESS_ISSUING_CERTIFICATE"
    openssl pkey -in "$issuing_key" -pubout -outform DER >"$private_public_key" 2>/dev/null \
        || fail_invalid_secret "AGENT_ACCESS_ISSUING_PRIVATE_KEY"
    if ! cmp -s "$certificate_public_key" "$private_public_key"; then
        fail_invalid_secret "AGENT_ACCESS_ISSUING_PRIVATE_KEY"
        return 1
    fi
    rm -f "$chain_issuing" "$chain_root" "$certificate_public_key" "$private_public_key"
}

prepare_compose_secret_files() {
    if [ -z "${repo_dir:-}" ]; then
        echo "repo_dir must be set before sourcing compose_secrets.sh." >&2
        exit 1
    fi

    local compose_secrets_dir="${COMPOSE_SECRETS_DIR:-${repo_dir}/.deploy-state/compose-secrets}"
    local previous_umask
    local spec

    mkdir -p "$compose_secrets_dir"
    chmod 700 "$compose_secrets_dir"

    previous_umask="$(umask)"
    umask 077

    for spec in "${COMPOSE_SECRET_SPECS[@]}"; do
        local source_variable_name
        local secret_file_name
        local compose_file_variable_name
        local empty_policy
        local encoding
        local secret_file_path
        local secret_value

        read -r source_variable_name secret_file_name compose_file_variable_name empty_policy encoding <<<"$spec"

        if [ "${!source_variable_name+x}" != "x" ]; then
            echo "${source_variable_name} must be set before preparing Compose secret files." >&2
            exit 1
        fi

        secret_value="${!source_variable_name}"
        if [ "$empty_policy" = "required" ] && [ -z "$secret_value" ]; then
            echo "${source_variable_name} must not be empty." >&2
            exit 1
        fi

        secret_file_path="${compose_secrets_dir}/${secret_file_name}"
        rm -f "$secret_file_path"
        if [ "$encoding" = "pem" ]; then
            printf '%b' "$secret_value" >"$secret_file_path"
        else
            printf '%s' "$secret_value" >"$secret_file_path"
        fi
        # Compose bind-mounts file-backed secrets with host ownership, so non-root containers
        # need a read bit that is independent of the host UID/GID.
        chmod 444 "$secret_file_path"
        export "$compose_file_variable_name=$secret_file_path"
    done

    validate_compose_pki "$compose_secrets_dir"

    umask "$previous_umask"
}
