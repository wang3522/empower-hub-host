#!/bin/bash

set -e

# Change to the project root (one level up from the script's directory)
cd "$(dirname "$0")/.."

service dbus start &

cd simulator
python3 main.py &

cd ..
cd N2KClient

python3 main.py &

tail -f /dev/null