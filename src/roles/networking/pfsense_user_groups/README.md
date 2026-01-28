# pfSense User Groups Role

**Table of Contents**

* [Overview](#overview)
* [Supported Platforms](#supported-platforms)
* [Requirements](#requirements)
* [Role Variables](#role-variables)
* [Example Playbook](#example-playbook)

## Overview

This role manages **local pfSense user groups** using the `pfsensible.core` collection. It is intended for pfSense **2.7+** deployments and enforces group state (present/absent) based on the list you provide.

## Supported Platforms

* pfSense CE 2.7+
* pfSense Plus 23.09+

## Requirements

* Ansible 2.14+
* `pfsensible.core` collection installed (`ansible-galaxy collection install pfsensible.core`)
* pfSense API access configured and reachable from the Ansible control node

## Role Variables

Defaults are defined in `defaults/main.yml`.

| Variable | Default | Description |
| --- | --- | --- |
| `pfsense_user_groups_host` | `"{{ ansible_host }}"` | pfSense API hostname or IP. |
| `pfsense_user_groups_username` | `admin` | pfSense API username. |
| `pfsense_user_groups_password` | `"{{ vault_pfsense_password | default('pfsense') }}"` | pfSense API password. |
| `pfsense_user_groups_scheme` | `https` | API scheme. |
| `pfsense_user_groups_port` | `443` | API port. |
| `pfsense_user_groups_timeout` | `30` | API timeout in seconds. |
| `pfsense_user_groups_validate_certs` | `false` | Validate TLS certs. |
| `pfsense_user_groups_list` | `[]` | List of groups to manage. Each entry supports `name`, `scope`, `description`, `privileges`, `state`. |

### `pfsense_user_groups_list` structure

```yaml
pfsense_user_groups_list:
  - name: "admins"
    scope: "local"
    description: "Administrative users"
    privileges:
      - "page-all"
    state: present
```

Set `state: absent` to remove a group.

## Example Playbook

```yaml
- name: Manage pfSense local user groups
  hosts: pfsense_firewalls
  vars:
    pfsense_user_groups_list:
      - name: "admins"
        description: "Administrative users"
        privileges:
          - "page-all"
        state: present
      - name: "tempgroup"
        state: absent
  roles:
    - role: networking.pfsense_user_groups
```
