# Airflow Connector Role

This Ansible role manages Apache Airflow connections, allowing you to configure various external system connections for your Airflow instance.

## Description

The `airflow_connector` role provides a comprehensive way to manage Airflow connections through Ansible. It supports:

- Creating new connections
- Updating existing connections
- Deleting connections
- Importing connections from files
- Exporting connections to files
- Various connection types (PostgreSQL, MySQL, HTTP, AWS, GCP, etc.)

## Requirements

- Apache Airflow must be installed and configured
- Airflow CLI must be accessible
- Airflow database must be initialized and accessible

## Role Variables

### Core Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `airflow_connector_home` | `/opt/airflow` | Airflow home directory |
| `airflow_connector_binary_path` | `/usr/local/bin/airflow` | Path to Airflow binary |
| `airflow_connector_connections` | `[]` | List of connections to create |
| `airflow_connector_connections_to_delete` | `[]` | List of connection IDs to delete |

### Behavior Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `airflow_connector_list_connections` | `false` | Show connections list after creation |
| `airflow_connector_verbose` | `false` | Enable verbose output |
| `airflow_connector_restart_services` | `false` | Restart Airflow services after changes |

### Import/Export Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `airflow_connector_connections_import_file` | undefined | Path to file for importing connections |
| `airflow_connector_connections_export_file` | undefined | Path to file for exporting connections |
| `airflow_connector_connections_export_format` | `json` | Export format (json, yaml, env) |
| `airflow_connector_connections_export_conn_ids` | `[]` | Specific connection IDs to export |
| `airflow_connector_connections_export_secure` | `true` | Set restrictive permissions on export file |

## Connection Configuration

### Basic Connection Structure

```yaml
airflow_connector_connections:
  - conn_id: "my_connection"
    conn_type: "postgres"
    host: "localhost"
    port: 5432
    login: "username"
    password: "password"
    schema: "database_name"
    description: "My PostgreSQL connection"
    update_existing: true
    extra:
      sslmode: "prefer"
```

### Connection Types and Examples

#### PostgreSQL Connection
```yaml
- conn_id: "postgres_default"
  conn_type: "postgres"
  host: "localhost"
  port: 5432
  login: "airflow"
  password: "airflow"
  schema: "airflow"
  description: "Default PostgreSQL connection"
  extra:
    sslmode: "prefer"
```

#### MySQL Connection
```yaml
- conn_id: "mysql_default"
  conn_type: "mysql"
  host: "localhost"
  port: 3306
  login: "airflow"
  password: "airflow"
  schema: "airflow"
  description: "Default MySQL connection"
```

#### HTTP Connection
```yaml
- conn_id: "api_service"
  conn_type: "http"
  host: "api.example.com"
  port: 443
  description: "External API service"
  extra:
    endpoint_url: "https://api.example.com/v1"
```

#### AWS Connection
```yaml
- conn_id: "aws_default"
  conn_type: "aws"
  description: "AWS connection"
  extra:
    aws_access_key_id: "AKIA..."
    aws_secret_access_key: "..."
    region_name: "us-east-1"
```

#### Google Cloud Platform Connection
```yaml
- conn_id: "gcp_default"
  conn_type: "google_cloud_platform"
  description: "GCP connection"
  extra:
    key_path: "/path/to/service-account.json"
    project: "my-gcp-project"
    scope: "https://www.googleapis.com/auth/cloud-platform"
```

#### SSH Connection
```yaml
- conn_id: "ssh_server"
  conn_type: "ssh"
  host: "remote-server.com"
  port: 22
  login: "username"
  password: "password"
  description: "SSH connection to remote server"
```

#### Redis Connection
```yaml
- conn_id: "redis_default"
  conn_type: "redis"
  host: "localhost"
  port: 6379
  description: "Redis connection"
  extra:
    db: 0
```

## Example Playbooks

### Basic Usage

```yaml
- name: Configure Airflow connections
  hosts: airflow_servers
  roles:
    - role: airflow_connector
      vars:
        airflow_connector_connections:
          - conn_id: "postgres_dwh"
            conn_type: "postgres"
            host: "{{ postgres_host }}"
            port: 5432
            login: "{{ postgres_user }}"
            password: "{{ postgres_password }}"
            schema: "warehouse"
            description: "Data warehouse connection"
```

### Advanced Usage with Multiple Connection Types

```yaml
- name: Setup comprehensive Airflow connections
  hosts: airflow_servers
  roles:
    - role: airflow_connector
      vars:
        airflow_connector_verbose: true
        airflow_connector_list_connections: true
        airflow_connector_connections:
          # Database connections
          - conn_id: "postgres_prod"
            conn_type: "postgres"
            host: "prod-db.example.com"
            port: 5432
            login: "{{ vault_postgres_user }}"
            password: "{{ vault_postgres_password }}"
            schema: "production"
            description: "Production PostgreSQL"
            update_existing: true

          # API connections
          - conn_id: "external_api"
            conn_type: "http"
            host: "api.partner.com"
            port: 443
            description: "Partner API"
            extra:
              headers:
                Authorization: "Bearer {{ vault_api_token }}"

          # Cloud connections
          - conn_id: "aws_s3"
            conn_type: "aws"
            description: "AWS S3 connection"
            extra:
              aws_access_key_id: "{{ vault_aws_access_key }}"
              aws_secret_access_key: "{{ vault_aws_secret_key }}"
              region_name: "us-west-2"
```

### Connection Management

```yaml
- name: Manage Airflow connections
  hosts: airflow_servers
  roles:
    - role: airflow_connector
      vars:
        # Delete old connections
        airflow_connector_connections_to_delete:
          - "old_mysql_conn"
          - "deprecated_api"

        # Create new connections
        airflow_connector_connections:
          - conn_id: "new_mysql_conn"
            conn_type: "mysql"
            host: "new-mysql.example.com"
            port: 3306
            login: "airflow"
            password: "{{ mysql_password }}"

        # Export current connections
        airflow_connector_connections_export_file: "/tmp/airflow_connector_connections_backup.json"
        airflow_connector_connections_export_format: "json"
```

## Security Considerations

1. **Sensitive Data**: Use Ansible Vault for storing passwords and secrets
2. **File Permissions**: Export files are created with restrictive permissions (600)
3. **Connection Updates**: Use `update_existing: true` to overwrite existing connections
4. **Backup**: Always export connections before making bulk changes

## Dependencies

This role assumes that Apache Airflow is already installed and configured. It works well with the `apache_airflow` role.

## Example Integration with Apache Airflow Role

```yaml
- name: Deploy Airflow with connections
  hosts: airflow_servers
  roles:
    - role: apache_airflow
      vars:
        apache_airflow_version: "2.6.3"
        apache_airflow_executor: "CeleryExecutor"

    - role: airflow_connector
      vars:
        airflow_connector_connections:
          - conn_id: "postgres_airflow"
            conn_type: "postgres"
            host: "{{ apache_airflow_database_host }}"
            port: 5432
            login: "{{ apache_airflow_database_user }}"
            password: "{{ apache_airflow_database_password }}"
            schema: "{{ apache_airflow_database_name }}"
```

## Troubleshooting

1. **Airflow not found**: Ensure `airflow_connector_binary_path` points to the correct Airflow installation
2. **Database connection issues**: Verify Airflow database is accessible and initialized
3. **Permission errors**: Check that the Airflow user has proper permissions
4. **Connection already exists**: Use `update_existing: true` to overwrite existing connections

## License

MIT

## Author Information

This role was created for managing Airflow connections in enterprise environments.
