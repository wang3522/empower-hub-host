FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential libdbus-glib-1-dev libpython3-dev \
    libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 \
    dbus 
    
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

copy requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]