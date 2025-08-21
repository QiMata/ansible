# OpenLDAP Integration Capabilities Role

This role provides integration capabilities for OpenLDAP, including directory synchronization with Active Directory, REST API endpoints, webhook notifications, and custom attribute support.

## Features

- **Directory Synchronization**: Bidirectional sync with Active Directory and other LDAP servers
- **REST API**: RESTful API endpoints for programmatic access
- **Webhook Notifications**: Event-driven integrations for LDAP operations
- **Custom Attributes**: Support for custom schemas and attribute extensions
- **Federation**: SAML and OAuth2 identity federation
- **Middleware Integration**: Connect with enterprise applications

## Requirements

- OpenLDAP server already configured
- Python 3.6+ with Flask for REST API
- Additional packages: `python3-flask`, `python3-requests`, `python3-ldap3`

## Role Variables

### Directory Synchronization
```yaml
openldap_sync_enabled: true
openldap_sync_ad_enabled: false
openldap_sync_interval: 3600  # seconds
openldap_sync_bidirectional: false
```

### REST API Configuration
```yaml
openldap_rest_api_enabled: true
openldap_rest_api_port: 8389
openldap_rest_api_ssl: true
openldap_rest_api_auth_method: "token"  # token, basic, oauth2
```

### Webhook Configuration
```yaml
openldap_webhooks_enabled: true
openldap_webhook_events: ["add", "modify", "delete", "bind"]
openldap_webhook_endpoints: []
```

### Custom Attributes
```yaml
openldap_custom_schemas_enabled: true
openldap_custom_schemas: []
openldap_attribute_validation: true
```

## Dependencies

- `openldap_server`
- `python3-flask`
- `python3-ldap3`

## Example Playbook

```yaml
- hosts: ldap_servers
  roles:
    - role: openldap_integration
      openldap_rest_api_enabled: true
      openldap_sync_ad_enabled: true
      openldap_webhooks_enabled: true
      openldap_webhook_endpoints:
        - url: "https://api.company.com/ldap/notifications"
          events: ["add", "modify", "delete"]
          auth_token: "{{ vault_webhook_token }}"
```

## Testing

Use Molecule for testing:

```bash
cd roles/security_identity/openldap/openldap_integration
molecule test
```
