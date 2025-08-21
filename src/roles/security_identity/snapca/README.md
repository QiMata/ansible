# SnapCA Roles

This directory contains Ansible roles for managing certificates with [Smallstep Step CA](https://smallstep.com/docs/step-ca/). These roles provide a client-side interface for obtaining and managing certificates from a Step CA server, similar to how the Let's Encrypt roles work for public certificates.

## Available Roles

### snapca_client
The core client role that handles Step CA certificate operations:
- Installs Step CLI
- Bootstraps CA connection
- Obtains certificates using various provisioner types (JWK, OIDC, ACME, password)
- Manages certificate renewal
- Integrates with services

### snapca_unified  
A simplified wrapper role that provides a unified interface:
- Automatic authentication method selection
- Simplified configuration
- Sensible defaults for common use cases
- Consistent interface across deployments

## Comparison with Let's Encrypt Roles

| Feature | Let's Encrypt | SnapCA |
|---------|---------------|---------|
| **Certificate Source** | Public Let's Encrypt CA | Private Step CA |
| **Trust** | Publicly trusted | Internal/private trust |
| **Network Requirements** | Internet access | Internal network |
| **Challenge Methods** | HTTP-01, DNS-01 | JWK, OIDC, ACME, password |
| **Setup** | Simple (public CA) | Requires Step CA setup |
| **Best For** | Public services | Internal services, private PKI |

## Getting Started

### 1. Set up Step CA Server
First, deploy a Step CA server using the `infrastructure.shared.step_ca` role:

```yaml
- hosts: ca_servers
  roles:
    - infrastructure.shared.step_ca
```

### 2. Use SnapCA Client
For basic certificate management, use the unified role:

```yaml
- hosts: web_servers
  roles:
    - role: security_identity.snapca.snapca_unified
      vars:
        snapca_ca_url: "https://ca.internal.com:8443"
        snapca_domains:
          - "web.internal.com"
        snapca_token: "{{ vault_step_token }}"
        snapca_reload_services:
          - nginx
```

### 3. Advanced Configuration
For advanced scenarios, use the client role directly:

```yaml
- hosts: api_servers
  roles:
    - role: security_identity.snapca.snapca_client
      vars:
        snapca_client_ca_url: "https://ca.internal.com:8443"
        snapca_client_domains:
          - "api.internal.com"
        snapca_client_provisioner_type: "oidc"
        snapca_client_oidc_client_id: "{{ oidc_client_id }}"
        snapca_client_oidc_client_secret: "{{ oidc_client_secret }}"
```

## Authentication Methods

SnapCA supports multiple authentication methods:

- **JWK Tokens**: Bootstrap tokens for automated certificate issuance
- **OIDC**: Integration with identity providers (Google, Azure AD, etc.)
- **ACME**: Standard ACME protocol for automated certificate management
- **Password**: Password-based authentication for interactive use

## Security Considerations

- Store sensitive credentials in Ansible Vault
- Use strong authentication methods (OIDC preferred over passwords)
- Ensure Step CA server is properly secured
- Monitor certificate expiration and renewal
- Verify network security between clients and CA

## Related Roles

- `infrastructure.shared.step_ca` - Deploy Step CA server
- `security_identity.vault` - Vault integration with Step CA
- `security_identity.letsencrypt.*` - Public certificate alternatives

## Documentation

See individual role README files for detailed documentation:
- [snapca_client/README.md](snapca_client/README.md)
- [snapca_unified/README.md](snapca_unified/README.md)
