# Ansible Role: Filebeat

[![CI](https://github.com/your-org/ansible-role-filebeat/workflows/CI/badge.svg)](https://github.com/your-org/ansible-role-filebeat/actions?query=workflow%3ACI)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-monitoring_observability.filebeat-blue.svg)](https://galaxy.ansible.com/monitoring_observability/filebeat)

An Ansible role that installs and configures [Filebeat](https://www.elastic.co/beats/filebeat), a lightweight shipper for forwarding and centralizing log data. This role manages the complete lifecycle of Filebeat including installation, configuration, and service management.

## Features

- 📦 **Automated Installation**: Installs Filebeat from official repositories
- ⚙️ **Flexible Configuration**: Template-based configuration management
- 🔄 **Service Management**: Ensures Filebeat is enabled and running
- 🧪 **Molecule Testing**: Comprehensive testing with Docker and Podman
- 📊 **Log Shipping**: Pre-configured for Logstash output
- 🏷️ **Field Enrichment**: Automatic service and environment tagging

## Requirements

- **Operating System**: Debian/Ubuntu (APT-based systems)
- **Ansible**: >= 2.9
- **Python**: >= 3.6
- **Privileges**: Root or sudo access for package installation and service management

## Role Variables

### Default Variables

Currently, this role uses a minimal configuration approach with hardcoded values in the template. The following variables are implicitly used:

| Variable | Default | Description |
|----------|---------|-------------|
| `ansible_facts.env` | `production` | Environment identifier for log field enrichment |

### Template Variables

The Filebeat configuration template (`templates/filebeat.yml.j2`) includes:

- **Input Configuration**: Monitors `/var/log/netbox/netbox.log` by default
- **Output Configuration**: Ships logs to Logstash at `logstash.example.com:5044`
- **Field Enrichment**: Adds `service: netbox` and environment fields

### Customizable Variables (Recommended Enhancement)

For better flexibility, consider implementing these variables in `defaults/main.yml`:

```yaml
filebeat_inputs:
  - type: log
    paths:
      - /var/log/netbox/netbox.log
    fields:
      service: netbox

filebeat_output:
  logstash:
    hosts: ["logstash.example.com:5044"]

filebeat_environment: "{{ ansible_facts.env | default('production') }}"
```

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
├── tasks/
│   └── main.yml                # Main task definitions
├── templates/
│   └── filebeat.yml.j2         # Filebeat configuration template
├── handlers/
│   └── main.yml                # Service restart handlers
└── molecule/
    ├── default/                # Docker-based tests
    │   └── molecule.yml
    └── podman/                 # Podman-based tests
        └── molecule.yml
```

## Security Considerations

- **File Permissions**: Configuration file is set to `0644` (readable by all, writable by owner)
- **Service User**: Filebeat runs under its default service user
- **Network Access**: Ensure Logstash endpoint is accessible and secured
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
- Enhanced README documentation
- Added comprehensive testing examples
- Improved troubleshooting guide

### [1.0.0] - Initial Release
- Basic Filebeat installation and configuration
- Logstash output configuration
- Service management
- Molecule testing framework
