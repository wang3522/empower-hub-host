#!/usr/bin/bash

# Service configuration
REGULAR_SERVICES="hub-bl654.service hub-n2k.service hub-network-switch.service hub-provisioning.service hub-tbclient.service hub-telit.service"

# Configuration
HEALTH_CHECK_INTERVAL=30  # seconds
LOG_FILE="/data/hub/log/hub-watchdog.log"
RESTART_DELAY=5          # seconds between restart attempts
MAX_RESTART_ATTEMPTS=3   # maximum restart attempts before marking as failed

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if a service is active
is_service_active() {
    local service="$1"
    systemctl is-active --quiet "$service"
    return $?
}

# Function to check if a service is enabled
is_service_enabled() {
    local service="$1"
    systemctl is-enabled --quiet "$service"
    return $?
}

# Function to start a service
start_service() {
    local service="$1"
    log "Starting service: $service"
    if systemctl start "$service"; then
        log "Successfully started: $service"
        return 0
    else
        log "Failed to start: $service"
        return 1
    fi
}

# Function to restart a service with retry logic
restart_service() {
    local service="$1"
    local attempt=1
    
    log "Attempting to restart service: $service"
    
    while [ $attempt -le $MAX_RESTART_ATTEMPTS ]; do
        log "Restart attempt $attempt for $service"
        
        # Stop the service first
        systemctl stop "$service" 2>/dev/null
        sleep $RESTART_DELAY
        
        # Start the service
        if start_service "$service"; then
            log "Successfully restarted $service on attempt $attempt"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep $RESTART_DELAY
    done
    
    log "Failed to restart $service after $MAX_RESTART_ATTEMPTS attempts"
    return 1
}

# Health check function (placeholder - implement specific checks per service)
health_check() {
    local service="$1"
    
    # TODO: Implement specific health checks for each service
    case "$service" in
        "hub-bl654.service")
            # TODO: Add BL654 specific health check
            # Example: check if BLE interface is responsive
            log "Health check for $service - TODO: implement BL654 specific check"
            return 0
            ;;
        "hub-n2k.service")
            # TODO: Add NMEA 2000 specific health check
            # Example: check if N2K bus is active
            log "Health check for $service - TODO: implement N2K specific check"
            return 0
            ;;
        "hub-network-switch.service")
            # TODO: Add network switch health check
            # Example: check network connectivity
            log "Health check for $service - TODO: implement network switch check"
            return 0
            ;;
        "hub-provisioning.service")
            # TODO: Add provisioning service health check
            # Example: check API endpoint response
            log "Health check for $service - TODO: implement provisioning check"
            return 0
            ;;
        "hub-tbclient.service")
            # TODO: Add TB client health check
            # Example: check ThingsBoard connection
            log "Health check for $service - TODO: implement TB client check"
            return 0
            ;;
        "hub-telit.service")
            # TODO: Add Telit modem health check
            # Example: check modem AT command response
            log "Health check for $service - TODO: implement Telit check"
            return 0
            ;;
        *)
            log "Unknown service for health check: $service"
            return 1
            ;;
    esac
}

# Function to monitor a regular service
monitor_regular_service() {
    local service="$1"
    
    if ! is_service_active "$service"; then
        log "Service $service is not active, attempting restart"
        restart_service "$service"
    else
        # Perform health check
        if ! health_check "$service"; then
            log "Health check failed for $service, restarting"
            restart_service "$service"
        fi
    fi
}

# Function to monitor oneshot service
monitor_oneshot_service() {
    local service="$1"
    
    # For oneshot services with RemainAfterExit=yes, check if they exited successfully
    local exit_code=$(systemctl show -p ExecMainStatus --value "$service")
    local active_state=$(systemctl show -p ActiveState --value "$service")
    
    if [ "$active_state" != "active" ] || [ "$exit_code" != "0" ]; then
        log "Oneshot service $service needs restart (ActiveState: $active_state, ExitCode: $exit_code)"
        restart_service "$service"
    else
        # Perform health check even for oneshot services
        if ! health_check "$service"; then
            log "Health check failed for oneshot service $service, restarting"
            restart_service "$service"
        fi
    fi
}

# Function to initialize services
initialize_services() {
    log "Initializing hub services..."
    
    # Start regular services
    for service in $REGULAR_SERVICES; do
        if ! is_service_enabled "$service"; then
            log "Service $service is not enabled..."
        fi

        if ! is_service_active "$service"; then
            start_service "$service"
        fi
    done
    
    log "Service initialization complete"
}

# Signal handlers
cleanup() {
    log "Hub watchdog received termination signal, cleaning up..."
    exit 0
}

execute_factory_setup() {
    log "Starting factory setup mode..."
    # TODO: Implement factory setup scripts execution
    # Example factory setup tasks:
    # - Initial configuration
    # - Factory calibration
    # - Default settings application
    log "TODO: Implement factory setup script execution"
    # Add your factory setup commands here
    
    log "Factory setup complete"
}

# Function to execute validation scripts
execute_validation() {
    log "Starting validation mode..."
    # TODO: Implement validation script execution
    # Example validation tasks:
    # - Service functionality tests
    # - Hardware validation
    # - Configuration verification
    log "TODO: Implement validation script execution"
    # Add your validation commands here
    
    log "Validation complete"
}

# Trap signals
trap cleanup SIGTERM SIGINT SIGQUIT

# Main watchdog loop
main() {
    log "Starting Hub Watchdog..."

    # Check command line arguments
    case "${HUB_MODE:-}" in
        "factory")
            log "Starting Hub Watchdog in factory mode (from HUB_MODE env var)..."
            execute_factory_setup
            exit 0
            ;;
        "validation")
            log "Starting Hub Watchdog in validation mode (from HUB_MODE env var)..."
            execute_validation
            exit 0
            ;;
        "normal"|"")
            # Normal mode or no environment variable set
            log "Starting Hub Watchdog in normal mode..."
            initialize_services
            ;;
        *)
            log "Error: Unknown HUB_MODE environment variable value '$HUB_MODE'"
            log "Valid values: factory, validation, normal"
            exit 1
            ;;
    esac
    
    # Main monitoring loop
    while true; do
        # Monitor regular services
        for service in $REGULAR_SERVICES; do
            monitor_regular_service "$service"
        done
        
        # Wait before next check
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log "Error: Hub watchdog must be run as root"
    exit 1
fi

# Create log file if it doesn't exist
touch "$LOG_FILE"

# Start the watchdog
main "$@"