# infrastructure.docker_host

Installs and configures Docker Engine on a Linux VM (Debian/Ubuntu family by default), enables and starts the service, and optionally adds users to the `docker` group.

## Variables
- docker_users: [] — list of usernames to add to docker group
- docker_packages: ['docker-ce', 'docker-ce-cli', 'containerd.io'] — override per distro if needed

## Example
```yaml
- hosts: docker_vms
  become: true
  roles:
    - role: infrastructure.docker_host
      vars:
        docker_users: ['ubuntu']
```
