# OpenLDAP Data Management Role

This role provides comprehensive data management capabilities for OpenLDAP, including automated schema management, data validation, bulk operations, and data archiving.

## Features

- **Schema Management**: Automated schema versioning and migration tools
- **Data Validation**: Entry consistency checks and validation rules
- **Bulk Operations**: Mass import/export utilities beyond basic LDIF
- **Data Archiving**: Lifecycle management for old entries
- **Data Transformation**: Data mapping and transformation tools
- **Backup Integration**: Automated backup scheduling and retention

## Requirements

- OpenLDAP server already configured
- Python 3.6+ with ldap3 library
- Additional packages: `python3-yaml`, `python3-jsonschema`

## Role Variables

### Schema Management
```yaml
openldap_schema_management_enabled: true
openldap_schema_auto_migration: true
openldap_schema_validation: true
openldap_schema_backup_before_migration: true
```

### Data Validation
```yaml
openldap_data_validation_enabled: true
openldap_validation_rules_file: "/etc/openldap/validation/rules.yml"
openldap_validation_schedule: "0 2 * * *"  # Daily at 2 AM
```

### Bulk Operations
```yaml
openldap_bulk_operations_enabled: true
openldap_bulk_import_batch_size: 1000
openldap_bulk_export_format: "ldif"  # ldif, json, csv
openldap_bulk_parallel_workers: 4
```

### Data Archiving
```yaml
openldap_data_archiving_enabled: true
openldap_archive_retention_days: 365
openldap_archive_storage_path: "/var/lib/openldap/archive"
openldap_archive_compression: true
```

## Dependencies

- `openldap_server`
- `python3-ldap3`

## Example Playbook

```yaml
- hosts: ldap_servers
  roles:
    - role: openldap_data_management
      openldap_schema_auto_migration: true
      openldap_data_validation_enabled: true
      openldap_archive_retention_days: 180
```

## Testing

Use Molecule for testing:

```bash
cd roles/security_identity/openldap/openldap_data_management
molecule test
```
