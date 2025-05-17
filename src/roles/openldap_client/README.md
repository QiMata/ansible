# Ansible Role: Openldap Client

Installs and configures Openldap Client. This role manages installation packages and service configuration required to run Openldap Client on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - openldap_client
```
