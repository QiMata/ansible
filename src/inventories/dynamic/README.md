# Proxmox Dynamic Inventory Setup

This directory contains the configuration for dynamically pulling inventory from Proxmox VE.

## Files

- `proxmox.yml` - Basic Proxmox dynamic inventory configuration
- `proxmox-vault.yml` - Vault-based configuration for secure credential storage
- `vault_proxmox.yml` - Vault variables file (encrypt with ansible-vault)
- `.env.example` - Example environment configuration

## Setup Steps

### 1. Install Required Collection

```bash
ansible-galaxy install -r ../requirements.yml
```

### 2. Configure Proxmox Credentials

#### Option A: Direct Configuration (Less Secure)
Edit `proxmox.yml` and update the connection details:
- `url`: Your Proxmox server URL
- `user`: Proxmox username (e.g., ansible@pve)
- `password`: Proxmox password

#### Option B: Vault-based Configuration (Recommended)
1. Edit `vault_proxmox.yml` with your actual credentials
2. Encrypt the file:
   ```bash
   ansible-vault encrypt vault_proxmox.yml
   ```
3. Create a vault password file or use --ask-vault-pass

#### Option C: API Token (Most Secure)
1. Create an API token in Proxmox:
   - Go to Datacenter → Permissions → API Tokens
   - Create new token for your user
2. Update the configuration to use token_id and token_secret instead of password

### 3. Create Proxmox User and Permissions

Create a dedicated user for Ansible in Proxmox:

```bash
# Create user
pveum user add ansible@pve --password <password>

# Create role with required permissions
pveum role add ansible-role -privs "VM.Audit,VM.Monitor,Datastore.Audit"

# Assign role to user
pveum aclmod / -user ansible@pve -role ansible-role
```

### 4. Test the Configuration

```powershell
# Test basic inventory
.\scripts\test-proxmox-inventory.ps1

# Test with vault
.\scripts\test-proxmox-inventory.ps1 -UseVault

# Show inventory graph
.\scripts\test-proxmox-inventory.ps1 -ShowGraph
```

### 5. Use with Playbooks

```bash
# Run playbook with dynamic inventory
ansible-playbook -i inventories/dynamic/proxmox.yml playbooks/site.yml

# With vault
ansible-playbook -i inventories/dynamic/proxmox-vault.yml --vault-password-file vault_pass.txt playbooks/site.yml
```

## Inventory Groups

The dynamic inventory will automatically create groups based on:

- **Status**: `status_running`, `status_stopped`
- **Type**: `type_qemu`, `type_lxc`
- **Tags**: `tag_<tagname>` (if you use tags in Proxmox)

## Custom Grouping

You can customize the grouping by modifying the `keyed_groups` section in the YAML files. Examples:

```yaml
keyed_groups:
  # Group by node
  - key: proxmox_node
    prefix: node
  
  # Group by pool
  - key: proxmox_pool
    prefix: pool
  
  # Group by custom property
  - key: proxmox_description | regex_search('env=(\w+)') 
    prefix: env
```

## Filtering

Use the `filters` section to include/exclude VMs:

```yaml
filters:
  # Only running VMs
  - proxmox_status == "running"
  
  # Only production VMs (based on name)
  - proxmox_name is match("^prod-.*")
  
  # Exclude test VMs
  - not (proxmox_name is match(".*-test$"))
```

## Troubleshooting

1. **Connection Issues**: Check URL, credentials, and SSL settings
2. **Permission Errors**: Ensure the Proxmox user has proper permissions
3. **No VMs Found**: Check filters and verify VMs exist in Proxmox
4. **SSL Errors**: Set `validate_certs: false` for self-signed certificates

## Migration from Static Inventory

To migrate from your existing static inventory files:

1. Tag your VMs in Proxmox to match your current groups
2. Use the dynamic inventory alongside static files during transition
3. Update playbooks to use new group names if needed
4. Test thoroughly before removing static files
