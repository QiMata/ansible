# Ansible Role: Backup Netbox

Installs and configures Backup Netbox. This role manages installation packages and service configuration required to run Backup Netbox on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - backup_netbox
```
