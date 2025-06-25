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

#### `ota_progress(message: str)`

**Example**

```
ota_progress("2/4 files transferred")
```

#### `ota_error(message: str)`

**Example**

```
ota_error("Failed to write chunk {num} of {file}")
```

#### `ota_complete(message: str)`

**Example**

```
ota_complete("OTA transfer completed successfully")
```

### Methods

#### `version() -> str`

Returns the version of the BL654.

**Response:**

```
('v1',)
```

---

#### `initiate_ota(filepath: str) -> str`

Initiates an OTA transfer using the provided file path. Provided path should be to a .zip file containing all files needed for the bl654 version.

**Response:**

```
('OTA transfer started for {filepath}',)
```
