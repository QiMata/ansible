#!/usr/bin/env bash

# Test script to verify the Molecule Proxmox Docker setup
# This script performs basic validation of the environment

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Molecule Proxmox Docker Setup Test ===${NC}"

# Test 1: Check if Docker is available
echo -n "Checking Docker availability... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Docker is not installed or not in PATH"
    exit 1
fi

# Test 2: Check if Docker Compose is available
echo -n "Checking Docker Compose availability... "
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Docker Compose is not installed or not in PATH"
    exit 1
fi

# Test 3: Check if Docker daemon is running
echo -n "Checking Docker daemon... "
if docker info &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Docker daemon is not running"
    exit 1
fi

# Test 4: Check if required files exist
echo -n "Checking Dockerfile... "
if [[ -f "${SCRIPT_DIR}/Dockerfile.molecule-proxmox" ]]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Dockerfile.molecule-proxmox not found"
    exit 1
fi

echo -n "Checking Docker Compose file... "
if [[ -f "${SCRIPT_DIR}/docker-compose.molecule.yml" ]]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "docker-compose.molecule.yml not found"
    exit 1
fi

echo -n "Checking molecule configuration... "
if [[ -f "${PROJECT_ROOT}/src/molecule/proxmox/molecule.yml" ]]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "molecule.yml not found in src/molecule/proxmox/"
    exit 1
fi

# Test 5: Check environment file
echo -n "Checking environment configuration... "
if [[ -f "${PROJECT_ROOT}/src/molecule/proxmox/.env" ]]; then
    echo -e "${GREEN}✓${NC}"
    echo "  Environment file found at src/molecule/proxmox/.env"
elif [[ -f "${PROJECT_ROOT}/src/molecule/proxmox/.env.example" ]]; then
    echo -e "${YELLOW}!${NC}"
    echo "  Environment example found. Copy .env.example to .env and configure it."
else
    echo -e "${RED}✗${NC}"
    echo "  No environment configuration found"
    exit 1
fi

# Test 6: Try building the Docker image
echo -n "Testing Docker image build... "
cd "${PROJECT_ROOT}"
if docker build -f src/docker/Dockerfile.molecule-proxmox -t ansible-molecule-proxmox:test . &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
    echo "  Docker image built successfully"
    
    # Clean up test image
    docker rmi ansible-molecule-proxmox:test &> /dev/null || true
else
    echo -e "${RED}✗${NC}"
    echo "  Failed to build Docker image"
    exit 1
fi

echo -e "\n${GREEN}=== All tests passed! ===${NC}"
echo "Your Molecule Proxmox Docker setup is ready."
echo ""
echo "Next steps:"
echo "1. Configure your Proxmox credentials in src/molecule/proxmox/.env"
echo "2. Run: ./run-molecule-tests.sh build"
echo "3. Run: ./run-molecule-tests.sh start"
echo "4. Run: ./run-molecule-tests.sh test"
