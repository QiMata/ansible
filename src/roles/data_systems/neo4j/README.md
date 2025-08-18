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

### Security & TLS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `neo4j_tls_client_enable` | `true` | Enable TLS for client connections |
| `neo4j_tls_cluster_enable` | `{{ neo4j_cluster_enabled }}` | Enable TLS for cluster communication |
| `neo4j_certificates_source` | `self-signed` | Certificate source (`self-signed`, `custom`, `letsencrypt`) |
| `neo4j_initial_password` | `""` | Initial password for `neo4j` user |
| `neo4j_user_creation` | `[]` | List of additional users to create |

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

### High-Performance Production Setup

```yaml
---
- name: Deploy Neo4j Production Instance
  hosts: neo4j_production
  become: true
  roles:
    - role: data_systems/neo4j
      vars:
        neo4j_edition: enterprise
        neo4j_heap_size: "16G"
        neo4j_pagecache_size: "32G"
        neo4j_backup_enabled: true
        neo4j_backup_cron_enabled: true
        neo4j_backup_retention: 30
        neo4j_elk_integration: true
        neo4j_elk_host: "{{ elk_server }}"
        neo4j_metrics_enabled: true
        neo4j_logrotate_frequency: daily
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

```bash
# Test with Docker
molecule test

# Test with Podman
molecule test -s podman

# Test specific scenarios
molecule converge
molecule verify
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
