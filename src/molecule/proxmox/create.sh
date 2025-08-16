#!/bin/bash
# Create script for Proxmox LXC container

set -e

# Configuration
PROXMOX_HOST="${PROXMOX_HOST:-192.168.1.100}"
PROXMOX_USER="${PROXMOX_USER:-root@pam}"
PROXMOX_PASSWORD="${PROXMOX_PASSWORD}"
PROXMOX_NODE="${PROXMOX_NODE:-pve}"
CONTAINER_ID="${CONTAINER_ID:-999}"
CONTAINER_NAME="${CONTAINER_NAME:-debian-test-instance}"
TEMPLATE="${TEMPLATE:-debian-12-standard_12.2-1_amd64.tar.zst}"
STORAGE="${STORAGE:-local-lvm}"
MEMORY="${MEMORY:-1024}"
CORES="${CORES:-2}"
NETWORK="${NETWORK:-name=eth0,bridge=vmbr0,ip=dhcp}"

echo "Creating LXC container ${CONTAINER_NAME} (ID: ${CONTAINER_ID}) on Proxmox..."

# Create the container
pct create ${CONTAINER_ID} \
    local:vztmpl/${TEMPLATE} \
    --hostname ${CONTAINER_NAME} \
    --memory ${MEMORY} \
    --cores ${CORES} \
    --net0 ${NETWORK} \
    --storage ${STORAGE} \
    --unprivileged 1 \
    --start 1

# Wait for container to start
sleep 10

# Get container IP
CONTAINER_IP=$(pct exec ${CONTAINER_ID} -- ip route get 1 | awk '{print $NF;exit}')

echo "Container created with IP: ${CONTAINER_IP}"
echo "${CONTAINER_IP}" > /tmp/molecule_proxmox_ip

# Setup SSH access
pct exec ${CONTAINER_ID} -- bash -c "
    apt-get update
    apt-get install -y openssh-server python3
    systemctl enable ssh
    systemctl start ssh
    echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
    systemctl restart ssh
"

echo "Container ${CONTAINER_NAME} is ready for testing"
