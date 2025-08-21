# Ansible Tags for Vault Role

This role supports the following tags to selectively run specific parts of the deployment:

## Available Tags

### Infrastructure Tags
- `install` - Install Vault package and dependencies
- `config` - Configure Vault service and basic settings
- `storage` - Configure storage backend specific settings

### Security Tags
- `auth` - Configure authentication methods
- `policies` - Create and manage Vault policies
- `tls` - Configure TLS certificates

### Features Tags
- `secrets` - Configure secrets engines
- `monitoring` - Setup monitoring, telemetry, and audit logging
- `backup` - Configure backup and recovery scripts
- `pki` - Configure PKI secrets engine (legacy feature)

## Usage Examples

### Install and configure only basic Vault
```bash
ansible-playbook vault.yml --tags "install,config"
```

### Setup only authentication and policies
```bash
ansible-playbook vault.yml --tags "auth,policies"
```

### Configure monitoring and backup
```bash
ansible-playbook vault.yml --tags "monitoring,backup"
```

### Full deployment except PKI
```bash
ansible-playbook vault.yml --skip-tags "pki"
```

### Security-focused deployment
```bash
ansible-playbook vault.yml --tags "install,config,tls,auth,policies"
```

## Tag Dependencies

Some tags have logical dependencies:
- `auth`, `policies`, `secrets` require `install` and `config` to be run first
- `monitoring` benefits from having `config` completed
- `backup` requires the basic Vault installation

## Notes

- If no tags are specified, all tasks will run (default behavior)
- Some tasks may run regardless of tags if they're critical for basic functionality
- Use `--list-tags` to see all available tags in the playbook
