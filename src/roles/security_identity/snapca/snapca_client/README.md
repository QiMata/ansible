# Ansible Role: SnapCA Client

## Overview

The **SnapCA Client** role automates obtaining and renewing SSL/TLS certificates from a **Smallstep Step CA** (Certificate Authority) server. It installs the Step CLI client on your server, configures it to communicate with your Step CA, and obtains certificates using various provisioner types (JWK, OIDC, ACME, etc.). This role handles bootstrapping the client with the CA root certificate, certificate issuance, and renewal setup. Key features include:

- **Step CLI Installation:** Installs the official Smallstep CLI tool from the APT repository
- **CA Bootstrap:** Automatically downloads and trusts the Step CA root certificate
- **Multiple Provisioner Support:** Supports JWK tokens, OIDC, ACME, and password-based provisioners
- **Certificate Lifecycle:** Handles certificate issuance, renewal, and automated renewal via cron
- **Flexible Configuration:** Supports single and multiple domain certificates
- **Service Integration:** Can reload services after certificate renewal

## When to Use This Role

Use this role when:
- You have a Step CA server running and need to obtain certificates from it
- You want automated certificate management for your services
- You need certificates for internal services or private PKI
- You prefer Step CA over Let's Encrypt for your certificate management

**Comparison with Let's Encrypt roles:**
| Feature | Let's Encrypt | SnapCA Client (This Role) |
|---------|---------------|---------------------------|
| **Certificate Source** | Public Let's Encrypt CA | Private Step CA |
| **Trust** | Publicly trusted | Internal/private trust |
| **Network Requirements** | Internet access required | Internal network access |
| **Challenge Methods** | HTTP-01, DNS-01 | JWK tokens, OIDC, ACME |
| **Setup Complexity** | Simple (public CA) | Requires Step CA setup |
| **Best For** | Public-facing services | Internal services, private PKI |

## Supported Operating Systems/Platforms

This role is designed for **Debian-based Linux distributions** and has been tested on:

- **Debian 11 (Bullseye)** and **Debian 12 (Bookworm)**
- **Ubuntu LTS releases** (20.04, 22.04, 24.04)

The role uses APT for package management and systemd for service management.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| **Step CA Configuration** | | |
| `snapca_client_ca_url` | `""` | **Required.** Step CA server URL (e.g., `https://ca.example.com:8443`) |
| `snapca_client_ca_fingerprint` | `""` | **Optional.** CA root certificate fingerprint for verification |
| `snapca_client_provisioner` | `"admin"` | Provisioner name to use for certificate requests |
| `snapca_client_provisioner_type` | `"jwk"` | Type of provisioner: `jwk`, `oidc`, `acme`, `password` |
| **Certificate Configuration** | | |
| `snapca_client_domains` | `[]` | **Required.** List of domain names for the certificate |
| `snapca_client_san` | `[]` | Additional Subject Alternative Names |
| `snapca_client_certificate_path` | `"/etc/ssl/certs"` | Directory to store certificates |
| `snapca_client_certificate_name` | `"{{ snapca_client_domains[0] }}"` | Base name for certificate files |
| `snapca_client_key_size` | `2048` | RSA key size for certificate |
| **Authentication** | | |
| `snapca_client_token` | `""` | JWK token for authentication (when using JWK provisioner) |
| `snapca_client_password` | `""` | Password for password-based provisioner |
| `snapca_client_oidc_client_id` | `""` | OIDC client ID (when using OIDC provisioner) |
| `snapca_client_oidc_client_secret` | `""` | OIDC client secret (when using OIDC provisioner) |
| **Renewal Configuration** | | |
| `snapca_client_enable_renewal` | `true` | Enable automatic certificate renewal |
| `snapca_client_renewal_threshold` | `"30d"` | Renew certificates when they expire within this time |
| `snapca_client_renewal_cron_hour` | `"2"` | Hour to run renewal cron job |
| `snapca_client_renewal_cron_minute` | `"30"` | Minute to run renewal cron job |
| **Service Integration** | | |
| `snapca_client_reload_services` | `[]` | List of services to reload after certificate renewal |
| `snapca_client_post_renewal_commands` | `[]` | List of commands to run after certificate renewal |

## Tags

This role supports the following tags for selective execution:

- `snapca_install` - Install Step CLI and dependencies
- `snapca_bootstrap` - Bootstrap CA connection and trust
- `snapca_certificate` - Certificate issuance tasks
- `snapca_renewal` - Certificate renewal configuration
- `snapca_service` - Service integration and post-renewal actions

## Dependencies

- **Step CA Server:** A running Step CA server with configured provisioners
- **Network Access:** Client must be able to reach the Step CA server
- **DNS Resolution:** Domain names must resolve correctly if using domain validation

## Example Playbook

### Basic Usage with JWK Token

```yaml
- hosts: web_servers
  become: true
  roles:
    - role: security_identity.snapca.snapca_client
      vars:
        snapca_client_ca_url: "https://ca.internal.example.com:8443"
        snapca_client_domains:
          - "web.internal.example.com"
        snapca_client_token: "your-jwk-token-here"
        snapca_client_reload_services:
          - nginx
          - apache2
```

### OIDC Authentication

```yaml
- hosts: api_servers
  become: true
  roles:
    - role: security_identity.snapca.snapca_client
      vars:
        snapca_client_ca_url: "https://ca.internal.example.com:8443"
        snapca_client_provisioner_type: "oidc"
        snapca_client_provisioner: "google"
        snapca_client_domains:
          - "api.internal.example.com"
        snapca_client_oidc_client_id: "your-oidc-client-id"
        snapca_client_oidc_client_secret: "your-oidc-client-secret"
```

### ACME Protocol

```yaml
- hosts: acme_clients
  become: true
  roles:
    - role: security_identity.snapca.snapca_client
      vars:
        snapca_client_ca_url: "https://ca.internal.example.com:8443"
        snapca_client_provisioner_type: "acme"
        snapca_client_provisioner: "acme"
        snapca_client_domains:
          - "service.internal.example.com"
          - "service2.internal.example.com"
```

### Multi-Domain Certificate with Custom Paths

```yaml
- hosts: load_balancers
  become: true
  roles:
    - role: security_identity.snapca.snapca_client
      vars:
        snapca_client_ca_url: "https://ca.internal.example.com:8443"
        snapca_client_domains:
          - "lb1.internal.example.com"
          - "lb.internal.example.com"
        snapca_client_san:
          - "10.0.1.100"
          - "10.0.1.101"
        snapca_client_certificate_path: "/etc/haproxy/certs"
        snapca_client_certificate_name: "haproxy"
        snapca_client_token: "your-jwk-token-here"
        snapca_client_reload_services:
          - haproxy
        snapca_client_post_renewal_commands:
          - "systemctl reload haproxy"
```

## Testing Instructions

### Molecule Testing

This role includes Molecule scenarios for testing:

```bash
# Test with default scenario
cd roles/security_identity/snapca/snapca_client
molecule test

# Test specific scenario
molecule test -s default
```

### Manual Testing

1. **Set up a Step CA server** (use the `step_ca` role from infrastructure/shared)
2. **Configure a provisioner** on the Step CA
3. **Run this role** with appropriate variables
4. **Verify certificate creation:**
   ```bash
   ls -la /etc/ssl/certs/
   openssl x509 -in /etc/ssl/certs/your-domain.crt -text -noout
   ```

## Known Issues and Gotchas

- **Step CA Must Be Running:** The Step CA server must be accessible and properly configured before running this role
- **Provisioner Configuration:** Ensure the specified provisioner exists and is properly configured on the Step CA
- **Token Expiration:** JWK tokens have expiration times; ensure tokens are valid when running the role
- **Network Connectivity:** Client must be able to reach the Step CA server on the specified port
- **DNS Resolution:** If using domain validation, ensure DNS is properly configured
- **File Permissions:** Certificate files are created with restrictive permissions (600 for private keys)

## Security Implications

- **Private Keys:** Private keys are stored on the target host and should be protected appropriately
- **Token Storage:** JWK tokens and passwords are sensitive; use Ansible Vault for production deployments
- **CA Trust:** This role adds the Step CA as a trusted root; ensure you trust the CA operator
- **Network Security:** Communications with Step CA should be over TLS; verify the CA fingerprint when possible
- **Renewal Automation:** Automated renewal reduces manual intervention but requires ongoing monitoring

## Cross-Referencing

### Related Roles in This Repository

- **`infrastructure.shared.step_ca`** - For deploying the Step CA server itself
- **`security_identity.vault`** - For Vault integration with Step CA (RA mode)
- **`security_identity.letsencrypt.letsencrypt_setup`** - Alternative for public certificates
- **`security_identity.letsencrypt.letsencrypt_godaddy`** - Alternative for public certificates with DNS

### External Dependencies

- **Smallstep Step CLI:** This role installs and uses the official Step CLI
- **Step CA Server:** Requires a running Step CA instance
- **Certificate Management:** Consider using with configuration management for web servers (nginx, apache, etc.)

## Files Created

This role creates the following files on the target system:

- `/etc/ssl/certs/<domain>.crt` - Certificate file
- `/etc/ssl/private/<domain>.key` - Private key file  
- `/etc/ssl/certs/<domain>-fullchain.crt` - Full certificate chain
- `/root/.step/` - Step CLI configuration directory
- `/etc/cron.d/snapca-renewal` - Renewal cron job
- `/usr/local/bin/snapca-renew.sh` - Renewal script

The role is designed to be idempotent and can be run multiple times safely.
