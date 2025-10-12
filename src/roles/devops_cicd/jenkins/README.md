# Jenkins roles (Ansible)

This directory contains modular roles for installing, configuring, and operating Jenkins. Each sub-role covers a focused concern. For variables, usage, and detailed steps, follow the linked READMEs and files below.

## Roles overview

- Controller — install and configure the Jenkins controller (core, plugins, initialization)
  - Docs: [jenkins_controller/README.md](jenkins_controller/README.md)
- Agents — provision and manage Jenkins build agents
  - Docs: [jenkins_agent/README.md](jenkins_agent/README.md)
  - Registration helpers: [jenkins_agent_registration](jenkins_agent_registration/) ([defaults](jenkins_agent_registration/defaults/main.yml), [tasks](jenkins_agent_registration/tasks/main.yml))
- Configuration as Code (JCasC) — JCasC templates and reload hooks
  - Docs: [jenkins_casc/README.md](jenkins_casc/README.md)
- Credentials — manage credentials in Jenkins
  - Role: [jenkins_credentials](jenkins_credentials/) ([defaults](jenkins_credentials/defaults/main.yml), [tasks](jenkins_credentials/tasks/main.yml))
- SSL/HTTPS — TLS enablement and proxy wiring for Jenkins
  - Docs: [jenkins_ssl/README.md](jenkins_ssl/README.md)
- Backup — backup jobs and retention
  - Docs: [jenkins_backup/README.md](jenkins_backup/README.md)
- Restore — restore workflow/handlers
  - Role: [jenkins_restore](jenkins_restore/) ([defaults](jenkins_restore/defaults/main.yml), [tasks](jenkins_restore/tasks/main.yml))
- Monitoring — health checks, metrics, and log rotation
  - Role: [jenkins_monitoring](jenkins_monitoring/) ([defaults](jenkins_monitoring/defaults/main.yml), [tasks](jenkins_monitoring/tasks/main.yml))

> Note: This top-level README is intentionally brief. See each role’s README (where present) for variables, examples, and implementation notes.

## Testing these roles

Each role includes Molecule scenarios (`default`, `podman`, and `proxmox`). Use the repo’s shared Docker → Proxmox harness and documentation:

- Proxmox scenario guide: [src/molecule/proxmox/README.md](../../../molecule/proxmox/README.md)
- Dockerized Molecule harness: [src/docker/README.molecule.md](../../../docker/README.molecule.md)
- Project testing guide: [MOLECULE_TESTING_GUIDE.md](../../../../MOLECULE_TESTING_GUIDE.md)

## Conventions and dependencies

- Variables live under `defaults/main.yml`; handlers are in `handlers/main.yml` per role.
- Keep tasks idempotent and use handlers for service restarts/reloads.
- Ansible collections/roles are centralized in [requirements.yml](../../../requirements.yml).

## Where to start

- New to Jenkins in this repo? Begin with the controller: [jenkins_controller/README.md](jenkins_controller/README.md).
- Adding agents? See [jenkins_agent/README.md](jenkins_agent/README.md) and, if needed, the registration helpers under [jenkins_agent_registration](jenkins_agent_registration/).
- Managing configuration at scale? Review [jenkins_casc/README.md](jenkins_casc/README.md).
