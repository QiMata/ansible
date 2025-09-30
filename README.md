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
