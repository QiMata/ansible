#!/usr/bin/env bash

# Molecule Proxmox Docker Runner Script
# This script provides easy commands to run molecule tests in Docker

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DOCKER_COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.molecule.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if .env file exists
check_env_file() {
    if [[ ! -f "${PROJECT_ROOT}/src/molecule/proxmox/.env" ]]; then
        log_warn "No .env file found. Creating from template..."
        if [[ -f "${PROJECT_ROOT}/src/molecule/proxmox/.env.example" ]]; then
            cp "${PROJECT_ROOT}/src/molecule/proxmox/.env.example" "${PROJECT_ROOT}/src/molecule/proxmox/.env"
            log_warn "Please edit ${PROJECT_ROOT}/src/molecule/proxmox/.env with your Proxmox credentials"
            return 1
        else
            log_error ".env.example file not found!"
            return 1
        fi
    fi
    return 0
}

# Function to load environment variables
load_env() {
    if check_env_file; then
        log_info "Loading environment variables from .env file..."
        set -a
        source "${PROJECT_ROOT}/src/molecule/proxmox/.env"
        set +a
    fi
}

# Function to build the Docker image
build_image() {
    log_info "Building molecule-proxmox Docker image..."
    cd "${PROJECT_ROOT}"
    docker-compose -f "${DOCKER_COMPOSE_FILE}" build
    log_success "Docker image built successfully"
}

# Function to start the container
start_container() {
    log_info "Starting molecule-proxmox container..."
    cd "${PROJECT_ROOT}"
    docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d
    log_success "Container started successfully"
}

# Function to stop the container
stop_container() {
    log_info "Stopping molecule-proxmox container..."
    cd "${PROJECT_ROOT}"
    docker-compose -f "${DOCKER_COMPOSE_FILE}" down
    log_success "Container stopped successfully"
}

# Function to enter the container shell
shell() {
    log_info "Entering container shell..."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" exec molecule-proxmox /bin/bash
}

# Function to run molecule test
run_test() {
    local scenario=${1:-proxmox}
    log_info "Running molecule test for scenario: ${scenario}"
    
    docker-compose -f "${DOCKER_COMPOSE_FILE}" exec molecule-proxmox \
        bash -c "cd /ansible/src && molecule test -s ${scenario}"
}

# Function to run molecule create only
run_create() {
    local scenario=${1:-proxmox}
    log_info "Running molecule create for scenario: ${scenario}"
    
    docker-compose -f "${DOCKER_COMPOSE_FILE}" exec molecule-proxmox \
        bash -c "cd /ansible/src && molecule create -s ${scenario}"
}

# Function to run molecule converge only
run_converge() {
    local scenario=${1:-proxmox}
    log_info "Running molecule converge for scenario: ${scenario}"
    
    docker-compose -f "${DOCKER_COMPOSE_FILE}" exec molecule-proxmox \
        bash -c "cd /ansible/src && molecule converge -s ${scenario}"
}

# Function to run molecule destroy only
run_destroy() {
    local scenario=${1:-proxmox}
    log_info "Running molecule destroy for scenario: ${scenario}"
    
    docker-compose -f "${DOCKER_COMPOSE_FILE}" exec molecule-proxmox \
        bash -c "cd /ansible/src && molecule destroy -s ${scenario}"
}

# Function to show logs
show_logs() {
    docker-compose -f "${DOCKER_COMPOSE_FILE}" logs -f molecule-proxmox
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    build           Build the molecule-proxmox Docker image
    start           Start the molecule-proxmox container
    stop            Stop the molecule-proxmox container  
    shell           Enter the container shell
    test [scenario] Run full molecule test (default: proxmox)
    create [scenario] Run molecule create only
    converge [scenario] Run molecule converge only
    destroy [scenario] Run molecule destroy only
    logs            Show container logs
    help            Show this help message

Examples:
    $0 build
    $0 start
    $0 test
    $0 test proxmox
    $0 create
    $0 shell
    $0 stop

Before running tests, make sure to:
1. Copy .env.example to .env in src/molecule/proxmox/
2. Configure your Proxmox credentials in the .env file
3. Ensure network connectivity to your Proxmox server

EOF
}

# Main execution
main() {
    case "${1:-help}" in
        build)
            load_env
            build_image
            ;;
        start)
            load_env
            start_container
            ;;
        stop)
            stop_container
            ;;
        shell)
            shell
            ;;
        test)
            run_test "${2:-proxmox}"
            ;;
        create)
            run_create "${2:-proxmox}"
            ;;
        converge)
            run_converge "${2:-proxmox}"
            ;;
        destroy)
            run_destroy "${2:-proxmox}"
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $1"
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
