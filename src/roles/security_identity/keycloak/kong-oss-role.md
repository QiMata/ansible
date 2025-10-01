# Kong Gateway OSS Role

## Overview

This role installs and configures **Kong Gateway OSS** on Debian/Ubuntu hosts. It
follows the best practices outlined in the project documentation, supporting both
simple dev setups and production clusters. The role manages the APT repository,
installs the Kong package, deploys a `kong.conf` template, optionally runs
migrations, and ensures the Kong service is running.

## Supported Operating Systems/Platforms

- Debian 11/12
- Ubuntu 20.04/22.04

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `kong_version` | `3.6.0` | Kong package version to install |
| `kong_database` | `postgres` | Set to `off` for DB-less mode |
| `kong_pg_host` | `localhost` | PostgreSQL host |
| `kong_pg_port` | `5432` | PostgreSQL port |
| `kong_pg_user` | `kong` | Database user |
| `kong_pg_database` | `kong` | Database name |
| `kong_pg_password` | `kong` | Database password |

## Example Playbook

```yaml
- hosts: kong
  become: true
  vars:
    kong_pg_password: secret
  roles:
    - kong
```

The role supports running migrations once during deployment and can be used in
both development and production inventories. For production, combine multiple
`kong` hosts with a load balancer and a highly available PostgreSQL database as
recommended in the accompanying best practices guide.
