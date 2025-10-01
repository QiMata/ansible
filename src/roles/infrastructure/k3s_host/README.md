# infrastructure.k3s_host

Installs a single-node K3s server on a Linux VM. This role focuses on installation only; no cluster joining or advanced config.

## Variables
- k3s_version: '' — optional explicit version (e.g. v1.29.5+k3s1)
- k3s_agent: false — set true to install agent instead of server
- k3s_server_args: '' — extra args for k3s server service
- k3s_agent_args: '' — extra args for k3s agent service

## Example
```yaml
- hosts: k3s_vms
  become: true
  roles:
    - role: infrastructure.k3s_host
      vars:
        k3s_version: 'v1.29.5+k3s1'
        k3s_server_args: '--disable traefik'
```
