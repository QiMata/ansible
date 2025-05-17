# Ansible Role: Openldap Content

Installs and configures Openldap Content. This role manages installation packages and service configuration required to run Openldap Content on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - openldap_content
```
