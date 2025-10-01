# pfSense Role

## Overview

The **pfsense** role provides a simple framework for managing pfSense firewall
configuration via Ansible. It uses modules from the `pfsensible.core` collection
to configure interfaces, gateways, aliases and firewall rules. The role assumes
pfSense is already installed and reachable over SSH.

## Supported Platforms

- pfSense CE 2.7+
- pfSense Plus 23.09+

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `pfsense_interfaces` | `[]` | List of interface mappings (name, ip, mask, description) |
| `pfsense_gateways` | `[]` | List of gateway definitions |
| `pfsense_default_gateway` | `''` | Name of the default gateway to set |
| `pfsense_aliases` | `[]` | Firewall alias entries |
| `pfsense_rules` | `[]` | Firewall rule definitions |
| `pfsense_enable_ssh` | `true` | Enable SSH access on pfSense |

## Example Playbook

```yaml
- hosts: pfsense_firewalls
  gather_facts: false
  roles:
    - pfsense
```

Firewall rules and other settings should be provided via variables as shown in
the role README. Secrets like admin passwords should be stored with **Ansible
Vault**.
