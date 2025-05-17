# Ansible Role: Ha Proxy Load Balancer Setup

Installs and configures Ha Proxy Load Balancer Setup. This role manages installation packages and service configuration required to run Ha Proxy Load Balancer Setup on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - ha_proxy_load_balancer_setup
```
