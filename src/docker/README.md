# Dockerized Molecule → Proxmox test harness

This folder provides a Docker-based toolchain to create and test Proxmox LXC instances using the same flow our Molecule `proxmox` scenario uses. It runs entirely inside a container and talks to the Proxmox API.

Highlights:
- Reuses your repo under `/ansible/src` inside the runner container.
- Uses the existing Molecule Proxmox playbooks to create the LXC, configure SSH, and verify.
- Adds a convenient script to build a hardened Debian base template and export it into Proxmox Storage → CT Templates.

## Files
- `Dockerfile.molecule-proxmox` — Tools image with Ansible, Molecule, and helpers.
- `docker-compose.molecule.yml` — Runner container that mounts this repo and exposes Ansible/Molecule.
- `run-molecule-tests.ps1/.sh` — Orchestrate building the tools image, starting the runner, and executing Molecule.
- `run-role-tests.ps1` — Helper to run role-level tests.
- `test-setup.ps1/.sh` — Quick validation of local prerequisites.
- `create-hardened-debian-template.ps1` — End-to-end script to create, harden, and export a Debian LXC as a Proxmox CT Template tarball.

## Prereqs
- Docker Desktop / Engine
- Proxmox API credentials and storage details placed in an env file

Copy and fill one of:
- `src/docker/.env` (preferred in this folder)
- `src/molecule/proxmox/.env` (fallback)

Required keys (examples):
```
PROXMOX_URL=https://node1:8006
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=your-password
PROXMOX_NODE=node1
TEMPLATE_STORAGE=buildinfra
STORAGE=local-lvm
TEMPLATE=debian-12-standard_12.7-1_amd64.tar.zst
CONTAINER_ID=200
CONTAINER_IP=10.80.0.200
BRIDGE=vmbr0
IFACE=eth0
CIDR_BITS=24
GATEWAY=10.80.0.150
```

## Create a hardened Debian template
This uses the Proxmox API to create an LXC, configures SSH via `pct exec`, applies your hardening playbook, then exports a template tarball to your storage’s CT Templates area.

Windows PowerShell:
```powershell
# Full flow (create → harden → export → verify → cleanup)
pwsh -NoProfile -ExecutionPolicy Bypass -File src/docker/create-hardened-debian-template.ps1 -Become

# Skip create/harden when the CT already exists, and just export/verify/cleanup
pwsh -NoProfile -ExecutionPolicy Bypass -File src/docker/create-hardened-debian-template.ps1 -SkipCreate -SkipHarden -Become

# Keep the CT after exporting (disable cleanup)
pwsh -NoProfile -ExecutionPolicy Bypass -File src/docker/create-hardened-debian-template.ps1 -Cleanup:$false
```

What it does:
1) Builds/starts the runner container defined in `docker-compose.molecule.yml`.
2) Runs `src/molecule/proxmox/create.yml` to create or reuse CT `CONTAINER_ID`, set static IP/net0, and enable SSH for the `molecule` user.
3) Runs your hardening playbook (default `playbooks/hardened_debian.yml`) over SSH (`molecule/molecule123`).
4) Runs `src/playbooks/proxmox_lxc_make_template.yml` to:
   - Stop the CT.
   - Export its rootfs as `debian-<version>-hardened.tar.zst` into `/mnt/pve/<TEMPLATE_STORAGE>/template/cache` or upload via `pvesm upload` if the storage isn’t writable.
   - Verify the template is listed by Proxmox storage (`content=vztmpl`).
   - Optionally mark the CT as a “template” (for fast cloning) and then delete it if cleanup is enabled.

Verification:
- The play asserts the template is visible under Storage → `<TEMPLATE_STORAGE>` → CT Templates.

## Troubleshooting
- Ensure `.env` values match your Proxmox environment. Wrong storage/node or credentials will cause HTTP 401/404/500 errors.
- If storage is an NFS/CIFS mount that’s not writable, the play will export to `/var/lib/vz/template/cache` and upload with `pvesm`.
- You may see warnings about dynamic Proxmox inventory plugins; they’re benign for this flow.

## Running Molecule Proxmox scenario
```powershell
src/docker/run-molecule-tests.ps1 build
src/docker/run-molecule-tests.ps1 start
src/docker/run-molecule-tests.ps1 test proxmox
```
Inside the runner:
- `molecule list`
- `molecule status -s proxmox`

Refer to `src/molecule/proxmox/README.md` for scenario details.
