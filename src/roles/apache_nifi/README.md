# Ansible Role: Apache Nifi

Installs and configures Apache Nifi. This role manages installation packages and service configuration required to run Apache Nifi on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - apache_nifi
```
