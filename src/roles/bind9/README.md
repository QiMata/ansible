# Ansible Role: Bind9

Installs and configures Bind9. This role manages installation packages and service configuration required to run Bind9 on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - bind9
```
