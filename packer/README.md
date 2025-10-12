# Packer-in-Docker to run Ansible playbooks (Docker) and (optionally) build Proxmox LXC templates

This adds a small Dockerized Packer runner that can:

1) Provision a temporary Docker container and execute any playbook from this repo's `src/` tree using the Ansible "ansible-local" provisioner (smoke tests).

2) Optionally build a Proxmox LXC template by launching a base LXC from a Proxmox ostemplate, running your Ansible playbook over SSH, then saving the container as a new reusable Proxmox template. Note: for LXC templates, our preferred path is the Docker+Ansible Molecule-Proxmox flow described in `src/docker/README.md`.

Key points:
- No changes to your existing Ansible layout are required.
- The entire repo is bind-mounted into the Packer container at `/workspace`.
- Packer's Docker builder launches an Ubuntu container, installs Ansible, copies `src/` into `/opt/src`, and runs your playbook.
- Useful for quick, reproducible smoke tests or ephemeral provisioning.

## Files
- `packer/Dockerfile` — Packer CLI container (based on `hashicorp/packer`).
- `packer/template.pkr.hcl` — Packer template using the Docker builder and `ansible-local` provisioner.
- `packer/template.proxmox-lxc.pkr.hcl` — Packer template using the Proxmox builder (LXC) with the Ansible provisioner to create a Proxmox template.
- `packer/docker-compose.packer.yml` — Optional compose service for convenience.
- `packer/run-packer.ps1` — Windows/PowerShell wrapper.
- `packer/run-packer.sh` — Linux/macOS wrapper.

## Requirements
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Internet access for the base image and apt packages

## Quick start (Windows PowerShell)
1. From the repo root, run:

```powershell
# Example: run the base site playbook
./packer/run-packer.ps1 -Playbook 'playbooks/base.yml'

# With become and extra args
./packer/run-packer.ps1 -Playbook 'playbooks/base.yml' -Become -AnsibleExtraArgs '-e env=dev'
```

### Build a Proxmox LXC template (optional)
1. Copy `packer/.pkrvars.hcl.example` and fill in your Proxmox details:

```powershell
Copy-Item packer/.pkrvars.hcl.example packer/proxmox.pkrvars.hcl
notepad packer/proxmox.pkrvars.hcl
```

2. Run the builder. Provide a playbook path (relative to `src/`):

```powershell
./packer/run-packer.ps1 -Template proxmox-lxc -VarsFile 'packer/proxmox.pkrvars.hcl' -Playbook 'playbooks/base.yml' -Become
```

When complete, a new LXC template named per `template_name` will be available in your Proxmox node.

Recommended alternative (uses Molecule-Proxmox flow): see `src/docker/README.md` for `create-hardened-debian-template.ps1`, which creates the CT, applies hardening, exports a CT Template tar to storage, verifies it’s listed, and cleans up.

## Quick start (Linux/macOS)
```bash
# Example: run the base site playbook
./packer/run-packer.sh playbooks/base.yml

# With become and extra args
./packer/run-packer.sh playbooks/base.yml --become --extra '-e env=dev'
```

Proxmox LXC usage is similar using the bash wrapper (flags may differ slightly):

```bash
./packer/run-packer.sh --template proxmox-lxc --var-file packer/proxmox.pkrvars.hcl --playbook playbooks/base.yml --become
```

## Changing the base image
Set the `base_image` Packer variable via wrappers:
- PowerShell: `-BaseImage ubuntu:24.04`
- Bash: `BASE_IMAGE=ubuntu:24.04 ./packer/run-packer.sh playbooks/base.yml`

## Notes and tips
- The playbook path is relative to `src/`. For example, `playbooks/site.yml` or `playbooks/setup-redis.yml`.
- Ansible uses your project config from `/opt/workspace/ansible.cfg` and roles from `/opt/workspace/src/roles`.
- Inventory is a generated `localhost` target with local connection. This is ideal for roles/playbooks that can run locally inside a vanilla Ubuntu container.
- If your playbook requires remote hosts or cloud credentials, this pattern is not a fit—use Molecule or your normal runner.

For Proxmox:
- Ensure the ostemplate exists on your node (e.g. `local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst`).
- The Ansible provisioner connects over SSH to the LXC using `ssh_username`/`ssh_password` you provide in the vars file.
- The builder will mark the final container as a Proxmox template named `template_name`.

## Troubleshooting
- Permission denied to Docker socket: ensure the socket mount works. On Windows/macOS Docker Desktop, `/var/run/docker.sock` inside Linux containers is supported by default.
- Ansible collection/role dependencies: add them to `requirements.yml` and ensure your tasks don't rely on external state.
- For detailed logs, the wrappers set `PACKER_LOG=1`.

Proxmox:
- 401/403 from Proxmox API: verify URL, token or username/password, and permissions for creating LXC and templates.
- SSH timeout: check network_bridge connectivity and that the container got an IP via DHCP; adjust `ssh_timeout` if needed.

### Notes on Packer Proxmox LXC plugin
Historically, community plugins (e.g., Telmate) were used for Proxmox builds. Newer official plugins may not support all legacy LXC builder fields. If you hit unsupported-argument errors, prefer the Docker+Molecule Proxmox flow in `src/docker/` which uses the Proxmox API and Ansible directly for LXC lifecycle (create → harden → export template).
