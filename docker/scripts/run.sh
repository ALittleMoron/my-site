#! /bin/bash

# Check .env file exists
if [ ! -f .env ]; then
    echo ".env file could not be found"
    echo "Please create a .env file in the root directory"
    exit 1
fi

# Check docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose application could not be found. Install it."
    exit 1
fi

# Read .env file and export variables
export $(grep -v '^#' .env | xargs -0)

# Run docker-compose up with build option
docker compose up -d postgres minio postgresql_backup_ui
docker compose ps
docker compose pull
docker compose up -d --no-deps --remove-orphans application admin nginx
