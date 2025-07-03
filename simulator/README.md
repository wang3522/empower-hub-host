# N2K Simulator Dbus 

## Running on Mac Instructions

1. Make sure Homebrew is installed. https://brew.sh/
2. Install the following packages with Homebrew:
```
brew install pkg-config dbus pygobject3 gtk+3
```
3. cd into the simulator folder
```
cd simulator
```
4. Create virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```
5. Install requirements
```
pip install -r requirements.txt
```
6. **Start the dbus session bus** (run these in your terminal **before** running the simulator):
```
mkdir -p /tmp/mydbus
/opt/homebrew/opt/dbus/bin/dbus-daemon --session --fork --print-address --address=unix:path=/tmp/mydbus/session_bus_socket
export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/mydbus/session_bus_socket
```
7. Run the simulator
```
python main.py
```

You will also need to make sure that you have the dbus service running on the system. If you do not do this you will encounter errors when trying to set up the dbus server.
```
mkdir -p /tmp/mydbus
/opt/homebrew/opt/dbus/bin/dbus-daemon --session --fork --print-address --address=unix:path=/tmp/mydbus/session_bus_socket
export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/mydbus/session_bus_socket
```
> You must keep the terminal session with the exported `DBUS_SESSION_BUS_ADDRESS` active when running the simulator, or the simulator will not be able to connect to dbus.

## Docker Running Instructions
1. Start docker
2. Enter /simulator in terminal window
```bash
cd /simulator
```
4. Give execute permissions to shell scripts
```bash
chmod +x ./docker-build.sh
chmod +x ./docker-run-command.sh
chmod +x ./entrypoint.sh
```
5. Run ./docker-build.sh
6. Run ./docker-run-command.sh

## Simulated Data

At the moment, Dbus service methods only return constants.

### GetDevices
Returns

```string
'[{"id": "dc.1", "type": "dc"}, {"id": "ac.12", "type": "dc"}]'
```

### GetState
Returns

```string
'{"voltage": 12, "current": 2, "stateOfCharge": 75, "temperature": 23, "capacityRemaining": 1000}'
```
