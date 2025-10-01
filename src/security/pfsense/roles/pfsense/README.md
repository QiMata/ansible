# Ansible Role: pfSense

## Overview

This role manages pfSense firewall configuration using the
[pfsensible.core](https://github.com/pfsensible/core) collection. It assumes a
running pfSense instance with SSH access and Python available. The role can
configure interfaces, gateways, aliases and firewall rules so that pfSense can
be managed as code.

## Supported Platforms

* pfSense CE 2.7+
* pfSense Plus 23.09+

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `pfsense_interfaces` | `[]` | List of interface definitions (name, ip, mask, description) |
| `pfsense_gateways` | `[]` | List of gateway objects (name, interface, gateway, description) |
| `pfsense_default_gateway` | `''` | Name of the gateway to set as default |
| `pfsense_aliases` | `[]` | List of alias objects to create |
| `pfsense_rules` | `[]` | List of firewall rule dictionaries |
| `pfsense_enable_ssh` | `true` | Whether to enable SSH on pfSense |

## Example Playbook

```yaml
- hosts: pfsense_firewalls
  gather_facts: false
  roles:
    - role: pfsense
      vars:
        pfsense_interfaces:
          - name: LAN
            ip: 10.0.0.1
            mask: 24
        pfsense_aliases:
          - name: WEB_SERVERS
            type: host
            addresses:
              - 10.0.0.10
              - 10.0.0.11
        pfsense_rules:
          - interface: LAN
            action: pass
            protocol: tcp
            source: any
            destination: alias:WEB_SERVERS
            destination_port: 443
            description: Allow HTTPS to web servers
```

This role requires the `pfsensible.core` collection which is included in the
repository `requirements.yml` files. SSH keys or passwords should be managed with
Ansible Vault.
