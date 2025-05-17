# Ansible Role: Openldap Backup

Installs and configures Openldap Backup. This role manages installation packages and service configuration required to run Openldap Backup on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - openldap_backup
```
