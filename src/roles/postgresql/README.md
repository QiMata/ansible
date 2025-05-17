# Ansible Role: PostgreSQL

Installs and configures PostgreSQL on Debian/Ubuntu with optional high-availability (streaming replication or Patroni).

## Requirements

* Ansible ≥ 2.15  
* Python `psycopg2` on managed node (installed by default task)  
* `community.postgresql` and `community.general` collections for some tasks  

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `postgresql_version` | `15` | PostgreSQL major version to install |
| `postgresql_use_official_repo` | `false` | Use PGDG repository |
| `postgresql_env` | `prod` | `dev` or `prod` for sane defaults |
| `postgresql_enable_replication` | `false` | Enable streaming replication tasks |
| `postgresql_use_patroni` | `false` | Install and manage Patroni |
| … | … | … |

Refer to `defaults/main.yml` for the full list.

## Example Playbook

```yaml
- hosts: db_primary
  vars:
    postgresql_use_official_repo: true
    postgresql_version: 16
    postgresql_enable_replication: true
    postgresql_replication_role: primary
    postgresql_replication_password: "{{ vault_repl_pw }}"
    postgresql_admin_password: "{{ vault_pg_pw }}"
    postgresql_configure_firewall: true
    postgresql_allowed_hosts: ["10.0.0.0/24"]
  roles:
    - postgresql
```
