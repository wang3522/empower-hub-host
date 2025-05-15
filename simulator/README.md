# N2K Simulator Dbus 

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
