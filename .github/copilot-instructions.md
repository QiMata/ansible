# Copilot Instructions for This Repository

This repository is an Ansible mono-repo with roles, inventories, and a Dockerized Molecule workflow that provisions test instances on Proxmox (Docker → Proxmox).

## What to prioritize
- Reuse existing roles, variables, and testing assets under `src/**`.
- Prefer the Proxmox Molecule scenario in `src/molecule/proxmox/` when proposing or generating tests.
- Leverage the Docker harness in `src/docker/` to run Molecule locally/CI.
- Keep diffs minimal, idempotent, and aligned with existing style.

## Repository layout
- Roles and Ansible sources: `src/roles`, `src/playbooks`, `src/group_vars`, `src/host_vars`
- Proxmox Molecule scenario: `src/molecule/proxmox/`
- Dockerized test harness and scripts: `src/docker/`
- Root helpers and docs: `*.ps1`, `MOLECULE_TESTING_GUIDE.md`, `README.md`

## Conventions
- Use Ansible best practices: idempotent tasks, handlers for service changes, variables under `defaults/main.yml`.
- Prefer Molecule for role validation. Add/extend the Proxmox scenario rather than creating ad‑hoc scripts.
- Centralize dependencies in `requirements.yml` (Ansible) and `requirements.txt` (Python) when touching Molecule scenarios.

## How Docker → Proxmox Molecule testing works
1. Build a Docker image with Ansible/Molecule and Proxmox tooling using `src/docker/Dockerfile.molecule-proxmox`.
2. Start a container defined in `src/docker/docker-compose.molecule.yml` that mounts this repo and provides a stable toolchain.
3. Inside the container, run Molecule with the `proxmox` scenario found in `src/molecule/proxmox/`.
   - The scenario talks to the Proxmox API to create LXC containers/VMs, converges the role, verifies, and destroys.
   - Proxmox connection details are provided via environment file: copy `src/molecule/proxmox/.env.example` to `.env` and fill in host, token/credentials, node, storage, template, etc.
   - Key scenario files:
     - `molecule.yml` — driver/platforms and test configuration
     - `create.yml` / `destroy.yml` — lifecycle provisioning/cleanup
     - `converge.yml` — applies roles/playbooks under test
     - `verify.yml` — assertions and checks
     - `requirements.yml` / `requirements.txt` — collections and Python deps

## Quick start (Windows PowerShell)
- Validate local prerequisites: `src/docker/test-setup.ps1`
- Use the orchestrator script:
  - Build tools image: `src/docker/run-molecule-tests.ps1 build`
  - Start environment: `src/docker/run-molecule-tests.ps1 start`
  - Run Proxmox tests: `src/docker/run-molecule-tests.ps1 test proxmox`
  - Open a shell inside the container: `src/docker/run-molecule-tests.ps1 shell`

## Quick start (Linux/macOS)
- Validate local prerequisites: `src/docker/test-setup.sh`
- Use the orchestrator script:
  - Build tools image: `src/docker/run-molecule-tests.sh build`
  - Start environment: `src/docker/run-molecule-tests.sh start`
  - Run Proxmox tests: `src/docker/run-molecule-tests.sh test proxmox`
  - Open a shell inside the container: `src/docker/run-molecule-tests.sh shell`

## Helpful scripts and docs
- Orchestration: `src/docker/run-molecule-tests.ps1`, `src/docker/run-molecule-tests.sh`, `src/docker/Makefile`
- Role test runners: `src/docker/run-role-tests.ps1`, `src/docker/test-strategy.ps1`
- Scenario scaffolding: `src/docker/create-proxmox-scenarios.ps1`
- CI example: `src/docker/github-actions-example.yml`
- Proxmox scenario docs: `src/molecule/proxmox/README.md`
- Docker harness docs: `src/docker/README.molecule.md`
- Project testing guide: `MOLECULE_TESTING_GUIDE.md`

## Guardrails for suggestions
- Don’t add external dependencies where an in-repo equivalent exists.
- Keep the Molecule scenario name `proxmox` unless a new scenario is intentionally introduced.
- Reference files with repo-relative paths and prefer existing patterns from other roles/scenarios.

## Troubleshooting
- Validate Docker/Compose and local config: `src/docker/test-setup.ps1` or `src/docker/test-setup.sh`
- Logs and status via orchestrator scripts (`logs` subcommand). Inside the container, use `molecule list` and `molecule status -s proxmox`.
- Ensure `src/molecule/proxmox/.env` is present and correct (copy from `.env.example`).
