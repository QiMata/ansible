# Ansible Role: Mariadb Backups

Installs and configures Mariadb Backups. This role manages installation packages and service configuration required to run Mariadb Backups on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - mariadb_backups
```
