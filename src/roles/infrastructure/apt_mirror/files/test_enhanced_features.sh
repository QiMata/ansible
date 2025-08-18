#!/bin/bash
# APT Mirror Enhanced Features Test Script
# This script validates that all enhanced features are working correctly

set -e

# Configuration
MIRROR_HOST="${1:-localhost}"
HEALTH_PORT="${2:-8080}"
METRICS_PORT="${3:-9090}"
MIRROR_PATH="${4:-/var/spool/apt-mirror}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"
    
    echo "Running test: $test_name"
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if eval "$test_command" > /dev/null 2>&1; then
        result=0
    else
        result=1
    fi
    
    if [ $result -eq $expected_result ]; then
        log_info "✓ $test_name PASSED"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_error "✗ $test_name FAILED"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 1: Basic APT Mirror Installation
echo "=== Testing Basic APT Mirror Installation ==="
run_test "APT Mirror package installed" "dpkg -l | grep -q apt-mirror"
run_test "Mirror directory exists" "test -d $MIRROR_PATH"
run_test "Mirror configuration exists" "test -f /etc/apt/mirror.list"
run_test "Apache is running" "systemctl is-active apache2"

# Test 2: Health Monitoring
echo "=== Testing Health Monitoring ==="
run_test "Health service is running" "systemctl is-active apt-mirror-health"
run_test "Health endpoint responds" "curl -f http://$MIRROR_HOST:$HEALTH_PORT/health"
run_test "Health disk endpoint" "curl -f http://$MIRROR_HOST:$HEALTH_PORT/health/disk"
run_test "Health sync endpoint" "curl -f http://$MIRROR_HOST:$HEALTH_PORT/health/sync"
run_test "Health apache endpoint" "curl -f http://$MIRROR_HOST:$HEALTH_PORT/health/apache"

# Test 3: Performance Monitoring
echo "=== Testing Performance Monitoring ==="
run_test "Metrics service is running" "systemctl is-active apt-mirror-metrics"
run_test "Metrics endpoint responds" "curl -f http://$MIRROR_HOST:$METRICS_PORT/metrics"
run_test "Prometheus metrics format" "curl -s http://$MIRROR_HOST:$METRICS_PORT/metrics | grep -q 'apt_mirror_'"

# Test 4: GPG Key Management
echo "=== Testing GPG Key Management ==="
run_test "GPG directory exists" "test -d $MIRROR_PATH/.gnupg"
run_test "GPG verification script exists" "test -f /usr/local/bin/verify_gpg_keys.sh"
run_test "GPG verification script is executable" "test -x /usr/local/bin/verify_gpg_keys.sh"

# Test 5: Alerting System
echo "=== Testing Alerting System ==="
run_test "Alert manager script exists" "test -f /opt/apt-mirror-alerts/alert_manager.py"
run_test "Alert configuration exists" "test -f /opt/apt-mirror-alerts/config.yml"
run_test "Sync failure detection script exists" "test -f /opt/apt-mirror-alerts/detect_sync_failure.sh"
run_test "Storage monitoring script exists" "test -f /opt/apt-mirror-alerts/monitor_storage.sh"

# Test 6: Client Discovery
echo "=== Testing Client Discovery ==="
if systemctl is-active apt-mirror-discovery > /dev/null 2>&1; then
    run_test "Discovery service is running" "systemctl is-active apt-mirror-discovery"
    run_test "Discovery configuration exists" "test -f /opt/apt-mirror-discovery/discovery_service.py"
else
    log_warn "Client discovery service not enabled, skipping tests"
fi

# Test 7: Analytics
echo "=== Testing Analytics ==="
if systemctl is-active apt-mirror-analytics > /dev/null 2>&1; then
    run_test "Analytics service is running" "systemctl is-active apt-mirror-analytics"
    run_test "Analytics directory exists" "test -d /opt/apt-mirror-analytics"
    run_test "Log parser exists" "test -f /opt/apt-mirror-analytics/log_parser.py"
else
    log_warn "Analytics service not enabled, skipping tests"
fi

# Test 8: Configuration Files
echo "=== Testing Configuration Files ==="
run_test "Mirror list configuration" "test -s /etc/apt/mirror.list"
run_test "Apache apt-mirror site" "test -f /etc/apache2/sites-available/apt-mirror.conf"
run_test "Cron configuration" "test -f /etc/cron.d/apt-mirror"

# Test 9: Bandwidth Throttling
echo "=== Testing Bandwidth Throttling ==="
if grep -q "rate_limit" /etc/apt/mirror.list 2>/dev/null; then
    run_test "Bandwidth throttling configured" "grep -q 'rate_limit' /etc/apt/mirror.list"
    log_info "Bandwidth throttling is enabled"
else
    log_warn "Bandwidth throttling not configured"
fi

# Test 10: Selective Mirroring
echo "=== Testing Selective Mirroring ==="
if grep -q "# Selective mirroring" /etc/apt/mirror.list 2>/dev/null; then
    run_test "Selective mirroring configured" "grep -q '# Selective mirroring' /etc/apt/mirror.list"
    log_info "Selective mirroring is enabled"
else
    log_warn "Selective mirroring not configured"
fi

# Test 11: Service Status
echo "=== Testing Service Status ==="
SERVICES=(
    "apache2"
    "apt-mirror-health"
    "apt-mirror-metrics"
    "apt-mirror-alerts"
)

for service in "${SERVICES[@]}"; do
    if systemctl list-unit-files | grep -q "$service.service"; then
        run_test "$service service enabled" "systemctl is-enabled $service"
        run_test "$service service active" "systemctl is-active $service"
    else
        log_warn "Service $service not found"
    fi
done

# Test 12: Log Files
echo "=== Testing Log Files ==="
run_test "Mirror cron log exists" "test -f $MIRROR_PATH/var/cron.log"
run_test "Apache access log exists" "test -f /var/log/apache2/apt-mirror-access.log"

# Test 13: Network Connectivity
echo "=== Testing Network Connectivity ==="
run_test "Mirror HTTP endpoint" "curl -f http://$MIRROR_HOST/apt-mirror/"
run_test "Apache default page" "curl -f http://$MIRROR_HOST/"

# Test 14: Security Checks
echo "=== Testing Security Configuration ==="
run_test "apt-mirror user exists" "id apt-mirror"
run_test "Mirror directory permissions" "test -O $MIRROR_PATH"
run_test "GPG directory permissions" "test $(stat -c '%a' $MIRROR_PATH/.gnupg 2>/dev/null || echo '000') = '700'"

# Test 15: Performance Tests
echo "=== Testing Performance ==="
if command -v iotop > /dev/null 2>&1; then
    log_info "iotop available for I/O monitoring"
else
    log_warn "iotop not available"
fi

if command -v nethogs > /dev/null 2>&1; then
    log_info "nethogs available for network monitoring"
else
    log_warn "nethogs not available"
fi

# Summary
echo ""
echo "=== Test Summary ==="
echo "Tests run: $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    log_info "All tests passed! ✓"
    exit 0
else
    log_error "$TESTS_FAILED tests failed! ✗"
    echo ""
    echo "To troubleshoot failures:"
    echo "1. Check service logs: journalctl -u <service-name>"
    echo "2. Verify configuration files are correctly templated"
    echo "3. Check firewall settings for port access"
    echo "4. Ensure all dependencies are installed"
    exit 1
fi
