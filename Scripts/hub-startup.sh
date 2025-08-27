#!/bin/sh

log_info() {
    current_time=$(date +%F_%T)
    echo "$current_time,    INFO     [hub-startup.sh] $1" >> /data/hub/log/hub-startup.log
}

log_info "Starting hub-startup.sh"

gpioset -c 1 -z -C "hub-setup-can" 5=0        # turn off "SLOPE_IN" for can bus
. /data/hub/config/environmentfile

echo "alias ll='ls -al'" > /etc/profile.d/hub-profile.sh
while IFS='=' read -r key value; do
    [ -z "$key" ] && continue
    case "$key" in \#*) continue ;; esac
    echo "export $key=\"$value\"" >> /etc/profile.d/hub-profile.sh
done < /data/hub/config/environmentfile

chmod -R a=r /data/factory      # [x] removed after factory process

systemctl stop ModemManager
systemctl disable ModemManager
systemctl stop dnsmasq
systemctl disable dnsmasq
systemctl stop thingsboard-gateway
systemctl disable thingsboard-gateway

echo "nameserver 8.8.8.8" > /run/NetworkManager/resolv.conf

log_info "Finished hub-startup.sh"