#! /bin/bash

# Check .env file exists
if [ ! -f .env ]; then
    echo ".env file could not be found"
    echo "Please create a .env file in the root directory"
    exit 1
fi

# Check docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose could not be found"
    exit 1
fi

# Read .env file and export variables
export $(grep -v '^#' .env | xargs -0)

# Run docker-compose up with build option
docker-compose up --build
