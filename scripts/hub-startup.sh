#!/bin/sh

log_info() {
    current_time=$(date +%F_%T)
    echo "$current_time,    INFO     [hub-startup.sh] $1" >> /var/log/hub/hub-startup.log
}

log_info "Starting hub-startup.sh"

gpioset -c 1 -z -C "hub-setup-can" 5=0        # turn off "SLOPE_IN" for can bus

echo "alias ll='ls -al'" > /etc/profile.d/hub-profile.sh
echo "PATH=${PATH}:/usr/bin/hub" >> /etc/profile.d/hub-profile.sh
echo "HUB_LOG_LEVEL=${HUB_LOG_LEVEL}" >> /etc/profile.d/hub-profile.sh
echo "HUB_CONFIGDIR=${HUB_CONFIGDIR}" >> /etc/profile.d/hub-profile.sh
echo "HUB_LOGDIR=${HUB_LOGDIR}" >> /etc/profile.d/hub-profile.sh
echo "HUB_NET_CONFIG=${HUB_NET_CONFIG}" >> /etc/profile.d/hub-profile.sh
echo "export PATH HUB_LOG_LEVEL HUB_CONFIGDIR HUB_LOGDIR HUB_NET_CONFIG" >> /etc/profile.d/hub-profile.sh

counter=0

until ip link show wwan0; do
    log_info "Waiting for wwan0 to be available"
    sleep 1
    counter=$((counter+1))
    if [ $counter -gt 10 ]; then
        log_info "wwan0 not available after 10 seconds"
        break
    fi
done

udhcpc -q -f -i wwan0

echo "nameserver 8.8.8.8" > /run/NetworkManager/resolv.conf

log_info "Finished hub-startup.sh"