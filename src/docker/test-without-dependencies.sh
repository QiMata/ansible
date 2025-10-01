#!/bin/bash

# Script to run molecule tests without automatic dependency resolution
# This bypasses ansible-compat's automatic requirements installation

set -e

echo "Running molecule test with isolated dependencies..."

# Change to the source directory
cd /ansible/src

backup_path=""
cleanup() {
    if [ -n "$backup_path" ] && [ -f "$backup_path" ]; then
        echo "Restoring original requirements.yml..."
        mv "$backup_path" requirements.yml
    fi
}
trap cleanup EXIT

# Temporarily move the problematic requirements file
if [ -f "requirements.yml" ]; then
    echo "Backing up requirements.yml..."
    backup_path=$(mktemp /tmp/requirements.yml.XXXXXX)
    mv requirements.yml "$backup_path"
fi

# Use only the molecule-specific requirements
if [ -f "molecule/proxmox/requirements.yml" ]; then
    echo "Using molecule-specific requirements..."
    cp molecule/proxmox/requirements.yml requirements.yml
fi

# Run the molecule test
echo "Starting molecule test..."
molecule test -s proxmox

# Restore the original requirements file
cleanup
trap - EXIT

echo "Test completed."
