# Proxmox Dynamic Inventory Implementation Guide

## Summary

To replace your static inventory files with dynamic Proxmox inventory, I've created several configuration files and scripts. Here's what you need to do:

## Quick Setup (Recommended)

### 1. Set Environment Variables

Create a PowerShell profile or set these variables in your session:

```powershell
$env:PROXMOX_URL = "https://your-proxmox-server:8006"
$env:PROXMOX_USER = "ansible@pve"  # or ansible@pam
$env:PROXMOX_PASSWORD = "your-password"
$env:PROXMOX_VALIDATE_CERTS = "false"  # if using self-signed certs
```

### 2. Install Required Packages

Since the standard ansible-galaxy has Windows compatibility issues, install manually:

```powershell
# Install Python packages
pip install ansible proxmoxer requests

# Download required collections manually:
# 1. Download community.general: https://galaxy.ansible.com/community/general
#    Extract to: src/collections/ansible_collections/community/general/
# 2. Download community.proxmox: https://galaxy.ansible.com/community/proxmox
#    Extract to: src/collections/ansible_collections/community/proxmox/
```
Use the environment-based configuration file I created:

```powershell
cd src
ansible-inventory -i inventories/dynamic/proxmox-env.yml --list
```

## Configuration Files Created

1. **`inventories/dynamic/proxmox.yml`** - Basic configuration with hardcoded credentials
2. **`inventories/dynamic/proxmox-env.yml`** - Environment variable based (recommended)
3. **`inventories/dynamic/proxmox-vault.yml`** - Ansible vault based
4. **`inventories/dynamic/vault_proxmox.yml`** - Vault variables file
5. **`inventories/dynamic/README.md`** - Comprehensive documentation

## Proxmox Setup Requirements

### Create Ansible User in Proxmox

1. Access Proxmox web interface
2. Go to Datacenter → Permissions → Users
3. Add user: `ansible@pve` (or `ansible@pam` for local auth)
4. Go to Datacenter → Permissions → API Tokens (recommended for security)
5. Create API token for the ansible user

### Set Permissions

The ansible user needs these permissions:
- VM.Audit (to read VM information)
- VM.Monitor (to check VM status)  
- Datastore.Audit (to read datastore info)

```bash
# If you have CLI access to Proxmox:
pveum role add ansible-role -privs "VM.Audit,VM.Monitor,Datastore.Audit"
pveum aclmod / -user ansible@pve -role ansible-role
```

## Migration Strategy

### Phase 1: Parallel Operation
1. Keep your existing static inventory files
2. Test the dynamic inventory alongside them
3. Use specific inventory files for testing: `ansible-playbook -i inventories/dynamic/proxmox-env.yml`

### Phase 2: Group Mapping
1. Tag your VMs in Proxmox to match your current group structure
2. Update the `keyed_groups` section in the YAML files to create groups that match your current structure

### Phase 3: Full Migration
1. Update `ansible.cfg` to point to the dynamic inventory
2. Remove old static inventory files
3. Update documentation and scripts

## Testing Commands

```powershell
# Test connection to Proxmox
python -c "from proxmoxer import ProxmoxAPI; print('Proxmoxer library OK')"

# List all hosts from dynamic inventory
ansible-inventory -i inventories/dynamic/proxmox-env.yml --list

# Show inventory graph
ansible-inventory -i inventories/dynamic/proxmox-env.yml --graph

# Test with a simple ping
ansible all -i src/inventories/dynamic/proxmox-env.yml -m ping

# Run a playbook with dynamic inventory
ansible-playbook -i src/inventories/dynamic/proxmox-env.yml src/playbooks/site.yml
```

## Troubleshooting

### Common Issues

1. **"Plugin not found"**: Install community.proxmox collection (and community.general for module support)
2. **"Connection refused"**: Check Proxmox URL and firewall
3. **"Authentication failed"**: Verify credentials and permissions
4. **"No hosts found"**: Check filters and VM status in Proxmox

### Debug Mode

Add these to your inventory YAML for debugging:
```yaml
# Enable debug logging
debug: true

# Show all VMs regardless of status
filters: []
```

## Security Recommendations

1. **Use API Tokens** instead of passwords
2. **Use Environment Variables** instead of hardcoded credentials
3. **Use Ansible Vault** for production environments
4. **Restrict Proxmox user permissions** to minimum required

## Next Steps

1. Set up your Proxmox credentials
2. Install the community.general and community.proxmox collections manually
3. Test the dynamic inventory
4. Gradually migrate your playbooks
5. Remove static inventory files once everything works

The dynamic inventory will automatically discover all your VMs and create groups based on their status, type, and tags, making your infrastructure more maintainable and up-to-date.

