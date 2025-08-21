# OpenLDAP Multi-Factor Authentication (MFA) Role

This role configures multi-factor authentication for OpenLDAP, including TOTP/OTP integration, smart card authentication, and external authentication providers.

## Features

- **TOTP/OTP Integration**: Time-based one-time password support using Google Authenticator, FreeOTP, etc.
- **Smart Card Authentication**: PKCS#11 and certificate-based authentication
- **External Authentication**: OAuth2/SAML integration for federated identity
- **Flexible MFA Policies**: Per-user, per-group, and per-application MFA requirements

## Requirements

- OpenLDAP server already installed and configured
- Additional packages: `libpam-google-authenticator`, `opensc`, `libpam-pkcs11`
- For OAuth2/SAML: `python3-oauthlib`, `python3-saml2`

## Role Variables

### TOTP/OTP Configuration
```yaml
openldap_mfa_totp_enabled: true
openldap_mfa_totp_issuer: "{{ openldap_server_organization }}"
openldap_mfa_totp_window_size: 3
openldap_mfa_totp_rate_limit: 3
```

### Smart Card Configuration
```yaml
openldap_mfa_smartcard_enabled: false
openldap_mfa_pkcs11_module: "/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so"
openldap_mfa_ca_certificates: []
```

### External Authentication
```yaml
openldap_mfa_oauth2_enabled: false
openldap_mfa_oauth2_providers: []
openldap_mfa_saml_enabled: false
openldap_mfa_saml_providers: []
```

## Dependencies

- `openldap_server`

## Example Playbook

```yaml
- hosts: ldap_servers
  roles:
    - role: openldap_mfa
      openldap_mfa_totp_enabled: true
      openldap_mfa_smartcard_enabled: true
      openldap_mfa_oauth2_enabled: true
      openldap_mfa_oauth2_providers:
        - name: "google"
          client_id: "{{ vault_google_oauth_client_id }}"
          client_secret: "{{ vault_google_oauth_client_secret }}"
          authorization_url: "https://accounts.google.com/o/oauth2/auth"
          token_url: "https://oauth2.googleapis.com/token"
```

## Testing

Use Molecule for testing:

```bash
cd roles/security_identity/openldap/openldap_mfa
molecule test
```
