# Ansible Role: Neo4j

This role installs and configures the Neo4j graph database. It supersedes the former `neo4j_server` role and supports single-node or clustered deployments on Debian-based systems.

## Role Variables
See `defaults/main.yml` for the full list of variables controlling installation, clustering, security, backups and monitoring.

## Example Playbook
```yaml
- hosts: neo4j
  roles:
    - neo4j
```
