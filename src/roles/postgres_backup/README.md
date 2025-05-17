# Ansible Role: Postgres Backup

Installs and configures Postgres Backup. This role manages installation packages and service configuration required to run Postgres Backup on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - postgres_backup
```
