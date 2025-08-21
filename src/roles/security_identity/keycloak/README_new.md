# Keycloak Role

## Overview

The **Keycloak** Ansible role provides a comprehensive solution for installing, configuring, and managing [Keycloak](https://www.keycloak.org/) (an open-source Identity and Access Management server) on target hosts. This role has been significantly enhanced with production-ready features including:

### Core Features
* **System Requirements:** Ensures necessary system packages (e.g. `unzip`, `curl`, OpenJDK 17) are present on the host.
* **User Setup:** Creates a dedicated system user (default **`keycloak`**) with a non-login shell to run the Keycloak service.
* **Installation:** Downloads the specified Keycloak server tarball and unpacks it into the installation directory with version-specific paths.
* **Configuration:** Deploys comprehensive Keycloak configuration files and systemd service unit from Jinja2 templates.
* **Service Management:** Registers the Keycloak service with systemd, ensuring it is enabled to start on boot and is currently running.

### Production-Ready Enhancements

#### 1. **Initial Admin User Creation**
- Automatically creates the Keycloak admin user during installation
- Configurable admin username and password
- Verification of admin user creation and accessibility

#### 2. **TLS/HTTPS Support** 
- Built-in HTTPS/TLS configuration with certificate management
- Automatic keystore and truststore creation from PEM certificates  
- Support for custom certificate files and keystore passwords
- HTTPS health checks and admin console verification

#### 3. **Database Management**
- Automatic PostgreSQL database and user creation
- Configurable database connection parameters including custom ports
- Database connectivity validation and schema initialization
- Support for external database administration credentials

#### 4. **High Availability Clustering**
- JGroups/Infinispan cache configuration for clustering
- Multiple discovery mechanisms: static, DNS, Kubernetes
- TCP and UDP transport stack support
- Configurable cluster member management

#### 5. **Security and Network**
- Integrated firewall configuration (UFW, firewalld, iptables)
- Network security hardening with systemd service protections
- Configurable security policies and resource limits

#### 6. **Backup and Recovery**
- Automated backup system with configurable schedules
- Database backup integration with compression
- Configurable retention policies and cleanup
- Realm export/import functionality

#### 7. **Monitoring and Observability**
- Health check monitoring with automated scripts
- Metrics collection and logging configuration
- Centralized logging support with syslog integration
- Log rotation and management

#### 8. **Theme and Customization**
- Custom theme deployment and management
- Custom provider and extension installation
- Realm import/export capabilities
- Development mode support

#### 9. **Resource Management**
- JVM tuning and memory configuration optimization
- Systemd resource limits and service hardening
- Performance optimization settings
- CPU and memory quota management

#### 10. **Version Management**
- Automatic cleanup of old Keycloak versions
- Rollback mechanism support
- Version-specific installation directories
- Symlink management for current version

#### 11. **Configuration Validation**
- Pre-flight checks for system requirements
- Database connectivity validation before service start
- Configuration syntax checking and validation
- Comprehensive dependency verification

#### 12. **Development Support**
- Development mode configuration
- Test realm creation and management
- Sample configuration templates
- Enhanced debugging and logging

## Supported Operating Systems/Platforms

This role is currently designed for **Debian-based Linux distributions**. It uses the APT package manager in its tasks, so it has been tested and verified on:

* **Debian 12 (Bookworm)** – *Tested via Molecule* (Docker container image).
* **Ubuntu LTS** (e.g. 20.04, 22.04) – *Likely supported*, given similar package names and availability of OpenJDK 17 on these releases.
* *Other Debian/Ubuntu derivatives* that use `apt` should also work with little or no modification.

**Not supported out-of-the-box:** Red Hat Enterprise Linux, CentOS, AlmaLinux, etc. (no `yum/dnf` tasks are included). Adapting the role to RHEL-based systems would require adding equivalent YUM tasks for installing packages and possibly adjusting package names (e.g. OpenJDK 17 package on RHEL) and paths. The role also assumes a systemd-based OS for service management, so non-systemd environments would need modifications.

## Role Variables

Below is a comprehensive list of variables available for this role, organized by feature category. Most defaults are defined in the role's **defaults/main.yml**.

<details><summary>Role Variables (click to expand)</summary>

### Basic Configuration
| Variable                | Default Value                                                                                                            | Description |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `keycloak_version`      | "24.0.1"                                                                                                               | Version of Keycloak to install. This should match an official Keycloak release version. |
| `keycloak_user`         | "keycloak"                                                                                                             | System username under which Keycloak will run. |
| `keycloak_home`         | "/var/lib/keycloak"                                                                                                    | Base home directory for Keycloak. |
| `keycloak_install_dir`  | `{{ keycloak_home }}/keycloak-{{ keycloak_version }}`                                                                    | Directory where Keycloak will be installed. |
| `keycloak_download_url` | "https://github.com/keycloak/keycloak/releases/download/{{ keycloak_version }}/keycloak-{{ keycloak_version }}.tar.gz" | URL to download the Keycloak server archive. |
| `keycloak_hostname`     | `{{ inventory_hostname }}`                                                                                              | External hostname for the Keycloak server. |
| `keycloak_packages`     | `['unzip', 'curl', 'openjdk-17-jre-headless']`                                                                         | List of OS packages to install for Keycloak support. |

### Network Configuration
| Variable                | Default Value | Description |
| ----------------------- | ------------- | ----------- |
| `keycloak_http_port`    | 8080          | HTTP port for Keycloak when HTTPS is disabled. |
| `keycloak_https_port`   | 8443          | HTTPS port for Keycloak when TLS is enabled. |

### Database Configuration
| Variable                    | Default Value | Description |
| --------------------------- | ------------- | ----------- |
| `keycloak_db_host`         | ""            | **Required** - PostgreSQL host for Keycloak's database. |
| `keycloak_db_port`         | 5432          | PostgreSQL port. |
| `keycloak_db_name`         | "keycloak"    | PostgreSQL database name. |
| `keycloak_db_user`         | "keycloak"    | PostgreSQL username for Keycloak. |
| `keycloak_db_password`     | ""            | **Required** - Password for the database user. |
| `keycloak_db_create`       | false         | Whether to create database and user automatically. |
| `keycloak_db_admin_user`   | "postgres"    | Admin user for database creation. |
| `keycloak_db_admin_password` | ""          | Admin password for database creation. |

### Admin User Configuration
| Variable                    | Default Value | Description |
| --------------------------- | ------------- | ----------- |
| `keycloak_create_admin`    | true          | Whether to create initial admin user. |
| `keycloak_admin_user`      | "admin"       | Username for the Keycloak admin user. |
| `keycloak_admin_password`  | ""            | **Required if create_admin is true** - Password for admin user. |

### TLS/HTTPS Configuration
| Variable                        | Default Value                                           | Description |
| ------------------------------- | ------------------------------------------------------- | ----------- |
| `keycloak_enable_https`        | false                                                   | Enable HTTPS/TLS support. |
| `keycloak_cert_file`           | ""                                                      | Path to TLS certificate file. |
| `keycloak_key_file`            | ""                                                      | Path to TLS private key file. |
| `keycloak_keystore_path`       | `{{ keycloak_install_dir }}/conf/server.keystore`      | Path to Java keystore. |
| `keycloak_keystore_password`   | "changeit"                                              | Keystore password. |
| `keycloak_truststore_path`     | `{{ keycloak_install_dir }}/conf/server.truststore`    | Path to Java truststore. |
| `keycloak_truststore_password` | "changeit"                                              | Truststore password. |

### Clustering Configuration
| Variable                     | Default Value                                  | Description |
| ---------------------------- | ---------------------------------------------- | ----------- |
| `keycloak_cluster_enabled`  | false                                          | Enable clustering support. |
| `keycloak_cluster_name`     | "keycloak"                                     | Name of the cluster. |
| `keycloak_cache_stack`      | "tcp"                                          | Cache stack: tcp, udp, or kubernetes. |
| `keycloak_cluster_discovery` | "static"                                       | Discovery method: static, dns, kubernetes. |
| `keycloak_cluster_members`  | []                                             | List of cluster member IPs (for static discovery). |
| `keycloak_jgroups_bind_addr` | `{{ ansible_default_ipv4.address }}`          | JGroups bind address. |

### Firewall Configuration
| Variable                      | Default Value | Description |
| ----------------------------- | ------------- | ----------- |
| `keycloak_configure_firewall` | true          | Whether to configure firewall rules. |
| `keycloak_firewall_backend`   | "ufw"         | Firewall backend: ufw, firewalld, or iptables. |

### Backup Configuration
| Variable                       | Default Value                  | Description |
| ------------------------------ | ------------------------------ | ----------- |
| `keycloak_backup_enabled`     | false                          | Enable automated backups. |
| `keycloak_backup_schedule`    | "0 2 * * *"                    | Cron schedule for backups (daily at 2 AM). |
| `keycloak_backup_retention_days` | 7                           | Number of days to retain backups. |
| `keycloak_backup_dir`         | `{{ keycloak_home }}/backups`  | Directory for backup storage. |

### Monitoring and Logging
| Variable                        | Default Value | Description |
| ------------------------------- | ------------- | ----------- |
| `keycloak_monitoring_enabled`  | false         | Enable monitoring scripts. |
| `keycloak_metrics_enabled`     | false         | Enable metrics collection. |
| `keycloak_log_level`           | "INFO"        | Logging level. |
| `keycloak_log_format`          | "JSON"        | Log format: JSON or plain text. |
| `keycloak_centralized_logging` | false         | Enable centralized logging. |
| `keycloak_syslog_server`       | ""            | Syslog server for centralized logging. |

### Theme and Customization
| Variable                  | Default Value | Description |
| ------------------------- | ------------- | ----------- |
| `keycloak_custom_themes` | []            | List of custom themes to deploy. |
| `keycloak_custom_providers` | []         | List of custom providers to deploy. |
| `keycloak_realm_imports` | []            | List of realm files to import. |

### Resource Management
| Variable                    | Default Value | Description |
| --------------------------- | ------------- | ----------- |
| `keycloak_jvm_heap_min`    | "512m"        | Minimum JVM heap size. |
| `keycloak_jvm_heap_max`    | "2g"          | Maximum JVM heap size. |
| `keycloak_jvm_opts`        | []            | Additional JVM options. |
| `keycloak_systemd_limits`  | {}            | Systemd resource limits. |

### Version Management
| Variable                        | Default Value | Description |
| ------------------------------- | ------------- | ----------- |
| `keycloak_cleanup_old_versions` | false         | Remove old Keycloak versions. |
| `keycloak_max_versions_to_keep` | 2             | Number of versions to retain. |

### Configuration Validation
| Variable                    | Default Value | Description |
| --------------------------- | ------------- | ----------- |
| `keycloak_validate_config` | true          | Validate configuration before starting. |
| `keycloak_preflight_checks` | true         | Run pre-flight checks before installation. |

### Development Support
| Variable                     | Default Value | Description |
| ---------------------------- | ------------- | ----------- |
| `keycloak_dev_mode`         | false         | Enable development mode. |
| `keycloak_create_test_realm` | false         | Create a test realm. |
| `keycloak_test_realm_name`  | "test"        | Name of the test realm. |

### External Integration
| Variable                  | Default Value   | Description |
| ------------------------- | --------------- | ----------- |
| `keycloak_ldap_enabled`  | false           | Enable LDAP integration. |
| `keycloak_vault_enabled` | false           | Enable vault integration. |
| `keycloak_vault_provider` | "hashicorp"    | Vault provider: hashicorp or kubernetes. |

</details>

**Required Variables:**
- `keycloak_db_host` - PostgreSQL host
- `keycloak_db_password` - Database password
- `keycloak_admin_password` - Admin password (if `keycloak_create_admin` is true)
- `keycloak_cert_file` and `keycloak_key_file` - TLS certificate files (if `keycloak_enable_https` is true)

## Tags

This role does not define any task tags. All tasks will run by default when the role is invoked.

## Dependencies

**Role Dependencies:** The Keycloak role itself does not depend on any other Ansible roles. However, it requires the following Ansible collections:
- `community.postgresql` (for database management)
- `community.general` (for UFW firewall management)
- `ansible.posix` (for firewalld management)

Install these with:
```bash
ansible-galaxy collection install community.postgresql community.general ansible.posix
```

**External Service Requirements:**
* **PostgreSQL Database:** If `keycloak_db_create` is false, you must provision a PostgreSQL server separately.
* **Java Runtime:** OpenJDK 17 will be installed automatically.
* **Certificates:** For HTTPS, provide valid TLS certificates.
* **Systemd:** Required for service management.

## Example Playbook

### Basic Configuration

```yaml
- hosts: keycloak
  become: true
  vars:
    keycloak_db_host: "db.example.com"
    keycloak_db_password: "{{ vault_keycloak_db_password }}"
    keycloak_admin_password: "{{ vault_keycloak_admin_password }}"
    keycloak_hostname: "sso.example.com"
  roles:
    - role: keycloak
```

### Production Configuration with TLS and Clustering

```yaml
- hosts: keycloak_cluster
  become: true
  vars:
    # Database configuration
    keycloak_db_host: "db.example.com"
    keycloak_db_password: "{{ vault_keycloak_db_password }}"
    
    # Admin user
    keycloak_admin_password: "{{ vault_keycloak_admin_password }}"
    
    # TLS configuration
    keycloak_enable_https: true
    keycloak_cert_file: "/etc/ssl/certs/keycloak.crt"
    keycloak_key_file: "/etc/ssl/private/keycloak.key"
    
    # Clustering
    keycloak_cluster_enabled: true
    keycloak_cluster_members:
      - "10.0.1.10"
      - "10.0.1.11"
    
    # Monitoring and backup
    keycloak_monitoring_enabled: true
    keycloak_backup_enabled: true
    
    # Resource management
    keycloak_jvm_heap_max: "4g"
  roles:
    - role: keycloak
```

### Development Configuration

```yaml
- hosts: keycloak_dev
  become: true
  vars:
    keycloak_db_host: "localhost"
    keycloak_db_create: true
    keycloak_db_admin_password: "postgres"
    keycloak_db_password: "keycloak"
    keycloak_admin_password: "admin"
    keycloak_dev_mode: true
    keycloak_create_test_realm: true
    keycloak_configure_firewall: false
  roles:
    - role: keycloak
```

## Testing Instructions

This role includes comprehensive **Molecule** test scenarios for automated testing:

### Available Test Scenarios

1. **default** - Basic Keycloak installation with all standard features
2. **tls** - TLS/HTTPS configuration testing
3. **cluster** - Multi-node clustering configuration
4. **database** - Database creation and management testing

### Running Tests

```bash
# Install Molecule and dependencies
pip install molecule molecule[docker] docker testinfra

# Run all tests
molecule test

# Run specific scenario
cd molecule/tls
molecule test

# Debug a specific scenario
molecule create
molecule converge
molecule login
molecule verify
molecule destroy
```

### Test Coverage

The tests verify:
- ✅ Keycloak installation and service startup
- ✅ Database connectivity and schema creation
- ✅ Admin user creation and authentication
- ✅ TLS certificate configuration
- ✅ Cluster formation and replication
- ✅ Health checks and monitoring scripts
- ✅ Backup functionality
- ✅ Firewall configuration
- ✅ Resource management and JVM tuning

## Security Considerations

This role implements several security best practices:

* **Unprivileged User:** Keycloak runs as a dedicated system user, not root
* **File Permissions:** Configuration files have restrictive permissions (0640)
* **Network Security:** Integrated firewall configuration
* **Systemd Hardening:** Security settings in service unit file
* **TLS Support:** Built-in HTTPS configuration
* **Secret Management:** Support for Ansible Vault integration

**Important Security Notes:**
- Always use HTTPS in production (`keycloak_enable_https: true`)
- Store sensitive variables in Ansible Vault
- Keep Keycloak version updated for security patches
- Configure proper database security (SSL, strong passwords)
- Review and adjust firewall rules for your environment

## Troubleshooting

### Common Issues

1. **Service fails to start**
   - Check database connectivity: `systemctl status keycloak`
   - Verify database credentials in `/var/lib/keycloak/current/conf/keycloak.conf`
   - Check logs: `journalctl -u keycloak -f`

2. **Admin user creation fails**
   - Ensure Keycloak is healthy: `curl http://localhost:8080/health`
   - Check admin credentials are set correctly
   - Verify network connectivity to Keycloak

3. **TLS certificate issues**
   - Verify certificate files exist and are readable
   - Check keystore generation: `keytool -list -keystore /path/to/keystore`
   - Validate certificate chain

4. **Clustering not working**
   - Check JGroups configuration in logs
   - Verify cluster members can communicate on port 7800
   - Ensure all nodes use the same database

### Log Locations

- **Service logs:** `journalctl -u keycloak`
- **Keycloak logs:** `/var/log/keycloak/keycloak.log`
- **Health check logs:** `/var/log/keycloak/health.log`
- **Backup logs:** `/var/log/keycloak/backup.log`

## Changelog

### Version 2.0.0 (Current)
- ✅ Initial admin user creation
- ✅ TLS/HTTPS support with certificate management
- ✅ Database creation and management
- ✅ High availability clustering
- ✅ Firewall configuration (UFW, firewalld, iptables)
- ✅ Backup and recovery system
- ✅ Monitoring and health checks
- ✅ Theme and customization support
- ✅ Resource management and JVM tuning
- ✅ Version management and cleanup
- ✅ Configuration validation and pre-flight checks
- ✅ Development mode support
- ✅ Comprehensive test coverage

### Version 1.0.0
- Basic Keycloak installation
- SystemD service management
- PostgreSQL database configuration

## Contributing

To contribute to this role:

1. Fork the repository
2. Create a feature branch
3. Add or modify features
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

All contributions should include:
- Molecule tests for new features
- Updated variable documentation
- Example configurations
- Security considerations

## License

This role is licensed under the MIT License. See LICENSE file for details.
