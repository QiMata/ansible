# Airflow Webserver Role

This Ansible role installs and configures the Apache Airflow Webserver component for enterprise deployments with UI and API access.

## Features

- Configures Airflow Webserver with enterprise security settings
- Support for load balancing and reverse proxy configurations
- SSL/TLS termination capabilities
- Authentication and authorization (RBAC)
- Health monitoring and automatic restart capabilities
- Systemd service management
- Resource limits and security hardening

## Requirements

- Apache Airflow core installation (handled by apache_airflow role dependency)
- Systemd-based Linux distribution
- Python 3.7+

## Role Variables

### Core Configuration
- `airflow_webserver_user`: User to run the webserver service (default: airflow)
- `airflow_webserver_group`: Group for the webserver service (default: airflow)
- `airflow_webserver_home`: Airflow home directory (default: /opt/airflow)

### Network Settings
- `airflow_webserver_port`: Port for webserver (default: 8080)
- `airflow_webserver_host`: Host interface to bind (default: 0.0.0.0)
- `airflow_webserver_workers`: Number of worker processes (default: 4)
- `airflow_webserver_worker_timeout`: Worker timeout in seconds (default: 120)

### Authentication & Security
- `airflow_webserver_authenticate`: Enable authentication (default: false)
- `airflow_webserver_auth_backend`: Authentication backend
- `airflow_webserver_rbac`: Enable RBAC (default: true)
- `airflow_webserver_secret_key`: Secret key for sessions (CHANGE IN PRODUCTION)
- `airflow_webserver_csrf_enabled`: Enable CSRF protection (default: true)

### SSL/TLS Configuration
- `airflow_webserver_ssl_enabled`: Enable SSL (default: false)
- `airflow_webserver_ssl_cert`: Path to SSL certificate
- `airflow_webserver_ssl_key`: Path to SSL private key

### Load Balancer Support
- `airflow_webserver_enable_proxy_fix`: Enable proxy headers (default: false)
- `airflow_webserver_proxy_fix_x_for`: X-For header count (default: 1)
- `airflow_webserver_proxy_fix_x_proto`: X-Proto header count (default: 1)
- `airflow_webserver_proxy_fix_x_host`: X-Host header count (default: 1)
- `airflow_webserver_proxy_fix_x_port`: X-Port header count (default: 1)

### Service Management
- `airflow_webserver_service_enabled`: Enable webserver service (default: true)
- `airflow_webserver_service_state`: Service state (default: started)
- `airflow_webserver_restart_on_failure`: Auto-restart on failure (default: true)

### Resource Limits
- `airflow_webserver_memory_limit`: Memory limit for service (default: 2G)
- `airflow_webserver_cpu_limit`: CPU limit for service (default: 1000m)

## Dependencies

- `apache_airflow` role (automatically included)

## Example Playbook

### Basic Setup
```yaml
---
- hosts: webserver_nodes
  become: true
  roles:
    - role: airflow_webserver
      vars:
        airflow_webserver_port: 8080
        airflow_webserver_workers: 6
        airflow_webserver_memory_limit: "4G"
```

### SSL-Enabled Setup
```yaml
---
- hosts: webserver_nodes
  become: true
  roles:
    - role: airflow_webserver
      vars:
        airflow_webserver_ssl_enabled: true
        airflow_webserver_ssl_cert: "/path/to/certificate.crt"
        airflow_webserver_ssl_key: "/path/to/private.key"
        airflow_webserver_port: 443
```

### Load Balanced Setup
```yaml
---
- hosts: webserver_nodes
  become: true
  roles:
    - role: airflow_webserver
      vars:
        airflow_webserver_enable_proxy_fix: true
        airflow_webserver_proxy_fix_x_for: 2
        airflow_webserver_proxy_fix_x_proto: 1
        airflow_webserver_workers: 8
```

### LDAP Authentication Setup
```yaml
---
- hosts: webserver_nodes
  become: true
  roles:
    - role: airflow_webserver
      vars:
        airflow_webserver_authenticate: true
        airflow_webserver_auth_backend: "AUTH_LDAP"
        airflow_webserver_rbac: true
        airflow_webserver_secret_key: "{{ vault_airflow_secret_key }}"
```

## High Availability Setup

For HA deployment with multiple webservers behind a load balancer:

```yaml
airflow_webserver_workers: 6
airflow_webserver_enable_proxy_fix: true
airflow_webserver_secret_key: "{{ shared_secret_key }}"  # Same across all instances
```

## Monitoring

The role includes:
- Health check script at `{{ airflow_webserver_home }}/bin/webserver_health_check.sh`
- Automatic health monitoring via cron (every 2 minutes)
- HTTP health endpoint monitoring
- Memory usage monitoring
- Systemd journal logging

## Security Features

- CSRF protection enabled by default
- RBAC support
- SSL/TLS termination
- Service runs as non-root user
- Private temp directories
- Protected system directories
- Resource limits enforced
- No new privileges allowed

## API Access

The webserver provides both UI and REST API access:
- Web UI: `http(s)://server:port/`
- API: `http(s)://server:port/api/v1/`

## License

MIT

## Author

Your Organization
