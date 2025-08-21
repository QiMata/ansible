# OpenLDAP Compliance & Governance Role

This role implements compliance and governance features for OpenLDAP, including GDPR compliance tools, audit trails, compliance reporting, and data classification.

## Features

- **GDPR Compliance**: Data retention, deletion automation, and privacy controls
- **Audit Trail**: Comprehensive audit logging and compliance dashboards
- **Data Classification**: Sensitive data identification and protection
- **Compliance Reporting**: Automated compliance reports and metrics
- **Data Lineage**: Track data flow and transformations
- **Privacy Controls**: Data anonymization and pseudonymization

## Requirements

- OpenLDAP server already configured
- Python 3.6+ with compliance libraries
- Additional packages: `python3-pandas`, `python3-cryptography`

## Role Variables

### GDPR Compliance
```yaml
openldap_gdpr_enabled: true
openldap_gdpr_retention_policy: true
openldap_gdpr_right_to_deletion: true
openldap_gdpr_data_portability: true
openldap_gdpr_consent_management: true
```

### Data Retention
```yaml
openldap_retention_policies: []
openldap_default_retention_days: 2555  # 7 years
openldap_retention_auto_deletion: true
openldap_retention_grace_period: 30  # days
```

### Audit Configuration
```yaml
openldap_compliance_audit_enabled: true
openldap_audit_retention_years: 7
openldap_audit_encryption: true
openldap_audit_immutable: true
```

### Data Classification
```yaml
openldap_data_classification_enabled: true
openldap_classify_pii: true
openldap_classify_phi: true
openldap_classify_financial: true
```

## Dependencies

- `openldap_server`
- `openldap_logging`

## Example Playbook

```yaml
- hosts: ldap_servers
  roles:
    - role: openldap_compliance
      openldap_gdpr_enabled: true
      openldap_retention_auto_deletion: true
      openldap_data_classification_enabled: true
```

## Testing

Use Molecule for testing:

```bash
cd roles/security_identity/openldap/openldap_compliance
molecule test
```
