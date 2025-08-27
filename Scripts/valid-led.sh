#!/usr/bin/bash

# GPIO pin definitions (removing duplicates)
STATUS_LED=22    # Status LED/Wifi - GPIO_IO22 - gpio2.IO[22]
WWAN_LED=2       # wwan/LTE - GPIO_IO02 - gpio2.IO[2]
ETH_LED=3        # Ethernet - GPIO_IO03 - gpio2.IO[3]
CAN1_LED=20      # CAN1 - GPIO_IO20 - gpio2.IO[20]
CAN2_LED=21      # CAN2 - GPIO_IO21 - gpio2.IO[21]

CHIP_ID=0
CHIP_NAME="gpiochip${CHIP_ID}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

declare -A PIN_PIDS

cleanup() {
    echo "Running cleanup..."
    # Iterate through all pins with active processes
    for pin in "${!PIN_PIDS[@]}"; do
        pid=${PIN_PIDS[$pin]}
        echo "Killing PID $pid for GPIO pin $pin"
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
            wait $pid 2>/dev/null || true
        fi
    done
    # Clear the array
    PIN_PIDS=()
}

trap cleanup EXIT INT TERM HUP

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}This script must be run as root${NC}"
    exit 1
fi

if ! command -v gpioset &> /dev/null; then
    echo -e "${RED}gpioset command not found. Please install libgpiod-tools.${NC}"
    exit 1
fi

if [ ! -e "/dev/${CHIP_NAME}" ]; then
    echo -e "${RED}GPIO chip ${CHIP_NAME} not found${NC}"
    exit 1
fi

set_gpio() {
    local gpio_pin=$1
    local value=$2
    
    # Kill any existing process for this pin
    if [[ -n "${PIN_PIDS[$gpio_pin]}" ]]; then
        pid=${PIN_PIDS[$gpio_pin]}
        echo "Killing previous process (PID: $pid) for GPIO pin $gpio_pin"
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
            wait $pid 2>/dev/null || true
        fi
        unset PIN_PIDS[$gpio_pin]
    fi
    
    if [ "$value" -eq 1 ]; then
        echo "Setting GPIO $gpio_pin to ON"
        gpioset -c ${CHIP_ID} ${gpio_pin}=0 &
        local pid=$!
        PIN_PIDS[$gpio_pin]=$pid
        echo "Started process PID $pid for GPIO pin $gpio_pin (ON)"
        sleep 0.1
        return 0
    else
        echo "Setting GPIO $gpio_pin to OFF"
        gpioset -c ${CHIP_ID} ${gpio_pin}=1 &
        local pid=$!
        PIN_PIDS[$gpio_pin]=$pid
        echo "Started process PID $pid for GPIO pin $gpio_pin (OFF)"
        sleep 0.1
        return 0
    fi
}

test_led() {
    local gpio_pin=$1
    local led_name=$2
    
    echo -e "${YELLOW}Testing ${led_name} LED on GPIO 2.${gpio_pin}...${NC}"
    
    # Turn LED on
    if set_gpio ${gpio_pin} 1; then
        echo -e "${GREEN}${led_name} LED turned ON${NC}"
    else
        echo -e "${RED}Failed to turn ON ${led_name} LED${NC}"
        return 1
    fi
    
    # Wait for user to confirm
    read -p "Can you see the ${led_name} LED ON? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}${led_name} LED test failed (user reported LED not ON)${NC}"
        set_gpio ${gpio_pin} 0
        return 1
    fi
    
    # Turn LED off
    if set_gpio ${gpio_pin} 0; then
        echo -e "${GREEN}${led_name} LED turned OFF${NC}"
    else
        echo -e "${RED}Failed to turn OFF ${led_name} LED${NC}"
        return 1
    fi
    
    # Wait for user to confirm
    read -p "Can you see the ${led_name} LED OFF? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}${led_name} LED test failed (user reported LED not OFF)${NC}"
        return 1
    fi
    
    echo -e "${GREEN}${led_name} LED test passed!${NC}"
    return 0
}

# Function to blink LED for a specific duration
blink_led() {
    local gpio_pin=$1
    local led_name=$2
    local blink_count=$3
    local delay=0.5
    
    echo -e "${YELLOW}Blinking ${led_name} LED ${blink_count} times...${NC}"
    
    for ((i=1; i<=${blink_count}; i++)); do
        set_gpio ${gpio_pin} 1
        sleep ${delay}
        set_gpio ${gpio_pin} 0
        sleep ${delay}
    done
}

# Main test sequence
echo "=== Empower Hub LED Validation Tool ==="
echo "This script will test all LEDs connected to GPIOs."
echo "Please observe the LEDs and confirm if they turn on and off correctly."
echo

# Test each LED
test_led ${STATUS_LED} "Status/WiFi"
status_result=$?

test_led ${CAN1_LED} "CAN1"
can1_result=$?

test_led ${CAN2_LED} "CAN2"
can2_result=$?

# Test the two additional LEDs
test_led ${WWAN_LED} "WWAN/LTE"
wwan_result=$?

test_led ${ETH_LED} "Ethernet"
eth_result=$?

# Print summary
echo
echo "=== Test Results Summary ==="
[ ${status_result} -eq 0 ] && echo -e "${GREEN}Status/WiFi LED: PASS${NC}" || echo -e "${RED}Status/WiFi LED: FAIL${NC}"
[ ${can1_result} -eq 0 ] && echo -e "${GREEN}CAN1 LED: PASS${NC}" || echo -e "${RED}CAN1 LED: FAIL${NC}"
[ ${can2_result} -eq 0 ] && echo -e "${GREEN}CAN2 LED: PASS${NC}" || echo -e "${RED}CAN2 LED: FAIL${NC}"
[ ${wwan_result} -eq 0 ] && echo -e "${GREEN}WWAN/LTE LED: PASS${NC}" || echo -e "${RED}WWAN/LTE LED: FAIL${NC}"
[ ${eth_result} -eq 0 ] && echo -e "${GREEN}Ethernet LED: PASS${NC}" || echo -e "${RED}Ethernet LED: FAIL${NC}"

# Final blinking celebration if all tests passed
if [ ${status_result} -eq 0 ] && [ ${can1_result} -eq 0 ] && [ ${can2_result} -eq 0 ] && [ ${wwan_result} -eq 0 ] && [ ${eth_result} -eq 0 ]; then
    echo -e "\n${GREEN}All LED tests PASSED! Performing final validation sequence...${NC}"
    blink_led ${STATUS_LED} "Status/WiFi" 5
    blink_led ${CAN1_LED} "CAN1" 5
    blink_led ${CAN2_LED} "CAN2" 5
    blink_led ${WWAN_LED} "WWAN/LTE" 5
    blink_led ${ETH_LED} "Ethernet" 5
    echo -e "\n${GREEN}LED validation complete! All LEDs are functioning correctly.${NC}"
    # Call cleanup explicitly before exit
    cleanup
    exit 0
else
    echo -e "\n${RED}Some LED tests FAILED. Please check the hardware connections.${NC}"
    # Call cleanup explicitly before exit
    cleanup
    exit 1
fi