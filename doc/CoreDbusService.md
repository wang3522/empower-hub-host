# HubCore D-Bus Interfaces: BL654 and WiFi

- [WiFi Interface](#wifi-interface)
- [BL654 Interface](#bl654-interface)

## WiFi Interface

### Object Path

```
/org/navico/HubUtility/wifi
```

### Interface

```
org.navico.HubUtility.wifi
```

### Methods

#### `status() -> str`

Returns the current status of the WiFi.

**Response:**

```
{"data": {false|true}, "error": null}
```

---

#### `enable() -> str`

Enables WiFi.

**Response:**

```
{"data": "ok", "error": null}
```

---

#### `disable() -> str`

Disables WiFi.

**Response:**

```
{"data": "ok", "error": null}
```

---

#### `list() -> str`

Lists the available WiFi networks.

**Response:**

```
{"data": ["Wifi 1", "Wifi 2"], "error": null}
```

---

#### `restart() -> str`

Restarts WiFi.

**Response:**

```
{"data": {false|true}, "error": null}
```

---

#### `version() -> str`

Returns the version string for WiFi interface.

**Response:**

```
{"{version}",}
```

---

#### `configure(ssid: str, password: str) -> str`

Configures the WiFi network credentials.

**Response:**

```
{"data": {false|true}, "error": null}
```

---

## BL654 Interface

### Object Path

```
/org/navico/HubUtility/bl654
```

### Interface

```
org.navico.HubUtility.bl654
```

### Signals

#### `ota_error(message: str)`

**Example**

```
"error"
```

#### `ota_complete(message: str)`

**Example**

```
"success"
```

#### `notify_version(message: str)`

Handles notifying application version when requested from BL654

**Example**

```
"v1"
```

### Methods

#### `get_version() -> str`

Initiates fetching application version from BL654

**Response:**

```
('Requesting version from BL654...',)
```

---

#### `initiate_ota(filepath: str) -> str`

Initiates an OTA transfer using the provided file path. Provided path should be to a .zip file containing all files needed for the bl654 version.

**Response:**

```
('OTA transfer started for {filepath}',)
```
