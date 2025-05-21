#!/bin/bash

# Change to the project root (one level up from the script's directory)
cd "$(dirname "$0")/.."

docker run \
    --env "PYTHONUNBUFFERED=1" \
    --name hub-host-simulator \
    -v "$(pwd)/simulator:/simulator" \
    -v "$(pwd)/N2KClient:/N2KClient" \
    -v "$(pwd)/config:/etc/dbus-1/system.d" \
    hub-host-simulator:latest