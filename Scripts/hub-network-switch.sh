#!/usr/bin/bash

# Configuration
ETH_DEVICE="eth0"           # Ethernet interface
WIFI_DEVICE="wlan0"         # Wi-Fi interface
CELL_DEVICE="wwan0"         # Cellular interface
PING_TARGET="8.8.8.8"       # Reliable external server to test connectivity
CHECK_INTERVAL=5            # Seconds between checks
DHCP_TIMEOUT=30             # DHCP timeout in seconds for cellular
ACTIVE_DEVICE=""            # Current active device

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to configure DHCP for cellular device using udhcpc
configure_cellular_dhcp() {
    local device=$1
    local timeout=${2:-$DHCP_TIMEOUT}
    
    log_message "Configuring DHCP for $device using udhcpc with timeout ${timeout}s"
    
    # Kill any existing udhcpc processes for this interface
    pkill -f "udhcpc.*$device" 2>/dev/null
    
    # Remove any existing IP addresses
    ip addr flush dev "$device" 2>/dev/null
    
    # Start udhcpc with timeout
    # -q: quit after obtaining lease
    # -f: run in foreground
    # -i: interface
    # -t: send up to N discover packets (default 3)
    # -T: pause between packets (default 3 seconds)
    timeout "$timeout" udhcpc -q -f -i "$device" -t 5 -T 3 2>/dev/null
    
    if [ $? -eq 0 ]; then
        # Verify we got an IP address
        if ip addr show "$device" 2>/dev/null | grep -q "inet "; then
            log_message "DHCP configuration successful for $device"
            return 0
        fi
    fi
    
    log_message "DHCP configuration failed or timed out for $device"
    return 1
}

# Function to check if interface is active
is_connection_active() {
    local device=$1
    # Check if interface exists and is UP
    if ip link show "$device" 2>/dev/null | grep -q "state UP"; then
        # Check carrier state (physical link)
        local carrier=$(cat "/sys/class/net/$device/carrier" 2>/dev/null || echo 0)
        if [ "$carrier" = "1" ]; then
            # Check if interface has an IP address assigned
            if ip addr show "$device" 2>/dev/null | grep -q "inet "; then
                return 0  # Interface is up, has carrier, and has IP
            fi
        fi
    fi
    return 1  # Interface is down, no carrier, or no IP
}

# Function to check internet connectivity
check_internet() {
    local device=$1
    ping -c 2 -W 2 -I "$device" "$PING_TARGET" &>/dev/null
    return $?
}

# Function to get interface metric from routing table
get_interface_metric() {
    local device=$1
    ip route show default dev "$device" 2>/dev/null | grep -o 'metric [0-9]*' | cut -d' ' -f2
}

# Function to set default route by adjusting interface metric
set_default_route() {
    local device=$1
    local priority=$2
    
    # Check if already the default route with correct metric
    local current_metric=$(get_interface_metric "$device")
    if [ "$device" = "$ACTIVE_DEVICE" ] && [ "$current_metric" = "$priority" ]; then
        log_message "Default route already set to $device with metric $priority"
        return 0
    else
        ACTIVE_DEVICE="$device"
    fi

    # Get the gateway for this interface
    local gateway=$(ip route show dev "$device" | grep default | awk '{print $3}' | head -n1)
    if [ -z "$gateway" ]; then
        # Try to get gateway from the interface's network
        local network=$(ip route show dev "$device" | grep -v default | awk '/\/24|\/16|\/8/ {print $1}' | head -n1)
        if [ -n "$network" ]; then
            gateway=$(echo "$network" | sed 's/\.[0-9]*\//.1\//' | cut -d'/' -f1)
        fi
    fi
    
    if [ -z "$gateway" ]; then
        log_message "Error: Could not determine gateway for $device"
        return 1
    fi
    
    # Validate gateway is reachable (quick test)
    if ! ping -c 1 -W 1 -I "$device" "$gateway" &>/dev/null; then
        log_message "Warning: Gateway $gateway for $device may not be reachable"
        # Continue anyway as ping might be blocked
    fi

    # Remove existing default routes for this interface
    while ip route del default dev "$device" 2>/dev/null; do
        :
    done

    # Remove any existing default routes with high metrics to avoid conflicts
    for d in "$ETH_DEVICE" "$WIFI_DEVICE" "$CELL_DEVICE"; do
        if [ "$d" != "$device" ] && ip link show "$d" &>/dev/null; then
            # Set high metric for other interfaces
            local other_gateway=$(ip route show dev "$d" | grep default | awk '{print $3}' | head -n1)
            if [ -n "$other_gateway" ]; then
                ip route del default dev "$d" 2>/dev/null
                ip route add default via "$other_gateway" dev "$d" metric 600 2>/dev/null
            fi
        fi
    done

    # Add default route with specified metric for preferred interface
    if ip route add default via "$gateway" dev "$device" metric "$priority" 2>/dev/null; then
        log_message "Set default route to $device via $gateway with metric $priority"
        return 0
    else
        log_message "Failed to set default route for $device"
        return 1
    fi
}

# Function to bring interface up (if needed)
bring_interface_up() {
    local device=$1
    if ! ip link show "$device" 2>/dev/null | grep -q "state UP"; then
        ip link set "$device" up 2>/dev/null
        sleep 2  # Give interface time to come up
    fi
}

# Function to setup cellular connection
setup_cellular() {
    local device=$1
    
    # Bring interface up
    bring_interface_up "$device"
    
    if ! configure_cellular_dhcp "$device"; then
        log_message "Failed to configure DHCP for $device"
        return 1
    fi
    
    return 0
}

get_interface_stats_with_delta() {
    local device=$1
    local stats_file="/sys/class/net/$device/statistics"
    
    if [ -d "$stats_file" ]; then
        local rx_bytes=$(cat "$stats_file/rx_bytes" 2>/dev/null || echo 0)
        local tx_bytes=$(cat "$stats_file/tx_bytes" 2>/dev/null || echo 0)
        local rx_packets=$(cat "$stats_file/rx_packets" 2>/dev/null || echo 0)
        local tx_packets=$(cat "$stats_file/tx_packets" 2>/dev/null || echo 0)
        
        # Calculate deltas
        local prev_rx=${prev_rx_bytes[$device]:-0}
        local prev_tx=${prev_tx_bytes[$device]:-0}
        local delta_rx=$((rx_bytes - prev_rx))
        local delta_tx=$((tx_bytes - prev_tx))
        local delta_total=$((delta_rx + delta_tx))
        
        # Update previous values
        prev_rx_bytes[$device]=$rx_bytes
        prev_tx_bytes[$device]=$tx_bytes
        
        echo "RX: ${rx_bytes} bytes (${rx_packets} packets), TX: ${tx_bytes} bytes (${tx_packets} packets) | Delta: +${delta_rx}RX/+${delta_tx}TX (+${delta_total} total)"
        return $delta_total
    else
        echo "Interface $device not found"
        return 0
    fi
}

get_interface_stats() {
    local device=$1
    local stats_file="/sys/class/net/$device/statistics"
    
    if [ -d "$stats_file" ]; then
        local rx_bytes=$(cat "$stats_file/rx_bytes" 2>/dev/null || echo 0)
        local tx_bytes=$(cat "$stats_file/tx_bytes" 2>/dev/null || echo 0)
        local rx_packets=$(cat "$stats_file/rx_packets" 2>/dev/null || echo 0)
        local tx_packets=$(cat "$stats_file/tx_packets" 2>/dev/null || echo 0)
        
        echo "RX: ${rx_bytes} bytes (${rx_packets} packets), TX: ${tx_bytes} bytes (${tx_packets} packets)"
    else
        echo "Interface $device not found"
    fi
}

# Function to monitor traffic on inactive interfaces
monitor_inactive_interfaces() {
    local active_device=$1
    
    # Monitor active device traffic
    local active_stats=$(get_interface_stats_with_delta "$active_device")
    local active_delta=$?
    log_message "Active $active_device traffic: $active_stats"
    
    # Monitor inactive interfaces
    for device in "$ETH_DEVICE" "$WIFI_DEVICE" "$CELL_DEVICE"; do
        if [ "$device" != "$active_device" ] && ip link show "$device" &>/dev/null; then
            local stats=$(get_interface_stats_with_delta "$device")
            local delta_bytes=$?
            log_message "Traffic on inactive $device: $stats"
            
            # Check if there's unexpected traffic (more than minimal)
            if [ $delta_bytes -gt 1000 ]; then  # More than 1KB since last check
                log_message "WARNING: Unexpected traffic detected on inactive interface $device (+${delta_bytes} bytes)"
            fi
        fi
    done
}

cleanup_and_exit() {
    log_message "Received signal to exit. Printing final interface statistics:"
    
    # Print final stats for all interfaces
    for device in "$ETH_DEVICE" "$WIFI_DEVICE" "$CELL_DEVICE"; do
        if ip link show "$device" &>/dev/null; then
            local diff_bytes=$(get_interface_stats_with_delta "$device")
            local stats=$(get_interface_stats "$device")
            log_message "Final stats for $device: $stats (Changed: $diff_bytes bytes since last check)"
        fi
    done
    
    log_message "Network monitoring stopped"
    exit 0
}

trap cleanup_and_exit SIGINT SIGTERM

# Initialize stats tracking
declare -A prev_rx_bytes
declare -A prev_tx_bytes

# Initialize baseline stats
for device in "$ETH_DEVICE" "$WIFI_DEVICE" "$CELL_DEVICE"; do
    if ip link show "$device" &>/dev/null; then
        prev_rx_bytes[$device]=$(cat "/sys/class/net/$device/statistics/rx_bytes" 2>/dev/null || echo 0)
        prev_tx_bytes[$device]=$(cat "/sys/class/net/$device/statistics/tx_bytes" 2>/dev/null || echo 0)
    fi
done

# Main loop
while true; do
    log_message "Checking network connections..."
    
    # Check Ethernet
    bring_interface_up "$ETH_DEVICE"
    if is_connection_active "$ETH_DEVICE" && check_internet "$ETH_DEVICE"; then
        log_message "Ethernet ($ETH_DEVICE) is active and has internet"
        if set_default_route "$ETH_DEVICE" 100; then
            monitor_inactive_interfaces "$ETH_DEVICE"
            sleep "$CHECK_INTERVAL"
            continue
        fi
    else
        log_message "Ethernet ($ETH_DEVICE) is inactive or no internet"
    fi

    # Check Wi-Fi
    bring_interface_up "$WIFI_DEVICE"
    if is_connection_active "$WIFI_DEVICE" && check_internet "$WIFI_DEVICE"; then
        log_message "Wi-Fi ($WIFI_DEVICE) is active and has internet"
        if set_default_route "$WIFI_DEVICE" 200; then
            monitor_inactive_interfaces "$WIFI_DEVICE"
            sleep "$CHECK_INTERVAL"
            continue
        fi
    else
        log_message "Wi-Fi ($WIFI_DEVICE) is inactive or no internet"
    fi

    # Check Cellular
    if [ "$ACTIVE_DEVICE" != "$CELL_DEVICE" ]; then
        if setup_cellular "$CELL_DEVICE"; then
            if is_connection_active "$CELL_DEVICE" && check_internet "$CELL_DEVICE"; then
                log_message "Cellular ($CELL_DEVICE) is active and has internet"
                if set_default_route "$CELL_DEVICE" 300; then
                    monitor_inactive_interfaces "$CELL_DEVICE"
                    sleep "$CHECK_INTERVAL"
                    continue
                fi
            else
                log_message "Cellular ($CELL_DEVICE) is inactive or no internet"
            fi
        else
            log_message "Failed to setup cellular connection"
        fi
    else
        # Cellular is already active, just check if it still has internet
        if is_connection_active "$CELL_DEVICE" && check_internet "$CELL_DEVICE"; then
            log_message "Cellular ($CELL_DEVICE) remains active with internet"
            monitor_inactive_interfaces "$CELL_DEVICE"
            sleep "$CHECK_INTERVAL"
            continue
        else
            log_message "Cellular ($CELL_DEVICE) lost internet connection"
        fi
    fi

    log_message "No connections with internet available"
    # Monitor all interfaces when no connection is active
    # for device in "$ETH_DEVICE" "$WIFI_DEVICE" "$CELL_DEVICE"; do
    #     if ip link show "$device" &>/dev/null; then
    #         local stats=$(get_interface_stats "$device")
    #         log_message "Traffic on $device: $stats"
    #     fi
    # done
    
    sleep "$CHECK_INTERVAL"
done