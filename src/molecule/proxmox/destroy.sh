#!/bin/bash
# Destroy script for Proxmox LXC container

set -e

# Configuration
CONTAINER_ID="${CONTAINER_ID:-999}"
CONTAINER_NAME="${CONTAINER_NAME:-debian-test-instance}"

echo "Destroying LXC container ${CONTAINER_NAME} (ID: ${CONTAINER_ID})..."

# Stop and destroy the container
pct stop ${CONTAINER_ID} || true
pct destroy ${CONTAINER_ID} || true

# Clean up temporary files
rm -f /tmp/molecule_proxmox_ip

echo "Container ${CONTAINER_NAME} has been destroyed"
