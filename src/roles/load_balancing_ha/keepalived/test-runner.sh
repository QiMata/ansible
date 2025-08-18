#!/bin/bash
# Comprehensive test runner for keepalived role
# This script runs all molecule scenarios and validates the role functionality

set -e

ROLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROLE_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if molecule is installed
    if ! command -v molecule &> /dev/null; then
        error "Molecule is not installed. Install with: pip install molecule[docker]"
        exit 1
    fi
    
    # Check if docker is running
    if ! docker info &> /dev/null; then
        error "Docker is not running or not accessible"
        exit 1
    fi
    
    # Check if ansible is installed
    if ! command -v ansible &> /dev/null; then
        error "Ansible is not installed"
        exit 1
    fi
    
    success "All prerequisites met"
}

# Test a specific scenario
test_scenario() {
    local scenario=$1
    log "Testing scenario: $scenario"
    
    if [ ! -d "molecule/$scenario" ]; then
        warning "Scenario $scenario does not exist, skipping..."
        return 0
    fi
    
    # Run the full test cycle
    molecule test -s "$scenario"
    
    if [ $? -eq 0 ]; then
        success "Scenario $scenario passed"
        return 0
    else
        error "Scenario $scenario failed"
        return 1
    fi
}

# Lint the role
lint_role() {
    log "Running role linting..."
    
    # Ansible lint
    if command -v ansible-lint &> /dev/null; then
        log "Running ansible-lint..."
        ansible-lint .
    else
        warning "ansible-lint not found, skipping..."
    fi
    
    # YAML lint
    if command -v yamllint &> /dev/null; then
        log "Running yamllint..."
        yamllint .
    else
        warning "yamllint not found, skipping..."
    fi
    
    success "Linting completed"
}

# Run syntax check
syntax_check() {
    log "Running syntax checks..."
    
    # Check playbook syntax
    for playbook in examples/*.yml; do
        if [ -f "$playbook" ]; then
            log "Checking syntax of $playbook"
            ansible-playbook --syntax-check "$playbook"
        fi
    done
    
    success "Syntax checks passed"
}

# Generate test report
generate_report() {
    local results_file="test_results_$(date +%Y%m%d_%H%M%S).txt"
    
    log "Generating test report: $results_file"
    
    cat > "$results_file" << EOF
Keepalived Role Test Report
Generated: $(date)
Role Directory: $ROLE_DIR

Test Scenarios Run:
EOF
    
    for scenario in molecule/*/; do
        scenario_name=$(basename "$scenario")
        echo "- $scenario_name" >> "$results_file"
    done
    
    echo "" >> "$results_file"
    echo "Test completed successfully" >> "$results_file"
    
    success "Test report generated: $results_file"
}

# Main execution
main() {
    log "Starting comprehensive tests for keepalived role"
    log "Role directory: $ROLE_DIR"
    
    # Track failed scenarios
    failed_scenarios=()
    
    # Run checks
    check_prerequisites
    
    # Lint the role
    if ! lint_role; then
        warning "Linting issues found, but continuing with tests"
    fi
    
    # Syntax check
    if ! syntax_check; then
        error "Syntax checks failed"
        exit 1
    fi
    
    # List available scenarios
    log "Available test scenarios:"
    for scenario_dir in molecule/*/; do
        scenario_name=$(basename "$scenario_dir")
        echo "  - $scenario_name"
    done
    
    # Test each scenario
    for scenario_dir in molecule/*/; do
        scenario_name=$(basename "$scenario_dir")
        
        if ! test_scenario "$scenario_name"; then
            failed_scenarios+=("$scenario_name")
        fi
    done
    
    # Report results
    echo ""
    log "Test Summary:"
    
    if [ ${#failed_scenarios[@]} -eq 0 ]; then
        success "All test scenarios passed!"
        generate_report
        exit 0
    else
        error "The following scenarios failed:"
        for scenario in "${failed_scenarios[@]}"; do
            echo "  - $scenario"
        done
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    "lint")
        check_prerequisites
        lint_role
        ;;
    "syntax")
        check_prerequisites
        syntax_check
        ;;
    "scenario")
        if [ -z "$2" ]; then
            error "Please specify a scenario name"
            exit 1
        fi
        check_prerequisites
        test_scenario "$2"
        ;;
    "list")
        echo "Available scenarios:"
        for scenario_dir in molecule/*/; do
            scenario_name=$(basename "$scenario_dir")
            echo "  - $scenario_name"
        done
        ;;
    "help"|"-h"|"--help")
        cat << EOF
Keepalived Role Test Runner

Usage: $0 [command] [options]

Commands:
  (no command)    Run all tests
  lint            Run linting only
  syntax          Run syntax checks only
  scenario NAME   Run specific scenario
  list            List available scenarios
  help            Show this help

Examples:
  $0                    # Run all tests
  $0 lint              # Run linting only
  $0 scenario default  # Run default scenario only
  $0 list              # List available scenarios

EOF
        ;;
    *)
        main
        ;;
esac
