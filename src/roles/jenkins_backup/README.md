# Ansible Role: Jenkins Backup

Installs and configures Jenkins Backup. This role manages installation packages and service configuration required to run Jenkins Backup on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - jenkins_backup
```
