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
- `ansible.cfg` – basic configuration pointing Ansible at the bundled roles
- `requirements.yml` – collection dependencies required to run the playbooks
- `bin/` – helper scripts for executing Ansible
  - The `ansible-playbook` wrapper scripts now derive their default paths from the
    repository location, so they work no matter where the repository is cloned.
    Set environment variables (for the Bash script) or pass parameters/environment
    variables (for the PowerShell script) to override any of the defaults when
    needed.
- `docs/` – documentation files (for example `keycloak-role.md`,
  `kubeadm-guide.md`, `kong-oss-role.md`, and `proxmox-role.md`)
- `group_vars/` – group variable files used by the top level playbooks
 - `playbooks/` – simple playbooks demonstrating role usage such as `keycloak.yml`, `kubeadm.yml`, `kong.yml`, and `proxmox.yml`
- `src/` – primary Ansible project
  - `ansible.cfg` – configuration for running playbooks in `src`
  - `requirements.yml` – additional role and collection dependencies
  - `inventories/` – inventory files for environments such as `prod` and `dev`
  - `group_vars/` and `host_vars/` – variable definitions
  - `playbooks/` – service playbooks like `deploy_bind9.yml` and `deploy_step_ca.yml`
  - role directories organized under category folders, for example
    `infrastructure/linux/roles`, `security/linux/roles`, `databases/linux/roles`,
    `ci_cd/linux/roles`, etc. Each contains the individual service roles (Keycloak,
    Vault, PostgreSQL, Proxmox, and so on).
  - `molecule/` – test scenarios specific to some roles
  - `scripts/` – helper utilities for tasks like generating inventories

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
password that will be written into each host entry.

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