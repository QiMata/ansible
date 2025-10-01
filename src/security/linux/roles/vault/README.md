# Ansible Role: Vault

# Ansible Role: Vault

**Comprehensive HashiCorp Vault deployment** supporting multiple storage backends, authentication methods, secrets engines, high availability, monitoring, backup/recovery, and security features. This enhanced role provides enterprise-ready Vault configurations for development, staging, and production environments.

## Table of Contents

* [Overview](#ansible-role-vault)
* [Supported Platforms & Requirements](#supported-platforms--requirements)
* [Role Variables](#role-variables)
* [Storage Backends](#storage-backends)
* [Authentication Methods](#authentication-methods)
* [Secrets Engines](#secrets-engines)
* [Monitoring & Observability](#monitoring--observability)
* [Backup & Recovery](#backup--recovery)
* [High Availability](#high-availability)
* [Security Features](#security-features)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbooks](#example-playbooks)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Related Roles](#related-roles)

## Supported Platforms & Requirements

* **Operating Systems:** Debian 11 "Bullseye", Debian 12 "Bookworm", Ubuntu 20.04+
* **Ansible Version:** Requires Ansible **2.15** or higher
* **Python Requirements:** None specific on managed nodes
* **Ansible Collections:** 
  - `community.general` (>=6.0.0)
  - `ansible.posix` (>=1.3.0)
* **System Requirements:** Internet access for package downloads

## Role Variables

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `vault_version` | `"latest"` | Vault package version |
| `vault_user` | `vault` | System user for Vault |
| `vault_group` | `vault` | System group for Vault |
| `vault_addr` | `"0.0.0.0"` | Vault listen address |
| `vault_port` | `8200` | Vault listen port |
| `vault_ui` | `true` | Enable Vault Web UI |

### Storage Backends

| Variable | Default | Description |
|----------|---------|-------------|
| `vault_storage_backend` | `"file"` | Storage backend (file, raft, consul, s3, azure, gcp, mysql, postgresql) |
| `vault_file_storage_path` | `"{{ vault_data_dir }}"` | File storage path |
| `vault_raft_node_id` | `"{{ ansible_hostname }}"` | Raft node identifier |
| `vault_raft_retry_join` | `[]` | List of peers for auto-join |
| `vault_consul_address` | `"127.0.0.1:8500"` | Consul address |
| `vault_s3_bucket` | `""` | S3 bucket name |
| `vault_azure_account_name` | `""` | Azure storage account |
| `vault_gcp_bucket` | `""` | GCP storage bucket |

### Auto-Unsealing

| Variable | Default | Description |
|----------|---------|-------------|
| `vault_auto_unseal` | `false` | Enable auto-unsealing |
| `vault_auto_unseal_provider` | `""` | Provider (aws-kms, azure-keyvault, gcp-kms, transit) |
| `vault_aws_kms_region` | `""` | AWS KMS region |
| `vault_aws_kms_key_id` | `""` | AWS KMS key ID |
| `vault_azure_keyvault_name` | `""` | Azure Key Vault name |
| `vault_gcp_kms_project` | `""` | GCP KMS project |

### Authentication & Authorization

| Variable | Default | Description |
|----------|---------|-------------|
| `vault_auth_methods` | `[]` | List of authentication methods to configure |
| `vault_policies` | `[]` | List of policies to create |

### Secrets Engines

| Variable | Default | Description |
|----------|---------|-------------|
| `vault_secrets_engines` | `[]` | List of secrets engines to enable |

### Monitoring & Telemetry

| Variable | Default | Description |
|----------|---------|-------------|
| `vault_enable_telemetry` | `false` | Enable telemetry collection |
| `vault_telemetry_prometheus_retention` | `"24h"` | Prometheus metrics retention |
| `vault_audit_devices` | `[]` | List of audit devices |

### Backup & Recovery

| Variable | Default | Description |
|----------|---------|-------------|
| `vault_enable_backup` | `false` | Enable automated backups |
| `vault_backup_schedule` | `"0 2 * * *"` | Backup cron schedule |
| `vault_backup_retention_days` | `30` | Backup retention period |
| `vault_backup_s3_bucket` | `""` | S3 bucket for backup storage |

### High Availability

| Variable | Default | Description |
|----------|---------|-------------|
| `vault_enable_ha` | `false` | Enable HA configuration |
| `vault_api_addr` | `""` | API advertise address |
| `vault_ha_cluster_addr` | `""` | Cluster advertise address |

## Storage Backends

### File Storage (Default)
Simple single-node storage using local filesystem.

```yaml
vault_storage_backend: "file"
vault_file_storage_path: "/opt/vault/data"
```

### Raft Storage (Recommended for HA)
Integrated Storage providing high availability without external dependencies.

```yaml
vault_storage_backend: "raft"
vault_raft_node_id: "vault-1"
vault_raft_retry_join:
  - "https://vault-2.example.com:8200"
  - "https://vault-3.example.com:8200"
```

### Consul Storage
External Consul cluster for storage backend.

```yaml
vault_storage_backend: "consul"
vault_consul_address: "consul.example.com:8500"
vault_consul_path: "vault/"
vault_consul_token: "{{ consul_token }}"
```

### Cloud Storage
Support for AWS S3, Azure Blob, and GCP Cloud Storage.

```yaml
# AWS S3
vault_storage_backend: "s3"
vault_s3_bucket: "my-vault-storage"
vault_s3_region: "us-west-2"

# Azure Blob
vault_storage_backend: "azure"
vault_azure_account_name: "vaultstorage"
vault_azure_container: "vault"

# GCP Cloud Storage
vault_storage_backend: "gcp"
vault_gcp_bucket: "vault-storage-bucket"
```

## Authentication Methods

### LDAP/Active Directory
```yaml
vault_auth_methods:
  - name: "ldap"
    type: "ldap"
    config:
      url: "ldap://ldap.example.com"
      userdn: "ou=Users,dc=example,dc=com"
      groupdn: "ou=Groups,dc=example,dc=com"
      binddn: "cn=vault,ou=Service Accounts,dc=example,dc=com"
      bindpass: "{{ ldap_password }}"
```

### OIDC/JWT
```yaml
vault_auth_methods:
  - name: "oidc"
    type: "oidc"
    config:
      oidc_discovery_url: "https://auth.example.com/.well-known/openid_configuration"
      oidc_client_id: "vault"
      oidc_client_secret: "{{ oidc_secret }}"
```

### Kubernetes
```yaml
vault_auth_methods:
  - name: "kubernetes"
    type: "kubernetes"
    config:
      kubernetes_host: "https://kubernetes.default.svc.cluster.local"
      kubernetes_ca_cert: "{{ k8s_ca_cert }}"
```

### AWS IAM
```yaml
vault_auth_methods:
  - name: "aws"
    type: "aws"
    config:
      access_key: "{{ aws_access_key }}"
      secret_key: "{{ aws_secret_key }}"
      region: "us-west-2"
```

## Secrets Engines

### Key-Value v2
```yaml
vault_secrets_engines:
  - name: "kv"
    type: "kv-v2"
    path: "secret"
    max_versions: 10
```

### Database Secrets
```yaml
vault_secrets_engines:
  - name: "database"
    type: "database"
    path: "database"
    connections:
      - name: "postgres"
        plugin_name: "postgresql-database-plugin"
        connection_url: "postgresql://vault:{{password}}@postgres:5432/mydb"
```

### AWS Secrets
```yaml
vault_secrets_engines:
  - name: "aws"
    type: "aws"
    path: "aws"
    access_key: "{{ aws_access_key }}"
    secret_key: "{{ aws_secret_key }}"
```

### SSH Secrets
```yaml
vault_secrets_engines:
  - name: "ssh"
    type: "ssh"
    path: "ssh"
    generate_signing_key: true
```

### Transit Encryption
```yaml
vault_secrets_engines:
  - name: "transit"
    type: "transit"
    path: "transit"
    keys:
      - name: "app-encryption"
        type: "aes256-gcm96"
```

## Monitoring & Observability

### Prometheus Metrics
```yaml
vault_enable_telemetry: true
vault_telemetry_prometheus_retention: "24h"
```

### Audit Logging
```yaml
vault_audit_devices:
  - name: "file"
    type: "file"
    path: "/var/log/vault/audit.log"
    format: "json"
  - name: "syslog"
    type: "syslog"
    facility: "AUTH"
```

### Health Monitoring
The role creates health check scripts:
- `/usr/local/bin/vault_health_check.sh` - Automated health checks
- Cron job for continuous monitoring
- Integration with Prometheus metrics

## Backup & Recovery

### Automated Backups
```yaml
vault_enable_backup: true
vault_backup_schedule: "0 2 * * *"  # Daily at 2 AM
vault_backup_retention_days: 30
vault_backup_s3_bucket: "vault-backups"
```

### Backup Scripts
- `/usr/local/bin/vault_backup.sh` - Create backups
- `/usr/local/bin/vault_restore.sh` - Restore from backup
- `/usr/local/bin/vault_backup_verify.sh` - Verify backup integrity

### Disaster Recovery
Complete disaster recovery documentation is automatically generated at `{{ vault_config_dir }}/disaster_recovery.md`.

## High Availability

### Raft Cluster Configuration
```yaml
vault_storage_backend: "raft"
vault_enable_ha: true
vault_api_addr: "https://{{ ansible_default_ipv4.address }}:8200"
vault_ha_cluster_addr: "https://{{ ansible_default_ipv4.address }}:8201"
vault_raft_retry_join:
  - "https://vault-1.example.com:8200"
  - "https://vault-2.example.com:8200"
```

### Auto-Unsealing
```yaml
vault_auto_unseal: true
vault_auto_unseal_provider: "aws-kms"
vault_aws_kms_key_id: "alias/vault-unseal"
```

## Security Features

### TLS Configuration
```yaml
vault_tls_cert_src: "/path/to/vault.crt"
vault_tls_key_src: "/path/to/vault.key"
```

### Advanced Security
```yaml
vault_disable_mlock: false          # Enable memory locking
vault_entropy_augmentation: true    # Hardware entropy
vault_seal_wrap: true              # Additional encryption
```

### Policy Management
```yaml
vault_policies:
  - name: "admin"
    policy: |
      path "*" {
        capabilities = ["create", "read", "update", "delete", "list", "sudo"]
      }
```

## Example Playbooks

### Basic Single-Node Deployment
```yaml
- hosts: vault_server
  become: true
  roles:
    - vault
```

### HA Cluster with Raft
```yaml
- hosts: vault_cluster
  become: true
  vars:
    vault_storage_backend: "raft"
    vault_enable_ha: true
    vault_auto_unseal: true
    vault_auto_unseal_provider: "aws-kms"
    vault_aws_kms_key_id: "alias/vault-unseal"
  roles:
    - vault
```

### Enterprise Configuration
See `examples/vault_enhanced.yml` for a comprehensive enterprise deployment example.

## Testing Instructions

### Molecule Testing
```bash
# Test with Docker
molecule test

# Test with Podman
molecule test -s podman

# Test specific scenario
molecule test -s proxmox
```

### Manual Testing
1. Verify installation: `vault version`
2. Check health: `/usr/local/bin/vault_health_check.sh`
3. Test backup: `/usr/local/bin/vault_backup.sh`
4. Verify backup: `/usr/local/bin/vault_backup_verify.sh`

## Known Issues and Gotchas

### Storage Backend Considerations
- **File Storage**: Not suitable for production HA
- **Raft Storage**: Requires odd number of nodes (3 or 5 recommended)
- **Consul Storage**: External dependency, ensure Consul HA
- **Cloud Storage**: Requires proper IAM permissions

### Auto-Unsealing
- Requires proper cloud provider authentication
- Test unsealing process thoroughly
- Have manual unseal procedures as backup

### Backup & Recovery
- Test restore procedures regularly
- Raft snapshots require Vault to be running
- File-based backups can be taken with Vault stopped

## Security Implications

### Network Security
- Use TLS for all communications
- Restrict network access to Vault ports
- Consider using reverse proxy for additional security

### Authentication
- Use strong authentication methods (not userpass for production)
- Implement proper RBAC with policies
- Regular rotation of credentials

### Monitoring
- Enable audit logging for compliance
- Monitor for suspicious activities
- Set up alerting for health check failures

## Related Roles

- `consul` - For Consul storage backend
- `prometheus` - For metrics collection
- `nginx` - For reverse proxy/load balancing

---

**Note**: This role provides extensive configuration options. Start with basic configuration and gradually enable advanced features as needed.

## Table of Contents

* [Overview](#ansible-role-vault)
* [Supported Platforms & Requirements](#supported-platforms--requirements)
* [Role Variables](#role-variables)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Related Roles](#related-roles)

## Supported Platforms & Requirements

* **Operating Systems:** Debian 11 “Bullseye” and Debian 12 “Bookworm” (confirmed support in role metadata). Other Debian-based systems may work but are not explicitly tested.
* **Ansible Version:** Requires Ansible **2.15** or higher for full compatibility.
* **Python Requirements:** None specific on the managed node (the Vault binary and CLI are installed via package manager).
* **Ansible Collections:** None required – all modules used are included in Ansible Core (e.g. `apt`, `apt_key`, `service`, etc.).
* **System Requirements:** Internet access from the target node to HashiCorp’s APT repository (`apt.releases.hashicorp.com`) to download Vault. The role will automatically install needed APT packages (like **gnupg** and **apt-transport-https** for repository management).

## Role Variables

<details><summary>**Default Variables (from `defaults/main.yml`)**</summary>

| Variable                                                | Default Value                | Description                                                                                                                                                                                                                                                  |
| ------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `vault_version`                                         | `"latest"`                   | Vault package version to install. By default, the latest available version is installed. You can pin this to a specific version number (e.g. `"1.13.2"`).                                                                                                    |
| **Service and Directories**                             |                              |                                                                                                                                                                                                                                                              |
| `vault_user`                                            | `vault`                      | System user account under which Vault will run. The role creates this user (with no login shell) if it doesn’t exist.                                                                                                                                        |
| `vault_group`                                           | `vault`                      | System group for Vault file ownership.                                                                                                                                                                                                                       |
| `vault_config_dir`                                      | `/etc/vault`                 | Directory for Vault configuration files (e.g. the main `vault.hcl`).                                                                                                                                                                                         |
| `vault_data_dir`                                        | `/opt/vault/data`            | Directory for Vault data file storage (uses the **file storage** backend by default). Note: This default (file storage) is for single-node usage; see **Gotchas** below for HA considerations.                                                               |
| `vault_tls_dir`                                         | `{{ vault_config_dir }}/tls` | Directory to store TLS certificate and key for Vault.                                                                                                                                                                                                        |
| `vault_service_name`                                    | `vault`                      | Name of the systemd service to manage (Vault’s service). Generally should remain `vault` (the service installed by the Debian package).                                                                                                                      |
| **Networking**                                          |                              |                                                                                                                                                                                                                                                              |
| `vault_addr`                                            | `"0.0.0.0"`                  | Network address on which Vault will listen. Default is all interfaces (`0.0.0.0`), but you may restrict it (e.g. `127.0.0.1` for local-only).                                                                                                                |
| `vault_port`                                            | `8200`                       | TCP port for Vault’s listener (default Vault port **8200**). Make sure this port is allowed in your firewall for intended clients.                                                                                                                           |
| `vault_ui`                                              | `true`                       | Whether to enable the Vault Web UI. When `true`, the UI will be accessible at `http(s)://<address>:8200/ui`.                                                                                                                                                 |
| **TLS Settings** (Vault listener)                       |                              |                                                                                                                                                                                                                                                              |
| `vault_tls_cert_src`                                    | `""` (empty string)          | Path to an existing TLS **certificate** file to use for Vault’s listener. If left empty, Vault will **disable TLS** and listen via plain HTTP. **Recommended:** provide a certificate (and key) or use a reverse proxy for encryption in production.         |
| `vault_tls_key_src`                                     | `""` (empty string)          | Path to the TLS **private key** file for Vault’s listener. Must be provided if `vault_tls_cert_src` is set. Empty by default (TLS disabled).                                                                                                                 |
| **PKI Integration** (Vault as CA)                       |                              |                                                                                                                                                                                                                                                              |
| `vault_enable_pki`                                      | `false`                      | Whether to configure Vault’s PKI secrets engine and integration with an external CA (Smallstep *step-ca*). If `true`, the role will set up the PKI engine and either generate or import a CA certificate as per `vault_pki_mode`.                            |
| `vault_pki_mode`                                        | `"ra"`                       | Mode for Vault PKI integration. Options: **`"ra"`** (Vault as *Registration Authority* with an *upstream* CA) or **`"intermediate"`** (Vault as an intermediate CA with an upstream root). See **PKI Integration** in the Overview for details on each mode. |
| `vault_pki_common_name`                                 | `"Vault Intermediate CA"`    | Common Name for the root or intermediate CA certificate. Used when generating a CSR for intermediate mode (default name is “Vault Intermediate CA”). Change to match your organization/purpose.                                                              |
| `vault_pki_max_ttl`                                     | `"43800h"`                   | The maximum TTL (time-to-live) for certificates issued by Vault’s PKI (in hours). Default is 43800h (5 years). Adjust as needed for your PKI policy.                                                                                                         |
| **Step CA Integration** (when `vault_pki_mode == "ra"`) |                              |                                                                                                                                                                                                                                                              |
| `vault_stepca_role`                                     | `stepca-role`                | Name of the role to create in Vault’s PKI for the Step CA to use. The same name is used for the Vault AppRole authentication role.                                                                                                                           |
| `vault_stepca_policy`                                   | `smallstep`                  | Name of the Vault policy to create for Step CA. This policy will permit signing and issuing certificates (and revocation) for the specified role.                                                                                                            |
| `vault_stepca_token_ttl`                                | `"24h"`                      | Time-to-live for the Vault AppRole token that Step CA will use. After this period, Step CA will need to re-authenticate to Vault (choose a value aligning with your security requirements).                                                                  |

</details>

**Notes:** Refer to the role’s **`defaults/main.yml`** (and inline comments) for the full list of defaults. Generally, out-of-the-box defaults install Vault with a file storage backend and no TLS (unless you provide certs). Most defaults are suitable for a single-node development or testing setup; in production, you will likely override at least the network and TLS settings.

## Tags

This role does **not define any special Ansible tags** for its tasks. All tasks run by default when the role is applied. You do not need to specify any tags to use the role.

* *If you want to control or limit the execution of certain parts of this role, you can apply your own tags at playbook level.* For example, you might tag the role as `vault` in your play and then use `--tags vault` or `--skip-tags vault` when running Ansible. By default, however, there are no built-in tags to toggle sub-sections of this role.

## Dependencies

**None.** This role has no dependencies on other Ansible roles or collections (no role dependencies are listed in `meta/main.yml`). All required functionality is self-contained:

* **Ansible Modules:** Uses only standard modules from Ansible core (such as `ansible.builtin.apt`, `ansible.builtin.template`, etc.), so no additional Galaxy collections need to be installed.
* **System Packages:** The role will ensure necessary system packages are present. For example, it installs `gnupg` and `apt-transport-https` to add HashiCorp’s APT repository, and then installs the `vault` package from that repo. You do not need to pre-install anything aside from having a Debian system with internet access.

## Example Playbook

**Basic usage example:**

```yaml
- hosts: vault_servers
  become: yes  # Run with privilege to install packages and configure system
  roles:
    - vault
```

In the above simplest case, the role will install Vault with default settings: it will listen on port 8200 on all interfaces **without TLS** (since no certs provided), using the file storage at `/opt/vault/data`, and start the Vault service.

**Customized example with TLS and PKI:**

```yaml
- hosts: vault_servers
  become: yes
  vars:
    vault_tls_cert_src: "files/vault.example.com.crt"       # Path to your SSL cert
    vault_tls_key_src: "files/vault.example.com.key"         # Path to the corresponding key
    vault_enable_pki: true
    vault_pki_mode: "intermediate"
    vault_pki_common_name: "Example Corp Vault CA"
  roles:
    - vault
```

In this example, Vault will be installed and configured to use your provided TLS certificate for secure HTTPS access. It also enables the PKI engine in **intermediate** mode, meaning Vault will generate a Certificate Signing Request for an intermediate CA with Common Name “Example Corp Vault CA”. (You would then need to sign that CSR with your root CA — see **Known Issues** below.)

These examples assume you have defined a host group `vault_servers` in your inventory. Adjust host names/groups as needed.

## Testing Instructions

This role can be tested locally using **Molecule** (with the Docker driver) to simulate the target environment:

1. **Install Molecule and Dependencies:** Ensure you have Docker installed, then install Molecule and its Docker plugin, for example:

   ```bash
   pip install molecule molecule[docker]
   ```

2. **Run the Molecule test scenario:** Navigate to the role directory (e.g. `roles/vault` in the repository), and run:

   ```bash
   molecule test
   ```

   This will build a Docker container (Debian), apply the role, and run any verify tests (if configured). Molecule will report if the role converged successfully.

   * You can run steps individually for debugging: use `molecule converge` to apply the role, then `molecule verify` to run checks. Use `molecule login` to drop into the container for manual inspection if needed.

3. **Example CLI Usage:**

   * To test on Debian Bookworm: you might configure Molecule’s base image in `molecule/default/molecule.yml` to use a Bookworm image, then run `molecule converge`.
   * To clean up environments: use `molecule destroy` when done testing.

> **Note:** If no Molecule scenario is present for this role, you can create one using `molecule init scenario -r vault -d docker` and then adjust the default scenario to suit Debian testing. The repository’s Continuous Integration may also run Molecule tests for pull requests.

## Known Issues and Gotchas

* **Vault Initialization & Unsealing:** *This role does not automatically initialize or unseal Vault.* After the role runs, Vault will be installed and started, but in an **uninitialized, sealed state**. You must manually initialize Vault (e.g. run `vault operator init` on the Vault host or via Ansible) and then unseal it using the provided keys (or configure auto-unsealing via a cloud KMS if desired). Until unsealed, Vault’s API will return a 501/503 status (the role’s PKI setup tasks account for a 501 “not initialized” status but will not progress if Vault remains sealed). In short, **remember to init/unseal Vault** after using this role, otherwise Vault will not be usable.

* **No HA Storage Backend by Default:** The default storage backend is **file storage** on the local filesystem. This is **not** highly available – only suitable for single-node Vault instances or testing. If you need a HA setup (clustered Vault), you should configure a different storage backend (e.g. Integrated Storage/Raft or Consul) manually. You can override the configuration by providing a custom `vault.hcl` (e.g. via extra tasks or by modifying the template) to use Raft or Consul, but that is not handled out-of-the-box by this role.

* **PKI Intermediate Mode Requires External Signer:** When `vault_pki_mode: "intermediate"`, the role will generate an intermediate CA CSR and save it to `/tmp/vault_intermediate.csr` on the Vault host. **It is your responsibility to have this CSR signed by your root CA** (e.g. a Step CA or other internal CA). The role does *not* automatically handle the signing. After you sign the CSR externally, place the resulting certificate at `/tmp/vault_intermediate.crt` on the Vault host **before rerunning the play** (or run just the `vault` role again). The role will then import that certificate into Vault. If the certificate file is missing, the run will fail. (This process is usually facilitated by pairing this role with a **step-ca** role – see **Related Roles**.)

* **PKI “RA” Mode Requires Step CA Configuration:** If `vault_pki_mode: "ra"`, the role configures Vault to serve as an **upstream CA** (root) and creates a Vault AppRole for Step CA to use. However, you will need to configure your Step CA (Smallstep Certificate Authority) to use Vault as its CA. This typically involves setting up Step CA with a **Vault provisioner** (using the AppRole credentials and policy created by this role). The role doesn’t configure Step CA itself – it only prepares Vault. Ensure you retrieve the Vault AppRole **RoleID** and **SecretID** (e.g. via `vault read auth/approle/role/stepca-role/role-id` etc.) and update your Step CA config accordingly. Without configuring Step CA, simply enabling `ra` mode in this role will not complete the integration.

* **Firewall and Network Gotcha:** The role does **not configure any firewall**. Vault is set to listen on `0.0.0.0:8200` by default, which means it will be accessible on all network interfaces. In a production environment, ensure you have firewall rules or security groups restricting access to port 8200 to only trusted sources. If you want Vault to listen only on a specific interface (e.g. localhost), set `vault_addr` accordingly (for example, `vault_addr: "127.0.0.1"` to restrict to loopback).

* **Vault Service User:** The role creates a `vault` system user and group for running the service, but the official Vault Debian package’s systemd service may still run as root by default. Check the service configuration after installation – if it’s running as root and you prefer it to run as the `vault` user, you might need to adjust the systemd service file or use a drop-in to specify `User=vault` (the package currently does not do this automatically). Running Vault as a non-root user is a security best practice (the role lays the groundwork by creating the user and file ownerships).

* **Existing Data or Config:** If you run this role on a host that already has Vault data or configuration, be cautious. The role will overwrite the main config file (`vault.hcl`) and ensure certain directories exist with proper permissions. It will not delete existing data in `vault_data_dir`, but always back up any important config or data before rerunning in production just in case.

## Security Implications

Deploying Vault entails handling sensitive secrets. This role aims to follow security best practices, but you should be aware of the following:

* **TLS Encryption:** By default, if you do not supply `vault_tls_cert_src` and `vault_tls_key_src`, the role will configure Vault to **disable TLS** on its listener. This means Vault will accept unencrypted HTTP connections on port 8200. **This is insecure for any production use.** Always use TLS in production – either by providing a certificate/key to the role or by running Vault behind a TLS-terminating reverse proxy. If using a self-signed or internal CA cert, ensure clients trust that CA.

* **Firewall & Access Control:** Because Vault may listen on all interfaces, restrict network access to Vault’s port. Only allow trusted IPs or hosts (e.g. your application servers or administrators) to connect. Consider using network segmentation or firewall rules to protect Vault. Vault’s own policies will protect secrets, but preventing unauthorized network access is the first line of defense.

* **Vault Root Token & Unseal Keys:** When you initialize Vault, you will receive an initial **root token** and **unseal key(s)**. Treat these as highly sensitive secrets. This role does not manage those – it’s up to you to secure them. Best practice is to **unseal Vault using secure methods** (for example, initialize with Shamir’s key shares distributed to trusted operators, or use auto-unseal with a cloud KMS) and then store those keys in a secure manner (offline or in a secure vault). Remove unseal keys from the server file system after use. **Do not hardcode these secrets in playbooks**; handle them interactively or via Ansible Vault/encrypted vars if automation is needed.

* **File Permissions:** All Vault data and config files are owned by the `vault:vault` user/group and restricted to mode 0750 or stricter by this role. This prevents casual access by other users on the system. Do not loosen these permissions. The Vault TLS private key (`vault.key`) is set to 0600 for `vault` user only. Ensure any custom files you provide (certs/keys) also have appropriate permissions. Only privileged users or the vault service account should be able to read secret material.

* **Disable_mlock Setting:** The Vault config generated by this role **disables mlock** (`disable_mlock = true` in `vault.hcl`). This allows Vault to start without the ability to mlock memory. The reason is that enabling mlock often requires additional system configuration (give the Vault process the `IPC_LOCK` capability or running as root). The trade-off is that with mlock disabled, sensitive data in memory could be swapped to disk. For production, it’s recommended to enable mlock if possible (remove `disable_mlock` or set it to false) and grant the Vault service user permission to lock memory (e.g., via `/etc/security/limits.conf` and appropriate capabilities). This will prevent Vault from writing sensitive cryptographic material to swap.

* **Step CA Credentials (if using RA mode):** In the RA integration scenario, Vault creates an AppRole and policy for Step CA. The credentials (RoleID and SecretID) for that AppRole effectively become a **key to issue certificates** from Vault. Protect these credentials. Treat the SecretID like a password – it should be stored securely (e.g., in Step CA’s configuration which itself should be secured and not exposed). Rotate the SecretID if you suspect it may have been exposed (you can regenerate AppRole secrets in Vault).

* **Regular Updates:** HashiCorp releases Vault updates addressing security and functionality. Since this role installs a specific version (or latest), keep an eye on Vault releases. If using `vault_version: "latest"`, you will get updates when you run the role again, but you should still plan maintenance windows for Vault upgrades. Always read Vault release notes for any breaking changes or critical fixes.

By considering the above points and following Vault’s best practices, you can operate the Vault service more securely.

## Related Roles

* **Step CA (Smallstep Certificate Authority):** If you intend to use the PKI integration features of this Vault role, you will likely also deploy a **Step CA**. While this repository’s scope is Vault, a complementary Ansible role (or collection) for installing and configuring *step-ca* is recommended. For example, you might have a role `step_ca` in your repository or use a community role to set up the Smallstep CA. The Vault role’s PKI integration is designed to work hand-in-hand with Step CA:

  * In *intermediate mode*, Step CA serves as the root CA that signs Vault’s intermediate certificate.
  * In *RA mode*, Step CA is configured to delegate certificate signing to Vault via the AppRole credentials.

  Ensure you refer to the documentation of your Step CA role for setup instructions. (For instance, you may need to add a Vault provisioner in `step-ca` with the role and policy created by this role.)

* **Consul or Storage Backend Roles:** For a more robust HA Vault setup, you might integrate Vault with a backend like Consul (for storage/locking) or etcd. This repository might contain roles such as `consul` or `etcd`. While not explicitly required, using them in combination with the Vault role can enable storage backends. (E.g., use a Consul role to set up a cluster, then override Vault’s config to point to Consul as the storage backend.)

* **Roles Consuming Vault Secrets:** Other roles in this repository may utilize Vault for secrets management. For example, a **Keycloak** role or a **PostgreSQL** role might retrieve database passwords or credentials from Vault. Those roles might assume Vault is already set up. You can use this Vault role to prepare Vault, then other roles can be run to store or fetch secrets. (Look for documentation in those roles about Vault integration. For instance, if a role mentions variables like `vault_*_password`, it likely expects Vault to hold those secrets – you would load them into Vault accordingly.)

* **Common/Baseline Roles:** If your playbooks include a common setup role (for users, updates, etc.), run it before the Vault role. There are no direct links, but for example a “base” role that hardens the server or sets up firewalls might be relevant. In that case, ensure any firewall opened for Vault’s port is configured there.

**Cross-references:** The above roles are not prerequisites but can be part of a complete stack. See the repository documentation or each role’s README for how they can complement the Vault role. Always apply roles in a logical order (e.g., install Consul before configuring Vault to use Consul, initialize Vault before other roles attempt to read from it, etc.).

