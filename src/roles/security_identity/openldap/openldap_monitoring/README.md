# OpenLDAP Performance Monitoring Role

This role implements comprehensive monitoring for OpenLDAP servers, including Prometheus metrics, Grafana dashboards, health checks, and capacity planning.

## Features

- **Prometheus Integration**: Detailed LDAP metrics collection
- **Grafana Dashboards**: Pre-built visualizations for LDAP performance
- **Health Checks**: Comprehensive health monitoring
- **Capacity Planning**: Disk usage, memory, and performance trend analysis
- **Alerting**: Configurable alerts for critical conditions
- **Query Performance**: Slow query monitoring and optimization

## Requirements

- Prometheus server
- Grafana server (optional)
- Node Exporter for system metrics
- OpenLDAP server with monitoring enabled

## Role Variables

### Basic Monitoring
```yaml
openldap_monitoring_enabled: true
openldap_monitoring_prometheus: true
openldap_monitoring_grafana: true
openldap_monitoring_interval: 30  # seconds
```

### Prometheus Configuration
```yaml
openldap_prometheus_port: 9330
openldap_prometheus_endpoint: "/metrics"
openldap_prometheus_job_name: "openldap"
```

### Health Checks
```yaml
openldap_health_checks_enabled: true
openldap_health_check_interval: 60  # seconds
openldap_health_check_timeout: 10   # seconds
```

### Alerting
```yaml
openldap_alerting_enabled: true
openldap_alert_email: "admin@example.com"
openldap_alert_high_cpu: 80      # percentage
openldap_alert_high_memory: 85   # percentage
openldap_alert_disk_usage: 90    # percentage
```

## Dependencies

- `prometheus`
- `grafana` (optional)
- `openldap_server`

## Example Playbook

```yaml
- hosts: ldap_servers
  roles:
    - role: openldap_monitoring
      openldap_monitoring_prometheus: true
      openldap_alerting_enabled: true
      openldap_alert_email: "ldap-admin@company.com"
```

## Testing

Use Molecule for testing:

```bash
cd roles/security_identity/openldap/openldap_monitoring
molecule test
```
