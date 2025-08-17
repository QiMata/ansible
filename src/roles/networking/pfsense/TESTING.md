# pfSense Ansible Role - Testing Guide

This document provides comprehensive information about testing the pfSense Ansible role using Molecule.

## Overview

The pfSense role includes multiple test scenarios to validate different configuration patterns:

- **default**: Basic validation and configuration testing
- **basic_config**: Simple home/small office setup
- **enterprise**: Complex enterprise-grade configuration
- **vpn_config**: VPN-focused testing (OpenVPN + IPsec)

## Prerequisites

### Software Requirements

- Python 3.8+
- Docker
- Ansible 4.0+
- Molecule with Docker driver

### Installation

```bash
# Install dependencies
pip install molecule[docker] ansible-lint yamllint

# Install Ansible collections
ansible-galaxy collection install -r molecule/requirements.yml

# Or use the Makefile
make install-deps
```

## Test Scenarios

### Default Scenario

Basic validation test that ensures the role structure and basic functionality work correctly.

```bash
# Run default scenario
molecule test -s default

# Or using Makefile
make test
```

**What it tests:**
- Role variable validation
- Basic system settings
- Interface configuration
- DHCP and DNS setup
- Basic firewall rules

### Basic Configuration

Tests a simple home/small office setup with minimal features.

```bash
# Run basic configuration test
molecule test -s basic_config

# Or using Makefile
make test-basic
```

**What it tests:**
- WAN/LAN interface setup
- Basic DHCP configuration
- Simple DNS resolver
- Minimal firewall rules
- Feature flags (advanced features disabled)

### Enterprise Configuration

Comprehensive test for enterprise-grade deployments.

```bash
# Run enterprise test
molecule test -s enterprise

# Or using Makefile
make test-enterprise
```

**What it tests:**
- Multiple interfaces (WAN, LAN, DMZ, Management)
- VLAN configuration
- Multiple DHCP servers
- DNS with host overrides
- Complex firewall rules with aliases
- NAT rules for DMZ
- Traffic shaping/QoS
- User authentication
- Captive portal
- Package management
- Backup configuration

### VPN Configuration

Focused testing for VPN deployments (OpenVPN and IPsec).

```bash
# Run VPN test
molecule test -s vpn_config

# Or using Makefile
make test-vpn
```

**What it tests:**
- Certificate management
- OpenVPN server configuration
- OpenVPN client configuration
- IPsec site-to-site VPN
- IPsec mobile/remote access
- VPN-specific firewall rules
- Network isolation and security

## Running Tests

### Quick Commands

```bash
# Run all tests
make test-all

# Run specific scenario
make test-basic
make test-enterprise
make test-vpn

# Lint and syntax check only
make lint

# Validate configuration
make validate

# Clean up test artifacts
make clean
```

### Using Test Runner Script

```bash
# Run all scenarios
python molecule/test_runner.py

# Run specific scenario
python molecule/test_runner.py --scenario basic_config

# Lint only
python molecule/test_runner.py --lint-only

# Keep instances after testing
python molecule/test_runner.py --no-destroy
```

### Manual Molecule Commands

```bash
# Create and converge
molecule create -s default
molecule converge -s default

# Run verification
molecule verify -s default

# Interactive login (for debugging)
molecule login -s default

# Destroy instances
molecule destroy -s default

# Full test cycle
molecule test -s default
```

## Test Development

### Adding New Test Scenarios

1. Create new scenario directory:
```bash
mkdir molecule/new_scenario
```

2. Create required files:
- `molecule.yml` - Molecule configuration
- `converge.yml` - Playbook to test
- `verify.yml` - Verification tasks
- `prepare.yml` - Setup tasks (optional)

3. Update test runner and Makefile as needed.

### Writing Verification Tasks

Verification tasks should validate:

```yaml
- name: Verify configuration
  assert:
    that:
      - condition1
      - condition2
    fail_msg: "Descriptive failure message"
    success_msg: "Success message"
```

### Test Data and Mocking

For testing without actual pfSense instances:

```yaml
# In converge.yml
vars:
  pfsense_mock_mode: true
  # ... other test variables
```

## Continuous Integration

### GitHub Actions

The role includes comprehensive CI/CD pipeline:

- **Lint and Syntax**: YAML and Ansible linting
- **Matrix Testing**: Multiple Python versions and scenarios
- **Security Scanning**: Vulnerability scanning with Trivy
- **Documentation**: README and example validation
- **Release**: Automated releases on main branch

### Local CI Simulation

```bash
# Run full CI pipeline locally
make ci

# Development testing (faster)
make dev-test

# Security-focused testing
make security-test
```

## Debugging

### Test Failures

1. **Check logs**: Molecule provides detailed logs in `.molecule/`
2. **Keep instances**: Use `--no-destroy` to examine failed instances
3. **Interactive debugging**: Use `molecule login` for manual inspection
4. **Verbose output**: Add `-vvv` for detailed Ansible output

### Common Issues

**Docker issues:**
```bash
# Clean up Docker
docker system prune -f
make clean
```

**Collection issues:**
```bash
# Reinstall collections
ansible-galaxy collection install -r molecule/requirements.yml --force
```

**Permission issues:**
```bash
# Check Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

## Performance Testing

### Load Testing

While Molecule focuses on functional testing, performance testing requires additional tools:

```bash
# Example HTTP load testing
ab -n 1000 -c 10 http://test-pfsense/

# Network performance testing
iperf3 -c test-pfsense-ip
```

### Memory and Resource Testing

Monitor resource usage during tests:

```bash
# Monitor Docker container resources
docker stats

# System resource monitoring
htop
```

## Best Practices

### Test Organization

1. **Scenario naming**: Use descriptive names (basic_config, enterprise, etc.)
2. **Test isolation**: Each scenario should be independent
3. **Data validation**: Always verify expected outcomes
4. **Error handling**: Test both success and failure scenarios

### Test Data

1. **Realistic data**: Use realistic network ranges and configurations
2. **Security**: Use vault for sensitive test data
3. **Variety**: Test different configuration combinations
4. **Edge cases**: Include boundary and error conditions

### Maintenance

1. **Regular updates**: Keep test scenarios current with role changes
2. **Documentation**: Update test documentation with role changes
3. **Cleanup**: Regular cleanup of test artifacts
4. **Monitoring**: Monitor test execution times and resource usage

## Troubleshooting

### Common Test Failures

**Timeout issues:**
- Increase timeout values in molecule.yml
- Check Docker resource limits

**Network issues:**
- Verify Docker network configuration
- Check port conflicts

**Authentication issues:**
- Verify mock credentials
- Check pfsensible.core collection version

**Variable issues:**
- Validate YAML syntax
- Check variable precedence
- Verify test data format

### Getting Help

1. Check the [pfsensible.core documentation](https://github.com/pfsensible/core)
2. Review Molecule documentation
3. Check pfSense community forums
4. Open issues in the role repository

## Contributing

### Test Contributions

1. Add tests for new features
2. Update existing tests when modifying functionality
3. Ensure all scenarios pass before submitting PRs
4. Follow the existing test patterns and conventions

### Reporting Issues

When reporting test issues, include:

1. Molecule version and scenario
2. Error messages and logs
3. System information (OS, Docker version, etc.)
4. Steps to reproduce

## Future Enhancements

Planned testing improvements:

1. **Integration testing**: Real pfSense VM testing
2. **Performance benchmarks**: Automated performance testing
3. **Security scanning**: Enhanced security validation
4. **Multi-platform**: Testing on different OS platforms
5. **Parallel execution**: Concurrent test scenario execution
