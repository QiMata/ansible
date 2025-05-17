# Ansible Role: Jenkins Agent

Installs and configures Jenkins Agent. This role manages installation packages and service configuration required to run Jenkins Agent on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - jenkins_agent
```
