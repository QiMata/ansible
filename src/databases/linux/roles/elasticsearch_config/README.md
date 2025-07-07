# Ansible Role: Elasticsearch Config

Installs and configures Elasticsearch Config. This role manages installation packages and service configuration required to run Elasticsearch Config on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - elasticsearch_config
```
