#!/bin/sh

CONFIG_FILE="/data/hub/config/wap.conf"
INTERFACE="uap0"  # Change if your WiFi interface is different
CON_NAME="hub"

read_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Config file '$CONFIG_FILE' not found!"
        exit 1
    fi
    SSID=$(sed -n '1p' "$CONFIG_FILE")
    PASSWORD=$(sed -n '2p' "$CONFIG_FILE")
    STATIC_IP=$(sed -n '3p' "$CONFIG_FILE")
    GATEWAY=$(sed -n '4p' "$CONFIG_FILE")
    DNS=$(sed -n '5p' "$CONFIG_FILE")
    
    [ -z "$STATIC_IP" ] && STATIC_IP="10.42.0.1/24"
    [ -z "$GATEWAY" ] && GATEWAY="10.42.0.1"
    [ -z "$DNS" ] && DNS="8.8.8.8,8.8.4.4"

    if [ -z "$SSID" ] || [ -z "$PASSWORD" ]; then
        echo "SSID or password missing in config file!"
        exit 1
    fi

    echo "Configuration loaded:"
    echo "  SSID: $SSID"
    echo "  Static IP: $STATIC_IP"
    echo "  Gateway: $GATEWAY"
}

start_ap() {
    read_config

    # Stop any existing AP
    nmcli connection down "$CON_NAME" 2>/dev/null

    # Create AP connection if not exists
    if ! nmcli connection show "$CON_NAME" &>/dev/null; then
        nmcli connection add type wifi ifname "$INTERFACE" con-name "$CON_NAME" autoconnect no ssid "$SSID"
        nmcli connection modify "$CON_NAME" 802-11-wireless.mode ap 802-11-wireless.band bg
        nmcli connection modify "$CON_NAME" ipv4.method shared ipv4.addresses "$STATIC_IP" ipv4.gateway "$GATEWAY"
        nmcli connection modify "$CON_NAME" wifi-sec.key-mgmt wpa-psk
        nmcli connection modify "$CON_NAME" wifi-sec.psk "$PASSWORD"
    else
        nmcli connection modify "$CON_NAME" ssid "$SSID"
        nmcli connection modify "$CON_NAME" wifi-sec.psk "$PASSWORD"
    fi

    # Bring up the AP
    nmcli connection up "$CON_NAME"

    TIMEOUT=30
    COUNTER=0
    
    echo "Waiting for interface to be ready..."
    while [ $COUNTER -lt $TIMEOUT ]; do
        IP_ADDRESS=$(ip addr show "$INTERFACE" 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d'/' -f1 | head -1)
        
        if [ -n "$IP_ADDRESS" ] && [ "$IP_ADDRESS" = "$(echo "$STATIC_IP" | cut -d'/' -f1)" ]; then
            echo "AP is ready! IP Address: $IP_ADDRESS"
            break
        fi
        
        echo "Waiting... ($((COUNTER + 1))/$TIMEOUT)"
        sleep 1
        COUNTER=$((COUNTER + 1))
    done

    if [ -z "$IP_ADDRESS" ] || [ "$IP_ADDRESS" != "$(echo "$STATIC_IP" | cut -d'/' -f1)" ]; then
        echo "Failed to start AP or assign expected IP address"
        echo "Expected: $(echo "$STATIC_IP" | cut -d'/' -f1)"
        echo "Actual: $IP_ADDRESS"
        exit 1
    fi

    cd /data/hub/hub-provisioning || {
        echo "Failed to change to application directory"
        exit 1
    }
    python3 app.py --host="$IP_ADDRESS" --port=8080 --debug
}

stop_ap() {
    nmcli connection down "$CON_NAME"
}

case "$1" in
    start)
        start_ap
        ;;
    stop)
        stop_ap
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac