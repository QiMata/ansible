# Ansible Role: Kong Gateway

**Table of Contents**

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Cross-Referencing](#cross-referencing)

## Overview

This role installs and configures **Kong Gateway OSS** on Debian/Ubuntu hosts. It adds Kong's APT repository, installs the specified package version, deploys a `kong.conf` template, optionally runs database migrations, and ensures the `kong` service is enabled and running.

## Supported Operating Systems/Platforms

The role is tested on the following platforms:

* **Debian 11** (Bullseye) and **Debian 12** (Bookworm)
* **Ubuntu 20.04 LTS** (Focal) and **Ubuntu 22.04 LTS** (Jammy)

## Role Variables

Default values from `defaults/main.yml`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `kong_version` | `3.6.0` | Kong package version to install |
| `kong_user` | `kong` | System user running Kong |
| `kong_group` | `kong` | System group for Kong |
| `kong_database` | `postgres` | Set to `off` for DB-less mode |
| `kong_pg_host` | `localhost` | PostgreSQL host |
| `kong_pg_port` | `5432` | PostgreSQL port |
| `kong_pg_user` | `kong` | Database user |
| `kong_pg_database` | `kong` | Database name |
| `kong_pg_password` | `kong` | Database password |

## Tags

This role defines no tags. All tasks run whenever the role is applied.

## Dependencies

Requires Ansible **2.13** or newer and the **community.general** collection.

## Example Playbook

```yaml
- hosts: kong
  become: true
  vars:
    kong_pg_password: secret
  roles:
    - kong
```

## Testing Instructions

Molecule tests are provided under `molecule/default`. Run them with:

```bash
molecule test
```

This uses the Docker driver to verify the role's behaviour in a container.

## Known Issues and Gotchas

* The role expects valid PostgreSQL credentials unless `kong_database` is set to `off` for DB-less mode.
* Only Debian and Ubuntu are supported; other distributions will fail.

## Security Implications

Ensure the PostgreSQL password is stored securely (e.g., Ansible Vault) and restrict network access to Kong's admin/API ports (default 8000/8001).

## Cross-Referencing

Consider pairing this role with a PostgreSQL role for the database backend and **haproxy** for load balancing multiple Kong nodes.

