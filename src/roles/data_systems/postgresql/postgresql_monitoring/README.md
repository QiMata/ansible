# PostgreSQL Monitoring Extension

This role provides comprehensive monitoring and observability for PostgreSQL databases. It extends the base PostgreSQL role with monitoring capabilities including Prometheus metrics, health checks, and performance monitoring.

## Features

- **Prometheus Integration**: Installs and configures postgres_exporter for metrics collection
- **Health Checks**: Automated health monitoring with configurable thresholds
- **Performance Monitoring**: Slow query logging and pg_stat_statements integration
- **Replication Monitoring**: Tracks replication lag and slot status (when replication is enabled)
- **Custom Metrics**: Configurable custom queries for application-specific monitoring

## Usage

Include this role after the base PostgreSQL role:

```yaml
- hosts: postgresql_servers
  roles:
    - data_systems.postgresql
    - data_systems.postgresql.postgresql_monitoring
```

## Configuration

Key variables (see defaults/main.yml for complete list):

```yaml
postgresql_monitoring_enabled: true
postgresql_exporter_port: 9187
postgresql_health_check_enabled: true
postgresql_slow_query_log_enabled: true
```

## Monitoring Endpoints

- Prometheus metrics: `http://server:9187/metrics`
- Health check logs: `/var/log/postgresql_health_check.log`
- Replication check logs: `/var/log/postgresql_replication_check.log`

## Dependencies

- Base PostgreSQL role
- Prometheus server (for metrics collection)
- community.postgresql collection
