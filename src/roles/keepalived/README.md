# Ansible Role: Keepalived

Installs and configures Keepalived. This role manages installation packages and service configuration required to run Keepalived on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - keepalived
```
