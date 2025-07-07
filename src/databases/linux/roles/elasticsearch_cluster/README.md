# Ansible Role: Elasticsearch Cluster

Installs and configures Elasticsearch Cluster. This role manages installation packages and service configuration required to run Elasticsearch Cluster on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - elasticsearch_cluster
```
