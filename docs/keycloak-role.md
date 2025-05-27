# Keycloak Role

| Variable | Default | Description |
|----------|---------|-------------|
| `keycloak_version` | `24.0.1` | Keycloak release to install |
| `keycloak_db_host` | _(required)_ | PostgreSQL host |
| `keycloak_db_name` | `keycloak` | Database name |
| `keycloak_db_user` | `keycloak` | DB username |
| `keycloak_db_password` | _(vaulted)_ | DB password |

## Example

```yaml
- hosts: keycloak
  roles:
    - role: keycloak
      vars:
        keycloak_version: "24.0.1"
```
