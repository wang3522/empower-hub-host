#!/bin/bash

set -e

# Change to the project root (one level up from the script's directory)
cd "$(dirname "$0")/.."

# Start dbus service and wait for it to be available
service dbus start

# Start simulator
cd simulator
python3 main.py &

# Start N2KClient
cd ../N2KClient
python3 main.py &

tail -f /dev/null