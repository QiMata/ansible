# Ansible Role: Filebeat

[![CI](https://github.com/your-org/ansible-role-filebeat/workflows/CI/badge.svg)](https://github.com/your-org/ansible-role-filebeat/actions?query=workflow%3ACI)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-monitoring_observability.filebeat-blue.svg)](https://galaxy.ansible.com/monitoring_observability/filebeat)

An Ansible role that installs and configures [Filebeat](https://www.elastic.co/beats/filebeat), a lightweight shipper for forwarding and centralizing log data. This role manages the complete lifecycle of Filebeat including installation, configuration, and service management.

## Features

### Core Functionality
- 📦 **Automated Installation**: Installs Filebeat from official repositories (Debian/Ubuntu, RHEL/CentOS)
- ⚙️ **Flexible Configuration**: Comprehensive template-based configuration with 100+ variables
- 🔄 **Service Management**: Advanced service lifecycle management with health checks
- 🧪 **Extensive Testing**: Comprehensive Molecule testing with multiple scenarios

### Input & Output Flexibility
- 📊 **Multi-Input Support**: Log files, journald, Docker containers, and custom inputs
- 🎯 **Multiple Output Types**: Logstash, Elasticsearch, Kafka, File, and Console outputs
- 🔀 **Smart Processing**: Built-in processors for parsing, filtering, and enriching logs
- 🏷️ **Advanced Field Enrichment**: Global and input-specific tagging and metadata

### Security & Authentication
- 🔒 **SSL/TLS Support**: Complete SSL configuration with certificate management
- 🔑 **Multiple Authentication**: API keys, username/password, and certificate-based auth
- �️ **Security Hardening**: Configurable verification modes and cipher suites
- 📋 **Compliance Ready**: Security-focused configurations for audit requirements

### Performance & Scalability
- ⚡ **Performance Tuning**: Configurable buffers, queues, and resource limits
- 📈 **High-Volume Support**: Optimized settings for enterprise-scale log processing
- 🔄 **Load Balancing**: Multi-host output configuration with failover
- 💾 **Memory Management**: Advanced queue and harvester buffer configuration

### Operational Excellence
- 🔍 **Health Monitoring**: Built-in health checks and connectivity testing
- 📊 **Metrics Collection**: HTTP endpoint for monitoring and metrics collection
- 💾 **Configuration Backup**: Automatic backup and rollback capabilities
- 🔧 **Module Support**: Native Filebeat modules (Nginx, Apache, System, etc.)

### Monitoring & Observability
- 📈 **Self-Monitoring**: Integration with Elasticsearch monitoring cluster
- 🚨 **Alerting Ready**: Monitoring scripts and cron job integration
- 📋 **Operational Dashboards**: HTTP endpoints for status and metrics
- 🔍 **Troubleshooting**: Comprehensive logging and diagnostic capabilities

## Requirements

- **Operating System**: Debian/Ubuntu (APT-based) or RHEL/CentOS/Rocky/AlmaLinux (YUM-based)
- **Ansible**: >= 2.9
- **Python**: >= 3.6
- **Privileges**: Root or sudo access for package installation and service management
- **Collections**: `ansible.posix`, `community.general`

## Role Variables

### Essential Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `filebeat_inputs` | See defaults | List of input configurations |
| `filebeat_output_type` | `logstash` | Output type (logstash, elasticsearch, kafka, file, console) |
| `filebeat_environment` | `production` | Environment identifier for log field enrichment |

### Input Configuration

```yaml
filebeat_inputs:
  - type: log
    id: app-logs
    enabled: true
    paths:
      - /var/log/app/*.log
    fields:
      service: webapp
      log_type: application
    multiline:
      pattern: '^\d{4}-\d{2}-\d{2}'
      negate: true
      match: after
```

### Output Configuration

#### Logstash Output

> **Tip:** Deploy the server-side Beats intake with the `data_systems/logstash` role in this repository. Combine it with `data_systems/elasticsearch` and `data_systems/kibana` to deliver an end-to-end Elastic stack.
```yaml
filebeat_output_type: logstash
filebeat_logstash_hosts:
  - "logstash1.example.com:5044"
  - "logstash2.example.com:5044"
```

#### Elasticsearch Output
```yaml
filebeat_output_type: elasticsearch
filebeat_elasticsearch_hosts:
  - "https://es1.example.com:9200"
filebeat_elasticsearch_username: "filebeat_writer"
filebeat_elasticsearch_password: "{{ vault_password }}"
```

### Security Configuration

```yaml
# SSL/TLS Configuration
filebeat_ssl_enabled: true
filebeat_ssl_certificate: "/path/to/cert.crt"
filebeat_ssl_key: "/path/to/cert.key"
filebeat_ssl_verification_mode: "full"

# API Key Authentication
filebeat_api_key_enabled: true
filebeat_api_key_id: "{{ vault_api_key_id }}"
filebeat_api_key_value: "{{ vault_api_key_value }}"
```

### Advanced Features

```yaml
# Module Configuration
filebeat_modules_enabled:
  - name: nginx
    config:
      access:
        enabled: true
        var:
          paths: ["/var/log/nginx/access.log*"]

# Global Processors
filebeat_global_processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~

# Performance Tuning
filebeat_queue_mem_events: 4096
filebeat_harvester_buffer_size: 16384

# Monitoring
filebeat_monitoring_enabled: true
filebeat_http_enabled: true
filebeat_health_check_enabled: true
```

For a complete list of all variables and detailed configuration examples, see [CONFIGURATION.md](CONFIGURATION.md).

## Dependencies

None.

## Example Playbook

### Basic Usage

```yaml
---
- name: Deploy Filebeat for log shipping
  hosts: web_servers
  become: yes
  roles:
    - monitoring_observability.filebeat
```

### Advanced Usage with Custom Configuration

```yaml
---
- name: Deploy Filebeat with custom configuration
  hosts: application_servers
  become: yes
  vars:
    # Custom environment override
    ansible_facts:
      env: staging
  roles:
    - monitoring_observability.filebeat
  tags:
    - monitoring
    - logging
```

### Multi-Environment Deployment

```yaml
---
- name: Deploy Filebeat across environments
  hosts: all
  become: yes
  roles:
    - role: monitoring_observability.filebeat
      when: "'logging' in group_names"
```

## Configuration Details

### Default Filebeat Configuration

The role deploys a Filebeat configuration that:

1. **Monitors NetBox logs** at `/var/log/netbox/netbox.log`
2. **Enriches logs** with service and environment metadata
3. **Ships to Logstash** for further processing
4. **Handles service lifecycle** (enable, start, restart on config changes)

### Handler Configuration

The role includes a restart handler that:
- Triggers when the Filebeat configuration changes
- Ensures service continuity during updates
- Validates configuration before restart

## Testing

This role includes comprehensive testing with [Molecule](https://molecule.readthedocs.io/):

### Available Test Scenarios

- **default**: Docker-based testing with Debian 12
- **podman**: Podman-based testing for containerized environments
- **elasticsearch**: Tests Elasticsearch output configuration
- **ssl**: Tests SSL/TLS security features

### Running Tests

```bash
# Test with Docker (default)
molecule test

# Test with Podman
molecule test -s podman

# Test specific steps
molecule converge
molecule verify
```

### Test Matrix

| Platform | Container Runtime | Ansible Version | Status |
|----------|-------------------|-----------------|--------|
| Debian 12 | Docker | Latest | ✅ Supported |
| Debian 12 | Podman | Latest | ✅ Supported |

## File Structure

```
roles/monitoring_observability/filebeat/
├── README.md                    # This documentation
├── CONFIGURATION.md             # Comprehensive configuration guide
├── defaults/
│   └── main.yml                # Default variables and configuration
├── vars/
│   ├── Debian.yml              # Debian/Ubuntu specific variables
│   └── RedHat.yml              # RHEL/CentOS specific variables
├── meta/
│   └── main.yml                # Role metadata and dependencies
├── tasks/
│   ├── main.yml                # Main task orchestration
│   ├── validate.yml            # Configuration validation
│   ├── repo.yml                # Repository setup
│   ├── install.yml             # Package installation
│   ├── backup.yml              # Configuration backup
│   ├── config.yml              # Configuration deployment
│   ├── modules.yml             # Module management
│   ├── service.yml             # Service management
│   ├── health.yml              # Health checks
│   └── monitoring.yml          # Monitoring setup
├── templates/
│   ├── filebeat.yml.j2         # Main Filebeat configuration
│   ├── monitoring.yml.j2       # Monitoring configuration
│   ├── filebeat_monitor.sh.j2  # Monitoring script
│   ├── module_nginx.yml.j2     # Nginx module template
│   └── module_apache.yml.j2    # Apache module template
├── handlers/
│   └── main.yml                # Service restart handlers
├── files/
├── examples/
│   ├── basic-deployment.yml    # Basic usage example
│   ├── advanced-deployment.yml # Advanced features example
│   ├── multi-environment.yml   # Multi-environment setup
│   └── security-deployment.yml # Security-focused example
└── molecule/
    ├── default/                # Docker-based tests
    │   ├── molecule.yml
    │   └── tests/
    │       └── test_filebeat.py
    ├── podman/                 # Podman-based tests
    │   ├── molecule.yml
    │   └── tests/
    │       └── test_filebeat.py
    ├── elasticsearch/          # Elasticsearch output tests
    │   ├── molecule.yml
    │   └── tests/
    │       └── test_elasticsearch.py
    └── ssl/                    # SSL/TLS security tests
        ├── molecule.yml
        └── tests/
            └── test_ssl.py
```

## Security Considerations

- **File Permissions**: Configuration file is set to `0644` (readable by all, writable by owner)
- **Service User**: Filebeat runs under its default service user
- **Network Access**: Ensure Logstash endpoints managed by the `data_systems/logstash` role are accessible and secured
- **Log Permissions**: Verify Filebeat has read access to monitored log files

## Troubleshooting

### Common Issues

1. **Service fails to start**
   ```bash
   # Check service status
   sudo systemctl status filebeat
   
   # Check configuration syntax
   sudo filebeat test config
   ```

2. **Logs not shipping**
   ```bash
   # Verify connectivity to Logstash
   telnet logstash.example.com 5044
   
   # Check Filebeat logs
   sudo journalctl -u filebeat -f
   ```

3. **Permission issues**
   ```bash
   # Verify log file permissions
   ls -la /var/log/netbox/netbox.log
   
   # Check Filebeat user permissions
   sudo -u filebeat cat /var/log/netbox/netbox.log
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add or update tests as needed
5. Run the test suite (`molecule test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Author Information

This role was created as part of a comprehensive monitoring and observability infrastructure suite.

**Maintainer**: Infrastructure Team  
**Contact**: infrastructure@example.com  
**Documentation**: [Internal Wiki](https://wiki.example.com/ansible/filebeat)

## Changelog

### [Unreleased]
- ✅ **Configuration Flexibility**: Added comprehensive defaults with 100+ configurable variables
- ✅ **Multi-Input Support**: Support for log, journald, docker, and custom input types
- ✅ **Multiple Output Types**: Logstash, Elasticsearch, Kafka, File, and Console outputs
- ✅ **Security Features**: SSL/TLS configuration and API key authentication
- ✅ **Processing Capabilities**: Global and input-specific processors for log enrichment
- ✅ **Module Support**: Native Filebeat modules (Nginx, Apache, System, etc.)
- ✅ **Operational Features**: Configuration backup, validation, and health checks
- ✅ **Performance Tuning**: Configurable buffers, queues, and resource limits
- ✅ **Cross-Platform Support**: Added RHEL/CentOS/Rocky/AlmaLinux support
- ✅ **Monitoring Integration**: HTTP endpoints and self-monitoring capabilities
- ✅ **Enhanced Testing**: Additional test scenarios for Elasticsearch and SSL
- ✅ **Documentation**: Comprehensive configuration guide and examples

### [1.0.0] - Initial Release
- Basic Filebeat installation and configuration
- Logstash output configuration
- Service management
- Molecule testing framework
