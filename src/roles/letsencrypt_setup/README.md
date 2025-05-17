# Ansible Role: Letsencrypt Setup

Installs and configures Letsencrypt Setup. This role manages installation packages and service configuration required to run Letsencrypt Setup on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - letsencrypt_setup
```
