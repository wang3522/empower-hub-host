# Thingsboard Client

## Running on Mac Instructions
1. Make sure Homebrew is installed. https://brew.sh/
2. Install the following packages from brew
```
brew install pkg-config dbus pygobject3 gtk+3
```
3. Create virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```
4. Install requirements
```
pip install -r requirements.txt
```
5. Run the app
```
python main.py
```

You will also need to make sure that you have the dbus service runnin on the system. If you do not do this you will encounter errors when trying to set up the dbus server.
```
mkdir -p /tmp/mydbus
/opt/homebrew/opt/dbus/bin/dbus-daemon --session --fork --print-address --address=unix:path=/tmp/mydbus/session_bus_socket
export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/mydbus/session_bus_socket
```