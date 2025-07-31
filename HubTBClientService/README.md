# Thingsboard Client

## Running on Mac Instructions

1. Make sure Homebrew is installed: https://brew.sh/
2. Install the following packages with Homebrew:
   ```
   brew install pkg-config dbus pygobject3 gtk+3
   ```
3. Create and activate a virtual environment:

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install requirements:
   ```
   cd HubCoreService/HubCore/thingsboardClient
   pip install -r requirements.txt
   ```
5. **Start the dbus session bus** (run these in your terminal **before** running the app):

   ```
   mkdir -p /tmp/mydbus
   /opt/homebrew/opt/dbus/bin/dbus-daemon --session --fork --print-address --address=unix:path=/tmp/mydbus/session_bus_socket
   export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/mydbus/session_bus_socket
   ```

   > **Note:** If you are on an Intel Mac, the dbus path may be `/usr/local/opt/dbus/bin/dbus-daemon`.

6. Run the app:
   ```
   python main.py
   ```

> **Important:**  
> You must keep the terminal session with the exported `DBUS_SESSION_BUS_ADDRESS` active when running the app, or the app will not be able to connect to dbus.
