#!/bin/bash
# Comprehensive test script for the enhanced Configure Filebeat OS role
# This script runs all test scenarios and validates the enhancements

set -e

echo "========================================"
echo "Enhanced Filebeat OS Role Test Suite"
echo "========================================"

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    case $1 in
        "SUCCESS") echo -e "${GREEN}✓ $2${NC}" ;;
        "ERROR") echo -e "${RED}✗ $2${NC}" ;;
        "INFO") echo -e "${YELLOW}ℹ $2${NC}" ;;
    esac
}

# Function to run molecule test with error handling
run_molecule_test() {
    local scenario=$1
    print_status "INFO" "Running molecule test for scenario: $scenario"
    
    if molecule test -s "$scenario"; then
        print_status "SUCCESS" "Scenario $scenario passed"
        return 0
    else
        print_status "ERROR" "Scenario $scenario failed"
        return 1
    fi
}

# Test scenarios
scenarios=("default" "security" "advanced" "performance")
failed_scenarios=()

echo ""
print_status "INFO" "Starting test suite for enhanced Filebeat OS role"
echo ""

# Run each test scenario
for scenario in "${scenarios[@]}"; do
    echo "----------------------------------------"
    print_status "INFO" "Testing scenario: $scenario"
    echo "----------------------------------------"
    
    if run_molecule_test "$scenario"; then
        print_status "SUCCESS" "Scenario $scenario completed successfully"
    else
        failed_scenarios+=("$scenario")
        print_status "ERROR" "Scenario $scenario failed"
    fi
    echo ""
done

# Summary
echo "========================================"
echo "Test Summary"
echo "========================================"

total_scenarios=${#scenarios[@]}
failed_count=${#failed_scenarios[@]}
passed_count=$((total_scenarios - failed_count))

print_status "INFO" "Total scenarios: $total_scenarios"
print_status "SUCCESS" "Passed: $passed_count"

if [ $failed_count -gt 0 ]; then
    print_status "ERROR" "Failed: $failed_count"
    echo ""
    print_status "ERROR" "Failed scenarios:"
    for failed in "${failed_scenarios[@]}"; do
        echo "  - $failed"
    done
    echo ""
    print_status "ERROR" "Test suite failed with $failed_count failures"
    exit 1
else
    print_status "SUCCESS" "All scenarios passed!"
    echo ""
    print_status "SUCCESS" "✅ Enhanced Filebeat OS role test suite completed successfully!"
fi

echo ""
print_status "INFO" "Test features validated:"
echo "  • SSL/TLS Configuration"
echo "  • Authentication & Keystore"
echo "  • Multiple Output Types"
echo "  • Multiline Processing"
echo "  • Filebeat Modules"
echo "  • Custom Processors"
echo "  • Performance Tuning"
echo "  • Health Monitoring"
echo "  • Service Management"
echo "  • Cross-Platform Support"
echo ""
print_status "INFO" "Role is ready for production use!"
