# Docker Molecule Testing with Proxmox

This directory contains Docker configurations for running Molecule tests against Proxmox Virtual Environment (PVE).

## Overview

The Docker setup provides an isolated and reproducible environment for running Ansible Molecule tests that create and manage LXC containers on Proxmox servers. This eliminates the need to install Molecule and its dependencies locally.

## Files

- **`Dockerfile.molecule-proxmox`** - Docker image definition with Molecule, Ansible, and Proxmox dependencies
- **`docker-compose.molecule.yml`** - Docker Compose configuration for the testing environment
- **`run-molecule-tests.sh`** - Bash script for Linux/macOS to manage the Docker environment
- **`run-molecule-tests.ps1`** - PowerShell script for Windows to manage the Docker environment
- **`Makefile`** - Make targets for common Docker operations

## Prerequisites

1. **Docker Desktop** or Docker Engine installed
2. **Docker Compose** (usually included with Docker Desktop)
3. **Proxmox Virtual Environment** accessible from your Docker host
4. **Network connectivity** from Docker containers to Proxmox server

## Setup

### 1. Configure Environment Variables

Copy the environment template and configure your Proxmox credentials:

```bash
# Linux/macOS
cp ../molecule/proxmox/.env.example ../molecule/proxmox/.env

# Windows PowerShell
Copy-Item ..\molecule\proxmox\.env.example ..\molecule\proxmox\.env
```

Edit the `.env` file with your Proxmox server details:

```bash
# Proxmox server details
PROXMOX_HOST=your-proxmox-server.local
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=your-password

# Proxmox node configuration
PROXMOX_NODE=pve

# Container configuration
CONTAINER_ID=999
TEMPLATE=debian-12-standard_12.7-1_amd64.tar.zst
STORAGE=local-lvm
MEMORY=4096
CORES=2
```

### 2. Build the Docker Image

```bash
# Using the convenience script (Linux/macOS)
./run-molecule-tests.sh build

# Using PowerShell (Windows)
.\run-molecule-tests.ps1 build

# Using Make
make molecule-build

# Using Docker Compose directly
docker-compose -f docker-compose.molecule.yml build
```

## Usage

### Quick Start

1. **Start the environment:**
   ```bash
   ./run-molecule-tests.sh start    # Linux/macOS
   .\run-molecule-tests.ps1 start   # Windows
   ```

2. **Run a full test:**
   ```bash
   ./run-molecule-tests.sh test     # Linux/macOS
   .\run-molecule-tests.ps1 test    # Windows
   ```

3. **Stop the environment:**
   ```bash
   ./run-molecule-tests.sh stop     # Linux/macOS
   .\run-molecule-tests.ps1 stop    # Windows
   ```

### Available Commands

| Command | Description |
|---------|-------------|
| `build` | Build the Docker image |
| `start` | Start the container environment |
| `stop` | Stop and remove containers |
| `shell` | Enter the container for interactive use |
| `test [scenario]` | Run full molecule test suite |
| `create [scenario]` | Create test infrastructure only |
| `converge [scenario]` | Run Ansible playbooks only |
| `destroy [scenario]` | Destroy test infrastructure |
| `logs` | Show container logs |

### Interactive Development

Enter the container shell for interactive development and debugging:

```bash
# Linux/macOS
./run-molecule-tests.sh shell

# Windows
.\run-molecule-tests.ps1 shell

# Inside the container, you can run molecule commands directly:
cd /ansible/src
molecule list
molecule test -s proxmox
molecule create -s proxmox
molecule converge -s proxmox
molecule verify -s proxmox
molecule destroy -s proxmox
```

### Running Specific Scenarios

If you have multiple molecule scenarios, specify the scenario name:

```bash
./run-molecule-tests.sh test proxmox
./run-molecule-tests.sh create default
./run-molecule-tests.sh converge podman
```

## Docker Image Details

The `ansible-molecule-proxmox` image includes:

- **Python 3.11** - Latest stable Python runtime
- **Ansible Core 2.14+** - Latest Ansible automation platform
- **Molecule 6.0+** - Testing framework with Docker support
- **Essential collections** - community.general, ansible.posix, etc.
- **Development tools** - pytest, testinfra, yamllint, ansible-lint
- **Network tools** - SSH client, curl, wget, jq
- **Proxmox dependencies** - requests, urllib3, paramiko

## Networking

The Docker setup creates a bridge network (`molecule-network`) that allows:

- Container-to-container communication
- Container access to external Proxmox servers
- SSH connectivity to created LXC containers

Ensure your Proxmox server is accessible from the Docker host network.

## Volumes

The following volumes are mounted:

- **Project directory** (`../..:/ansible`) - Full read/write access to your Ansible project
- **SSH keys** (`~/.ssh:/home/ansible/.ssh:ro`) - Read-only access to your SSH keys
- **Molecule cache** - Persistent storage for molecule temporary files

## Security Considerations

1. **Credentials** - Store Proxmox credentials in the `.env` file, not in code
2. **Network access** - Ensure Docker containers can reach Proxmox but limit exposure
3. **SSH keys** - SSH keys are mounted read-only; consider using dedicated test keys
4. **LXC containers** - Test containers are created unprivileged by default

## Troubleshooting

### Common Issues

1. **Docker build fails:**
   - Ensure Docker Desktop is running
   - Check network connectivity for package downloads
   - Verify sufficient disk space

2. **Cannot connect to Proxmox:**
   - Verify PROXMOX_HOST and credentials in `.env`
   - Check network connectivity: `ping your-proxmox-server`
   - Ensure Proxmox API is accessible on port 8006

3. **LXC creation fails:**
   - Verify the container template exists on Proxmox
   - Check available storage space
   - Ensure CONTAINER_ID is not already in use

4. **SSH connection fails:**
   - Verify the LXC container started successfully
   - Check if SSH is enabled in the container template
   - Ensure network configuration allows SSH access

### Debugging

Enable verbose output:

```bash
# Inside the container
export MOLECULE_DEBUG=1
export ANSIBLE_VERBOSITY=3
molecule test -s proxmox
```

View container logs:

```bash
./run-molecule-tests.sh logs
```

Check molecule status:

```bash
# Inside the container
molecule list -s proxmox
molecule status -s proxmox
```

## Integration with CI/CD

This Docker setup can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Molecule Tests
  run: |
    cd src/docker
    ./run-molecule-tests.sh build
    ./run-molecule-tests.sh start
    ./run-molecule-tests.sh test
    ./run-molecule-tests.sh stop
  env:
    PROXMOX_HOST: ${{ secrets.PROXMOX_HOST }}
    PROXMOX_USER: ${{ secrets.PROXMOX_USER }}
    PROXMOX_PASSWORD: ${{ secrets.PROXMOX_PASSWORD }}
```

## Performance Tips

1. **Use local template cache** - Store frequently used LXC templates locally
2. **Persistent volumes** - Keep molecule cache between runs
3. **Parallel testing** - Run multiple scenarios with different container IDs
4. **Resource limits** - Adjust container memory/CPU based on test requirements

## Advanced Configuration

### Custom Molecule Scenarios

To test different configurations:

1. Create new scenario directories under `src/molecule/`
2. Configure scenario-specific variables in `molecule.yml`
3. Run with: `./run-molecule-tests.sh test your-scenario`

### Proxmox API Tokens

For better security, use API tokens instead of passwords:

```bash
# In .env file
PROXMOX_TOKEN_ID=your-token-id
PROXMOX_TOKEN_SECRET=your-token-secret
# Comment out PROXMOX_PASSWORD
```

### Custom Docker Networks

Modify `docker-compose.molecule.yml` to use existing networks or custom configurations.

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review molecule and Proxmox documentation
3. Verify your environment configuration
4. Check container and molecule logs for detailed error messages
