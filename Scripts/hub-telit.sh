#!/usr/bin/bash

# Telit LTE Modem Initialization Script
# Uses atinout binary to configure modem on /dev/ttyUSB0

MODEM_PORT="/dev/ttyUSB2"
MODEM_PORT_DEBUG="/dev/ttyUSB0"
ATINOUT="/usr/bin/atinout"
REQUIRED_USB_MODE="1"
REQUIRED_APN="iot.aer.net"
REQUIRED_OPERATOR_MODE="0"
TIMEOUT=30
LOG_FILE="/data/hub/log/hub-telit.log"
ICCID_FILE="/data/factory/hub-telit.iccid"
IMEI_FILE="/data/factory/hub-telit.imei"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to flush the UART buffer
flush_uart() {
    local port="$1"
    dd if="$port" iflag=nonblock count=1000 bs=1 >/dev/null 2>&1
    sleep 0.2
}

# Function to send AT command and get response
send_at_command() {
    local command="$1"
    local timeout_seconds="${2:-5}"
    local max_retries="${3:-3}"
    local retry_delay="${4:-2}"

    local attempt=1
    local response=""
    local tmp_input=""
    local tmp_output=""

    local port="${ACTIVE_MODEM_PORT:-$MODEM_PORT}"

    cleanup_temp_files() {
        if [ -n "$tmp_input" ] && [ -f "$tmp_input" ]; then rm -f "$tmp_input"; fi
        if [ -n "$tmp_output" ] && [ -f "$tmp_output" ]; then rm -f "$tmp_output"; fi
    }
    trap cleanup_temp_files EXIT

    while [ $attempt -le $max_retries ]; do
        flush_uart "$port"
        
        tmp_input=$(mktemp)
        tmp_output=$(mktemp)
        
        printf "%s\r\n" "$command" > "$tmp_input"
        
        if timeout "$timeout_seconds" "$ATINOUT" "$tmp_input" "$port" "$tmp_output"; then
            sleep 0.5
            response=$(cat "$tmp_output")

            if echo "$response" | grep -q "OK"; then
                cleanup_temp_files
                trap - EXIT
                echo "$response"
                return 0
            else
                log "[warn] AT command '$command' returned error (attempt $attempt/$max_retries)"
            fi
        else
            log "[error] AT command '$command' timed out after $timeout_seconds seconds (attempt $attempt/$max_retries)"
            local response="ERROR: TIMEOUT"
        fi

        cleanup_temp_files
        if [ $attempt -lt $max_retries ]; then
            log "[info] Retrying AT command '$command' in $retry_delay seconds"
            sleep $retry_delay
        fi
        attempt=$((attempt + 1))
    done
        
    log "[error] AT command '$command' failed after $max_retries attempts"
    trap - EXIT
    echo "$response"
    return 1
}

# Check if atinout binary exists
check_atinout() {
    if [ ! -x "$ATINOUT" ]; then
        log "[error] atinout binary not found at $ATINOUT"
        return 1
    fi
    log "[info] Found atinout binary at $ATINOUT"
    return 0
}

# Check if modem port exists
check_modem_port() {
    if [ -c "$MODEM_PORT" ]; then
        ACTIVE_MODEM_PORT="$MODEM_PORT"
        flush_uart "$ACTIVE_MODEM_PORT"
        log "[info] Modem port $MODEM_PORT found"
    elif [ -c "$MODEM_PORT_DEBUG" ]; then
        ACTIVE_MODEM_PORT="$MODEM_PORT_DEBUG"
        flush_uart "$ACTIVE_MODEM_PORT"
        log "[warn] Modem port $MODEM_PORT not found, falling back to debug port $MODEM_PORT_DEBUG"
    else
        log "[error] Neither modem port $MODEM_PORT nor debug port $MODEM_PORT_DEBUG found"
        return 1
    fi
    return 0
}

# Check modem connectivity
check_modem_connectivity() {
    log "[info] Checking modem connectivity..."
    
    local response=$(send_at_command "AT")
    if echo "$response" | grep -q "OK"; then
        log "[info] Modem is responding"
        return 0
    else
        log "[error] Modem is not responding"
        return 1
    fi
}

# Get current USB configuration
get_usb_config() {
    log "[info] Getting current USB configuration..."
    
    local response=$(send_at_command "AT#USBCFG?")
    if echo "$response" | grep -q "OK"; then
        local current_mode=$(echo "$response" | grep "#USBCFG:" | sed 's/.*#USBCFG: \([0-9]*\).*/\1/')
        echo "$current_mode"
        return 0
    else
        log "[error] Failed to get USB configuration"
        return 1
    fi
}

# Set USB configuration to mode 1 (DIAG+MODEM+MODEM+ECM)
set_usb_config() {
    local target_mode="$1"
    
    log "[info] Setting USB configuration to mode $target_mode (DIAG+MODEM+MODEM+ECM)..."
    
    local response=$(send_at_command "AT#USBCFG=$target_mode")
    if echo "$response" | grep -q "OK"; then
        log "[info] USB configuration set successfully"
        log "[info] Modem reboot required for changes to take effect"
        return 0
    else
        log "[error] Failed to set USB configuration"
        return 1
    fi
}

# Get current APN configuration
get_apn_config() {
    log "[info] Getting current APN configuration..."
    
    local response=$(send_at_command "AT+CGDCONT?" 10)
    if echo "$response" | grep -q "+CGDCONT: 1,"; then
        local current_apn=$(echo "$response" | grep "+CGDCONT: 1," | awk -F '"' '{print $4}')
        echo "$current_apn"
        return 0
    else
        log "[error] Failed to get APN configuration"
        return 1
    fi
}

# Set APN configuration
set_apn_config() {
    local target_apn="$1"
    
    log "[info] Setting APN to $target_apn..."
    
    local response=$(send_at_command "AT+CGDCONT=1,\"IP\",\"$target_apn\"")
    if echo "$response" | grep -q "OK"; then
        log "[info] APN configuration set successfully"
        return 0
    else
        log "[error] Failed to set APN configuration"
        return 1
    fi
}

# Get current operator selection mode
get_operator_config() {
    log "[info] Getting current operator selection mode..."
    
    local response=$(send_at_command "AT+COPS?")
    if echo "$response" | grep -q "OK"; then
        local current_mode=$(echo "$response" | grep "+COPS:" | sed 's/.*+COPS: \([0-9]*\).*/\1/')
        echo "$current_mode"
        return 0
    else
        log "[error] Failed to get operator selection mode"
        return 1
    fi
}

# Set operator selection to automatic
set_operator_config() {
    local target_mode="$1"
    
    log "[info] Setting operator selection to automatic (mode $target_mode)..."
    
    local response=$(send_at_command "AT+COPS=$target_mode")
    if echo "$response" | grep -q "OK"; then
        log "[info] Operator selection set successfully"
        return 0
    else
        log "[error] Failed to set operator selection"
        return 1
    fi
}

# Check ECM mode status
check_ecm_mode() {
    log "[info] Checking ECM mode status..."
    
    local response=$(send_at_command "AT#ECM?")
    if echo "$response" | grep -q "OK"; then
        local ecm_status=$(echo "$response" | grep "#ECM:" | sed 's/.*#ECM: [0-9]*,\([0-9]*\).*/\1/')
        echo "$ecm_status"
        return 0
    else
        log "[error] Failed to get ECM mode status"
        return 1
    fi
}

# Enable ECM mode
enable_ecm_mode() {
    log "[info] Enabling ECM mode..."
    
    local response=$(send_at_command "AT#ECM=1,0")
    if echo "$response" | grep -q "OK"; then
        log "[info] ECM mode enabled successfully"
        return 0
    else
        log "[error] Failed to enable ECM mode"
        return 1
    fi
}

# Check PDP context status
check_pdp_context() {
    log "[info] Checking PDP context status..."
    
    local response=$(send_at_command "AT+CGACT?")
    if echo "$response" | grep -q "OK"; then
        local pdp_status=$(echo "$response" | grep "+CGACT: 1," | sed 's/.*+CGACT: 1,\([0-9]*\).*/\1/')
        echo "$pdp_status"
        return 0
    else
        log "[error] Failed to get PDP context status"
        return 1
    fi
}

# Activate PDP context
activate_pdp_context() {
    log "[info] Activating PDP context..."
    
    local response=$(send_at_command "AT+CGACT=1,1")
    if echo "$response" | grep -q "OK"; then
        log "[info] PDP context activated successfully"
        return 0
    else
        log "[error] Failed to activate PDP context"
        return 1
    fi
}

# Check EPS Network Registration Status
check_eps_registration() {
    log "[info] Checking EPS Network Registration Status..."
    
    local response=$(send_at_command "AT+CEREG?")
    if echo "$response" | grep -q "OK"; then
        local reg_status=$(echo "$response" | grep "+CEREG:" | sed 's/.*+CEREG: [0-9]*,\([0-9]*\).*/\1/')
        case "$reg_status" in
            "1")
                log "[info] EPS registered (home network)"
                return 0
                ;;
            "5")
                log "[info] EPS registered (roaming)"
                return 0
                ;;
            "0")
                log "[error] EPS not registered and not searching"
                return 1
                ;;
            "2")
                log "[error] EPS not registered but searching"
                return 1
                ;;
            "3")
                log "[error] EPS registration denied"
                return 1
                ;;
            *)
                log "[error] EPS registration status unknown: $reg_status"
                return 1
                ;;
        esac
    else
        log "[error] Failed to get EPS registration status"
        return 1
    fi
}

# Check GPRS Network Registration Status
check_gprs_registration() {
    log "[info] Checking GPRS Network Registration Status..."
    
    local response=$(send_at_command "AT+CGREG?")
    if echo "$response" | grep -q "OK"; then
        local reg_status=$(echo "$response" | grep "+CGREG:" | sed 's/.*+CGREG: [0-9]*,\([0-9]*\).*/\1/')
        case "$reg_status" in
            "1")
                log "[info] GPRS registered (home network)"
                return 0
                ;;
            "5")
                log "[info] GPRS registered (roaming)"
                return 0
                ;;
            "0")
                log "[error] GPRS not registered and not searching"
                return 1
                ;;
            "2")
                log "[error] GPRS not registered but searching"
                return 1
                ;;
            "3")
                log "[error] GPRS registration denied"
                return 1
                ;;
            *)
                log "[error] GPRS registration status unknown: $reg_status"
                return 1
                ;;
        esac
    else
        log "[error] Failed to get GPRS registration status"
        return 1
    fi
}

# Wait for network registration
wait_for_registration() {
    log "[info] Waiting for network registration..."
    
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if check_eps_registration >/dev/null 2>&1 || check_gprs_registration >/dev/null 2>&1; then
            log "[info] Network registration successful"
            return 0
        fi
        
        attempts=$((attempts + 1))
        echo -n "."
        sleep 2
    done
    
    echo
    log "[error] Network registration failed after timeout"
    return 1
}

# Reboot modem
reboot_modem() {
    log "[info] Rebooting modem..."
    
    local response=$(send_at_command "AT#REBOOT")
    if echo "$response" | grep -q "OK"; then
        log "[info] Modem reboot command sent successfully"
        log "[info] Waiting for modem to restart..."
        sleep 10
        return 0
    else
        log "[error] Failed to send reboot command"
        return 1
    fi
}

# Wait for modem to be ready after reboot
wait_for_modem() {
    log "[info] Waiting for modem to be ready..."
    
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if check_modem_connectivity >/dev/null 2>&1; then
            log "[info] Modem is ready"
            return 0
        fi
        
        attempts=$((attempts + 1))
        echo -n "."
        sleep 2
    done
    
    echo
    log "[error] Modem failed to respond after reboot"
    return 1
}

read_and_save_iccid() {
    log "[info] Reading ICCID..."
    local response=$(send_at_command "AT+ICCID")
    if echo "$response" | grep -q "+ICCID:"; then
        local iccid=$(echo "$response" | grep "+ICCID:" | sed 's/.*+ICCID: *\([0-9]\+\).*/\1/')
        if [ -n "$iccid" ]; then
            echo "$iccid" > "$ICCID_FILE"
            log "[info] ICCID read and saved: $iccid"
            return 0
        else
            log "[error] Failed to parse ICCID"
            return 1
        fi
    else
        log "[error] Failed to read ICCID"
        return 1
    fi
}

read_and_save_imei() {
    log "[info] Reading IMEI..."
    local response=$(send_at_command "AT+CGSN")
    # IMEI is usually a 15-digit number in the response
    local imei=$(echo "$response" | grep -oE '[0-9]{15}' | head -n1)
    if [ -n "$imei" ]; then
        echo "$imei" > "$IMEI_FILE"
        log "[info] IMEI read and saved: $imei"
        return 0
    else
        log "[error] Failed to read IMEI"
        return 1
    fi
}

enable_gpsd() {
    log "[info] Enabling GPS..."
    local response
    response=$(send_at_command 'AT$GPSP=1')
    if echo "$response" | grep -q "OK"; then
        log "[info] GPS enabled successfully: $response"
        sleep 5
        return 0
    else
        log "[error] Failed to enable GPS: $response"
        return 1
    fi
}

read_gps_data() {
    local duration="${1:-120}"
    local interval="${2:-1}"
    local elapsed=0

    log "[info] Reading GPS data every $interval second(s) for $([ "$duration" -eq -1 ] && echo "infinite" || echo "$duration seconds")..."

    enable_gpsd

    if [ "$duration" -eq -1 ]; then
        while true; do
            local response
            response=$(send_at_command 'AT$GPSACP')
            if echo "$response" | grep -q "\$GPSACP:"; then
                log "[gps] $response"
            else
                log "[gps][error] Failed to read GPS data: $response"
            fi
            sleep "$interval"
        done
    else
        while [ $elapsed -lt $duration ]; do
            local response
            response=$(send_at_command 'AT$GPSACP')
            if echo "$response" | grep -q "\$GPSACP:"; then
                log "[gps] $response"
            else
                log "[gps][error] Failed to read GPS data: $response"
            fi
            sleep "$interval"
            elapsed=$((elapsed + interval))
        done

        # Stop GPS after reading
        log "[info] Stopping GPS after $duration seconds..."
        send_at_command 'AT$GPSP=0'
    fi
}

monitor_uart() {    
    log "[info] Starting UART monitoring on $MODEM_PORT_DEBUG"
    
    if [ ! -c "$MODEM_PORT_DEBUG" ]; then
        log "[error] UART port $MODEM_PORT_DEBUG not found"
        return 1
    fi

    send_at_command 'AT#TRACE=1'
    flush_uart "$MODEM_PORT_DEBUG"
    
    while true; do
        if stdbuf -o0 dd if="$MODEM_PORT_DEBUG" bs=1024 count=1 iflag=nonblock 2>/dev/null | grep -q .; then
            stdbuf -o0 dd if="$MODEM_PORT_DEBUG" bs=1024 count=1 2>/dev/null | 
            while IFS= read -r line; do
                log "[telit] $line"
            done
        fi
        sleep 0.5
    done
}

cleanup() {
    log "[warn] Received termination signal, cleaning up..."
    exit 0
}

set_active_modem_port() {
    local usb_mode="$1"
    if [ "$usb_mode" = "1" ]; then
        ACTIVE_MODEM_PORT="$MODEM_PORT"
    else
        ACTIVE_MODEM_PORT="$MODEM_PORT_DEBUG"
    fi
    log "[info] Using $ACTIVE_MODEM_PORT for AT commands (USB mode: $usb_mode)"
}

trap cleanup SIGTERM SIGINT SIGQUIT

# Main function
main() {
    log "[info] Starting Telit LTE modem initialization..."
    sleep 1
        
    # Check prerequisites
    if ! check_atinout; then
        exit 1
    fi
    
    if ! check_modem_port; then
        exit 1
    fi
    
    # Check modem connectivity
    if ! check_modem_connectivity; then
        exit 1
    fi
    
    # Check and configure USB mode first
    log "[info] Checking usb config"
    current_usb_mode=$(get_usb_config)
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    log "[info] Current USB mode: $current_usb_mode"
    
    if [ "$current_usb_mode" != "$REQUIRED_USB_MODE" ]; then
        if ! set_usb_config "$REQUIRED_USB_MODE"; then
            exit 1
        fi
        
        # Reboot modem immediately after USB mode change
        log "[info] USB mode changed, rebooting modem..."
        # if ! reboot_modem; then
        #     exit 1
        # fi
        
        if ! wait_for_modem; then
            exit 1
        fi
        
        # Verify USB configuration after reboot
        new_usb_mode=$(get_usb_config)
        if [ $? -ne 0 ]; then
            log "[warn] Could not verify new USB configuration"
        else
            set_active_modem_port "$new_usb_mode"
            if [ "$new_usb_mode" = "$REQUIRED_USB_MODE" ]; then
                log "[info] USB configuration verified: mode $new_usb_mode (DIAG+MODEM+MODEM+ECM)"
            else
                log "[error] USB configuration verification failed: expected $REQUIRED_USB_MODE, got $new_usb_mode"
                exit 1
            fi
        fi
    else
        log "[info] USB mode is already configured correctly (mode $REQUIRED_USB_MODE)"
    fi
    
    # Now configure APN and operator settings (after potential reboot)
    # Check and configure APN
    current_apn=$(get_apn_config)
    if [ $? -ne 0 ]; then
        log "[warn] Could not retrieve current APN configuration, attempting to set..."
        if ! set_apn_config "$REQUIRED_APN"; then
            log "[error] Failed to set APN configuration, continuing..."
        else
            log "[info] APN configured to $REQUIRED_APN"
        fi
    elif [ "$current_apn" != "$REQUIRED_APN" ]; then
        if ! set_apn_config "$REQUIRED_APN"; then
            log "[error] Failed to set APN configuration, continuing..."
        else
            log "[info] APN configured to $REQUIRED_APN"
        fi
    else
        log "[info] APN is already configured correctly ($REQUIRED_APN)"
    fi
    
    # Check and configure operator selection
    current_operator_mode=$(get_operator_config)
    if [ $? -ne 0 ]; then
        log "[warn] Could not retrieve current operator selection mode, attempting to set..."
        if ! set_operator_config "$REQUIRED_OPERATOR_MODE"; then
            log "[error] Failed to set operator selection, continuing..."
        else
            log "[info] Operator selection configured to automatic"
        fi
    elif [ "$current_operator_mode" != "$REQUIRED_OPERATOR_MODE" ]; then
        if ! set_operator_config "$REQUIRED_OPERATOR_MODE"; then
            log "[error] Failed to set operator selection, continuing..."
        else
            log "[info] Operator selection configured to automatic"
        fi
    else
        log "[info] Operator selection is already configured correctly (automatic)"
    fi
    
    # Check network registration status
    log "[info] Checking network registration status..."
    if check_eps_registration; then
        log "[info] EPS network registration OK"
    elif check_gprs_registration; then
        log "[info] GPRS network registration OK"
    else
        log "[warn] Network not registered, waiting for registration..."
        if ! wait_for_registration; then
            log "[error] Network registration failed"
            exit 1
        fi
    fi
    
    # Check and enable ECM mode
    current_ecm_mode=$(check_ecm_mode)
    if [ $? -ne 0 ]; then
        log "[warn] Could not retrieve current ECM mode status"
    elif [ "$current_ecm_mode" != "1" ]; then
        if ! enable_ecm_mode; then
            log "[error] Failed to enable ECM mode, continuing..."
        else
            log "[info] ECM mode enabled successfully"
        fi
    else
        log "[info] ECM mode is already enabled"
    fi
    
    # Check and activate PDP context
    current_pdp_status=$(check_pdp_context)
    if [ $? -ne 0 ]; then
        log "[error] Could not retrieve PDP context status"
    elif [ "$current_pdp_status" != "1" ]; then
        if ! activate_pdp_context; then
            log "[error] Failed to activate PDP context, continuing..."
        else
            log "[info] PDP context activated successfully"
        fi
    else
        log "[info] PDP context is already active"
    fi

    read_and_save_iccid
    read_and_save_imei
    
    log "[info] Telit modem initialization completed successfully"
    
    monitor_uart
}

touch "$LOG_FILE"

# Run main function
main "$@"