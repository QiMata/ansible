# Ansible Role: Jenkins Credentials

Table of Contents

- Overview
- Supported Jenkins/Scope
- Role Variables
- Supported Credential Types
- Example Playbook
- Idempotence and Behavior
- Testing Notes (Molecule → Proxmox)
- Known Issues and Gotchas
- Security Notes

## Overview

This role manages Jenkins credentials via the Jenkins HTTP API. It can create a default SSH private key credential for agents and any number of custom credentials, keeping your Jenkins controller’s credentials in code and applied idempotently.

The role talks directly to the Jenkins controller using Ansible's uri module. No Jenkins plugins are installed by this role; it assumes standard credentials APIs are available.

## Supported Jenkins/Scope

- Targets an existing Jenkins controller reachable over HTTP.
- Uses the “system” store and the global domain (`/credentials/store/system/domain/_/`).
- Runs from any host with network access to Jenkins; typically the controller host itself or a control node with delegate_to.

## Role Variables

Defaults are defined in `defaults/main.yml`.

Primary toggles and API behavior

- `jenkins_credentials_enabled` (bool, default: true) — Master switch for this role.
- `jenkins_credentials_api_timeout` (int, default: 30)
- `jenkins_credentials_api_retries` (int, default: 3)

Admin access and controller addressing

- `jenkins_admin_user` (string, default: "admin") — Jenkins admin username.
- `jenkins_admin_password` (string, required) — Jenkins admin password or API token.
- `jenkins_http_port` (int, default: 8080)
- Controller URL base used by tasks: `http://{{ ansible_default_ipv4.address }}:{{ jenkins_http_port }}`. Override via inventory facts or by delegating tasks to a host that can reach Jenkins at that address.

Default SSH credential for agents

- `jenkins_credentials_ssh_key_id` (string, default: "jenkins-ssh-key")
- `jenkins_credentials_ssh_user` (string, default: `{{ jenkins_agent_user | default('jenkins') }}`)
- `jenkins_credentials_ssh_private_key` (string, default: empty) — PEM private key.
- `jenkins_credentials_ssh_passphrase` (string, default: empty)

Custom credentials list

- `jenkins_credentials_list` (list, default: [])
  - Each item must include `id`, `type`, `description`, `scope` (optional, default GLOBAL) and type-specific fields as shown below.

## Supported Credential Types

Provide items in `jenkins_credentials_list` with `type` set to one of:

- `secret_text`
  - Fields: `id`, `description`, `secret`, `scope`
- `username_password`
  - Fields: `id`, `description`, `username`, `password`, `scope`
- `ssh_private_key`
  - Fields: `id`, `description`, `username`, `private_key`, `passphrase` (optional), `scope`

Templates used to build request payloads are under `templates/`:

- `credential-secret_text.json.j2`
- `credential-username_password.json.j2`
- `credential-ssh_private_key.json.j2`

## Example Playbook

Minimal usage on the controller host itself:

```yaml
- name: Configure Jenkins credentials
  hosts: jenkins_controller
  gather_facts: true
  vars:
    jenkins_admin_user: admin
    jenkins_admin_password: "{{ vault_jenkins_admin_password }}"
    jenkins_credentials_ssh_private_key: "{{ vault_jenkins_ssh_private_key }}"
    jenkins_credentials_list:
      - id: "github-token"
        type: "secret_text"
        description: "GitHub Personal Access Token"
        secret: "{{ vault_github_token }}"
        scope: "GLOBAL"
      - id: "docker-registry"
        type: "username_password"
        description: "Docker Registry Credentials"
        username: "docker-user"
        password: "{{ vault_docker_password }}"
        scope: "GLOBAL"
      - id: "ssh-deploy-key"
        type: "ssh_private_key"
        description: "SSH Deploy Key"
        username: "deploy"
        private_key: "{{ vault_deploy_private_key }}"
        passphrase: "{{ vault_deploy_passphrase }}"
        scope: "GLOBAL"
  roles:
    - devops_cicd/jenkins/jenkins_credentials
```

If running from a control node, delegate tasks or override the base URL so the API points at your Jenkins controller host/IP rather than `ansible_default_ipv4.address` of the running node.

## Idempotence and Behavior

- The role first waits for Jenkins API readiness, then fetches a CSRF crumb and posts credentials to the system/global domain.
- The default SSH credential is only attempted when `jenkins_credentials_ssh_private_key` is non-empty.
- Custom credentials are sent using the matching Jinja template and form-urlencoded body.
- HTTP 200 or 302 are treated as success for create calls. Existing credentials may result in a 302 without change; failures are not fatal by default (`failed_when: false`) to allow re-runs.
- Optional verification step lists current credentials and prints their IDs when `jenkins_credentials_verify | default(true)`.

## Testing Notes (Molecule → Proxmox)

This repository includes a Docker → Proxmox Molecule workflow. To validate this role:

- Use the tools image and Proxmox scenario under `src/molecule/proxmox/` as described in `MOLECULE_TESTING_GUIDE.md` and `src/docker/README.molecule.md`.
- Supply Jenkins controller access (host/port, admin credentials) via inventory or environment. The scenario will provision instances on Proxmox; ensure Jenkins is installed and reachable before converging this role, or include it in the converge play.

## Known Issues and Gotchas

- Addressing: Tasks use `ansible_default_ipv4.address` to form the URL. If you run against localhost or a node with multiple interfaces, override the URL/host or delegate to the controller.
- CSRF crumb: Jenkins must have the crumb issuer endpoint enabled; otherwise requests will fail. The role fetches the crumb at `/crumbIssuer/api/json`.
- Missing Groovy template: Tasks reference `manage-credentials.groovy.j2` for optional init script deployment. If this template is not present, add it or disable that task; ensure your Jenkins init path is correct via `jenkins_controller_home`.
- Create-only semantics: The API calls here post credentials; they don’t update or delete existing ones. To change a value, rotate the ID or manage updates via Groovy/Job DSL.

## Security Notes

- Never commit secrets. Use Ansible Vault or external secret managers for values like `jenkins_admin_password`, tokens, and private keys.
- Prefer Jenkins API tokens over user passwords.
- Limit credential scope to GLOBAL only when required; consider folder/domain scoping if you extend this role.
- Restrict network access to the Jenkins API from the host running this role.
