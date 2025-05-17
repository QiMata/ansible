# Ansible Role: Haproxy

Installs and configures Haproxy. This role manages installation packages and service configuration required to run Haproxy on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - haproxy
```
