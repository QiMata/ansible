# Ansible Role: Grafana

Installs and configures Grafana. This role manages installation packages and service configuration required to run Grafana on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - grafana
```
