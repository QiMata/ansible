# Ansible Role: Openldap Replication

Installs and configures Openldap Replication. This role manages installation packages and service configuration required to run Openldap Replication on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - openldap_replication
```
