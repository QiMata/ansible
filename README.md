# Ansible Infrastructure Management

This repository contains a large collection of Ansible configuration used to deploy and manage
various services across multiple environments.  It provides reusable roles, ready-made playbooks
and inventories that help automate everything from base system setup to complex applications.

## Purpose
The project aims to simplify infrastructure administration by codifying the installation and
configuration of common open source software such as DNS (BIND9), identity management (Keycloak),
certificate authorities (Step CA), databases (PostgreSQL, MariaDB), and many other tools.  Roles
and playbooks are organized so they can be reused for different clients and environments.

## Repository Layout
- `ansible.cfg` – consolidated configuration that points Ansible at the inventories and roles under `src/`.
- `requirements.yml` – canonical role and collection dependencies for the entire project.
- `bin/` – helper scripts for executing Ansible.
  - The `ansible-playbook` wrapper scripts derive their default paths from the
    repository location, so they work no matter where the repository is cloned.
    Set environment variables (for the Bash script) or pass parameters/environment
    variables (for the PowerShell script) to override any of the defaults when
    needed.
- `docs/` – documentation files (for example `keycloak-role.md`,
  `kubeadm-guide.md`, `kong-oss-role.md`, and `proxmox-role.md`). Historical project
  briefs now live under `docs/briefings/`.
- `tools/windows/maintenance/` – archived PowerShell helpers that capture one-off
  maintenance scripts and legacy migration snippets.
- `src/` – primary Ansible project content:
  - `inventories/` – dynamic inventory scripts plus static sample inventories (including `legacy/` snapshots).
  - `group_vars/` and `host_vars/` – variable definitions shared across playbooks.
  - `playbooks/` – service playbooks like `deploy_bind9.yml` and `deploy_step_ca.yml`.
  - role directories organized under category folders, for example
    `infrastructure/linux/roles`, `security/linux/roles`, `databases/linux/roles`,
    `ci_cd/linux/roles`, etc. Each contains the individual service roles (Keycloak,
    Vault, PostgreSQL, Proxmox, and so on).
  - `molecule/` – test scenarios specific to some roles.
  - `scripts/` – Python utilities (now packaged as importable modules) for tasks like
    generating inventories.

Each role is built to be modular and can be tested independently using Molecule.  The playbooks
combine these roles to configure complete systems. Molecule scenarios in this repository work with
either the **Docker** or **Podman** driver, so you may use whichever container engine is available.

## Run a playbook via Packer (Docker builder)
This repo includes a containerized Packer workflow that provisions an ephemeral Ubuntu container and runs an Ansible playbook from `src/` inside it using the `ansible-local` provisioner.

Why use this?
- Consistent toolchain, no Ansible setup required on the host
- Simple smoke tests for roles/playbooks targeting localhost

Key files
- `packer/template.pkr.hcl` — defines Docker builder + ansible-local
- `packer/Dockerfile` — builds the Packer runner image (includes Docker CLI)
- `packer/run-packer.ps1`, `packer/run-packer.sh` — wrappers that rebuild and run Packer
- `src/playbooks/smoke_localhost.yml` — minimal smoke test playbook

Prerequisites
- Docker (Linux containers)

Quick start (Windows PowerShell, run from repo root)
- Smoke test:
  - `./packer/run-packer.ps1 -Playbook 'playbooks/smoke_localhost.yml' -Limit 'localhost'`
- Run another playbook (example):
  - `./packer/run-packer.ps1 -Playbook 'playbooks/base.yml' -Limit 'localhost' -Become`

Quick start (Linux/macOS)
- Smoke test:
  - `./packer/run-packer.sh playbooks/smoke_localhost.yml --limit localhost`
- Run another playbook (example):
  - `./packer/run-packer.sh playbooks/base.yml --limit localhost --become`

Notes
- Playbook paths are relative to `src/`.
- The wrapper rebuilds the runner image to pick up Dockerfile changes.
- By default the Docker builder discards image artifacts; this flow is for provisioning/tests.
- Pass additional Ansible args via `-AnsibleExtraArgs` (PowerShell) or `--extra` (bash), e.g. `-AnsibleExtraArgs @('-e','foo=bar')`.

## Inventory generation helper

The repository includes a helper script at `src/scripts/create_ansible_inventory.py` that can
generate environment specific inventory files from a PostgreSQL database. The script now accepts
CLI options (with environment variable fallbacks) for the SSH user and the privilege escalation
password that will be written into each host entry. Input rows are validated (for example IP
addresses must be parseable) so malformed records raise clear exceptions instead of producing
broken inventories, and the module is covered by unit tests in `tests/test_create_ansible_inventory.py`.

```bash
export ANSIBLE_INVENTORY_USER=ansible
export ANSIBLE_BECOME_PASS="$(ansible-vault view creds.yml --vault-password-file ~/.vault_pass | jq -r .become_pass)"

python src/scripts/create_ansible_inventory.py \
  --db_conn_str "postgresql://user:password@db.example.com/inventory" \
  --output_directory ./generated-inventory
```

You can also provide the credentials explicitly on the command line by passing
`--ansible-user` and `--become-pass`. For security, prefer sourcing these values from a secrets
manager such as **Ansible Vault**, HashiCorp Vault, or injecting them through environment variables
in your CI pipeline rather than hardcoding them in scripts.

## Service playbooks for MinIO, Spark, Prometheus, and Grafana

Playbooks for several commonly requested data-platform services are available under
`src/playbooks/`:

| Playbook | Inventory group | Primary role | Notes |
| --- | --- | --- | --- |
| `minio.yml` | `minio_servers` | `data_systems.minio` | Enables TLS, Prometheus metrics, and replication. Secrets such as `vault_minio_root_password` must be populated via Ansible Vault. |
| `spark.yml` | `spark_master_nodes`, `spark_worker_nodes` | `data_analytics.spark_role` | Configures HA masters, workers, and exposes JMX metrics for Prometheus. Shared secrets like `vault_spark_auth_secret` should reside in Vault. |
| `prometheus.yml` | `prometheus_servers` | `monitoring_observability.prometheus` | Builds scrape targets for MinIO and Spark based on the generated inventory and wires in Alertmanager endpoints. |
| `grafana.yml` | `grafana_servers` | `monitoring_observability.grafana` | Provisions TLS, datasource connections (Prometheus and Loki), and alert contact points fed by Vault secrets. |

Each playbook expects inventories generated by `create_ansible_inventory.py` (or your own INI files)
to provide the required host groups. After generating an inventory, run any of the playbooks from
the repository root:

```bash
python src/scripts/create_ansible_inventory.py \
  --db_conn_str "postgresql://user:password@db.example.com/inventory" \
  --output_directory ./generated-inventory

ansible-playbook -i generated-inventory/prod.ini src/playbooks/minio.yml \
  --limit minio_servers \
  --vault-password-file ~/.vault_pass

ansible-playbook -i generated-inventory/prod.ini src/playbooks/prometheus.yml \
  --limit prometheus_servers \
  --vault-password-file ~/.vault_pass
```

Adjust the `--limit` flag for the appropriate host group (`spark_master_nodes`, `spark_worker_nodes`,
`grafana_servers`, etc.) and supply any required extra variables or Vault secrets.

To keep the entry points CI-friendly, `tests/test_playbook_syntax.py` performs an
`ansible-playbook --syntax-check` run for each new playbook using the lightweight inventory stored
in `tests/fixtures/minimal_inventory.ini`. This guards against syntax drift whenever the roles or
playbooks change.

## Ignored build artifacts

To keep the repository clean, generated Ansible assets are ignored by default. Local collections
(`collections/`), cached facts (`.ansible_facts/`), Molecule working directories (`.molecule/`),
bytecode (`__pycache__/` and `*.pyc`), retry files (`*.retry`), and temporary logs (`*.log` and
`logs/`) should never be committed. If you need to share sample outputs or log excerpts, copy only
the relevant snippets into documentation instead of adding the raw files to version control.

## Managing vaulted secrets

Host and group secrets (for example the privilege escalation password) are stored in
`src/group_vars/all/vault.yml`, which is encrypted with **Ansible Vault**. To work with vaulted
data:

1. Create a local vault password file (for example `vault_password.txt`) that contains the vault
   password. This file is ignored by Git, so keep it outside of version control.
2. When running playbooks, provide the password with `--vault-password-file`:
   ```bash
   ansible-playbook -i src/inventories/JaredRhodes.ini src/playbooks/<playbook>.yml \
     --vault-password-file vault_password.txt
   ```
3. To view or edit vaulted data, run:
   ```bash
   ansible-vault view src/group_vars/all/vault.yml --vault-password-file vault_password.txt
   ansible-vault edit src/group_vars/all/vault.yml --vault-password-file vault_password.txt
   ```

New secrets should be added to `src/group_vars/all/vault.yml` and referenced from inventories or
group variable files using templated variables such as
`ansible_become_pass: "{{ vault_ansible_become_pass_common }}"`.

## Base playbook variable layout

The `src/playbooks/base.yml` playbook is designed to work against an arbitrary inventory group.
Set the `base_target_group` extra-var (or define it in inventory) to control which hosts are
targeted; it defaults to the broad `all` group when unspecified. The playbook expects the
following variable files to exist relative to the repository root:

- `src/group_vars/all.yml`
- `src/group_vars/systems_admin/shared_tools/ansible_semaphore/all.yml`
- `src/group_vars/systems_admin/shared_tools/ansible_semaphore/mariadb_galera.yml`

These files contain the baseline defaults needed by the `base` role. Override them by copying the
same relative layout into your own project or by providing inventory-specific `group_vars` and
`host_vars`. This keeps the playbook runnable across environments without requiring host-specific
files in version control.
## Data product orchestration playbook

A full data and analytics stack can now be deployed with the orchestrator playbook at
`src/playbooks/data_product.yml`. The playbook chains the base hardening role with
PostgreSQL, Redis, Apache Airflow, MinIO, Apache Spark, Apache NiFi, the Amundsen
catalog, Apache Superset, Prometheus, Grafana, and the Elasticsearch stack so that
cross-service credentials and dependencies are wired automatically.

### Prerequisites
1. Install the required community roles and collections before running the playbook:
   ```bash
   ansible-galaxy install -r requirements.yml
   ```
2. Copy the sample inventory and adjust addresses to match your environment. The
   repository ships with `src/inventories/data_product_sample/hosts.ini` which includes
   group definitions for database, message broker, analytics, monitoring, storage, and
   search tiers.
3. Update `src/inventories/data_product_sample/group_vars/all/vault.yml` with production
   credentials and encrypt it with Ansible Vault. The orchestrator expects the following
   vaulted variables:
   - `vault_airflow_db_password`
   - `vault_airflow_fernet_key`
   - `vault_data_product_redis_password`
   - `vault_data_product_minio_root_password`
   - `vault_data_product_elasticsearch_api_password`
   - `vault_data_product_nifi_sensitive_key`
   - `vault_data_product_amundsen_neo4j_password`
   - `vault_data_product_amundsen_db_password`
   - `vault_superset_db_password`
   - `vault_superset_secret_key`
   - `vault_grafana_admin_password`

### Running the playbook
```bash
ansible-playbook \
  -i src/inventories/data_product_sample/hosts.ini \
  src/playbooks/data_product.yml \
  --vault-password-file ~/.vault_pass
```

Use the `--tags` flag to run targeted subsets (for example `--tags database,airflow`)
while iterating on specific services.

### Recommended validation steps
- Syntax check the playbook:
  ```bash
  ansible-playbook -i src/inventories/data_product_sample/hosts.ini src/playbooks/data_product.yml --syntax-check
  ```
- Execute the Molecule smoke scenario for the aggregated deployment (see
  `src/molecule/data_product`) after installing the delegated driver plugin:
  ```bash
  pip install 'molecule-plugins[delegated]'
  cd src && molecule test -s data_product
  ```

The sample inventory provides cross-service variables for Airflow ↔ PostgreSQL/Redis,
Superset ↔ Redis/PostgreSQL, and Grafana ↔ Prometheus/Elasticsearch so the default run
works end-to-end once secrets are vaulted and hostnames are updated.
