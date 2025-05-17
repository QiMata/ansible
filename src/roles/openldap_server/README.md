# Ansible Role: Openldap Server

Installs and configures Openldap Server. This role manages installation packages and service configuration required to run Openldap Server on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - openldap_server
```
