# Ansible Role: Neo4j

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-neo4j-blue.svg)](https://galaxy.ansible.com/jared_rhodes/neo4j)

This Ansible role installs and configures the Neo4j graph database on Debian-based systems. It supersedes the former `neo4j_server` role and provides comprehensive support for:

- **Single-node deployments** - Standalone Neo4j instances
- **Cluster deployments** - Multi-node clusters with core and read replica servers
- **Enterprise & Community editions** - Support for both Neo4j editions
- **Security configurations** - TLS/SSL, authentication, and authorization
- **Backup management** - Automated backup scheduling and retention
- **Monitoring integration** - Metrics export and ELK stack integration
- **Performance tuning** - Memory, heap, and cache optimization

## Key Features

### 🚀 **Multi-Version Support & Upgrades**
- Safe version upgrades with pre/post validation
- Automatic backup before upgrades
- Rollback capability
- Version pinning support

### 🔗 **Advanced Clustering**
- Enhanced cluster discovery methods (LIST, DNS, K8S)
- Configurable timeouts and health checks
- Automatic cluster member management
- Advanced cluster monitoring

### 🗄️ **Database Management**
- Multi-database support and management
- Individual database backup strategies
- Database-specific configurations
- Automated database creation

### 🔐 **Advanced Security**
- LDAP authentication and authorization
- OAuth integration support
- Enhanced audit logging
- Password policy enforcement
- Procedure and function whitelisting

### 🔌 **Plugin Management**
- Automated plugin installation (APOC, GDS, etc.)
- Version-specific plugin handling
- Plugin configuration management
- Security settings for plugins

### 📊 **Data Import/Export**
- Automated CSV import capabilities
- Scheduled data exports
- Data seeding scripts
- Multiple export formats (Cypher, GraphML)

### 📈 **Performance Monitoring**
- Query performance monitoring
- JMX metrics export
- Health check automation
- Alerting integration
- Slow query tracking

### 🏗️ **High Availability & Disaster Recovery**
- HAProxy load balancing integration
- Cross-region backup strategies
- Disaster recovery planning
- Automated failover configuration

### ⚙️ **Configuration Management**
- Hardware-optimized configurations
- Environment-specific settings
- Custom configuration overrides
- Template-based configuration

### 🔄 **Service Dependencies**
- Service dependency management
- Health check integration
- Systemd service ordering
- Pre-start validation checks

## Requirements

- **Ansible**: >= 2.12
- **Target OS**: Debian 11+ (Bullseye, Bookworm) or Ubuntu 20.04+ (Focal, Jammy)
- **Python**: >= 3.6 on target hosts
- **Systemd**: Required for service management

## Role Variables

### Core Installation Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_edition` | `enterprise` | Neo4j edition (`enterprise` or `community`) |
| `neo4j_release_track` | `latest` | Release track (`latest`, `4.4`, `5.0`, etc.) |
| `neo4j_version` | `""` | Specific version to install (leave empty for latest) |
| `neo4j_accept_license` | `true` | Accept Neo4j Enterprise license agreement |
| `neo4j_upgrade_enabled` | `false` | Enable upgrade functionality |
| `neo4j_backup_before_upgrade` | `true` | Create backup before upgrading |
| `neo4j_rollback_enabled` | `true` | Enable rollback capability |
| `neo4j_version_pin` | `true` | Pin package version after installation |

### Network Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_listen_address` | `0.0.0.0` | IP address Neo4j binds to |
| `neo4j_advertised_address` | `{{ ansible_default_ipv4.address }}` | IP address advertised to clients |
| `neo4j_bolt_port` | `7687` | Bolt protocol port |
| `neo4j_http_enabled` | `false` | Enable HTTP connector |
| `neo4j_https_enabled` | `true` | Enable HTTPS connector |
| `neo4j_http_port` | `7474` | HTTP connector port |
| `neo4j_https_port` | `7473` | HTTPS connector port |

### Clustering Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_cluster_enabled` | `false` | Enable clustering (Enterprise only) |
| `neo4j_core_count` | `{{ groups['neo4j_core'] \| length }}` | Number of core servers |
| `neo4j_read_replica_count` | `{{ groups['neo4j_replica'] \| length }}` | Number of read replicas |
| `neo4j_cluster_discovery_type` | `LIST` | Cluster discovery method (`LIST`, `DNS`, `K8S`) |
| `neo4j_cluster_routing_ttl` | `300s` | Cluster routing TTL |
| `neo4j_cluster_topology_refresh` | `5s` | Topology refresh interval |
| `neo4j_cluster_catch_up_timeout` | `10m` | Catch-up timeout |
| `neo4j_cluster_join_timeout` | `10m` | Cluster join timeout |

### Security & TLS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_tls_client_enable` | `true` | Enable TLS for client connections |
| `neo4j_tls_cluster_enable` | `{{ neo4j_cluster_enabled }}` | Enable TLS for cluster communication |
| `neo4j_certificates_source` | `self-signed` | Certificate source (`self-signed`, `custom`, `letsencrypt`) |
| `neo4j_initial_password` | `""` | Initial password for `neo4j` user |
| `neo4j_user_creation` | `[]` | List of additional users to create |
| `neo4j_ldap_enabled` | `false` | Enable LDAP authentication |
| `neo4j_ldap_server` | `""` | LDAP server hostname |
| `neo4j_oauth_enabled` | `false` | Enable OAuth authentication |
| `neo4j_password_policy_enabled` | `true` | Enable password policy enforcement |
| `neo4j_audit_enabled` | `{{ neo4j_edition == 'enterprise' }}` | Enable audit logging |
| `neo4j_procedures_whitelist` | `[]` | Whitelisted procedures |
| `neo4j_functions_whitelist` | `[]` | Whitelisted functions |

### Database Management

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_databases` | `[{name: neo4j, default: true}]` | List of databases to create |
| `neo4j_database_backup_individual` | `true` | Enable individual database backups |
| `neo4j_default_database` | `neo4j` | Default database name |

### Plugin Management

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_plugins` | `[{name: apoc, enabled: true}]` | List of plugins to install |
| `neo4j_plugin_dir` | `/var/lib/neo4j/plugins` | Plugin installation directory |
| `neo4j_apoc_export_file_enabled` | `true` | Enable APOC file export |
| `neo4j_apoc_import_file_enabled` | `true` | Enable APOC file import |

### Data Import/Export

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_import_enabled` | `false` | Enable data import functionality |
| `neo4j_import_sources` | `[]` | List of data sources to import |
| `neo4j_export_scheduled` | `false` | Enable scheduled data exports |
| `neo4j_data_seeding` | `[]` | List of data seeding scripts |
| `neo4j_csv_import_enabled` | `true` | Enable CSV import functionality |
| `neo4j_import_dir` | `/var/lib/neo4j/import` | Import directory |
| `neo4j_export_dir` | `/var/lib/neo4j/export` | Export directory |

### Performance Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_heap_size` | `""` | JVM heap size (e.g., `2G`, auto-detected if empty) |
| `neo4j_pagecache_size` | `""` | Page cache size (e.g., `4G`, auto-detected if empty) |

### Backup Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_backup_enabled` | `{{ neo4j_edition == 'enterprise' }}` | Enable backup functionality |
| `neo4j_backup_listen_address` | `127.0.0.1:6362` | Backup service listen address |
| `neo4j_backup_cron_enabled` | `false` | Enable automated backup scheduling |
| `neo4j_backup_hour` | `2` | Hour to run daily backups |
| `neo4j_backup_dir` | `/var/backups/neo4j` | Backup storage directory |
| `neo4j_backup_retention` | `7` | Days to retain backup files |

### Monitoring & Metrics

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_metrics_enabled` | `{{ neo4j_edition == 'enterprise' }}` | Enable metrics export |
| `neo4j_metrics_listen` | `:2004` | Metrics endpoint listen address |
| `neo4j_query_monitoring` | `true` | Enable query performance monitoring |
| `neo4j_slow_query_threshold` | `1000ms` | Threshold for slow query logging |
| `neo4j_connection_monitoring` | `true` | Enable connection monitoring |
| `neo4j_health_checks` | `[{name: database_available, enabled: true}]` | Health check configurations |
| `neo4j_alerting_enabled` | `false` | Enable alerting system |
| `neo4j_jmx_enabled` | `true` | Enable JMX monitoring |
| `neo4j_jmx_port` | `3637` | JMX port |

### High Availability & Disaster Recovery

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_ha_proxy_enabled` | `false` | Enable HAProxy load balancing |
| `neo4j_load_balancer_config` | `{}` | Load balancer configuration |
| `neo4j_cross_region_backup` | `false` | Enable cross-region backups |
| `neo4j_disaster_recovery_plan` | `false` | Enable disaster recovery features |
| `neo4j_ha_health_check_interval` | `3s` | HA health check interval |
| `neo4j_ha_failover_timeout` | `40s` | HA failover timeout |

### Service Dependencies

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_depends_on_services` | `[]` | List of service dependencies |
| `neo4j_wait_for_services` | `true` | Wait for dependencies before starting |
| `neo4j_health_check_retries` | `10` | Number of health check retries |
| `neo4j_health_check_delay` | `5` | Delay between health checks |
| `neo4j_service_start_timeout` | `300` | Service start timeout |

### Configuration Templates

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_config_template` | `neo4j.conf.j2` | Configuration template file |
| `neo4j_custom_config` | `{}` | Custom configuration overrides |
| `neo4j_environment_config` | `{}` | Environment-specific configuration |
| `neo4j_hardware_optimized_config` | `true` | Enable hardware-optimized configuration |
| `neo4j_elk_integration` | `false` | Enable ELK stack integration |
| `neo4j_elk_host` | `""` | Elasticsearch/Logstash host |
| `neo4j_elk_port` | `5044` | Logstash port |
| `neo4j_elk_cloud_id` | `""` | Elastic Cloud ID |
| `neo4j_elk_username` | `""` | ELK authentication username |
| `neo4j_elk_password` | `""` | ELK authentication password |

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_logrotate_enable` | `true` | Enable log rotation |
| `neo4j_logrotate_rotation` | `7` | Number of rotated logs to keep |
| `neo4j_logrotate_frequency` | `weekly` | Log rotation frequency |
| `neo4j_log_level` | `INFO` | Neo4j logging level |

## Dependencies

This role has no external Ansible Galaxy dependencies.

## Example Playbooks

### Basic Single-Node Installation

```yaml
---
- name: Deploy Neo4j standalone
  hosts: neo4j_servers
  become: true
  roles:
    - role: data_systems/neo4j
      vars:
        neo4j_edition: community
        neo4j_initial_password: "{{ vault_neo4j_password }}"
        neo4j_heap_size: "2G"
        neo4j_pagecache_size: "4G"
```

### Enterprise Cluster Deployment

```yaml
---
- name: Deploy Neo4j Enterprise Cluster
  hosts: neo4j_cluster
  become: true
  roles:
    - role: data_systems/neo4j
      vars:
        neo4j_edition: enterprise
        neo4j_cluster_enabled: true
        neo4j_initial_password: "{{ vault_neo4j_password }}"
        neo4j_tls_client_enable: true
        neo4j_tls_cluster_enable: true
        neo4j_backup_enabled: true
        neo4j_backup_cron_enabled: true
        neo4j_metrics_enabled: true
        neo4j_user_creation:
          - username: app_user
            password: "{{ vault_app_user_password }}"
            roles: ["reader"]
          - username: admin_user
            password: "{{ vault_admin_password }}"
            roles: ["admin"]
```

### High-Performance Production Setup with All Features

```yaml
---
- name: Deploy Neo4j Production Instance with Enhanced Features
  hosts: neo4j_production
  become: true
  roles:
    - role: data_systems/neo4j
      vars:
        neo4j_edition: enterprise
        neo4j_accept_license: true
        neo4j_heap_size: "16G"
        neo4j_pagecache_size: "32G"
        
        # Multi-database setup
        neo4j_databases:
          - name: production
            default: true
          - name: analytics
            default: false
          - name: staging
            default: false
        
        # Plugin configuration
        neo4j_plugins:
          - name: apoc
            enabled: true
          - name: graph-data-science
            enabled: true
        
        # Security configuration
        neo4j_ldap_enabled: true
        neo4j_ldap_server: "ldap.company.com"
        neo4j_audit_enabled: true
        neo4j_password_policy_enabled: true
        neo4j_procedures_whitelist:
          - "apoc.export.*"
          - "apoc.import.*"
          - "gds.*"
        
        # Backup and recovery
        neo4j_backup_enabled: true
        neo4j_backup_cron_enabled: true
        neo4j_backup_retention: 30
        neo4j_database_backup_individual: true
        neo4j_disaster_recovery_plan: true
        neo4j_cross_region_backup: true
        
        # Monitoring and alerting
        neo4j_metrics_enabled: true
        neo4j_query_monitoring: true
        neo4j_slow_query_threshold: "500ms"
        neo4j_jmx_enabled: true
        neo4j_alerting_enabled: true
        neo4j_alerting_webhook: "https://hooks.slack.com/services/..."
        
        # Data management
        neo4j_import_enabled: true
        neo4j_export_scheduled: true
        neo4j_data_seeding:
          - name: initial_schema
            statements:
              - "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE"
              - "CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name)"
            execute: true
        
        # Service dependencies
        neo4j_depends_on_services:
          - name: "elasticsearch"
            type: "port"
            host: "elasticsearch.company.com"
            port: 9200
          - name: "ldap"
            type: "port" 
            host: "ldap.company.com"
            port: 389
        
        # ELK integration
        neo4j_elk_integration: true
        neo4j_elk_host: "{{ elk_server }}"
        neo4j_logrotate_frequency: daily
```

### Cluster Setup with Advanced Features

```yaml
---
- name: Deploy Neo4j Enterprise Cluster with Advanced Features
  hosts: neo4j_cluster
  become: true
  roles:
    - role: data_systems/neo4j
      vars:
        neo4j_edition: enterprise
        neo4j_cluster_enabled: true
        neo4j_cluster_discovery_type: "LIST"
        neo4j_cluster_minimum_core_cluster_size_at_formation: 3
        neo4j_cluster_minimum_core_cluster_size_at_runtime: 3
        
        # HA configuration
        neo4j_ha_proxy_enabled: true
        neo4j_ha_health_check_interval: "2s"
        neo4j_ha_failover_timeout: "30s"
        
        # Security
        neo4j_tls_client_enable: true
        neo4j_tls_cluster_enable: true
        neo4j_audit_enabled: true
        
        # Plugins and data
        neo4j_plugins:
          - name: apoc
            enabled: true
          - name: graph-data-science
            enabled: true
        
        # Monitoring
        neo4j_health_checks:
          - name: database_available
            enabled: true
          - name: cluster_healthy
            enabled: true
        
        # Backup strategy
        neo4j_backup_enabled: true
        neo4j_database_backup_individual: true
        neo4j_disaster_recovery_plan: true
```

### Upgrade Scenario

```yaml
---
- name: Upgrade Neo4j with Safety Measures
  hosts: neo4j_servers
  become: true
  roles:
    - role: data_systems/neo4j
      vars:
        neo4j_upgrade_enabled: true
        neo4j_version: "5.15.0"
        neo4j_backup_before_upgrade: true
        neo4j_pre_upgrade_checks: true
        neo4j_post_upgrade_validation: true
        neo4j_rollback_enabled: true
        neo4j_upgrade_strategy: "rolling"
        neo4j_upgrade_timeout: "600"
```

## Inventory Examples

### Single Node
```ini
[neo4j_servers]
neo4j-01 ansible_host=10.0.1.10
```

### Cluster Setup
```ini
[neo4j_core]
neo4j-core-01 ansible_host=10.0.1.10
neo4j-core-02 ansible_host=10.0.1.11
neo4j-core-03 ansible_host=10.0.1.12

[neo4j_replica]
neo4j-replica-01 ansible_host=10.0.1.20
neo4j-replica-02 ansible_host=10.0.1.21

[neo4j_cluster:children]
neo4j_core
neo4j_replica
```

## User Management

The role supports creating additional Neo4j users during deployment:

```yaml
neo4j_user_creation:
  - username: readonly_user
    password: "{{ vault_readonly_password }}"
    roles: ["reader"]
  - username: analyst
    password: "{{ vault_analyst_password }}"
    roles: ["reader", "publisher"]
  - username: dba
    password: "{{ vault_dba_password }}"
    roles: ["admin"]
```

## Security Considerations

1. **Passwords**: Always use Ansible Vault for sensitive passwords
2. **TLS Certificates**: For production, use proper CA-signed certificates
3. **Network Security**: Configure firewalls to restrict access to Neo4j ports
4. **File Permissions**: The role sets appropriate file ownership and permissions
5. **License Compliance**: Ensure compliance with Neo4j Enterprise license terms

## Performance Tuning Guidelines

### Memory Configuration
- **Heap Size**: Typically 30-50% of system RAM, max 31GB
- **Page Cache**: Remaining available RAM after heap allocation
- **Example for 64GB system**: `heap_size: "24G"`, `pagecache_size: "35G"`

### Storage Recommendations
- Use SSD storage for optimal performance
- Separate data and transaction log directories if possible
- Ensure adequate IOPS for concurrent operations

## Backup & Recovery

When `neo4j_backup_enabled` is true, the role configures:
- Online backup capability via `neo4j-admin backup`
- Optional cron-based scheduled backups
- Configurable retention policies
- Backup validation and monitoring

Manual backup example:
```bash
neo4j-admin backup --backup-dir=/var/backups/neo4j --name=manual-backup
```

## Monitoring Integration

### Metrics Export
When enabled, Neo4j exports metrics compatible with:
- Prometheus (via JMX exporter)
- Graphite (direct export)
- Custom monitoring solutions

### ELK Stack Integration
The role can configure Filebeat for log shipping to:
- Elasticsearch clusters
- Logstash instances
- Elastic Cloud deployments

## Testing

This role includes comprehensive test suites using Molecule:

### Test Scenarios

1. **Default Tests**: Basic single-node installation
2. **Enhanced Tests**: All advanced features including clustering
3. **Podman Tests**: Container-based testing

```bash
# Run all tests
molecule test

# Test enhanced features
molecule test -s enhanced

# Test with Podman
molecule test -s podman

# Test specific scenarios
molecule converge -s enhanced
molecule verify -s enhanced

# Run integration tests
ansible-playbook molecule/enhanced/test_integration.yml
```

### Test Coverage

The test suite validates:
- ✅ Basic installation and service management
- ✅ Plugin installation and configuration
- ✅ Security settings and authentication
- ✅ Clustering functionality
- ✅ Backup and recovery procedures
- ✅ Monitoring and health checks
- ✅ High availability features
- ✅ Data import/export capabilities
- ✅ Service dependencies
- ✅ Upgrade procedures

### Manual Testing

```bash
# Test database connectivity
cypher-shell -u neo4j -p password "RETURN 1 as test"

# Test APOC plugin
cypher-shell -u neo4j -p password "CALL apoc.help('export')"

# Test cluster status (if clustered)
curl -u neo4j:password http://localhost:7474/db/cluster/overview

# Run health checks
/usr/local/bin/neo4j-health-check.sh database_available

# Test backup functionality
/usr/local/bin/neo4j-database-backup.sh neo4j
```

## Troubleshooting

### Common Issues

1. **License Acceptance**: Ensure `neo4j_accept_license: true` for Enterprise
2. **Memory Errors**: Adjust heap and page cache sizes based on available RAM
3. **Port Conflicts**: Verify no other services use configured ports
4. **Certificate Issues**: Check TLS configuration and certificate validity
5. **Cluster Formation**: Ensure all cluster members can communicate

### Log Locations
- Neo4j logs: `/var/log/neo4j/`
- Service logs: `journalctl -u neo4j`
- Debug logs: `/var/log/neo4j/debug.log`

## License

MIT

## Author Information

This role was created by **Jared Rhodes** as part of a comprehensive Ansible automation suite for data systems infrastructure.

---

**Tags**: neo4j, graph-database, clustering, enterprise, debian, ubuntu, backup, monitoring, tls
