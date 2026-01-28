# pfSense Users Role

**Table of Contents**

* [Overview](#overview)
* [Supported Platforms](#supported-platforms)
* [Requirements](#requirements)
* [Role Variables](#role-variables)
* [Example Playbook](#example-playbook)

## Overview

This role manages **local pfSense users** using the `pfsensible.core` collection. It is intended for pfSense **2.7+** deployments and enforces user state (present/absent) based on the desired list you provide.

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
| `pfsense_users_host` | `"{{ ansible_host }}"` | pfSense API hostname or IP. |
| `pfsense_users_username` | `admin` | pfSense API username. |
| `pfsense_users_password` | `"{{ vault_pfsense_password | default('pfsense') }}"` | pfSense API password. |
| `pfsense_users_scheme` | `https` | API scheme. |
| `pfsense_users_port` | `443` | API port. |
| `pfsense_users_timeout` | `30` | API timeout in seconds. |
| `pfsense_users_validate_certs` | `false` | Validate TLS certs. |
| `pfsense_users_list` | `[]` | List of users to manage. Each entry supports `username`, `password`, `full_name`, `email`, `expires`, `disabled`, `scope`, `uid`, `groups`, `privileges`, `state`. |

### `pfsense_users_list` structure

```yaml
pfsense_users_list:
  - username: "netadmin"
    password: "{{ vault_netadmin_password }}"
    full_name: "Network Administrator"
    email: "netadmin@example.com"
    expires: "2025-12-31"
    disabled: false
    scope: "user"
    uid: 2001
    groups:
      - "admins"
    privileges:
      - "page-all"
    state: present
```

Set `state: absent` to remove a user.

## Example Playbook

```yaml
- name: Manage pfSense local users
  hosts: pfsense_firewalls
  vars:
    pfsense_users_list:
      - username: "netadmin"
        password: "{{ vault_netadmin_password }}"
        full_name: "Network Administrator"
        email: "netadmin@example.com"
        groups:
          - "admins"
        privileges:
          - "page-all"
        state: present
      - username: "tempuser"
        state: absent
  roles:
    - role: networking.pfsense_users
```
