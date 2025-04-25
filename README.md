# Host System Architecture

## Environment Variables
The following environment variables are configured for the host system:

- `HUB_LOG_LEVEL=DEBUG`: Sets the log level for the Hub application to DEBUG.
- `HUB_CONFIGDIR=/etc/hub`: Specifies the directory where configuration files are stored.
- `HUB_LOGDIR=/var/log/hub`: Specifies the directory where log files are stored.
- `HUB_NET_CONFIG=/etc/hub/network-config.json`: Specifies the path to the network configuration file.

These variables are automatically set during startup and do not require manual configuration.

## Application Binary Path
Hub application-related binaries are stored in the following directory:
```
/usr/bin/hub/
```

This directory is included in the system `PATH` during startup, so there is no need to export it manually.

## Services
The following services are configured for the host system:

1. **hub-czone**
   - Description: Hub CZone Core Service.
   - Behavior: Automatically restarts on failure with a 5-second delay.
   - Service File: `/etc/systemd/system/hub-czone.service`

2. **hub-interface**
   - Description: Hub Interface Service.
   - Behavior: Automatically restarts on failure with a 5-second delay.
   - Service File: `/etc/systemd/system/hub-interface.service`

3. **hub-setup**
   - Description: Hub Setup Service.
   - Behavior: Runs once during startup.
   - Service File: `/etc/systemd/system/hub-startup.service`

## Host Code Structure
The host system codebase is organized into the following directories:

- **config**: Contains all host-related configuration files, such as network settings, environment files, and service configurations.
- **CZoneCore**: Contains the C++ implementation of the CZone Core, including modules for CAN communication, D-Bus services, and core management.
- **HubInterface**: Implements BLE, LTE, WiFi, ThingsBoard (TB), and LED services, along with D-Bus interfaces for communication.
- **scripts**: Contains standalone scripts, such as `hub-startup.sh`, used for initialization and setup tasks.
- **service**: Contains systemd service files for managing the lifecycle of the Hub services.

