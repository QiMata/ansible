# OpenLDAP Password Policies Role

This role implements comprehensive password policies for OpenLDAP, including complexity requirements, expiration rules, account lockout policies, and history management.

## Features

- **Password Complexity**: Minimum length, character requirements, dictionary checks
- **Password Expiration**: Configurable password age and warning periods
- **Account Lockout**: Brute force protection with configurable thresholds
- **Password History**: Prevent reuse of recent passwords
- **Quality Checks**: Integration with external password quality libraries
- **Grace Logins**: Allow limited logins after password expiration

## Requirements

- OpenLDAP server with ppolicy overlay support
- Additional packages: `libpwquality-tools`, `cracklib-runtime`

## Role Variables

### Basic Password Policy
```yaml
openldap_password_policies_enabled: true
openldap_password_min_length: 8
openldap_password_max_length: 128
openldap_password_min_classes: 3  # character classes required
```

### Password Expiration
```yaml
openldap_password_max_age: 90  # days
openldap_password_min_age: 1   # days
openldap_password_warning: 7   # days before expiration
openldap_password_grace_logins: 3
```

### Account Lockout
```yaml
openldap_lockout_enabled: true
openldap_lockout_threshold: 5
openldap_lockout_duration: 1800  # seconds
openldap_lockout_observation_window: 900  # seconds
```

### Password History
```yaml
openldap_password_history_enabled: true
openldap_password_history_count: 12
```

## Dependencies

- `openldap_server`

## Example Playbook

```yaml
- hosts: ldap_servers
  roles:
    - role: openldap_password_policies
      openldap_password_min_length: 12
      openldap_lockout_threshold: 3
      openldap_password_max_age: 60
```

## Testing

Use Molecule for testing:

```bash
cd roles/security_identity/openldap/openldap_password_policies
molecule test
```
