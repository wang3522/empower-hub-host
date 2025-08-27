#!/bin/sh

cd /data/hub/hub-bl654 || {
    echo "Failed to change to application directory"
    exit 1
}
python3 main.py