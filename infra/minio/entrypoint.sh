#!/bin/sh
set -eu

read_secret_file() {
    file_path="$1"

    if [ ! -r "$file_path" ]; then
        echo "MinIO secret file is not readable: ${file_path}" >&2
        exit 1
    fi

    cat "$file_path"
}

export MINIO_ROOT_USER="$(read_secret_file /run/secrets/minio_access_key)"
export MINIO_ROOT_PASSWORD="$(read_secret_file /run/secrets/minio_secret_key)"

exec minio "$@"
