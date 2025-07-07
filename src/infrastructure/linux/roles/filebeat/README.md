# Ansible Role: Filebeat

Installs and configures Filebeat. This role manages installation packages and service configuration required to run Filebeat on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - filebeat
```
