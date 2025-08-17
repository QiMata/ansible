# Ansible Role: MariaDB Security

**Table of Contents**

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Related Roles](#related-roles)

## Overview

**MariaDB Security** is an Ansible role that provides comprehensive security hardening for MariaDB database servers. This role implements industry best practices for database security including SSL/TLS encryption, advanced user management, password validation, audit logging, and security hardening measures. Key features include:

* **SSL/TLS Encryption:** Configures end-to-end encryption for client connections and Galera cluster communication using self-signed or custom certificates
* **Advanced User Management:** Implements role-based access control (RBAC) with granular privileges and SSL requirements
* **Password Validation:** Enforces strong password policies using MariaDB's password validation plugins
* **Audit Logging:** Comprehensive logging of database activities for compliance and security monitoring
* **Security Hardening:** Removes default accounts, disables dangerous functions, and implements secure configuration settings
* **Certificate Management:** Automated SSL certificate generation and management for secure communications
* **Firewall Integration:** UFW firewall rules for MariaDB and Galera cluster ports
* **Encryption at Rest:** Optional encryption of database files and logs

## Supported Operating Systems/Platforms

This role is tested on and supports **Debian** and **Ubuntu** Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

## Role Variables

Below is a list of important variables for this role, along with their default values (defined in **`defaults/main.yml`**):

### SSL/TLS Configuration
| Variable | Default Value | Description |
|----------|---------------|-------------|
| `mariadb_ssl_enabled` | `true` | Enable SSL/TLS encryption for MariaDB |
| `mariadb_ssl_directory` | `/etc/mysql/ssl` | Directory for SSL certificates |
| `mariadb_ssl_generate_ca` | `true` | Generate a Certificate Authority |
| `mariadb_ssl_generate_certs` | `true` | Generate SSL certificates |
| `mariadb_galera_ssl_enabled` | `true` | Enable SSL for Galera cluster communication |

### Password Validation
| Variable | Default Value | Description |
|----------|---------------|-------------|
| `mariadb_password_validation_enabled` | `true` | Enable password validation plugin |
| `mariadb_password_validation_length` | `12` | Minimum password length |
| `mariadb_password_validation_mixed_case_count` | `1` | Required mixed case characters |
| `mariadb_password_validation_number_count` | `1` | Required numeric characters |
| `mariadb_password_validation_special_char_count` | `1` | Required special characters |

### Security Hardening
| Variable | Default Value | Description |
|----------|---------------|-------------|
| `mariadb_security_hardening_enabled` | `true` | Enable security hardening |
| `mariadb_remove_anonymous_users` | `true` | Remove anonymous user accounts |
| `mariadb_remove_remote_root` | `true` | Remove remote root access |
| `mariadb_remove_test_database` | `true` | Remove test database |
| `mariadb_local_infile` | `false` | Disable LOCAL INFILE |

### User Management
| Variable | Default Value | Description |
|----------|---------------|-------------|
| `mariadb_users` | `[]` | List of users to create |
| `mariadb_roles` | `[]` | List of roles to create |

### Audit Logging
| Variable | Default Value | Description |
|----------|---------------|-------------|
| `mariadb_audit_enabled` | `true` | Enable audit logging |
| `mariadb_audit_log_file` | `/var/log/mysql/audit.log` | Audit log file path |
| `mariadb_audit_log_policy` | `ALL` | Audit logging policy |

## Dependencies

* **Ansible Version:** This role requires Ansible **2.13** or higher
* **Collections:** 
  - `community.mysql`
  - `community.crypto`
  - `community.general`
* **System Requirements:** MariaDB server must be installed and running

## Example Playbook

```yaml
---
- name: Secure MariaDB installation
  hosts: mariadb_servers
  become: true
  vars:
    mariadb_users:
      - name: "app_user"
        password: "SecurePassword123!"
        hosts: ["localhost", "10.0.0.%"]
        privileges: "app_db.*:ALL"
        require_ssl: true
      - name: "readonly_user"
        password: "ReadOnlyPass456!"
        hosts: ["10.0.1.%"]
        privileges: "app_db.*:SELECT"
        
    mariadb_roles:
      - name: "app_role"
        privileges: "app_db.*:SELECT,INSERT,UPDATE,DELETE"
      - name: "admin_role"
        privileges: "*.*:ALL"
        
    mariadb_firewall_enabled: true
    mariadb_firewall_allowed_ips:
      - "10.0.0.0/24"
      - "192.168.1.0/24"
      
  roles:
    - mariadb_security
```

## Testing Instructions

To test this role using Molecule:

1. **Install test dependencies:**
   ```bash
   pip install molecule[docker] ansible-lint
   ```

2. **Run the test:**
   ```bash
   cd roles/mariadb_security
   molecule test
   ```

## Known Issues and Gotchas

* **SSL Certificate Generation:** Self-signed certificates are generated by default. For production use, consider using certificates from a trusted CA
* **Password Validation:** Existing passwords that don't meet new requirements will need to be updated
* **Galera SSL:** SSL configuration for Galera requires coordination across all cluster nodes
* **Firewall Rules:** Ensure cluster nodes can communicate on required Galera ports (4567, 4568, 4444)

## Security Implications

* **SSL Certificates:** Store private keys securely and restrict access
* **Audit Logs:** Contains sensitive information - ensure proper log rotation and secure storage
* **User Passwords:** Use Ansible Vault to encrypt passwords in playbooks
* **Firewall:** Properly configure allowed IP ranges to prevent unauthorized access

## Related Roles

* **[mariadb_galera_loadbalancer_install](../mariadb_galera_loadbalancer_install/README.md)** – Load balancer with SSL support
* **[mariadb_backups](../mariadb_backups/README.md)** – Backup solution that can encrypt backups
* **[mariadb_monitoring](../mariadb_monitoring/README.md)** – Monitoring that includes security metrics
* **[mariadb_performance_tuning](../mariadb_performance_tuning/README.md)** – Performance optimization
