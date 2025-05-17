# Ansible Role: Jenkins Controller

Installs and configures Jenkins Controller. This role manages installation packages and service configuration required to run Jenkins Controller on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - jenkins_controller
```
