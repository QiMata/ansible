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
