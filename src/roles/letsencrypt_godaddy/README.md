# Ansible Role: Letsencrypt Godaddy

Installs and configures Letsencrypt Godaddy. This role manages installation packages and service configuration required to run Letsencrypt Godaddy on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - letsencrypt_godaddy
```
