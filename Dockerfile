FROM ubuntu:latest

WORKDIR /app

# Only copy the required directories to save space
COPY HubCoreService /app/HubCoreService
COPY N2KClient /app/N2KClient
COPY simulator /app/simulator
COPY config/org.navico.CzoneCpp.conf /etc/dbus-1/system.d/czonecpp.conf

ENV TB_HOST=192.168.2.54
ENV TB_PORT=1883
ENV TB_ACCESS_TOKEN=billy-test

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    build-essential \
    libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev \
    libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev \
    libexpat1-dev liblzma-dev tk-dev libffi-dev \
    libtirpc-dev libnsl-dev \
    python3-dbus python3-gi \
    libgirepository-2.0-dev \
    libdbus-glib-1-dev \
    minicom \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment, then install dependencies
RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install -e /app/N2KClient \
    && /app/venv/bin/pip install -r /app/HubCoreService/HubCore/thingsboardClient/requirements_docker.txt

# Use the virtual environment's Python to run main.py (entrypoint)
CMD ["/bin/bash", "-c", "service dbus start && PYTHONPATH=/app/simulator /app/venv/bin/python -m simulator.main & /app/venv/bin/python HubCoreService/HubCore/thingsboardClient/main.py"]