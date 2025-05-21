#!/bin/bash

set -e

# Change to the project root (one level up from the script's directory)
cd "$(dirname "$0")/.."

service dbus start &

python3 -m simulator.main &

python3 -m N2KClient.main &

tail -f /dev/null