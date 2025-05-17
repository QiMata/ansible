# Ansible Role: Elasticsearch Snapshot

Installs and configures Elasticsearch Snapshot. This role manages installation packages and service configuration required to run Elasticsearch Snapshot on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - elasticsearch_snapshot
```
