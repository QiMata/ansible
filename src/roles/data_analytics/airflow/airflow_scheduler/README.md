# Airflow Scheduler Role

This Ansible role installs and configures the Apache Airflow Scheduler component for enterprise deployments.

## Features

- Configures Airflow Scheduler with enterprise-grade settings
- Supports multiple scheduler instances for high availability
- Health monitoring and automatic restart capabilities
- Systemd service management
- Resource limits and security hardening
- Comprehensive logging configuration

## Requirements

- Apache Airflow core installation (handled by apache_airflow role dependency)
- Systemd-based Linux distribution
- Python 3.7+

## Role Variables

### Core Configuration
- `airflow_scheduler_user`: User to run the scheduler service (default: airflow)
- `airflow_scheduler_group`: Group for the scheduler service (default: airflow)
- `airflow_scheduler_home`: Airflow home directory (default: /opt/airflow)

### Scheduler Settings
- `airflow_scheduler_instances`: Number of scheduler instances (default: 1)
- `airflow_scheduler_heartrate`: Scheduler heartbeat interval in seconds (default: 5)
- `airflow_scheduler_max_threads`: Maximum threads for scheduler (default: 2)
- `airflow_scheduler_catchup_by_default`: Enable DAG catchup by default (default: false)

### Performance Tuning
- `airflow_scheduler_max_tis_per_query`: Max task instances per query (default: 512)
- `airflow_scheduler_dag_dir_list_interval`: DAG directory scan interval (default: 300)
- `airflow_scheduler_zombie_task_threshold`: Zombie task threshold in seconds (default: 300)

### Service Management
- `airflow_scheduler_service_enabled`: Enable scheduler service (default: true)
- `airflow_scheduler_service_state`: Service state (default: started)
- `airflow_scheduler_restart_on_failure`: Auto-restart on failure (default: true)

### Resource Limits
- `airflow_scheduler_memory_limit`: Memory limit for service (default: 2G)
- `airflow_scheduler_cpu_limit`: CPU limit for service (default: 1000m)

## Dependencies

- `apache_airflow` role (automatically included)

## Example Playbook

```yaml
---
- hosts: scheduler_nodes
  become: true
  roles:
    - role: airflow_scheduler
      vars:
        airflow_scheduler_instances: 2
        airflow_scheduler_max_threads: 4
        airflow_scheduler_memory_limit: "4G"
        airflow_scheduler_heartrate: 3
```

## High Availability Setup

For HA deployment with multiple schedulers (Airflow 2.0+):

```yaml
airflow_scheduler_instances: 2
airflow_scheduler_max_threads: 4
airflow_scheduler_heartrate: 3
```

## Monitoring

The role includes:
- Health check script at `{{ airflow_scheduler_home }}/bin/scheduler_health_check.sh`
- Automatic health monitoring via cron (every 5 minutes)
- Systemd journal logging
- PID file monitoring

## Security

- Service runs as non-root user
- Private temp directories
- Protected system directories
- Resource limits enforced
- No new privileges allowed

## License

MIT

## Author

Your Organization
