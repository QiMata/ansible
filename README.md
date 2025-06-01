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
- `docs/` – documentation files (for example `keycloak-role.md`)
- `group_vars/` – group variable files used by the top level playbooks
- `playbooks/` – simple playbooks demonstrating role usage
- `molecule/` – Molecule scenarios used for testing roles
- `src/` – primary Ansible project
  - `ansible.cfg` – configuration for running playbooks in `src`
  - `requirements.yml` – additional role and collection dependencies
  - `bin/` – helper scripts for executing Ansible
  - `inventories/` – inventory files for environments such as `prod` and `dev`
  - `group_vars/` and `host_vars/` – variable definitions
  - `playbooks/` – service playbooks like `deploy_bind9.yml` and `deploy_step_ca.yml`
  - `roles/` – dozens of roles covering services including BIND9, Keycloak, Jenkins,
    OpenLDAP, HAProxy, Step CA, NetBox and more
  - `molecule/` – test scenarios specific to some roles
  - `scripts/` – helper utilities for tasks like generating inventories

Each role is built to be modular and can be tested independently using Molecule.  The playbooks
combine these roles to configure complete systems.
