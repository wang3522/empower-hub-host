FROM ubuntu:latest

WORKDIR /app

# Only copy the required directories to save space
COPY HubTBClientService /app/HubTBClientService
COPY N2KClient /app/N2KClient
COPY simulator /app/simulator
COPY N2KClient/n2kclient/appsettings.json /data/hub/config/appsettings.json

ENV TB_HOST={YOUR_TB_HOST_ENDPOINT}
ENV TB_PORT={YOUR_TB_HOST_PORT}
ENV TB_ACCESS_TOKEN={YOUR_TB_ACCESS_TOKEN}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential libdbus-glib-1-dev libpython3-dev \
    libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 \
    dbus \
    && rm -rf /var/lib/apt/lists/*

RUN echo '<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN" "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">\
<busconfig>\
    <policy user="root">\
        <allow own="org.navico.HubN2K"/>\
        <allow send_destination="org.navico.HubN2K"/>\
        <allow receive_sender="org.navico.HubN2K"/>\
        <allow own="org.navico.HubUtility"/>\
        <allow send_destination="org.navico.HubUtility"/>\
        <allow receive_sender="org.navico.HubUtility"/>\
        <allow own="org.navico.HubUtility.bl654"/>\
        <allow send_destination="org.navico.HubUtility.bl654"/>\
        <allow receive_sender="org.navico.HubUtility.bl654"/>\
    </policy>\
</busconfig>' > /etc/dbus-1/system.d/org.navico.Hub.conf

# Create and activate a virtual environment, then install dependencies
RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install -e /app/N2KClient \
    && /app/venv/bin/pip install -r /app/HubTBClientService/requirements_docker.txt

# Use the virtual environment's Python to run main.py (entrypoint)
CMD ["/bin/bash", "-c", "dbus-daemon --system --fork && PYTHONPATH=/app/simulator /app/venv/bin/python -m simulator.main & /app/venv/bin/python HubTBClientService/main.py"]