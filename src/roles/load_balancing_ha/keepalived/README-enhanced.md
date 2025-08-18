# keepalived Ansible Role - Enhanced Edition

**Table of Contents**

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Advanced Features](#advanced-features)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbooks](#example-playbooks)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Related Roles](#related-roles)

## Overview

This role installs and configures **Keepalived**, a service that provides high availability by using the Virtual Router Redundancy Protocol (VRRP) on Linux systems. This comprehensive role now supports advanced features including:

- ✅ **Multiple VRRP instances** for complex HA scenarios
- ✅ **Unicast mode** for cloud environments (AWS, Azure, GCP)
- ✅ **Advanced authentication** including IPSec/AH and no authentication
- ✅ **Health checking** with custom scripts and interface tracking
- ✅ **IPv6 support** for modern network environments
- ✅ **Configuration validation** and backup
- ✅ **Multi-distribution support** (Debian, Ubuntu, RedHat, CentOS, SUSE)
- ✅ **Comprehensive logging** and monitoring integration
- ✅ **VLAN interface support**
- ✅ **Non-preemptive mode** for stable failover
- ✅ **VRRP timers configuration**
- ✅ **Weight-based failover**
- ✅ **Sync groups** for coordinated failover

When applied, the role performs the following functions:

* **Package Installation:** Installs Keepalived on multiple Linux distributions
* **Advanced Configuration:** Supports complex multi-instance setups with health checks
* **Network Configuration:** Handles VLAN interfaces and IPv6
* **Service Management:** Comprehensive service lifecycle management
* **Monitoring:** Built-in health monitoring and SNMP support
* **Security:** Multiple authentication modes and configuration validation

## Supported Operating Systems/Platforms

This role is tested on and supports the following Linux distributions:

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)
* **RedHat/CentOS** – 8 and 9
* **Rocky Linux** – 8 and 9
* **AlmaLinux** – 8 and 9
* **SUSE Linux Enterprise** – 15

## Role Variables

### Basic Configuration (Backward Compatible)

These variables maintain backward compatibility with existing deployments:

| Variable | Default | Description |
|----------|---------|-------------|
| `keepalived_state` | `BACKUP` | VRRP state (MASTER/BACKUP) |
| `keepalived_priority` | `100` | VRRP priority (0-255) |
| `keepalived_interface` | `eth0` | Network interface |
| `keepalived_router_id` | `51` | Virtual Router ID |
| `keepalived_virtual_ip` | `192.168.50.100` | Virtual IP address |
| `keepalived_virtual_cidr` | `32` | CIDR prefix length |
| `keepalived_auth_pass` | `vrrp_secret` | Authentication password |

### Global Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `keepalived_global_defs` | `{}` | Global configuration block |
| `keepalived_enable_syslog` | `true` | Enable syslog logging |
| `keepalived_log_level` | `INFO` | Log level (DEBUG, INFO, NOTICE, WARNING, ERR, CRIT, ALERT, EMERG) |
| `keepalived_validate_config` | `true` | Validate configuration before applying |
| `keepalived_backup_config` | `true` | Backup existing configuration |
| `keepalived_enable_ipv6` | `false` | Enable IPv6 support |
| `keepalived_enable_snmp` | `false` | Enable SNMP support |

### Advanced Configuration

#### VRRP Instances

Configure multiple VRRP instances for complex scenarios:

```yaml
keepalived_vrrp_instances:
  - name: "VI_WEB"
    state: "MASTER"
    interface: "eth0"
    virtual_router_id: 51
    priority: 150
    advert_int: 1                    # Advertisement interval
    master_down_interval: null       # Custom master down interval
    preempt: true                    # Enable/disable preemption
    preempt_delay: 0                 # Preemption delay
    
    # Unicast configuration for cloud environments
    unicast_src_ip: "192.168.1.10"
    unicast_peers:
      - "192.168.1.11"
      - "192.168.1.12"
    
    # Authentication options
    authentication:
      auth_type: "PASS"              # PASS, AH, or null
      auth_pass: "secret"
      ah_key: ""                     # For AH authentication
    
    # Virtual IPs (IPv4 and IPv6 supported)
    virtual_ipaddresses:
      - ip: "192.168.1.100"
        cidr: 32
      - ip: "2001:db8::100"
        cidr: 128
        dev: "eth0"                  # Optional device override
        scope: "global"              # Optional scope
        label: "web-vip"             # Optional label
    
    # Health checking
    track_interfaces:
      - name: "eth0"
        weight: -10
    track_scripts:
      - "check_service"
    
    # Notification scripts
    notify_master: "/etc/keepalived/scripts/web_master.sh"
    notify_backup: "/etc/keepalived/scripts/web_backup.sh"
    notify_fault: "/etc/keepalived/scripts/web_fault.sh"
    smtp_alert: true
```

#### Health Check Scripts

```yaml
keepalived_vrrp_scripts:
  - name: "check_nginx"
    script: "/etc/keepalived/scripts/check_nginx.sh"
    interval: 2                      # Check interval in seconds
    timeout: 3                       # Script timeout
    weight: -10                      # Weight adjustment on failure
    fall: 3                          # Failures before state change
    rise: 2                          # Successes before state change
    user: "root"                     # User to run script as
    init_fail: false                 # Assume initial failure
```

#### Sync Groups

Coordinate multiple VRRP instances:

```yaml
keepalived_vrrp_sync_groups:
  - name: "SERVICES"
    instances:
      - "VI_WEB"
      - "VI_DB"
    notify_master: "/etc/keepalived/scripts/group_master.sh"
    notify_backup: "/etc/keepalived/scripts/group_backup.sh"
    smtp_alert: true
```

#### Custom Scripts

Deploy custom health check and notification scripts:

```yaml
keepalived_custom_scripts:
  - name: "check_nginx.sh"
    content: |
      #!/bin/bash
      curl -f http://localhost:80/health >/dev/null 2>&1
    mode: "0755"
    owner: "root"
    group: "root"
```

## Advanced Features

### 🌩️ Cloud Environment Support

The role supports cloud environments through unicast mode, essential for AWS, Azure, and GCP:

```yaml
keepalived_vrrp_instances:
  - name: "VI_CLOUD"
    # Use unicast instead of multicast
    unicast_src_ip: "{{ ansible_default_ipv4.address }}"
    unicast_peers: 
      - "10.0.1.10"
      - "10.0.1.11"
    # Cloud virtual IP (configure in cloud console)
    virtual_ipaddresses:
      - ip: "{{ cloud_virtual_ip }}"
        cidr: 32
```

### 🔐 Authentication Options

Multiple authentication modes for different security requirements:

```yaml
# IPSec/AH authentication (strongest)
authentication:
  auth_type: "AH"
  ah_key: "0x12345678901234567890123456789012"

# Simple password authentication
authentication:
  auth_type: "PASS"
  auth_pass: "your_secret_password"

# No authentication (trusted networks only)
authentication:
  auth_type: null
```

### 🌐 IPv6 Support

Full IPv6 support for modern networks:

```yaml
keepalived_enable_ipv6: true
virtual_ipaddresses:
  - ip: "2001:db8::100"
    cidr: 128
  - ip: "192.168.1.100"
    cidr: 32
```

### 🔧 VLAN Interface Support

Automatically create and configure VLAN interfaces:

```yaml
keepalived_create_vlan_interfaces: true
keepalived_vlan_interfaces:
  - name: "eth0.100"
    device: "eth0"
    vlan_id: 100
    ip: "192.168.100.10/24"
    gateway: "192.168.100.1"
```

### ⚙️ Non-preemptive Mode

Prevent unwanted failbacks:

```yaml
keepalived_vrrp_instances:
  - name: "VI_STABLE"
    preempt: false  # Disable preemption
    # Other configuration...
```

### ⏱️ VRRP Timer Configuration

Fine-tune VRRP timers:

```yaml
keepalived_vrrp_instances:
  - name: "VI_CUSTOM_TIMERS"
    advert_int: 2                    # Advertisement interval
    master_down_interval: 10         # Custom master down interval
    preempt_delay: 30               # Wait before preempting
```

### 📊 Configuration Validation and Backup

Ensure configuration integrity:

```yaml
keepalived_validate_config: true    # Validate syntax before applying
keepalived_backup_config: true      # Backup existing configuration
keepalived_backup_dir: "/etc/keepalived/backup"
```

### 📝 Logging and Monitoring

Comprehensive logging and monitoring:

```yaml
keepalived_enable_syslog: true
keepalived_log_level: "DEBUG"
keepalived_log_facility: "daemon"
keepalived_enable_snmp: true
keepalived_enable_data_dump: true
keepalived_data_dump_file: "/tmp/keepalived.data"
```

## Tags

The role supports the following Ansible tags for selective execution:

- `keepalived` - All keepalived tasks
- `install` - Package installation only
- `config` - Configuration tasks only
- `service` - Service management only
- `scripts` - Custom script deployment
- `network` - Network configuration
- `vlan` - VLAN interface configuration
- `logging` - Logging configuration
- `snmp` - SNMP configuration
- `validate` - Configuration validation
- `backup` - Configuration backup
- `monitoring` - Monitoring setup
- `ipv6` - IPv6 configuration

Usage examples:
```bash
# Install packages only
ansible-playbook -i inventory site.yml --tags install

# Update configuration only
ansible-playbook -i inventory site.yml --tags config

# Deploy scripts only
ansible-playbook -i inventory site.yml --tags scripts
```

## Dependencies

- **Ansible Version:** 2.13 or higher
- **Collections:** 
  - `ansible.posix` (for sysctl module)
  - Built-in modules (no external collections required)
- **System Requirements:**
  - Network capabilities for VRRP (NET_ADMIN, NET_RAW)
  - Firewall configured to allow VRRP traffic (protocol 112)
- **Optional Dependencies:**
  - `snmp` package (if SNMP monitoring is enabled)
  - `rsyslog` (for advanced logging)

## Example Playbooks

### 🚀 Quick Start (Backward Compatible)

```yaml
- hosts: loadbalancers
  become: yes
  vars:
    keepalived_state: "{{ 'MASTER' if inventory_hostname == groups['loadbalancers'][0] else 'BACKUP' }}"
    keepalived_priority: "{{ 150 if inventory_hostname == groups['loadbalancers'][0] else 100 }}"
    keepalived_virtual_ip: 192.168.1.100
    keepalived_auth_pass: "{{ vault_keepalived_password }}"
  roles:
    - keepalived
```

### ☁️ Cloud Environment (AWS/Azure/GCP)

```yaml
- hosts: cloud_loadbalancers
  become: yes
  vars:
    keepalived_vrrp_instances:
      - name: "VI_CLOUD"
        state: "{{ 'MASTER' if inventory_hostname == groups['cloud_loadbalancers'][0] else 'BACKUP' }}"
        interface: "{{ ansible_default_ipv4.interface }}"
        virtual_router_id: 51
        priority: "{{ 150 if inventory_hostname == groups['cloud_loadbalancers'][0] else 100 }}"
        # Essential for cloud environments
        unicast_src_ip: "{{ ansible_default_ipv4.address }}"
        unicast_peers: "{{ groups['cloud_loadbalancers'] | map('extract', hostvars, 'ansible_default_ipv4') | map(attribute='address') | list }}"
        authentication:
          auth_type: "PASS"
          auth_pass: "{{ vault_keepalived_password }}"
        virtual_ipaddresses:
          - ip: "{{ cloud_virtual_ip }}"
            cidr: 32
        track_scripts:
          - "health_check"
    
    keepalived_vrrp_scripts:
      - name: "health_check"
        script: "/etc/keepalived/scripts/health.sh"
        interval: 5
        weight: -50
    
    keepalived_custom_scripts:
      - name: "health.sh"
        content: |
          #!/bin/bash
          curl -f http://localhost:{{ app_port | default('80') }}/health >/dev/null 2>&1
        mode: "0755"
  
  roles:
    - keepalived
```

### 🏢 Enterprise Multi-Instance Setup

```yaml
- hosts: enterprise_loadbalancers
  become: yes
  vars:
    # Multiple services with different priorities
    keepalived_vrrp_instances:
      # Web tier
      - name: "VI_WEB"
        state: "{{ 'MASTER' if inventory_hostname == groups['web_primary'][0] else 'BACKUP' }}"
        virtual_router_id: 51
        priority: "{{ 200 if inventory_hostname in groups['web_primary'] else 100 }}"
        virtual_ipaddresses:
          - ip: "192.168.1.100"
            cidr: 32
        track_scripts: ["check_web"]
        
      # Database tier  
      - name: "VI_DB"
        state: "{{ 'MASTER' if inventory_hostname == groups['db_primary'][0] else 'BACKUP' }}"
        virtual_router_id: 52
        priority: "{{ 200 if inventory_hostname in groups['db_primary'] else 100 }}"
        preempt: false  # Non-preemptive for database stability
        virtual_ipaddresses:
          - ip: "192.168.1.101"
            cidr: 32
          - ip: "2001:db8::101"
            cidr: 128
        track_scripts: ["check_db"]
    
    # Coordinated failover
    keepalived_vrrp_sync_groups:
      - name: "ENTERPRISE_SERVICES"
        instances: ["VI_WEB", "VI_DB"]
        notify_master: "/etc/keepalived/scripts/enterprise_master.sh"
    
    # Comprehensive health checks
    keepalived_vrrp_scripts:
      - name: "check_web"
        script: "/etc/keepalived/scripts/check_web.sh"
        interval: 2
        weight: -20
      - name: "check_db"
        script: "/etc/keepalived/scripts/check_db.sh"
        interval: 5
        weight: -30
  
  roles:
    - keepalived
```

For more examples, see the `examples/` directory.

## Testing Instructions

The role includes comprehensive Molecule test scenarios:

### 🧪 Basic Testing
```bash
cd src/roles/load_balancing_ha/keepalived
molecule test
```

### ☁️ Cloud Mode Testing
```bash
molecule test -s unicast
```

### 🔄 Multi-Instance Testing
```bash
molecule test -s multi-instance
```

### 🐳 Container Testing
```bash
molecule test -s podman
```

### Test Coverage

Each scenario tests:
- ✅ Package installation across distributions
- ✅ Configuration generation and validation
- ✅ Service management and startup
- ✅ Feature-specific functionality
- ✅ Backward compatibility
- ✅ Error handling and edge cases

## Known Issues and Gotchas

### ☁️ Cloud Environments
- **Multicast Limitation**: Cloud providers block multicast traffic. Always use `unicast_src_ip` and `unicast_peers`.
- **Virtual IP Management**: In cloud environments, configure the VIP in the provider's console rather than letting keepalived assign it.
- **Security Groups**: Ensure VRRP traffic (protocol 112) is allowed between instances.

### 🌐 Network Configuration
- **Firewall Rules**: VRRP uses IP protocol 112. Ensure it's allowed between cluster members.
- **Split-brain Prevention**: Implement proper network monitoring to prevent split-brain scenarios.
- **Interface Names**: Cloud instances may have different interface names (`ens3`, `eth0`, etc.). Use `ansible_default_ipv4.interface`.

### 🔒 Authentication Considerations
- **AH Authentication**: Requires IPSec kernel modules. May not work in containers.
- **Password Security**: PASS authentication transmits passwords in clear text.
- **Key Management**: Store authentication keys in Ansible Vault.

### 📦 Container Environments
- **Privileged Mode**: Containers need `NET_ADMIN` and `NET_RAW` capabilities.
- **Network Mode**: Use host networking or custom networks with proper routing.

## Security Implications

### 🔐 Authentication Security
- **PASS Mode**: Clear-text transmission. Use only on trusted networks.
- **AH Mode**: Cryptographic authentication with IPSec. Recommended for production.
- **No Authentication**: Only for completely isolated environments.

### 📜 Script Security
- **Root Execution**: Custom scripts run as root. Audit all script content.
- **File Permissions**: The role sets secure permissions but review custom scripts.
- **Input Validation**: Ensure scripts handle edge cases safely.

### 🌐 Network Security
- **VRRP Traffic**: Secure against rogue VRRP advertisements.
- **SNMP Access**: If enabled, configure SNMP security properly.
- **Log Security**: Protect log files containing potentially sensitive information.

### 🔑 Secrets Management
```yaml
# Use Ansible Vault for sensitive data
keepalived_auth_pass: "{{ vault_keepalived_password }}"
slack_webhook_url: "{{ vault_slack_webhook }}"
```

## Related Roles

This role integrates well with:

- **🔄 HAProxy/Nginx**: Load balancing and reverse proxy
- **🗄️ PostgreSQL/MySQL**: Database clustering
- **📊 Prometheus/Grafana**: Monitoring and alerting
- **🔐 Vault/Consul**: Service discovery and secrets management
- **🌐 Network roles**: Firewall and network configuration

### Integration Example
```yaml
- name: Complete HA Stack
  hosts: loadbalancers
  roles:
    - firewall          # Configure firewall rules
    - keepalived        # This role
    - haproxy           # Load balancer
    - prometheus-node   # Monitoring
```

## Changelog

### v2.0.0 (Latest)
- ✅ Added multi-distribution support (RedHat, SUSE)
- ✅ Implemented unicast mode for cloud environments
- ✅ Added IPv6 support
- ✅ Added comprehensive health checking
- ✅ Added configuration validation and backup
- ✅ Added VLAN interface support
- ✅ Added sync groups and multiple authentication modes
- ✅ Enhanced logging and monitoring
- ✅ Comprehensive test coverage with Molecule

### v1.0.0
- Basic keepalived installation and configuration
- Single VRRP instance support
- Debian/Ubuntu support only

---

**Need Help?** Check the `examples/` directory for real-world configuration patterns, or review the Molecule tests for comprehensive usage examples.
