# Ansible Role: Let's Encrypt Unified

## Overview

The **letsencrypt_unified** role is a wrapper role that automatically selects between the two specialized Let's Encrypt roles in this repository based on your requirements:

- **[letsencrypt_setup](../letsencrypt_setup/README.md)** - Uses Certbot for single-domain certificates with HTTP-01 or DNS-01 challenges
- **[letsencrypt_godaddy](../letsencrypt_godaddy/README.md)** - Uses acme.sh for multi-domain certificates with DNS-01 challenge (GoDaddy only)

This role provides a unified interface while leveraging the specialized capabilities of each underlying role.

## When to Use This Role

Use this wrapper role when:
- You want a consistent interface across different certificate scenarios
- You have mixed requirements (some single-domain, some multi-domain certificates)
- You want automatic selection based on your configuration
- You prefer not to choose between the underlying roles manually

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `security_identity_letsencrypt_unified_domains` | `[]` | **Required.** List of domains for the certificate. Single item uses `letsencrypt_setup`, multiple items use `letsencrypt_godaddy`. Backwards compatibility for `letsencrypt_domains` is retained. |
| `security_identity_letsencrypt_unified_email` | `""` | Email address for Let's Encrypt account registration and notifications. Legacy `letsencrypt_email` is still accepted. |
| `security_identity_letsencrypt_unified_client` | `"auto"` | Force client selection: `"auto"`, `"certbot"`, or `"acme.sh"`. Older `letsencrypt_client` continues to work. |
| `security_identity_letsencrypt_unified_challenge_method` | `"dns"` | Challenge method: `"dns"` or `"http"` (HTTP only available with certbot). Legacy `letsencrypt_challenge_method` values are honoured. |
| `security_identity_letsencrypt_unified_godaddy_api_key` | `""` | GoDaddy API key (required for DNS challenges). Falls back to `godaddy_api_key` when provided. |
| `security_identity_letsencrypt_unified_godaddy_api_secret` | `""` | GoDaddy API secret (required for DNS challenges). Falls back to `godaddy_api_secret`. |
| `security_identity_letsencrypt_unified_webroot_path` | `"/var/www/html"` | Webroot path for HTTP challenges (certbot only). Falls back to `webroot_path`. |

> **Compatibility note:** The legacy variables shown above without the `security_identity_` prefix are still supported through runtime fallbacks, but new automation should prefer the namespaced variants for ansible-lint compliance.

## Selection Logic

The role automatically selects the underlying implementation based on:

1. **Client preference:** If `letsencrypt_client` is set to `"certbot"` or `"acme.sh"`, that client is used
2. **Domain count:** Single domain defaults to certbot, multiple domains default to acme.sh
3. **Challenge method:** HTTP challenges require certbot
4. **Capabilities:** Wildcard certificates require DNS challenge and work with both clients

## Example Playbooks

### Single Domain with HTTP Challenge
```yaml
- hosts: webservers
  become: true
  roles:
    - role: security_identity.letsencrypt.letsencrypt_unified
      vars:
        security_identity_letsencrypt_unified_domains: ["example.com"]
        security_identity_letsencrypt_unified_email: "admin@example.com"
        security_identity_letsencrypt_unified_challenge_method: "http"
        security_identity_letsencrypt_unified_webroot_path: "/var/www/html"
```

### Multiple Domains with DNS Challenge
```yaml
- hosts: webservers
  become: true
  roles:
    - role: security_identity.letsencrypt.letsencrypt_unified
      vars:
        security_identity_letsencrypt_unified_domains: ["example.com", "www.example.com", "api.example.com"]
        security_identity_letsencrypt_unified_email: "admin@example.com"
        security_identity_letsencrypt_unified_challenge_method: "dns"
        security_identity_letsencrypt_unified_godaddy_api_key: "{{ vault_godaddy_api_key }}"
        security_identity_letsencrypt_unified_godaddy_api_secret: "{{ vault_godaddy_api_secret }}"
```

### Force Specific Client
```yaml
- hosts: webservers
  become: true
  roles:
    - role: security_identity.letsencrypt.letsencrypt_unified
      vars:
        security_identity_letsencrypt_unified_domains: ["example.com"]
        security_identity_letsencrypt_unified_email: "admin@example.com"
        security_identity_letsencrypt_unified_client: "acme.sh"  # Force acme.sh even for single domain
        security_identity_letsencrypt_unified_challenge_method: "dns"
        security_identity_letsencrypt_unified_godaddy_api_key: "{{ vault_godaddy_api_key }}"
        security_identity_letsencrypt_unified_godaddy_api_secret: "{{ vault_godaddy_api_secret }}"
```

## Limitations

- Only supports GoDaddy DNS challenges (both underlying roles use GoDaddy)
- HTTP challenges only available when using certbot
- Variable names are mapped between the two underlying roles

## Implementation Details

This wrapper role:
1. Validates input parameters
2. Maps unified variables to role-specific variables
3. Includes the appropriate underlying role based on selection logic
4. Provides consistent error messages and validation

The actual certificate operations are performed by the underlying specialized roles, ensuring you get the full benefits and features of each implementation.
