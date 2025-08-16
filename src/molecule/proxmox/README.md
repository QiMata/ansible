# Molecule Proxmox Testing

This directory contains Molecule configuration for testing Ansible roles using Proxmox LXC containers.

## Prerequisites

1. **Proxmox Server**: A running Proxmox VE server with LXC container templates
2. **Network Access**: Your machine must be able to reach the Proxmox server and created containers
3. **Debian Template**: A Debian LXC template available in Proxmox

## Setup

1. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Proxmox server details
   ```

3. **Verify Proxmox Access**:
   Make sure you can access your Proxmox server and have permissions to create/destroy LXC containers.

## Configuration

Edit the following files as needed:

- **`.env`**: Proxmox server connection details
- **`molecule.yml`**: Main Molecule configuration
- **`converge.yml`**: Your role testing playbook

## Usage

### Full Test Cycle
```bash
molecule test -s proxmox
```

### Step by Step
```bash
# Create container
molecule create -s proxmox

# Prepare container
molecule prepare -s proxmox

# Run your role/playbook
molecule converge -s proxmox

# Run verification tests
molecule verify -s proxmox

# Destroy container
molecule destroy -s proxmox
```

## Customization

### Testing Different Roles
To test a specific role, set the `target_role` variable:

```bash
molecule converge -s proxmox -- -e target_role=your_role_name
```

### Container Configuration
Modify the environment variables in `.env`:

- `CONTAINER_ID`: Unique ID for the LXC container
- `TEMPLATE`: LXC template to use
- `MEMORY`: RAM allocation (MB)
- `CORES`: CPU cores
- `STORAGE`: Proxmox storage name

### Network Configuration
The default configuration uses DHCP. For static IP, modify the `NETWORK` variable in `.env`:

```bash
NETWORK=name=eth0,bridge=vmbr0,ip=192.168.1.100/24,gw=192.168.1.1
```

## Troubleshooting

1. **Connection Issues**: Verify Proxmox credentials and network access
2. **Template Not Found**: Ensure the specified template exists in Proxmox
3. **Container Creation Fails**: Check Proxmox logs and available resources
4. **SSH Issues**: Verify the container has SSH enabled and accessible

## Multiple Instances

To run multiple test instances simultaneously, use different container IDs:

```bash
CONTAINER_ID=1001 molecule test -s proxmox
CONTAINER_ID=1002 molecule test -s proxmox
```
