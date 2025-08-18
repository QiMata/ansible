# APT Mirror Enhanced Features Testing Guide

This document provides comprehensive testing instructions for the enhanced APT mirror role.

## Prerequisites

- Ansible 2.13 or higher
- Target system: Ubuntu 20.04/22.04 or Debian 11/12
- Minimum 20GB free disk space for testing
- Root/sudo access on target system

## Quick Test

Run the basic test script to validate all features:

```bash
# On the mirror server
chmod +x /opt/apt-mirror/files/test_enhanced_features.sh
./files/test_enhanced_features.sh localhost 8080 9090 /var/spool/apt-mirror
```

## Molecule Testing

### Setup Molecule Environment

```bash
# Install molecule with docker driver
pip install molecule[docker] ansible-lint yamllint

# Navigate to role directory
cd src/roles/infrastructure/apt_mirror

# Run default molecule test
molecule test

# Run enhanced features test
molecule test -s enhanced
```

### Manual Testing Scenarios

#### 1. Basic Mirror Functionality

```yaml
# test-basic.yml
- hosts: test_server
  vars:
    deployment_profile: "simple"
    apt_mirror_mirrors:
      - name: "ubuntu_test"
        base_url: "http://archive.ubuntu.com/ubuntu"
        distributions: ["jammy"]
        components: ["main"]
  roles:
    - infrastructure/apt_mirror
```

Run and verify:
```bash
ansible-playbook test-basic.yml -i inventory
curl http://test_server/apt-mirror/
```

#### 2. Health Monitoring Test

```bash
# Check health endpoints
curl http://test_server:8080/health
curl http://test_server:8080/health/disk
curl http://test_server:8080/health/sync
curl http://test_server:8080/health/apache

# Verify JSON response format
curl -s http://test_server:8080/health | jq '.'
```

#### 3. Performance Monitoring Test

```bash
# Check Prometheus metrics
curl http://test_server:9090/metrics
curl -s http://test_server:9090/metrics | grep apt_mirror_

# Verify metrics are updating
curl -s http://test_server:9090/metrics | grep apt_mirror_disk_usage_percent
```

#### 4. GPG Key Management Test

```bash
# Verify GPG setup
sudo -u apt-mirror gpg --homedir /var/spool/apt-mirror/.gnupg --list-keys
/usr/local/bin/verify_gpg_keys.sh

# Check GPG verification logs
tail -f /var/log/apt-mirror-gpg.log
```

#### 5. Alerting System Test

```bash
# Test storage alert
sudo dd if=/dev/zero of=/var/spool/apt-mirror/test_file bs=1M count=1000
/opt/apt-mirror-alerts/monitor_storage.sh

# Test sync failure detection
/opt/apt-mirror-alerts/detect_sync_failure.sh

# Check alert logs
tail -f /var/log/apt-mirror-alerts.log
```

#### 6. Bandwidth Throttling Test

Enable bandwidth throttling and verify configuration:
```bash
grep -i rate_limit /etc/apt/mirror.list
grep -i nthreads /etc/apt/mirror.list

# Monitor bandwidth during sync
sudo nethogs -d 5
```

#### 7. Selective Mirroring Test

Configure selective mirroring:
```yaml
apt_mirror_selective_mirroring_enabled: true
apt_mirror_package_filters:
  - type: "exclude"
    pattern: ".*-dev$"
```

Verify filtered packages:
```bash
# Check mirror.list for filtered content
cat /etc/apt/mirror.list

# Verify excluded packages are not downloaded
find /var/spool/apt-mirror -name "*-dev*.deb" | wc -l
```

#### 8. Client Metrics Test

```bash
# Generate some client traffic
for i in {1..10}; do
  curl http://test_server/apt-mirror/dists/jammy/Release
done

# Check analytics logs
tail -f /var/log/apache2/apt-mirror-access.log

# Verify analytics processing
/opt/apt-mirror-analytics/log_parser.py
```

#### 9. Service Integration Test

```bash
# Check all services are running
systemctl status apt-mirror-health
systemctl status apt-mirror-metrics
systemctl status apt-mirror-discovery
systemctl status apt-mirror-analytics
systemctl status apt-mirror-alerts

# Verify service dependencies
systemctl list-dependencies apt-mirror-health
```

#### 10. Load Testing

Simulate high client load:
```bash
# Install apache bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://test_server/apt-mirror/

# Monitor during load test
curl http://test_server:8080/health
curl http://test_server:9090/metrics
```

## Expected Results

### Health Check Response
```json
{
  "overall_status": "healthy",
  "timestamp": "2025-08-18T10:30:00",
  "checks": {
    "disk_space": {
      "status": "healthy",
      "used_percent": 45.2,
      "free_gb": 150.5
    },
    "apache_status": {
      "status": "healthy",
      "service_active": true
    },
    "last_sync": {
      "status": "healthy",
      "last_sync": "2025-08-18T04:00:00",
      "hours_ago": 6.5
    }
  }
}
```

### Metrics Response Sample
```
# HELP apt_mirror_disk_usage_percent Disk usage percentage
# TYPE apt_mirror_disk_usage_percent gauge
apt_mirror_disk_usage_percent 45.2

# HELP apt_mirror_package_count Number of packages in mirror
# TYPE apt_mirror_package_count gauge
apt_mirror_package_count 25430

# HELP apt_mirror_client_requests_total Total client requests
# TYPE apt_mirror_client_requests_total counter
apt_mirror_client_requests_total{client_ip="10.0.1.100",package="nginx"} 5
```

## Troubleshooting

### Common Issues

1. **Health service not starting**
   ```bash
   # Check Python dependencies
   pip3 install flask psutil requests
   
   # Check service logs
   journalctl -u apt-mirror-health -f
   ```

2. **Metrics service fails**
   ```bash
   # Install Prometheus client
   pip3 install prometheus-client
   
   # Check port conflicts
   netstat -tulpn | grep :9090
   ```

3. **GPG key import fails**
   ```bash
   # Check keyserver connectivity
   gpg --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C
   
   # Verify GPG configuration
   sudo -u apt-mirror gpg --homedir /var/spool/apt-mirror/.gnupg --list-keys
   ```

4. **Alerting not working**
   ```bash
   # Test email configuration
   echo "Test" | mail -s "Test" admin@example.com
   
   # Check SMTP logs
   tail -f /var/log/mail.log
   ```

5. **Mirror sync issues**
   ```bash
   # Manual sync test
   sudo -u apt-mirror apt-mirror /etc/apt/mirror.list
   
   # Check mirror logs
   tail -f /var/spool/apt-mirror/var/cron.log
   ```

### Performance Tuning

1. **Optimize bandwidth usage**
   - Adjust `apt_mirror_bandwidth_limit`
   - Configure sync during off-peak hours
   - Use selective mirroring to reduce data

2. **Storage optimization**
   - Enable package filtering
   - Set size limits
   - Regular pruning schedule

3. **Monitoring optimization**
   - Adjust health check intervals
   - Configure log rotation
   - Set appropriate retention periods

## Validation Checklist

- [ ] Basic mirror functionality works
- [ ] Health endpoints respond correctly
- [ ] Metrics are collected and exposed
- [ ] GPG keys are properly managed
- [ ] Alerts are sent for configured conditions
- [ ] Bandwidth throttling works as expected
- [ ] Selective mirroring filters packages correctly
- [ ] Client access is tracked and analyzed
- [ ] All services start automatically
- [ ] Log rotation is configured
- [ ] Firewall rules allow necessary traffic
- [ ] Performance is acceptable under load

## Continuous Integration

Add to your CI/CD pipeline:
```yaml
# .github/workflows/test-apt-mirror.yml
name: Test APT Mirror Role
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run molecule tests
        run: |
          pip install molecule[docker]
          molecule test
      - name: Run enhanced features test
        run: |
          molecule test -s enhanced
```
