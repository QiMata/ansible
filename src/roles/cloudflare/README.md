# Ansible Role: Cloudflare

Installs and configures Cloudflare. This role manages installation packages and service configuration required to run Cloudflare on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - cloudflare
```
