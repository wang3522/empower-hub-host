#!/bin/sh

# add connection check with thingsboard gateway [todo]
# start thingsboard-gateway service [todo]


cd /data/hub/hub-tbclient || {
    echo "Failed to change to application directory"
    exit 1
}
python3 main.py