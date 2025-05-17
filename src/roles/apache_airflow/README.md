# Ansible Role: Apache Airflow

Installs and configures Apache Airflow. This role manages installation packages and service configuration required to run Apache Airflow on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - apache_airflow
```
