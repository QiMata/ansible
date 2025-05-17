# Ansible Role: Neo4j Server

Installs and configures Neo4j Server. This role manages installation packages and service configuration required to run Neo4j Server on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - neo4j_server
```
