# Ansible Role: SnapCA Unified

## Overview

The **SnapCA Unified** role is a wrapper role that provides a simplified interface for obtaining certificates from Smallstep Step CA. It automatically configures the underlying `snapca_client` role based on your requirements, providing a unified interface for common certificate scenarios.

This role simplifies certificate management by:
- Providing sensible defaults for common use cases
- Automatically selecting appropriate provisioner types
- Handling authentication method selection
- Streamlining configuration for typical deployments

## When to Use This Role

Use this wrapper role when:
- You want a simplified interface for Step CA certificate management
- You have standard certificate requirements without complex customization
- You prefer not to configure the underlying `snapca_client` role directly
- You want consistent configuration across multiple deployments

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| **Basic Configuration** | | |
| `snapca_ca_url` | `""` | **Required.** Step CA server URL (e.g., `https://ca.internal.com:8443`) |
| `snapca_domains` | `[]` | **Required.** List of domain names for the certificate |
| `snapca_provisioner` | `"admin"` | Provisioner name to use |
| `snapca_auth_method` | `"auto"` | Authentication method: `auto`, `token`, `password`, `oidc`, `acme` |
| **Authentication** | | |
| `snapca_token` | `""` | JWK token (when using token auth) |
| `snapca_password` | `""` | Password (when using password auth) |
| `snapca_oidc_client_id` | `""` | OIDC client ID (when using OIDC auth) |
| `snapca_oidc_client_secret` | `""` | OIDC client secret (when using OIDC auth) |
| **Certificate Options** | | |
| `snapca_certificate_path` | `"/etc/ssl/certs"` | Directory to store certificates |
| `snapca_certificate_name` | `"{{ snapca_domains[0] }}"` | Base name for certificate files |
| `snapca_san` | `[]` | Additional Subject Alternative Names |
| `snapca_validity` | `"24h"` | Certificate validity duration |
| **Service Integration** | | |
| `snapca_reload_services` | `[]` | Services to reload after certificate renewal |
| `snapca_enable_renewal` | `true` | Enable automatic certificate renewal |
| `snapca_renewal_time` | `"02:30"` | Time to run renewal (HH:MM format) |

## Authentication Method Selection

The `snapca_auth_method` variable controls how authentication is handled:

- **`auto`** (default): Automatically selects based on provided credentials
  - Uses `token` if `snapca_token` is provided
  - Uses `password` if `snapca_password` is provided  
  - Uses `oidc` if `snapca_oidc_client_id` is provided
  - Falls back to `acme` if no credentials are provided
- **`token`**: Force JWK token authentication
- **`password`**: Force password authentication
- **`oidc`**: Force OIDC authentication
- **`acme`**: Force ACME protocol

## Example Playbooks

### Simple Certificate with Token Authentication

```yaml
- hosts: web_servers
  become: true
  roles:
    - role: security_identity.snapca.snapca_unified
      vars:
        snapca_ca_url: "https://ca.internal.com:8443"
        snapca_domains:
          - "web.internal.com"
        snapca_token: "{{ vault_snapca_token }}"
        snapca_reload_services:
          - nginx
```

### Multi-Domain Certificate with OIDC

```yaml
- hosts: api_servers
  become: true
  roles:
    - role: security_identity.snapca.snapca_unified
      vars:
        snapca_ca_url: "https://ca.internal.com:8443"
        snapca_domains:
          - "api.internal.com"
          - "api-v2.internal.com"
        snapca_auth_method: "oidc"
        snapca_oidc_client_id: "{{ vault_oidc_client_id }}"
        snapca_oidc_client_secret: "{{ vault_oidc_client_secret }}"
        snapca_reload_services:
          - apache2
```

### ACME Protocol (No Authentication Required)

```yaml
- hosts: acme_clients
  become: true
  roles:
    - role: security_identity.snapca.snapca_unified
      vars:
        snapca_ca_url: "https://ca.internal.com:8443"
        snapca_domains:
          - "service.internal.com"
        snapca_auth_method: "acme"
        snapca_validity: "168h"  # 1 week
```

### Load Balancer with IP SANs

```yaml
- hosts: load_balancers
  become: true
  roles:
    - role: security_identity.snapca.snapca_unified
      vars:
        snapca_ca_url: "https://ca.internal.com:8443"
        snapca_domains:
          - "lb.internal.com"
        snapca_san:
          - "10.0.1.100"
          - "10.0.1.101"
        snapca_token: "{{ vault_snapca_token }}"
        snapca_certificate_path: "/etc/haproxy/certs"
        snapca_certificate_name: "haproxy"
        snapca_reload_services:
          - haproxy
```

## Dependencies

This role depends on:
- `security_identity.snapca.snapca_client` - The underlying client role

## Files Created

This role creates the same files as the `snapca_client` role:

- Certificate: `{{ snapca_certificate_path }}/{{ snapca_certificate_name }}.crt`
- Private Key: `/etc/ssl/private/{{ snapca_certificate_name }}.key`
- Full Chain: `{{ snapca_certificate_path }}/{{ snapca_certificate_name }}-fullchain.crt`
- Renewal Script: `/usr/local/bin/snapca-renew.sh`
- Cron Job: `/etc/cron.d/snapca-renewal`

## Security Considerations

- Store sensitive credentials (tokens, passwords) in Ansible Vault
- Ensure Step CA server is properly secured and accessible
- Verify certificate permissions are appropriate for your services
- Monitor certificate expiration and renewal processes
- Use strong authentication methods when available

## Troubleshooting

### Common Issues

1. **CA Connection Failed**
   - Verify `snapca_ca_url` is correct and accessible
   - Check network connectivity to Step CA server
   - Ensure CA certificate fingerprint is correct if specified

2. **Authentication Failed**
   - Verify credentials are correct for the chosen auth method
   - Check that the provisioner exists on the Step CA
   - Ensure provisioner is configured for the selected auth type

3. **Certificate Validation Failed**
   - Verify domain names are correct and resolvable
   - Check that SAN entries are properly formatted
   - Ensure Step CA is configured to issue certificates for the requested domains

4. **Service Reload Failed**
   - Verify services exist and are running
   - Check service configuration accepts the certificate location
   - Ensure proper file permissions on certificate files
