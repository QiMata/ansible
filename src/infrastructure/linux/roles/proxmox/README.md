# Ansible Role: proxmox

This role installs and configures **Proxmox VE** on Debian-based hosts. It adds the Proxmox APT repository, installs the `proxmox-ve` package group, and optionally creates or joins a Proxmox cluster.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `proxmox_repo_release` | `bookworm` | Debian release for the repo |
| `proxmox_repo_url` | `http://download.proxmox.com/debian/pve` | Repository base URL |
| `proxmox_repo_key_url` | `https://download.proxmox.com/debian/proxmox-release-{{ proxmox_repo_release }}.gpg` | Repository GPG key |
| `proxmox_packages` | `[proxmox-ve, open-iscsi]` | Packages to install |
| `proxmox_cluster_enabled` | `false` | Whether to configure clustering |
| `proxmox_cluster_master` | `false` | Set to true on the first node |
| `proxmox_cluster_name` | `pve-cluster` | Cluster name when creating |
| `proxmox_cluster_address` | _undefined_ | IP of existing cluster to join |

## Example Playbook

```yaml
- hosts: proxmox
  become: true
  vars:
    proxmox_cluster_enabled: true
    proxmox_cluster_master: true
  roles:
    - proxmox
```

When `proxmox_cluster_enabled` is true, the first node (with `proxmox_cluster_master: true`) will run `pvecm create` to create the cluster. Additional nodes should set `proxmox_cluster_master: false` and provide `proxmox_cluster_address` of an existing member to join.
