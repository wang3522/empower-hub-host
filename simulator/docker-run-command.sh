docker run \
    --env "PYTHONUNBUFFERED=1" \
    --name hub-host-simulator \
    -v ./src:/simulator \
    -v /Users/aconnolly/repos/empower-hub-host/N2KClient:/N2KClient \
    -v ./config:/etc/dbus-1/system.d \
    hub-host-simulator:latest