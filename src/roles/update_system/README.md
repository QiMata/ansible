# Ansible Role: Update System

Installs and configures Update System. This role manages installation packages and service configuration required to run Update System on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - update_system
```
