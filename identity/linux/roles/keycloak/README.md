# Ansible Role: Keycloak

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
* [Related Roles](#related-roles)

## Overview

The **Keycloak** role installs and configures [Keycloak](https://www.keycloak.org/) on a host and manages it as a systemd service. It performs the following actions:

* Installs required packages such as **unzip**, **curl** and **OpenJDK&nbsp;17**.
* Creates a dedicated system user (default `keycloak`).
* Downloads and extracts the specified Keycloak version to the installation directory.
* Deploys configuration (`keycloak.conf`) and a systemd unit file.
* Enables and starts the Keycloak service.

Running the role yields a Keycloak server connected to PostgreSQL and running under a non-privileged account.

## Supported Operating Systems/Platforms

This role targets **Debian-based** Linux distributions and has been tested on Debian&nbsp;12. Ubuntu LTS releases (20.04/22.04) are expected to work as well. RHEL/CentOS systems are not supported without modifications.

## Role Variables

The main variables for this role are listed below (see `defaults/main.yml` for the full set):

| Variable | Default | Description |
|----------|---------|-------------|
| `keycloak_version` | `"24.0.1"` | Version to install |
| `keycloak_user` | `"keycloak"` | System account for the service |
| `keycloak_home` | `/var/lib/keycloak` | Base directory |
| `keycloak_install_dir` | `{{ keycloak_home }}/keycloak-{{ keycloak_version }}` | Installation path |
| `keycloak_download_url` | GitHub release URL for the version | Tarball source |
| `keycloak_http_port` | `8080` | HTTP port |
| `keycloak_packages` | `['unzip', 'curl', 'openjdk-17-jre-headless']` | Packages installed |
| `keycloak_db_host` | **required** | PostgreSQL host |
| `keycloak_db_name` | `"keycloak"` | Database name |
| `keycloak_db_user` | `"keycloak"` | Database user |
| `keycloak_db_password` | **required** | Database password |
| `keycloak_hostname` | inventory hostname | External hostname |

## Tags

No Ansible task tags are defined. All tasks run whenever the role is included.

## Dependencies

The role has no direct Ansible role dependencies. It does require an existing **PostgreSQL** database and internet access to download the Keycloak archive (unless `keycloak_download_url` points to an internal mirror). Systemd must be available to manage the service.

## Example Playbook

```yaml
- hosts: keycloak
  become: true
  vars:
    keycloak_db_host: "db.example.com"
    keycloak_db_password: "{{ vault_keycloak_db_password }}"
  roles:
    - role: keycloak
```

## Testing Instructions

A Molecule scenario is provided under `molecule/`. Run `molecule test` in that directory to verify the role in a container environment.

## Known Issues and Gotchas

* The PostgreSQL port is fixed at **5432** in the template.
* The role does **not** create the initial Keycloak admin user.
* Old version directories remain after upgrading `keycloak_version`.
* No TLS/HTTPS configuration is included by default.

## Security Implications

Keycloak runs as the unprivileged `keycloak` user. The configuration file is written with mode `0640` to protect credentials. Because the service listens on HTTP port `8080` by default, consider placing it behind a TLS-terminating proxy or enabling HTTPS manually.

## Related Roles

Other roles in this repository can complement this one, such as the PostgreSQL role for database provisioning and HAProxy for TLS termination or load balancing.
