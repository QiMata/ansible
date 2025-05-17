# Ansible Role: Minio

Installs and configures Minio. This role manages installation packages and service configuration required to run Minio on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - minio
```
