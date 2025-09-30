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
- `ansible.cfg` – central configuration for running playbooks in this repository
- `requirements.yml` – role and collection dependencies consumed by `ansible-galaxy`
- `bin/` – helper scripts for executing Ansible
- `docs/` – documentation files (for example `keycloak-role.md`,
  `kubeadm-guide.md`, `kong-oss-role.md`, and `proxmox-role.md`)
- `inventories/` – inventory files for environments such as `prod` and `dev`
- `group_vars/` and `host_vars/` – variable definitions consumed by playbooks
- `playbooks/` – service playbooks like `deploy_bind9.yml`, `deploy_step_ca.yml`,
  `keycloak.yml`, and `proxmox.yml`
- `roles/` – shared Ansible roles that are not tied to a specific platform
- Category directories such as `infrastructure/`, `security/`, `databases/`,
  `data_platform/`, `communication/`, `ci_cd/`, and `identity/` that contain
  additional Linux roles grouped by domain
- `molecule/` – test scenarios specific to certain roles
- `scripts/` – helper utilities for tasks like generating inventories
- `files/` and `docker/` – supporting assets referenced by playbooks and roles

Each role is built to be modular and can be tested independently using Molecule.  The playbooks
combine these roles to configure complete systems. Molecule scenarios in this repository work with
either the **Docker** or **Podman** driver, so you may use whichever container engine is available.
