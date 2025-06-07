# Proxmox Role

## Overview

The **proxmox** role installs Proxmox VE and can optionally bootstrap a cluster. It is useful for both small dev environments and larger production setups. The role adds the Proxmox APT repository, installs the `proxmox-ve` package set, and can run `pvecm create` or `pvecm add` based on variables.

## Supported Operating Systems/Platforms

- Debian 11/12
- Ubuntu 20.04/22.04

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `proxmox_repo_release` | `bookworm` | Debian release used for the repo |
| `proxmox_repo_url` | `http://download.proxmox.com/debian/pve` | Repository base URL |
| `proxmox_repo_key_url` | `https://download.proxmox.com/debian/proxmox-release-{{ proxmox_repo_release }}.gpg` | Repository GPG key |
| `proxmox_packages` | `[proxmox-ve, open-iscsi]` | Package list to install |
| `proxmox_cluster_enabled` | `false` | Enable cluster configuration |
| `proxmox_cluster_master` | `false` | Whether this node creates the cluster |
| `proxmox_cluster_name` | `pve-cluster` | Cluster name when creating |
| `proxmox_cluster_address` | _undefined_ | Address of an existing node to join |

## Example Playbook

```yaml
- hosts: proxmox
  become: true
  vars:
    proxmox_cluster_enabled: true
    proxmox_cluster_master: false
    proxmox_cluster_address: 10.0.0.1
  roles:
    - proxmox
```

In the example above, the host joins an existing cluster at `10.0.0.1`. Set `proxmox_cluster_master: true` on the first node to initialize the cluster instead.
