#!/bin/bash

# Script to run molecule tests without automatic dependency resolution
# This bypasses ansible-compat's automatic requirements installation

set -e

echo "Running molecule test with isolated dependencies..."

# Change to the source directory
cd /ansible/src

# Temporarily move the problematic requirements file
if [ -f "requirements.yml" ]; then
    echo "Backing up requirements.yml..."
    mv requirements.yml requirements.yml.backup
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
if [ -f "requirements.yml.backup" ]; then
    echo "Restoring original requirements.yml..."
    mv requirements.yml.backup requirements.yml
fi

echo "Test completed."
