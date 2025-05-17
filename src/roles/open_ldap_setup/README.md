# Ansible Role: Open Ldap Setup

Installs and configures Open Ldap Setup. This role manages installation packages and service configuration required to run Open Ldap Setup on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - open_ldap_setup
```
