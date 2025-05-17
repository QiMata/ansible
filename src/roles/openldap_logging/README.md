# Ansible Role: Openldap Logging

Installs and configures Openldap Logging. This role manages installation packages and service configuration required to run Openldap Logging on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - openldap_logging
```
