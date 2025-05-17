# Ansible Role: Sshd

Installs and configures Sshd. This role manages installation packages and service configuration required to run Sshd on a host.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Example Playbook

```yaml
- hosts: all
  roles:
    - sshd
```
