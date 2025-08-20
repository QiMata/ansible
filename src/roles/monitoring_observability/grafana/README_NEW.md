# Ansible Role: Grafana

**Table of Contents**

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Cross-Referencing](#cross-referencing)

## Overview

This role installs and configures **Grafana** (open-source analytics & monitoring web UI) on target hosts with comprehensive enterprise features. It handles installation via Grafana's official APT repository, sets up necessary configuration, and ensures the Grafana service is running. The role is designed to be **idempotent** and highly configurable via variables.

### Key Features

#### Core Configuration
* **Package Installation:** Adds Grafana's official package repository and installs a specified version of Grafana via `apt`, allowing you to pin or upgrade Grafana easily (default version **10.4.0**).
* **Port and Protocol Configuration:** Customizable HTTP/HTTPS port, protocol, domain, and root URL settings.
* **Service Configuration:** Deploys a pre-configured `grafana.ini` with custom settings, including admin user credentials and database config. Automatically starts and enables the **`grafana-server`** service.

#### Plugin Management
* **Plugin Installation:** Automated installation and management of Grafana plugins via `grafana-cli`.
* **Plugin Verification:** Validates plugin installation and provides status reporting.

#### High-Availability Support
* **External Database Support:** Full support for PostgreSQL and MySQL databases for clustering.
* **Session Management:** Configurable session storage (file, Redis) for multi-instance deployments.
* **Load Balancer Integration:** Health check endpoints and configuration templates for HAProxy and NGINX.
* **Database Migration:** Automated migration from SQLite to external databases with backup support.

#### Security Features
* **SSL/TLS Configuration:** Built-in HTTPS setup with certificate management and secure headers.
* **OAuth/SSO Integration:** Support for multiple OAuth providers (Google, GitHub, and more).
* **API Key Management:** Automated provisioning and management of API keys with secure storage.
* **Service Accounts:** Service account creation and token management for programmatic access.
* **Security Headers:** Comprehensive security headers (HSTS, CSP, XSS protection, frame options).
* **LDAP Integration:** External LDAP directory integration for user authentication.

#### Organization and User Management
* **Organization Provisioning:** Automated creation and configuration of Grafana organizations.
* **User Management:** Bulk user creation with role assignment and team membership.
* **Team Management:** Team creation and member assignment across organizations.

#### Advanced Data Source Management
* **Enhanced Configuration:** Support for authentication, custom headers, and advanced settings.
* **Template Rendering:** Fixed Jinja2 template rendering for dynamic data source configuration.
* **Connectivity Testing:** Automated data source connectivity validation.
* **Service Discovery:** Integration points for dynamic data source discovery.

#### Dashboard Management
* **Dashboard Provisioning:** Automated dashboard import from files, Git repositories, and APIs.
* **Folder Management:** Organization of dashboards into structured folders.
* **Backup and Versioning:** Comprehensive dashboard backup with versioned exports.
* **Git Integration:** Automated dashboard synchronization from Git repositories.

#### Alerting System
* **Alert Rules:** Provisioning of alert rules with complex conditions and data sources.
* **Contact Points:** Configuration of notification channels (email, Slack, webhooks, etc.).
* **Notification Policies:** Advanced routing policies for alert notifications.
* **Health Monitoring:** Automated alerting system health checks.

#### Performance and Scaling
* **Performance Tuning:** Memory limits, CPU quotas, query timeouts, and caching configuration.
* **Resource Monitoring:** Performance monitoring scripts with automated alerting.
* **Caching Support:** Redis and Memcached integration for improved performance.
* **Database Optimization:** Connection pooling and query optimization settings.

#### Monitoring and Observability
* **Self-Monitoring:** Built-in Grafana self-monitoring dashboard and alerts.
* **External Integration:** Configuration templates for Prometheus, Zabbix, Nagios monitoring.
* **Log Management:** Centralized logging configuration with logrotate integration.
* **Health Checks:** Comprehensive health monitoring with automated reporting.

#### Backup and Restore
* **Full Instance Backup:** Complete Grafana instance backup including database, configuration, and dashboards.
* **Automated Scheduling:** Cron-based automated backup with retention policies.
* **Disaster Recovery:** Complete restore functionality with validation and rollback.
* **Dashboard Versioning:** Individual dashboard backup and restore capabilities.

## Supported Operating Systems/Platforms

This role is tested on and designed for Debian-based Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal) and 22.04 LTS (Jammy)

> **Note:** The role uses Debian/Ubuntu conventions (apt package manager and repository). It will **not** work on RHEL/CentOS or other non-Debian systems without modification. Ensure target hosts are running a supported Debian/Ubuntu version. The role's installation steps (adding apt repo and key) assume internet access to Grafana's package servers.

## Role Variables

Below is a comprehensive list of variables for this role, organized by functionality:

### Core Configuration Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_version` | `"10.4.0"` | Version of Grafana to install |
| `grafana_http_port` | `3000` | HTTP port for Grafana service |
| `grafana_protocol` | `http` | Protocol (http/https) |
| `grafana_domain` | `localhost` | Domain name for Grafana |
| `grafana_root_url` | `""` | Custom root URL (auto-generated if empty) |
| `grafana_admin_user` | `admin` | Admin username |
| `grafana_admin_password` | `{{ vault_grafana_admin_password }}` | Admin password (use Ansible Vault) |

### SSL/TLS Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_https_enabled` | `false` | Enable HTTPS |
| `grafana_cert_file` | `""` | Path to SSL certificate |
| `grafana_cert_key` | `""` | Path to SSL private key |

### Database Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_database.type` | `sqlite3` | Database type (sqlite3, mysql, postgres) |
| `grafana_database.host` | `""` | Database host |
| `grafana_database.name` | `grafana` | Database name |
| `grafana_database.user` | `grafana` | Database user |
| `grafana_database.password` | `""` | Database password |
| `grafana_database_migration_enabled` | `false` | Enable database migration |

### Plugin Management

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_plugins_enabled` | `false` | Enable plugin management |
| `grafana_plugins` | `[]` | List of plugins to install |

### High Availability Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_ha_enabled` | `false` | Enable HA mode |
| `grafana_session_provider` | `file` | Session storage provider |
| `grafana_session_provider_config` | `""` | Session provider configuration |
| `grafana_lb_enabled` | `false` | Enable load balancer integration |

### Security Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_security_enabled` | `false` | Enable security features |
| `grafana_security_headers` | `{}` | Security headers configuration |
| `grafana_cors_enabled` | `false` | Enable CORS |

### OAuth/SSO Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_oauth_enabled` | `false` | Enable OAuth |
| `grafana_oauth_providers` | `{}` | OAuth provider configurations |

### Organization and User Management

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_organizations_enabled` | `false` | Enable organization management |
| `grafana_organizations` | `[]` | List of organizations to create |
| `grafana_users_enabled` | `false` | Enable user management |
| `grafana_users` | `[]` | List of users to create |
| `grafana_teams_enabled` | `false` | Enable team management |
| `grafana_teams` | `[]` | List of teams to create |

### API and Service Account Management

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_api_keys_enabled` | `false` | Enable API key management |
| `grafana_api_keys` | `[]` | List of API keys to create |
| `grafana_service_accounts_enabled` | `false` | Enable service account management |
| `grafana_service_accounts` | `[]` | List of service accounts to create |

### Dashboard Management

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_dashboard_provisioning_enabled` | `false` | Enable dashboard provisioning |
| `grafana_dashboard_folders` | `[]` | List of dashboard folders |
| `grafana_dashboard_providers` | `[]` | Dashboard provider configurations |

### Alerting Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_alerting_enabled` | `false` | Enable alerting |
| `grafana_alerting_rules` | `[]` | List of alert rules |
| `grafana_contact_points` | `[]` | Notification contact points |
| `grafana_notification_policies` | `[]` | Notification policies |

### Performance Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_performance_enabled` | `false` | Enable performance tuning |
| `grafana_performance_config` | `{}` | Performance configuration |
| `grafana_memory_limit` | `""` | Memory limit for systemd |
| `grafana_cpu_limit` | `""` | CPU limit for systemd |
| `grafana_caching_enabled` | `false` | Enable caching |

### Monitoring Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_monitoring_enabled` | `false` | Enable self-monitoring |
| `grafana_monitoring_config` | `{}` | Monitoring configuration |
| `grafana_external_monitoring` | `[]` | External monitoring integrations |

### Backup and Restore

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_backup_enabled` | `true` | Enable backup functionality |
| `grafana_backup_path` | `/var/backups/grafana` | Backup directory |
| `grafana_backup_retention_days` | `30` | Backup retention period |
| `grafana_backup_full_enabled` | `false` | Enable full instance backup |
| `grafana_restore_enabled` | `false` | Enable restore functionality |
| `grafana_restore_from_path` | `""` | Restore source path |

### Data Source Configuration

The role includes enhanced data source configuration with support for:
- Basic and advanced authentication
- Custom headers
- SSL/TLS settings
- Connection timeouts
- Advanced provider-specific settings

Example data source configuration:
```yaml
grafana_datasources:
  - name: Prometheus
    type: prometheus
    url: "http://prometheus:9090"
    access: proxy
    isDefault: true
    basicAuth: false
    customHeaders:
      "X-Custom-Header": "value"
    jsonData:
      httpMethod: "POST"
      queryTimeout: "60s"
    secureJsonData:
      httpHeaderValue1: "secret-value"
```

### LDAP Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `grafana_ldap_enabled` | `false` | Enable LDAP authentication |
| `grafana_ldap_file` | `/etc/grafana/ldap.toml` | LDAP configuration file path |

## Tags

This role supports the following Ansible tags for selective execution:

* `grafana_install` - Installation and basic configuration
* `grafana_config` - Configuration file management
* `grafana_plugins` - Plugin management
* `grafana_security` - Security configuration
* `grafana_oauth` - OAuth/SSO setup
* `grafana_users` - User and organization management
* `grafana_dashboards` - Dashboard provisioning
* `grafana_alerting` - Alerting configuration
* `grafana_monitoring` - Monitoring setup
* `grafana_backup` - Backup operations
* `grafana_restore` - Restore operations

## Dependencies

This role requires the following Ansible collections:
- `community.general` (>=5.0.0)
- `community.grafana` (>=1.5.0)
- `community.mysql`
- `community.postgresql`
- `ansible.posix`

### Installation
```bash
ansible-galaxy collection install community.general community.grafana community.mysql community.postgresql ansible.posix
```

## Example Playbook

### Basic Installation
```yaml
- hosts: grafana_servers
  become: true
  roles:
    - role: grafana
      grafana_admin_password: "{{ vault_grafana_admin_password }}"
```

### High-Availability Setup
```yaml
- hosts: grafana_servers
  become: true
  roles:
    - role: grafana
      grafana_admin_password: "{{ vault_grafana_admin_password }}"
      grafana_ha_enabled: true
      grafana_database:
        type: postgres
        host: "postgres.example.com:5432"
        name: grafana
        user: grafana
        password: "{{ vault_grafana_db_password }}"
      grafana_session_provider: redis
      grafana_session_provider_config: "redis.example.com:6379"
      grafana_lb_enabled: true
```

### Enterprise Features Setup
```yaml
- hosts: grafana_servers
  become: true
  roles:
    - role: grafana
      # Core configuration
      grafana_admin_password: "{{ vault_grafana_admin_password }}"
      grafana_https_enabled: true
      grafana_cert_file: "/etc/ssl/certs/grafana.crt"
      grafana_cert_key: "/etc/ssl/private/grafana.key"
      
      # Plugin management
      grafana_plugins_enabled: true
      grafana_plugins:
        - grafana-clock-panel
        - grafana-simple-json-datasource
        - grafana-worldmap-panel
      
      # OAuth configuration
      grafana_oauth_enabled: true
      grafana_oauth_providers:
        google:
          enabled: true
          client_id: "{{ vault_google_client_id }}"
          client_secret: "{{ vault_google_client_secret }}"
          scopes: "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
          auth_url: "https://accounts.google.com/o/oauth2/auth"
          token_url: "https://accounts.google.com/o/oauth2/token"
          api_url: "https://www.googleapis.com/oauth2/v1/userinfo"
          allow_sign_up: true
      
      # Organization and user management
      grafana_organizations_enabled: true
      grafana_organizations:
        - name: "DevOps Team"
          id: 2
      
      grafana_users_enabled: true
      grafana_users:
        - name: "John Doe"
          email: "john@example.com"
          login: "john.doe"
          password: "{{ vault_john_password }}"
          org_id: 2
          role: "Editor"
      
      # Dashboard management
      grafana_dashboard_provisioning_enabled: true
      grafana_dashboard_folders:
        - name: "Infrastructure"
          uid: "infrastructure"
        - name: "Applications"
          uid: "applications"
      
      grafana_dashboard_providers:
        - name: "git-dashboards"
          type: "git"
          options:
            url: "https://github.com/company/grafana-dashboards.git"
            path: "dashboards/"
            branch: "main"
      
      # Alerting configuration
      grafana_alerting_enabled: true
      grafana_contact_points:
        - name: "ops-email"
          type: "email"
          settings:
            addresses: "ops@example.com"
        - name: "slack-alerts"
          type: "slack"
          settings:
            url: "{{ vault_slack_webhook_url }}"
            channel: "#alerts"
      
      # Performance and monitoring
      grafana_performance_enabled: true
      grafana_monitoring_enabled: true
      grafana_caching_enabled: true
      grafana_caching_config:
        type: "redis"
        redis:
          address: "redis.example.com:6379"
          password: "{{ vault_redis_password }}"
      
      # Backup configuration
      grafana_backup_enabled: true
      grafana_backup_full_enabled: true
      grafana_backup_schedule: "0 2 * * *"  # Daily at 2 AM
```

## Testing Instructions

### Prerequisites
1. Install required Ansible collections:
   ```bash
   ansible-galaxy collection install community.general community.grafana community.mysql community.postgresql ansible.posix
   ```

2. Install testing dependencies:
   ```bash
   pip install molecule molecule-plugins[docker] testinfra pytest
   ```

### Running Tests

#### Basic Functionality Test
```bash
cd src/roles/monitoring_observability/grafana
molecule test
```

#### Test Specific Scenarios
```bash
# Test with plugins enabled
molecule test -s plugins

# Test HA configuration
molecule test -s ha

# Test with all features enabled
molecule test -s full-features
```

#### Manual Testing
```bash
# Start test environment
molecule create
molecule converge

# Run specific tests
molecule verify

# Cleanup
molecule destroy
```

### Test Coverage

The role includes comprehensive tests for:
- ✅ Package installation and service management
- ✅ Configuration file generation and permissions
- ✅ Plugin installation and management
- ✅ Security configuration and SSL setup
- ✅ High availability features
- ✅ Database connectivity and migration
- ✅ API and service account management
- ✅ Dashboard provisioning and backup
- ✅ Alerting configuration
- ✅ Monitoring and health checks
- ✅ Performance tuning
- ✅ Backup and restore functionality

## Known Issues and Gotchas

### Template Rendering Issue (Fixed)
**Issue:** The original role used `copy` instead of `template` for datasource provisioning, causing Jinja2 placeholders to not render properly.
**Resolution:** Updated to use `template` module with proper Jinja2 rendering.

### Database Migration Considerations
**Issue:** Migration from SQLite to external databases requires careful planning.
**Resolution:** Automated backup before migration and validation steps included.

### Plugin Installation Dependencies
**Issue:** Some plugins require specific Grafana versions or additional dependencies.
**Resolution:** Plugin validation and version checking included.

### OAuth Configuration Complexity
**Issue:** OAuth provider configuration varies significantly between providers.
**Resolution:** Comprehensive examples and validation included for common providers.

### High Availability Setup
**Issue:** HA setup requires external database and session storage.
**Resolution:** Comprehensive validation and health checks ensure proper HA configuration.

### Performance Tuning
**Issue:** Performance settings depend on workload and infrastructure.
**Resolution:** Configurable settings with monitoring and alerting for performance metrics.

## Security Implications

### Sensitive Data Management
- **Admin passwords** must be stored in Ansible Vault
- **OAuth client secrets** should be encrypted
- **Database passwords** require secure storage
- **API keys and tokens** are stored with restricted permissions (600)

### Network Security
- **Firewall rules** are automatically configured
- **SSL/TLS** support with certificate validation
- **Security headers** prevent common web vulnerabilities
- **CORS** configuration for cross-origin requests

### Access Control
- **LDAP integration** for centralized authentication
- **OAuth/SSO** for enterprise identity providers
- **Role-based access control** with organization and team management
- **Service accounts** for programmatic access

### Monitoring and Auditing
- **Security event logging** with centralized log management
- **Failed authentication monitoring** with alerting
- **Configuration change tracking** through backups
- **Health monitoring** with security-focused alerts

## Cross-Referencing

### Related Roles
- **Prometheus** - Metrics collection and alerting
- **Elasticsearch** - Log aggregation and search
- **NGINX/HAProxy** - Load balancing and reverse proxy
- **Redis** - Session storage and caching
- **PostgreSQL/MySQL** - Database backends

### Integration Points
- **Data Sources**: Prometheus, Elasticsearch, InfluxDB, MySQL, PostgreSQL
- **Authentication**: LDAP, OAuth (Google, GitHub, Azure AD)
- **Notifications**: Email, Slack, PagerDuty, webhooks
- **Monitoring**: Prometheus metrics, external monitoring systems
- **Storage**: Local filesystem, S3, GCS for backups

### Documentation References
- [Grafana Official Documentation](https://grafana.com/docs/)
- [Grafana API Reference](https://grafana.com/docs/grafana/latest/http_api/)
- [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
- [Grafana High Availability](https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/)
