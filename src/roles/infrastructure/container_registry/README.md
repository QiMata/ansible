# infrastructure.container_registry

Installs a private Docker registry (registry:2) running via Docker. Assumes a Docker host is available (use `infrastructure.docker_host` first). Provides simple, insecure-by-default registry suitable for internal networks or testing. Add TLS/proxy as needed.

## Variables
- registry_name: 'registry'
- registry_image: 'registry:2'
- registry_data_dir: '/var/lib/registry'
- registry_port: 5000
- registry_bind: '0.0.0.0'
- registry_env: {} — additional environment variables for the container

## Example
```yaml
- hosts: registry_vms
  become: true
  roles:
    - infrastructure.docker_host
    - role: infrastructure.container_registry
      vars:
        registry_port: 5000
```
