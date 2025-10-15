# Ansible Role: Elasticsearch

This Ansible role installs, configures, and manages Elasticsearch clusters. It provides a comprehensive solution for deploying Elasticsearch with security features, cluster configuration, and LDAP integration. This role combines the functionality of the previous `elasticsearch_install`, `elasticsearch_config`, `elasticsearch_security`, and `elasticsearch_cluster` roles into a unified, maintainable solution.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Role Variables](#role-variables)
- [Dependencies](#dependencies)
- [Example Playbooks](#example-playbooks)
- [Tags](#tags)
- [Handlers](#handlers)
- [Testing](#testing)
- [License](#license)

## Features

- **Installation**: Automated Elasticsearch installation with repository setup
- **Configuration**: Flexible cluster and node configuration
- **Security**: X-Pack security with TLS/SSL support
- **LDAP Integration**: Active Directory/LDAP authentication support
- **Cluster Management**: Multi-node cluster setup with discovery configuration
- **JVM Tuning**: Customizable heap size and JVM options
- **Certificate Management**: TLS certificate deployment and configuration

## Requirements

- Ansible >= 2.13
- Target systems: Ubuntu 20.04+, Debian 11+
- Python 3.6+ on target hosts
- Internet connectivity for package downloads (unless using local repositories)

## Role Variables

### Basic Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_version` | `"8.x"` | Elasticsearch version to install |
| `elasticsearch_cluster_name` | `"elasticsearch-cluster"` | Name of the Elasticsearch cluster |
| `elasticsearch_node_roles` | `[]` | List of node roles (master, data, ingest, etc.) |
| `elasticsearch_network_host` | `"{{ ansible_default_ipv4.address }}"` | Network interface to bind to |
| `elasticsearch_heap_size` | `"2g"` | JVM heap size allocation |
| `elasticsearch_install_java` | `true` | Whether to install OpenJDK automatically |
| `elasticsearch_environment` | `"production"` | Environment type (dev, staging, production) |

### Storage and Paths

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_data_paths` | `["/var/lib/elasticsearch"]` | List of data storage paths |
| `elasticsearch_log_path` | `"/var/log/elasticsearch"` | Log directory path |
| `elasticsearch_config_path` | `"/etc/elasticsearch"` | Configuration directory |
| `elasticsearch_path_repo` | `[]` | Snapshot repository paths |
| `elasticsearch_store_type` | `"fs"` | Storage type (fs, niofs, mmapfs, hybridfs) |
| `elasticsearch_allow_mmapfs` | `true` | Allow memory-mapped file system |

### Security Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_enable_security` | `false` | Enable X-Pack security features |
| `elasticsearch_tls_provided` | `false` | Whether TLS certificates are pre-provided |
| `elasticsearch_api_key_enabled` | `false` | Enable API key authentication |
| `elasticsearch_audit_enabled` | `false` | Enable security auditing |
| `elasticsearch_field_level_security` | `false` | Enable field-level security |
| `elasticsearch_document_level_security` | `false` | Enable document-level security |

### Plugin Management

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_plugins` | `[]` | List of plugins to install |
| `elasticsearch_plugins_remove` | `[]` | List of plugins to remove |

### Index Template Management

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_index_templates` | `[]` | Index templates to create |
| `elasticsearch_component_templates` | `[]` | Component templates to create |
| `elasticsearch_index_lifecycle_policies` | `[]` | ILM policies to create |
| `elasticsearch_custom_analyzers` | `{}` | Custom text analyzers |
| `elasticsearch_custom_filters` | `{}` | Custom token filters |
| `elasticsearch_custom_tokenizers` | `{}` | Custom tokenizers |

### Snapshot and Backup

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_snapshot_repositories` | `[]` | Snapshot repositories configuration |
| `elasticsearch_snapshot_policies` | `[]` | Automated snapshot policies |
| `elasticsearch_backup_retention_days` | `30` | Backup retention period |

### Monitoring and Alerting

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_enable_monitoring` | `false` | Enable X-Pack monitoring |
| `elasticsearch_monitoring_cluster_uuid` | `""` | Monitoring cluster UUID |
| `elasticsearch_watcher_enabled` | `false` | Enable Watcher for alerting |
| `elasticsearch_alerting_enabled` | `false` | Enable alerting features |

### Performance Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_thread_pool_settings` | `{}` | Thread pool configuration |
| `elasticsearch_circuit_breaker_settings` | `{}` | Circuit breaker settings |
| `elasticsearch_cache_settings` | `{}` | Cache configuration |
| `elasticsearch_jvm_options` | `[]` | Additional JVM options |
| `elasticsearch_bootstrap_memory_lock` | `true` | Lock process memory |

### Load Balancer/Proxy

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_behind_proxy` | `false` | Whether ES is behind a proxy |
| `elasticsearch_proxy_settings` | `{}` | Proxy configuration settings |
| `elasticsearch_http_compression` | `true` | Enable HTTP compression |
| `elasticsearch_http_cors_enabled` | `false` | Enable CORS |

### Health Checks and Validation

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_health_check_enabled` | `true` | Enable automated health checks |
| `elasticsearch_health_check_retries` | `30` | Health check retry count |
| `elasticsearch_health_check_delay` | `10` | Delay between health checks |
| `elasticsearch_validate_config` | `true` | Validate configuration |
| `elasticsearch_validate_cluster_health` | `true` | Validate cluster health |

### Upgrade Management

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_rolling_upgrade` | `false` | Enable rolling upgrade mode |
| `elasticsearch_upgrade_validation` | `true` | Validate before upgrade |
| `elasticsearch_backup_before_upgrade` | `true` | Backup before upgrade |
| `elasticsearch_upgrade_timeout` | `600` | Upgrade timeout in seconds |

### LDAP Integration

| Variable | Default | Description |
|----------|---------|-------------|
| `elasticsearch_ldap_url` | `""` | LDAP server URL |
| `elasticsearch_ldap_bind_dn` | `""` | LDAP bind distinguished name |
| `elasticsearch_ldap_bind_password` | `""` | LDAP bind password |
| `elasticsearch_ldap_user_base_dn` | `""` | Base DN for user searches |
| `elasticsearch_ldap_group_base_dn` | `""` | Base DN for group searches |
| `elasticsearch_ldap_admin_group_dn` | `""` | DN of the admin group |
| `elasticsearch_ldap_user_group_dn` | `""` | DN of the user group |

See `defaults/main.yml` for the complete list of configurable variables and their detailed structure.

## Dependencies

This role has no external Ansible Galaxy dependencies, but requires:
- Java (OpenJDK 11+ recommended)
- systemd for service management

## Example Playbooks

### Single Node Deployment

```yaml
---
- name: Deploy Single Node Elasticsearch
  hosts: elasticsearch_servers
  become: true
  roles:
    - role: data_systems/elasticsearch
      vars:
        elasticsearch_cluster_name: "single-node-cluster"
        elasticsearch_node_roles: ["master", "data", "ingest"]
        elasticsearch_heap_size: "4g"
        elasticsearch_environment: "development"
        elasticsearch_health_check_enabled: true
```

### Multi-Node Cluster Deployment

```yaml
---
- name: Deploy Elasticsearch Cluster
  hosts: elasticsearch_cluster
  become: true
  roles:
    - role: data_systems/elasticsearch
      vars:
        elasticsearch_cluster_name: "production-cluster"
        elasticsearch_heap_size: "8g"
        elasticsearch_environment: "production"
        elasticsearch_bootstrap_memory_lock: true

- name: Configure Master Nodes
  hosts: elasticsearch_master
  become: true
  vars:
    elasticsearch_node_roles: ["master"]

- name: Configure Data Nodes
  hosts: elasticsearch_data
  become: true
  vars:
    elasticsearch_node_roles: ["data", "ingest"]
    elasticsearch_data_paths:
      - "/data1/elasticsearch"
      - "/data2/elasticsearch"
```

### Production Cluster with Full Features

```yaml
---
- name: Deploy Production Elasticsearch with All Features
  hosts: elasticsearch_cluster
  become: true
  roles:
    - role: data_systems/elasticsearch
      vars:
        elasticsearch_cluster_name: "production-cluster"
        elasticsearch_environment: "production"
        elasticsearch_heap_size: "16g"
        
        # Security
        elasticsearch_enable_security: true
        elasticsearch_tls_provided: true
        elasticsearch_audit_enabled: true
        
        # Storage
        elasticsearch_data_paths:
          - "/data1/elasticsearch"
          - "/data2/elasticsearch"
        elasticsearch_path_repo:
          - "/backup/elasticsearch"
        
        # Plugins
        elasticsearch_plugins:
          - name: "repository-s3"
          - name: "analysis-icu"
          - name: "mapper-murmur3"
        
        # Monitoring
        elasticsearch_enable_monitoring: true
        elasticsearch_watcher_enabled: true
        
        # Snapshots
        elasticsearch_snapshot_repositories:
          - name: "backup-repo"
            type: "fs"
            settings:
              location: "/backup/elasticsearch"
        
        elasticsearch_snapshot_policies:
          - name: "daily-backup"
            schedule: "0 2 * * *"
            repository: "backup-repo"
            config:
              retention:
                expire_after: "30d"
        
        # Performance
        elasticsearch_jvm_options:
          - "-XX:+UseG1GC"
          - "-XX:MaxGCPauseMillis=200"
        
        # Index Templates
        elasticsearch_index_templates:
          - name: "logs-template"
            index_patterns: ["logs-*"]
            settings:
              number_of_shards: 1
              number_of_replicas: 1
            mappings:
              properties:
                timestamp:
                  type: date
                message:
                  type: text
                  analyzer: standard
```

### Secure Cluster with LDAP

```yaml
---
- name: Deploy Secure Elasticsearch with LDAP
  hosts: elasticsearch_cluster
  become: true
  roles:
    - role: data_systems/elasticsearch
      vars:
        elasticsearch_cluster_name: "secure-cluster"
        elasticsearch_enable_security: true
        elasticsearch_tls_provided: true
        elasticsearch_audit_enabled: true
        
        # LDAP Configuration
        elasticsearch_ldap_url: "ldap://ldap.company.com:389"
        elasticsearch_ldap_bind_dn: "cn=elasticsearch,ou=services,dc=company,dc=com"
        elasticsearch_ldap_bind_password: "{{ vault_ldap_password }}"
        elasticsearch_ldap_user_base_dn: "ou=users,dc=company,dc=com"
        elasticsearch_ldap_group_base_dn: "ou=groups,dc=company,dc=com"
        elasticsearch_ldap_admin_group_dn: "cn=elasticsearch-admins,ou=groups,dc=company,dc=com"
        elasticsearch_ldap_user_group_dn: "cn=elasticsearch-users,ou=groups,dc=company,dc=com"
        
        # Advanced Security
        elasticsearch_api_key_enabled: true
        elasticsearch_field_level_security: true
        elasticsearch_audit_settings:
          enabled: true
          outputs: ["logfile"]
          logfile:
            events:
              include: ["access_denied", "access_granted", "authentication_failed"]
```

### Development Environment

```yaml
---
- name: Deploy Development Elasticsearch
  hosts: elasticsearch_dev
  become: true
  roles:
    - role: data_systems/elasticsearch
      vars:
        elasticsearch_cluster_name: "dev-cluster"
        elasticsearch_environment: "development"
        elasticsearch_heap_size: "2g"
        elasticsearch_validate_cluster_health: false
        elasticsearch_plugins:
          - name: "analysis-icu"
        elasticsearch_custom_analyzers:
          my_analyzer:
            tokenizer: "standard"
            filter: ["lowercase", "stop"]
```

### Monitoring and Alerting Setup

```yaml
---
- name: Deploy Elasticsearch with Monitoring
  hosts: elasticsearch_cluster
  become: true
  roles:
    - role: data_systems/elasticsearch
      vars:
        elasticsearch_cluster_name: "monitored-cluster"
        
        # Monitoring
        elasticsearch_enable_monitoring: true
        elasticsearch_monitoring_collection_enabled: true
        elasticsearch_watcher_enabled: true
        
        # Health Checks
        elasticsearch_health_check_enabled: true
        elasticsearch_health_check_retries: 30
        elasticsearch_health_check_delay: 5
        
        # Performance Monitoring
        elasticsearch_thread_pool_settings:
          search:
            size: 16
            queue_size: 1000
          write:
            size: 8
            queue_size: 10000
```

### Inventory Example

```ini
[elasticsearch_cluster]
es-master-01 ansible_host=10.0.1.10
es-master-02 ansible_host=10.0.1.11
es-master-03 ansible_host=10.0.1.12
es-data-01 ansible_host=10.0.1.20
es-data-02 ansible_host=10.0.1.21
es-data-03 ansible_host=10.0.1.22

[elasticsearch_master]
es-master-01
es-master-02
es-master-03

[elasticsearch_data]
es-data-01
es-data-02
es-data-03

[elasticsearch_cluster:vars]
elasticsearch_cluster_name=production-cluster
elasticsearch_environment=production
elasticsearch_heap_size=8g
```

## Tags

This role supports the following tags for selective execution:

- `install`: Execute only installation tasks
- `config`: Execute only configuration tasks  
- `security`: Execute only security-related tasks
- `storage`: Execute only storage configuration tasks
- `performance`: Execute only performance tuning tasks
- `plugins`: Execute only plugin management tasks
- `monitoring`: Execute only monitoring and alerting tasks
- `templates`: Execute only index template management tasks
- `snapshots`: Execute only snapshot and backup tasks
- `health`: Execute only health check tasks
- `validation`: Execute only validation tasks

Example usage:
```bash
# Install and configure Elasticsearch
ansible-playbook playbook.yml --tags "install,config"

# Configure security and monitoring
ansible-playbook playbook.yml --tags "security,monitoring"

# Set up backups and health checks
ansible-playbook playbook.yml --tags "snapshots,health"

# Full deployment
ansible-playbook playbook.yml --tags "all"
```

## Handlers

The role includes the following handlers:

- `update apt cache`: Updates the package cache when repositories are modified
- `restart elasticsearch`: Restarts the Elasticsearch service when configuration changes

## File Structure

```
elasticsearch/
├── defaults/
│   └── main.yml                        # Comprehensive default variables
├── handlers/
│   └── main.yml                        # Service and configuration handlers
├── meta/
│   └── main.yml                        # Role metadata and dependencies
├── molecule/
│   └── default/                        # Molecule test scenarios
├── tasks/
│   ├── main.yml                        # Main task orchestration
│   ├── validation.yml                  # Pre-deployment validation
│   ├── install.yml                     # Installation tasks
│   ├── storage.yml                     # Storage and filesystem configuration
│   ├── config.yml                      # Basic configuration tasks
│   ├── performance.yml                 # Performance tuning tasks
│   ├── plugins.yml                     # Plugin management tasks
│   ├── security.yml                    # Security setup tasks
│   ├── monitoring.yml                  # Monitoring and alerting tasks
│   ├── templates.yml                   # Index template management
│   ├── snapshots.yml                   # Snapshot and backup configuration
│   └── health_checks.yml               # Health validation tasks
├── templates/
│   ├── elasticsearch.list.j2           # APT repository configuration
│   ├── elasticsearch.yml.j2            # Main Elasticsearch configuration
│   ├── elasticsearch-tmpfiles.conf.j2  # Systemd tmpfiles configuration
│   ├── jvm.options.j2                  # JVM heap configuration
│   ├── jvm.options.d/
│   │   └── custom.options.j2            # Custom JVM options
│   ├── monitoring.yml.j2                # Monitoring configuration
│   ├── role_mapping.yml.j2              # LDAP role mapping
│   ├── cleanup-snapshots.sh.j2          # Snapshot cleanup script
│   ├── manual-snapshot.sh.j2            # Manual snapshot script
│   └── health-check.sh.j2               # Health monitoring script
└── README.md                           # This comprehensive documentation
```

## Testing

This role includes Molecule tests for validation:

```bash
# Install molecule and dependencies
pip install molecule molecule-plugins[docker]

# Run tests
cd roles/data_systems/elasticsearch
molecule test
```

The tests validate:
- Package installation
- Service status
- Configuration file deployment
- Basic cluster functionality

## Troubleshooting

### Common Issues

1. **Java Installation**: Ensure Java is installed or set `elasticsearch_install_java: true`
2. **Memory Settings**: Adjust `elasticsearch_heap_size` based on available system memory
3. **Network Binding**: Verify `elasticsearch_network_host` is accessible by other cluster nodes
4. **Security**: When enabling security, ensure certificates are properly deployed

### Logs

Elasticsearch logs are available at:
- `/var/log/elasticsearch/`

Service status:
```bash
systemctl status elasticsearch
journalctl -u elasticsearch -f
```

## License

MIT

## Author Information

This role was created as part of the data systems infrastructure automation project.
