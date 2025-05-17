# Ansible Role: Glusterfs Setup

Installs and configures Glusterfs Setup. This role manages installation packages and service configuration required to run Glusterfs Setup on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - glusterfs_setup
```
