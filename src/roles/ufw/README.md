# Ansible Role: Ufw

Installs and configures Ufw. This role manages installation packages and service configuration required to run Ufw on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - ufw
```
