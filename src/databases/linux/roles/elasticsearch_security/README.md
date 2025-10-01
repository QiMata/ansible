# Ansible Role: Elasticsearch Security

Installs and configures Elasticsearch Security. This role manages installation packages and service configuration required to run Elasticsearch Security on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - elasticsearch_security
```
