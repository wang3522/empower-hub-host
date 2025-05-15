#!/bin/bash

set -e

service dbus start &

python3 /simulator/main.py &

python3 -m N2KClient.main &

tail -f /dev/null