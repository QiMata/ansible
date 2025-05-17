# Ansible Role: Prometheus

Installs and configures Prometheus. This role manages installation packages and service configuration required to run Prometheus on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - prometheus
```
