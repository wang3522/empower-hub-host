#!/usr/bin/bash

# GPIO pin definitions for High Side Switches
# High Switch 1
HS1_EN1=8        # High Switch 1 EN1 (Out 1) - GPIO_IO08 - GPIO2.8
HS1_EN2=9        # High Switch 1 EN2 (Out 2) - GPIO_IO09 - GPIO2.9
HS1_SEL1=11      # High Switch 1 SEL1 - GPIO_IO11 - GPIO2.11
HS1_SEL2=12      # High Switch 1 SEL2 - GPIO_IO12 - GPIO2.12
HS1_LATCH=10     # High Switch 1 LATCH - GPIO_IO10 - GPIO2.10
HS1_DIA_EN=13    # High Switch 1 DIA_EN - GPIO_IO13 - GPIO2.13
HS1_SNS=6        # [x] find out correct pin and chip

# High Switch 2
HS2_EN1=14       # High Switch 2 EN1 (Out 3) - GPIO_IO14 - GPIO2.14
HS2_EN2=15       # High Switch 2 EN2 (Out 4) - GPIO_IO15 - GPIO2.15
HS2_SEL1=17      # High Switch 2 SEL1 - GPIO_IO17 - GPIO2.17
HS2_SEL2=18      # High Switch 2 SEL2 - GPIO_IO18 - GPIO2.18
HS2_LATCH=16     # High Switch 2 LATCH - GPIO_IO16 - GPIO2.16
HS2_DIA_EN=19    # High Switch 2 DIA_EN - GPIO_IO19 - GPIO2.19
HS2_SNS=7        # [x] find out correct pin and chip

CHIP_ID=0
CHIP_NAME="gpiochip${CHIP_ID}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
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

if ! command -v gpioget &> /dev/null; then
    echo -e "${RED}gpioget command not found. Please install libgpiod-tools.${NC}"
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
        echo "Setting GPIO $gpio_pin to HIGH"
        gpioset -c ${CHIP_ID} ${gpio_pin}=1 &
        local pid=$!
        PIN_PIDS[$gpio_pin]=$pid
        echo "Started process PID $pid for GPIO pin $gpio_pin (HIGH)"
        sleep 0.1
        return 0
    else
        echo "Setting GPIO $gpio_pin to LOW"
        gpioset -c ${CHIP_ID} ${gpio_pin}=0 &
        local pid=$!
        PIN_PIDS[$gpio_pin]=$pid
        echo "Started process PID $pid for GPIO pin $gpio_pin (LOW)"
        sleep 0.1
        return 0
    fi
}

# Function to read a GPIO input value
read_gpio() {
    local gpio_pin=$1
    local value
    
    # [x] Makesure chipid is correct for sns pin, Read the GPIO pin using gpioget
    value=$(gpioget -c ${CHIP_ID} ${gpio_pin} 2>/dev/null)
    
    # Check if the read was successful
    if [ $? -eq 0 ]; then
        echo $value
        return 0
    else
        echo "Error reading GPIO pin $gpio_pin"
        return 1
    fi
}

# Initialize switch pins to default state
initialize_switch() {
    local switch=$1
    
    echo -e "${BLUE}Initializing High Side Switch $switch to default state...${NC}"
    
    if [ "$switch" -eq 1 ]; then
        # Default state for High Switch 1
        set_gpio ${HS1_EN1} 0
        set_gpio ${HS1_EN2} 0
        set_gpio ${HS1_SEL1} 0
        set_gpio ${HS1_SEL2} 0
        set_gpio ${HS1_LATCH} 0
        set_gpio ${HS1_DIA_EN} 0
    else
        # Default state for High Switch 2
        set_gpio ${HS2_EN1} 0
        set_gpio ${HS2_EN2} 0
        set_gpio ${HS2_SEL1} 0
        set_gpio ${HS2_SEL2} 0
        set_gpio ${HS2_LATCH} 0
        set_gpio ${HS2_DIA_EN} 0
    fi
    
    echo -e "${GREEN}High Side Switch $switch initialized${NC}"
}

# Test output enable/disable
test_output() {
    local switch=$1
    local output=$2
    local en_pin
    local output_name
    
    if [ "$switch" -eq 1 ]; then
        if [ "$output" -eq 1 ]; then
            en_pin=${HS1_EN1}
            output_name="Output 1"
        else
            en_pin=${HS1_EN2}
            output_name="Output 2"
        fi
    else
        if [ "$output" -eq 1 ]; then
            en_pin=${HS2_EN1}
            output_name="Output 3"
        else
            en_pin=${HS2_EN2}
            output_name="Output 4"
        fi
    fi
    
    echo -e "${YELLOW}Testing High Switch $switch - $output_name (GPIO 2.${en_pin})...${NC}"
    
    # Enable output
    set_gpio ${en_pin} 1
    echo -e "${GREEN}$output_name enabled${NC}"
    
    read -p "Is $output_name ON? (Measure output with a multimeter or check connected device) (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}$output_name enable test failed${NC}"
        set_gpio ${en_pin} 0
        return 1
    fi
    
    # Disable output
    set_gpio ${en_pin} 0
    echo -e "${GREEN}$output_name disabled${NC}"
    
    read -p "Is $output_name OFF? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}$output_name disable test failed${NC}"
        return 1
    fi
    
    echo -e "${GREEN}$output_name test passed!${NC}"
    return 0
}

# Test SEL pins (mode selection)
test_sel_pins() {
    local switch=$1
    local sel1_pin
    local sel2_pin
    
    if [ "$switch" -eq 1 ]; then
        sel1_pin=${HS1_SEL1}
        sel2_pin=${HS1_SEL2}
    else
        sel1_pin=${HS2_SEL1}
        sel2_pin=${HS2_SEL2}
    fi
    
    echo -e "${YELLOW}Testing High Switch $switch - SEL pins...${NC}"
    
    # Test SEL1
    set_gpio ${sel1_pin} 1
    echo -e "${GREEN}SEL1 set to HIGH${NC}"
    
    read -p "Did the switch behavior change as expected for SEL1=HIGH? (y/n): " -n 1 -r
    echo
    sel1_result=$?
    set_gpio ${sel1_pin} 0
    
    # Test SEL2
    set_gpio ${sel2_pin} 1
    echo -e "${GREEN}SEL2 set to HIGH${NC}"
    
    read -p "Did the switch behavior change as expected for SEL2=HIGH? (y/n): " -n 1 -r
    echo
    sel2_result=$?
    set_gpio ${sel2_pin} 0
    
    # Test both SEL1 and SEL2
    set_gpio ${sel1_pin} 1
    set_gpio ${sel2_pin} 1
    echo -e "${GREEN}Both SEL1 and SEL2 set to HIGH${NC}"
    
    read -p "Did the switch behavior change as expected for SEL1=HIGH, SEL2=HIGH? (y/n): " -n 1 -r
    echo
    both_sel_result=$?
    set_gpio ${sel1_pin} 0
    set_gpio ${sel2_pin} 0
    
    if [[ ${sel1_result} -eq 0 && ${sel2_result} -eq 0 && ${both_sel_result} -eq 0 ]]; then
        echo -e "${GREEN}SEL pins test passed!${NC}"
        return 0
    else
        echo -e "${RED}SEL pins test failed${NC}"
        return 1
    fi
}

# Test LATCH function
test_latch() {
    local switch=$1
    local latch_pin
    
    if [ "$switch" -eq 1 ]; then
        latch_pin=${HS1_LATCH}
    else
        latch_pin=${HS2_LATCH}
    fi
    
    echo -e "${YELLOW}Testing High Switch $switch - LATCH function...${NC}"
    
    # Set LATCH
    set_gpio ${latch_pin} 1
    echo -e "${GREEN}LATCH set to HIGH${NC}"
    
    read -p "Did the switch latch as expected? (y/n): " -n 1 -r
    echo
    latch_high_result=$?
    
    # Clear LATCH
    set_gpio ${latch_pin} 0
    echo -e "${GREEN}LATCH set to LOW${NC}"
    
    read -p "Did the switch unlatch as expected? (y/n): " -n 1 -r
    echo
    latch_low_result=$?
    
    if [[ ${latch_high_result} -eq 0 && ${latch_low_result} -eq 0 ]]; then
        echo -e "${GREEN}LATCH test passed!${NC}"
        return 0
    else
        echo -e "${RED}LATCH test failed${NC}"
        return 1
    fi
}

# Test diagnostics enable and read SNS pin
test_dia_en() {
    local switch=$1
    local dia_en_pin
    local sns_pin
    local en_pin
    
    if [ "$switch" -eq 1 ]; then
        dia_en_pin=${HS1_DIA_EN}
        sns_pin=${HS1_SNS}
        en_pin=${HS1_EN1}
    else
        dia_en_pin=${HS2_DIA_EN}
        sns_pin=${HS2_SNS}
        en_pin=${HS2_EN1}
    fi
    
    echo -e "${YELLOW}Testing High Switch $switch - Diagnostics function...${NC}"
    
    # Enable diagnostics
    set_gpio ${dia_en_pin} 1
    echo -e "${GREEN}Diagnostics enabled${NC}"
    
    # Read initial SNS value
    local initial_sns=$(read_gpio ${sns_pin})
    echo -e "${BLUE}Initial SNS pin value: ${initial_sns}${NC}"
    
    # Enable output to test diagnostics in normal state
    set_gpio ${en_pin} 1
    echo -e "${GREEN}Output enabled to test diagnostics${NC}"
    
    # Read SNS value with output on
    sleep 0.5 # Give time for SNS to update
    local output_on_sns=$(read_gpio ${sns_pin})
    echo -e "${BLUE}SNS pin value with output ON: ${output_on_sns}${NC}"
    
    read -p "Would you like to test fault detection? This requires creating a fault condition (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Please create a fault condition (e.g., short circuit or overload) and press Enter${NC}"
        read -p "Press Enter when ready..."
        
        # Read SNS value during fault
        sleep 0.5 # Give time for SNS to update
        local fault_sns=$(read_gpio ${sns_pin})
        echo -e "${BLUE}SNS pin value during fault: ${fault_sns}${NC}"
        
        # Check if SNS value changed during fault
        if [ "$fault_sns" != "$output_on_sns" ]; then
            echo -e "${GREEN}Fault detected! SNS pin value changed.${NC}"
        else
            echo -e "${YELLOW}No change in SNS pin value. Fault may not be detected or not present.${NC}"
        fi
        
        echo -e "${YELLOW}Please remove the fault condition and press Enter${NC}"
        read -p "Press Enter when ready..."
    fi
    
    # Disable output
    set_gpio ${en_pin} 0
    echo -e "${GREEN}Output disabled${NC}"
    
    # Disable diagnostics
    set_gpio ${dia_en_pin} 0
    echo -e "${GREEN}Diagnostics disabled${NC}"
    
    # Final read of SNS pin
    sleep 0.5 # Give time for SNS to update
    local final_sns=$(read_gpio ${sns_pin})
    echo -e "${BLUE}Final SNS pin value: ${final_sns}${NC}"
    
    read -p "Did diagnostic functionality work as expected? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Diagnostics test passed!${NC}"
        return 0
    else
        echo -e "${RED}Diagnostics test failed${NC}"
        return 1
    fi
}

# Main test sequence
echo "=== Empower Hub High Side Switch Validation Tool ==="
echo "This script will test all functions of the TPS2HB35BQPWPRQ1 high side switches."
echo "Please have appropriate measurement equipment connected to monitor outputs."
echo

# Test High Side Switch 1
echo -e "${BLUE}=== Testing High Side Switch 1 ===${NC}"
initialize_switch 1

test_output 1 1  # Test Output 1
hs1_out1_result=$?

test_output 1 2  # Test Output 2
hs1_out2_result=$?

test_sel_pins 1  # Test SEL pins
hs1_sel_result=$?

test_latch 1     # Test LATCH function
hs1_latch_result=$?

test_dia_en 1    # Test diagnostics with SNS reading
hs1_dia_result=$?

# Test High Side Switch 2
echo -e "${BLUE}=== Testing High Side Switch 2 ===${NC}"
initialize_switch 2

test_output 2 1  # Test Output 3
hs2_out1_result=$?

test_output 2 2  # Test Output 4
hs2_out2_result=$?

test_sel_pins 2  # Test SEL pins
hs2_sel_result=$?

test_latch 2     # Test LATCH function
hs2_latch_result=$?

test_dia_en 2    # Test diagnostics with SNS reading
hs2_dia_result=$?

# Print summary
echo
echo "=== Test Results Summary ==="
echo -e "${BLUE}High Side Switch 1:${NC}"
[ ${hs1_out1_result} -eq 0 ] && echo -e "${GREEN}Output 1: PASS${NC}" || echo -e "${RED}Output 1: FAIL${NC}"
[ ${hs1_out2_result} -eq 0 ] && echo -e "${GREEN}Output 2: PASS${NC}" || echo -e "${RED}Output 2: FAIL${NC}"
[ ${hs1_sel_result} -eq 0 ] && echo -e "${GREEN}SEL Pins: PASS${NC}" || echo -e "${RED}SEL Pins: FAIL${NC}"
[ ${hs1_latch_result} -eq 0 ] && echo -e "${GREEN}LATCH: PASS${NC}" || echo -e "${RED}LATCH: FAIL${NC}"
[ ${hs1_dia_result} -eq 0 ] && echo -e "${GREEN}Diagnostics: PASS${NC}" || echo -e "${RED}Diagnostics: FAIL${NC}"

echo -e "${BLUE}High Side Switch 2:${NC}"
[ ${hs2_out1_result} -eq 0 ] && echo -e "${GREEN}Output 3: PASS${NC}" || echo -e "${RED}Output 3: FAIL${NC}"
[ ${hs2_out2_result} -eq 0 ] && echo -e "${GREEN}Output 4: PASS${NC}" || echo -e "${RED}Output 4: FAIL${NC}"
[ ${hs2_sel_result} -eq 0 ] && echo -e "${GREEN}SEL Pins: PASS${NC}" || echo -e "${RED}SEL Pins: FAIL${NC}"
[ ${hs2_latch_result} -eq 0 ] && echo -e "${GREEN}LATCH: PASS${NC}" || echo -e "${RED}LATCH: FAIL${NC}"
[ ${hs2_dia_result} -eq 0 ] && echo -e "${GREEN}Diagnostics: PASS${NC}" || echo -e "${RED}Diagnostics: FAIL${NC}"

# Final result
hs1_result=$((${hs1_out1_result} + ${hs1_out2_result} + ${hs1_sel_result} + ${hs1_latch_result} + ${hs1_dia_result}))
hs2_result=$((${hs2_out1_result} + ${hs2_out2_result} + ${hs2_sel_result} + ${hs2_latch_result} + ${hs2_dia_result}))

if [ ${hs1_result} -eq 0 ] && [ ${hs2_result} -eq 0 ]; then
    echo -e "\n${GREEN}All high side switch tests PASSED!${NC}"
    echo -e "${GREEN}High side switch validation complete! All functions are working correctly.${NC}"
    # Call cleanup explicitly before exit
    cleanup
    exit 0
else
    echo -e "\n${RED}Some high side switch tests FAILED. Please check the hardware connections.${NC}"
    # Call cleanup explicitly before exit
    cleanup
    exit 1
fi