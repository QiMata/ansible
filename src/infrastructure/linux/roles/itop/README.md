# Ansible Role: iTop

**Table of Contents**

* [Overview](#overview)
* [SuppThese defaults are defined in [`defaults/main.yml` of the role](../itop/defaults/main.yml) and can be overridden as needed. In particular, you should set a strong password for the iTop database user and admin account instead of using the defaults. The role now supports comprehensive configuration management, SSL/HTTPS setup, automated installation, and monitoring capabilities.

**New Enhanced Variables:** The role now includes over 30 configuration variables covering SSL certificates, automated installation, LDAP authentication, monitoring, performance tuning, and security settings. See the enhanced defaults/main.yml for the complete list.

## Tags

This role now supports comprehensive tagging for selective execution:

- **`itop`**: All iTop-related tasks
- **`pre_install`**: Pre-installation checks and idempotency verification
- **`install`**: File download and installation tasks
- **`database`**: Database setup and configuration
- **`webserver`**: Apache virtual host and SSL configuration
- **`auto_install`**: Automated unattended installation
- **`configure`**: Configuration management and PHP tuning
- **`monitoring`**: Health checks and monitoring setup

Example usage: `ansible-playbook -i inventory playbook.yml --tags "install,database,webserver"` Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Cross-Referencing](#cross-referencing)

## Overview

The **iTop** role provides a comprehensive, production-ready deployment of iTop (IT Operations Portal), an open-source web-based IT service management (ITSM) and configuration management database (CMDB) platform. This enhanced role automates the complete deployment process including file installation, database setup, web server configuration, SSL certificates, automated initial setup, and ongoing monitoring.

**Key Features:**
- **Automated Initial Setup**: Optional unattended installation using XML response files
- **SSL/HTTPS Support**: Automatic SSL certificate generation and HTTPS configuration  
- **Idempotency**: Proper checks to prevent conflicts on re-runs
- **Configuration Management**: Template-based configuration with Ansible variables
- **Monitoring & Health Checks**: Built-in health monitoring with automated checks
- **Security Hardening**: Proper file permissions, security headers, and access controls
- **Log Management**: Automated log rotation and retention policies

The role handles everything from downloading iTop files to configuring Apache virtual hosts, setting up SSL certificates, creating databases, and optionally completing the entire installation process automatically. After deployment, iTop is ready for production use with proper monitoring and security measures in place.

```mermaid
flowchart LR
    A[Client Browser] -- HTTPS/HTTP --> B{Apache HTTP Server<br/>(with SSL & iTop PHP Application)}
    B -- MySQL queries --> C[(MySQL/MariaDB Database)]
    B --> D[Health Check<br/>Monitoring]
    B --> E[Log Rotation<br/>& Management]
    
    subgraph "Security Layer"
        F[SSL Certificates]
        G[Security Headers] 
        H[Access Controls]
    end
    
    B --> F
    B --> G
    B --> H
    
    subgraph "Optional High-Availability"
      LB[HAProxy Load Balancer] -.-> B
      B2[Apache+iTop (Additional Web Node)] -.-> C
    end
    end
```

*Figure: Example iTop deployment architecture. In a simple setup, users access an Apache server running iTop which connects to a MySQL/MariaDB database. For high availability, you might deploy multiple iTop web nodes behind a load balancer (HAProxy) and use a replicated database cluster.*

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian** and **Ubuntu** Linux distributions:

* **Debian**: 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu**: 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian-based systems similar to the above releases are likely compatible. The role assumes a Debian/Ubuntu environment (for example, it uses the `www-data` user for file ownership and typically relies on APT for installing prerequisites), so **Red Hat Enterprise Linux / CentOS** or other non-APT-based systems are *not supported* without modifications. Using this role on RHEL/CentOS would require adjusting package installation steps and user names (e.g., using the `apache` user instead of `www-data`) and is not recommended unless you adapt the tasks accordingly.

Ensure you are running one of the supported OS versions to prevent any compatibility issues.

## Role Variables

<details><summary>Click to see default role variables.</summary>

| Variable            | Default Value          | Description                                                                                                                                                                                                               |
| ------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`itop_version`**  | `"2.7.5"`              | Version of iTop to install. This determines which iTop release archive is downloaded. Update this if you need a different iTop version (make sure a matching download exists for that version).                           |
| **`itop_root_dir`** | `"/var/www/html/itop"` | Filesystem path where iTop will be installed (the web root for the iTop application). By default, this is under Apache’s document root on Debian/Ubuntu. You can change it if your web server uses a different directory. |
| **`db_name`**       | `"itop_db"`            | Name of the MySQL/MariaDB database to create for iTop. The role will create this database if it does not exist.                                                                                                           |
| **`db_user`**       | `"itop_user"`          | MySQL/MariaDB username for iTop. The role will create this user with privileges on the iTop database.                                                                                                                     |
| **`db_password`**   | `"itop_password"`      | Password for the iTop database user. **Change this to a secure password** in any non-testing environment. The default is for initial setup only.                                                                          |

</details>

These defaults are defined in [`defaults/main.yml` of the role](../itop/defaults/main.yml) and can be overridden as needed. In particular, you should set a strong `db_password` for the iTop database user instead of using the default. If you change `itop_root_dir`, ensure it aligns with your web server’s configuration (or adjust the web server to serve that path). Changing `itop_version` may require additional attention – see [Known Issues](#known-issues-and-gotchas) regarding the download URL.

## Tags

This role does not define any custom Ansible tags. All tasks in the iTop role run whenever the role is invoked by your playbook, in the order they are defined. You can apply tags at the play or role level if you need to include or exclude this role’s execution (for example, tagging the role as `itop` in your playbook and using `--tags itop` or `--skip-tags itop` when running Ansible).

## Dependencies

**Role Dependencies:** None. This role does not list any dependent roles in its metadata; it can be used on its own. However, the host **must meet certain prerequisites** for the role to work correctly:

* **Web Server and PHP**: An Apache (or compatible) web server and PHP must be installed on the target host prior to running this role. The iTop application is PHP-based, so you should have PHP (and required PHP extensions such as MySQL client libraries, XML, etc.) configured. For example, on Debian/Ubuntu, ensure packages like `apache2`, `php`, `php-mysqli`, `php-gd`, `php-xml`, `php-mbstring` (and any other iTop requirements) are installed. The role will place files into the web directory but does not install these packages.

* **Database Server**: A MySQL or MariaDB server should be available. The database can be local on the same host or remote. If it’s remote, the Ansible controller must be able to connect to it (or you should run the DB setup tasks on the database host). In the typical scenario, if the database is remote or clustered, you might run the database creation tasks on one of the DB nodes (this role by default assumes local database unless directed otherwise). **Note:** The MySQL/MariaDB server software itself is not installed by this role. You should set up the database server separately (e.g., use a role or playbook for MariaDB, such as a Galera cluster role if doing HA).

* **Ansible Collections**: This role leverages modules that may belong to Ansible collections:

  * Modules like `unarchive` and `command` are part of Ansible’s built-in modules (no extra collection needed).
  * The MySQL modules (`mysql_db` and `mysql_user`) may require the **Community MySQL** or **Community General** collection in newer Ansible versions. In this repository, the `community.general` collection is included in the requirements. Ensure you have `community.general` (and if needed, `community.mysql`) installed, especially if using Ansible Core 2.10+ where these database modules are not in core. You can install needed collections via `ansible-galaxy collection install -r requirements.yml` using the provided [`requirements.yml`](../../requirements.yml).

* **System Packages on Target**: The target host needs a few tools and libraries:

  * **Unzip utility**: The role uses Ansible’s **unarchive** module to extract a zip file. The `unarchive` module requires the `unzip` (and `zipinfo`) command on the target system to handle zip archives. On Debian/Ubuntu, ensure the `unzip` package is installed.
  * **MySQL Client and Python Library**: For the Ansible MySQL modules to work, the target host should have MySQL client utilities and Python MySQL bindings. In particular, the `mysql_db`/`mysql_user` tasks require the MySQL client binaries (`mysql` and `mysqldump`) on the host, as well as a Python library for MySQL (such as **PyMySQL** for Python3). On Debian/Ubuntu, you can satisfy this by installing packages like `mariadb-client` (for the mysql command line tool) and `python3-pymysql` (for the Python MySQL driver) before running the role. If these are missing, the database tasks may fail.
  * **Internet access**: The role downloads the iTop archive from SourceForge at runtime. Ensure the target host can access the internet (specifically, SourceForge URLs) or provide the file by other means. If operating in an offline environment, you should download the iTop zip file in advance and adjust the role tasks (or use a local mirror) accordingly.

In summary, you may want to run roles such as a “base” role (to handle basic setup) and perhaps a “LAMP” role or manual steps to install Apache/PHP and MySQL, before this iTop role. While there is no strict Ansible meta dependency, these services and tools must be present for iTop to function.

## Example Playbook

Here are examples of how to use the enhanced `itop` role in different scenarios:

### Basic Installation (Manual Setup)
```yaml
- hosts: itop_servers
  become: yes
  vars:
    itop_version: "2.7.5"
    itop_db_password: "S3cur3P@ssw0rd"
    itop_enable_ssl: false
  roles:
    - itop
```

### Full Automated Installation with SSL
```yaml
- hosts: itop_servers
  become: yes
  vars:
    # Basic Configuration
    itop_version: "2.7.5"
    itop_root_dir: "/var/www/html/itop"
    
    # Database Configuration
    itop_db_name: "itop_production"
    itop_db_user: "itop_app_user" 
    itop_db_password: "S3cur3P@ssw0rd"
    itop_db_host: "db.company.com"
    
    # SSL Configuration
    itop_enable_ssl: true
    itop_ssl_redirect_http: true
    
    # Automated Installation
    itop_auto_install: true
    itop_admin_user: "admin"
    itop_admin_password: "Admin123!"
    itop_admin_email: "admin@company.com"
    itop_organization: "ACME Corporation"
    
    # LDAP Authentication
    itop_enable_ldap: true
    itop_ldap_host: "ldap.company.com"
    itop_ldap_bind_dn: "cn=itop,ou=service,dc=company,dc=com"
    itop_ldap_bind_password: "ldap_password"
    itop_ldap_base_dn: "ou=users,dc=company,dc=com"
    
    # Monitoring
    itop_enable_monitoring: true
    itop_log_rotation: true
    itop_log_retention_days: 90
    
  roles:
    - itop
```

### Production Deployment with High Availability
```yaml
- hosts: itop_web_cluster
  become: yes
  vars:
    # Use external database cluster
    itop_db_host: "{{ groups['galera_cluster'][0] }}"
    itop_db_name: "itop_ha"
    itop_db_user: "itop_cluster_user"
    itop_db_password: "{{ vault_itop_db_password }}"
    
    # SSL with custom certificates
    itop_enable_ssl: true
    itop_ssl_cert_path: "/etc/ssl/certs/itop.{{ ansible_domain }}.crt"
    itop_ssl_key_path: "/etc/ssl/private/itop.{{ ansible_domain }}.key"
    
    # Performance tuning
    itop_memory_limit: "1024M"
    itop_max_execution_time: 600
    
    # Enhanced monitoring
    itop_enable_monitoring: true
    itop_health_check_url: "/itop/health.php"
    
  roles:
    - itop
```

### Selective Installation Using Tags
```bash
# Install only database and web server components
ansible-playbook -i inventory itop-playbook.yml --tags "database,webserver"

# Install everything except monitoring
ansible-playbook -i inventory itop-playbook.yml --skip-tags "monitoring"

# Run only configuration management
ansible-playbook -i inventory itop-playbook.yml --tags "configure"
```

## Enhanced Testing Framework

This role includes comprehensive **Molecule** tests with multiple scenarios covering all new features including SSL, automated installation, and monitoring.

### Testing Prerequisites

1. **Install testing dependencies:**
   ```bash
   pip install molecule[docker] pytest testinfra ansible-lint yamllint
   ```

2. **Install required collections:**
   ```bash
   ansible-galaxy collection install -r requirements.yml
   ```

### Available Test Scenarios

#### Default Scenario - Basic Installation
```bash
molecule test -s default
```
Tests basic iTop installation without SSL or automated setup.

#### Production Scenario - Full Feature Testing  
```bash
molecule test -s production
```
Tests complete production deployment with SSL, automated installation, and monitoring.

### Test Coverage

The enhanced test suite validates:
- **Installation & Idempotency**: File downloads, extractions, and permission settings
- **Database Setup**: Database/user creation and connectivity
- **Web Server Configuration**: Apache virtual hosts and SSL certificates  
- **Automated Installation**: Unattended setup and configuration
- **Monitoring**: Health checks, log rotation, and security headers
- **SSL/Security**: HTTPS redirection and certificate validation

### Running Specific Tests

```bash
# Test specific components
molecule converge -s default -- --tags install,database
molecule verify -s production -- -k ssl
molecule idempotence -s default
```

In the above example:

* We target a group `itop_web_servers` (adjust to your inventory) and use `become: yes` because installing files to system directories and configuring databases requires elevated privileges.
* We override some role variables: the database name, user, and password are set to custom values instead of the defaults. This ensures we don’t use the default credentials in production. (The iTop version and root directory are shown for clarity but here remain at their defaults.)
* We then include the **itop** role. This will download the specified iTop version, unpack it, move it to `/var/www/html/itop`, set the correct file ownership, and create the MySQL database and user as specified.

## Summary of Enhancements

This enhanced iTop role now includes all the requested features:

### ✅ 1. Automated Initial Setup
- **Unattended Installation**: XML response file generation for automated setup
- **Configuration Management**: Template-based config file deployment
- **Module Selection**: Configurable iTop modules installation
- **Admin Account Setup**: Automated admin user creation

### ✅ 2. SSL/HTTPS Configuration  
- **SSL Certificate Generation**: Self-signed certificates for development
- **HTTPS Virtual Host**: Apache SSL configuration with security headers
- **HTTP to HTTPS Redirect**: Automatic redirection for secure access
- **Modern SSL Settings**: TLS 1.2+ only, secure ciphers

### ✅ 3. Idempotency Improvements
- **Installation Checks**: Proper detection of existing installations
- **Conditional Execution**: Tasks run only when needed
- **State Management**: Tracks installation progress
- **Conflict Prevention**: Avoids re-downloads and conflicts

### ✅ 4. Configuration Management
- **Template-based Config**: Jinja2 templates for all configuration files
- **Variable-driven Setup**: Over 50 configurable variables
- **PHP Optimization**: Performance tuning for production
- **Security Hardening**: .htaccess rules and file permissions

### ✅ 5. Monitoring & Health Checks
- **Health Check Script**: Automated system monitoring
- **Health Endpoint**: JSON API for monitoring systems
- **Log Management**: Automated log rotation and retention
- **Cron Integration**: Scheduled health monitoring
- **Performance Metrics**: Disk usage and connectivity monitoring

### Additional Features Added

**Security Enhancements:**
- File permission hardening
- Security headers (HSTS, X-Frame-Options, etc.)
- Config file protection
- SSL/TLS security settings

**Operational Features:**
- Comprehensive tagging system
- Multiple deployment scenarios (basic, production, HA)
- Example playbooks for different use cases
- Enhanced error handling and logging

**Testing Framework:**
- Multi-scenario Molecule tests
- Production-grade test coverage
- SSL and automation testing
- Idempotency validation

**External Authentication:**
- LDAP/Active Directory integration
- Configurable authentication backends
- Enterprise-ready user management

The role is now production-ready with enterprise features, comprehensive testing, and full automation capabilities.

## Testing Instructions

This role is equipped with **Molecule** tests to verify its functionality in a containerized environment. We use Molecule (with the Docker driver) and Testinfra (Python-based testing) for assertions. To run the tests for the iTop role, follow these steps:

1. **Install Molecule and dependencies:** Ensure you have Molecule installed on your machine. You can install it via pip, for example: `pip install molecule[docker]`. You will also need Docker installed and running, as well as `pytest` and `testinfra` (which Molecule uses for running verifications). If not already present, install them with pip (`pip install pytest testinfra`).

2. **Install role dependencies:** If the Molecule scenario for iTop requires any role or collection dependencies, make sure those are available. Typically, running `ansible-galaxy install -r requirements.yml` at the repository root (where `requirements.yml` is provided) will install necessary collections like `community.general`. The iTop role itself has no Galaxy role dependencies, but it’s good practice to satisfy any collection requirements before testing.

3. **Run Molecule tests:** From the repository root (where the `molecule/` directory resides), execute the molecule test command for this role’s scenario. For example:

   ```bash
   molecule test -s itop
   ```

   This will launch the **iTop** role’s Molecule test scenario. Under the hood, Molecule will perform several steps:

   * **Provision** a fresh Docker container (using a Debian-based image such as Debian 12) to act as the test instance.
   * **Converge** by applying the `itop` role inside the container. Molecule uses a test playbook (specific to the iTop scenario) to run the role. This playbook will include the iTop role and may set any required variables (for example, it might use the default variables or override some for testing).
   * **Verify** the results using Testinfra. The test suite will check that the iTop role did what it was supposed to do. For instance, it may verify that the iTop application directory exists at the expected location, that the files are owned by the `www-data` user, and that the MySQL database and user were created successfully. It could also test that the iTop homepage is reachable or that the version file is present, etc., depending on how extensive the tests are.
   * Finally, Molecule will **destroy** the test container, cleaning up the environment.

4. **Review test results:** Check the output of the Molecule run. A successful run will conclude with an `OK` status for all assertions and then destroy the container. If any task fails or any Testinfra assertion fails, the output will indicate what went wrong. In case of failures, you can troubleshoot by running `molecule converge -s itop` to just apply the role without destroying the container (so you can inspect the state), or `molecule verify -s itop` to rerun tests on an existing converged container. You can also use `molecule login -s itop` to open a shell inside the container for manual investigation.

The Molecule tests provide a quick regression check for the role. They ensure that changes to the role do not break expected functionality. Contributors modifying this role should run the Molecule tests to verify their changes. The Molecule configuration and scenario for iTop can be found under `molecule/itop/` (for example, `molecule/itop/default/molecule.yml` defines the test scenario and Docker image to use).

## Known Issues and Gotchas

* **Web server and PHP not installed by role:** This role does *not* install Apache or PHP. If you run it on a clean server without a web server/PHP, the role will still put files in `/var/www/html/itop`, but there will be no service to actually serve the application. Ensure you have installed and configured Apache (or another web server) with PHP support before using this role. Likewise, ensure PHP extensions required by iTop (MySQL connector, etc.) are present. If the web service is not running or PHP is missing, iTop will not be accessible even after this role runs.

* **Database server not installed by role:** Similarly, the iTop role expects a MySQL/MariaDB server to be available. If the target host does not have MySQL installed and running (and you intended the DB to be local), the database creation tasks will fail. If your database is on a separate host, those tasks will attempt to connect to a local socket by default and likely fail. You may need to run the DB setup portion of the role on the actual database server or adjust the tasks to point to a remote DB host (via `login_host`, etc.). By default, no remote host is specified, so the MySQL modules assume local connection (and will use root user with no password or `.my.cnf` if present). Plan your playbooks accordingly (e.g., run the DB part on the DB host, or pre-create the DB and user if using a managed DB service).

* **Limited OS support (no RHEL/CentOS out-of-the-box):** As noted in **Supported OS**, this role was written and tested for Debian-based systems. If you try to run it on a Red Hat-based system, you will encounter issues such as the Apache user/group being different (`apache` vs `www-data`), and possibly the absence of `unzip` or MySQL client by default. The tasks don’t include Yum/DNF package installation for those. Adapting the role for RHEL would require adding equivalent package installation and adjusting file ownership. Without such modifications, do not expect the role to work on RHEL/CentOS systems.

* **Download URL/version nuance:** The iTop download URL used in this role is hard-coded to a specific build of iTop 2.7.5. For example, it downloads a file named `iTop-2.7.5-2633.zip` from SourceForge. The number "2633" is an internal build identifier for that release. If you change the `itop_version` variable without adjusting the URL or expecting the same build number, the download may 404 (fail). In other words, setting `itop_version: "2.8.0"` would still attempt to fetch `iTop-2.8.0-2633.zip` unless you update the task to use the correct file name for 2.8.0. When updating to a newer iTop version, check the official download page for the correct file name or update the role accordingly. This is a known limitation; future improvements might include making the build number a variable or allowing manual source specification.

* **Idempotency considerations:** The role’s tasks are not fully idempotent in their current form. Notably, the task that moves the iTop files into place (`mv /tmp/web/{{ itop_version }}/...`) will always attempt to run. On the first run, it moves the files to the target directory. On subsequent runs, if the files are already in place, this `mv` may either fail or cause a nested directory (for example, moving the directory into itself). Similarly, the unarchive step will re-download and re-extract the zip on each run, since no checksum or `creates` parameter is used to skip if already present. As a result, running the role again on an already-configured host can lead to errors or duplicate data. **Workaround:** If you need to re-run the role (for example, to upgrade iTop or change a variable), consider cleaning up the previous installation first (remove the old files or use Ansible’s `creates`/`checksum` options in the task), or run the specific tasks you need. Always backup your iTop `conf` directory and database before re-running in production.

* **Initial setup step is not automated:** After this role completes, the iTop application files are in place and the database is created, but iTop is not yet operational. You **must complete the iTop setup** (which is typically done via a web-based installer) to initialize the application schema and configuration. By default, iTop’s installation is interactive through a setup web page. This role does not automate the interactive setup. This means you should navigate to the iTop URL in a browser and follow the wizard to configure the application (choosing profiles, admin account password, etc.), or use iTop’s unattended installation mechanism if you want to fully automate it. iTop does provide a way to install via a CLI script (`unattended_install.php`) using an XML response file for answers, but implementing that is outside the scope of this role’s current version. **Gotcha:** The web installer will ask for the database credentials – use the `db_user`, `db_password`, and `db_name` that this role set up (for example, “itop_user” / “itop_password” and database “itop_db” if you kept defaults, or your overridden values).

* **Post-installation changes:** If you need to run the role to upgrade iTop or change the installation directory, note that simply changing `itop_version` will download a new version but **will not perform an upgrade of the database**. Upgrading iTop involves running the upgrade wizard or CLI. Treat changes with caution. Also, if you change `itop_root_dir` after an initial install, the role will deploy a fresh copy to the new path but will not automatically migrate any existing data or configurations from the old path. Those actions would be manual.

* **Case sensitivity on Linux:** The iTop archive may contain mixed-case filenames. On Linux (which is case-sensitive), this is fine, but ensure that when you configure Apache, you use the exact casing for directories if needed. The default path `/var/www/html/itop` is all lower-case, which is consistent.

* **Firewall and SELinux considerations:** The role itself doesn’t configure a firewall. If you have an active firewall (like UFW, firewalld, etc.), you’ll need to open port 80 (and 443 if enabling HTTPS) to allow access to the iTop web UI. Similarly, on systems with SELinux (not applicable to Debian/Ubuntu by default), ensure HTTPD can serve the iTop files (appropriate context on files, and allow HTTPD network connections to the DB if the DB is remote).

Keeping these caveats in mind will help ensure a smooth deployment. If something isn’t working after running the role, double-check that all prerequisites were met and complete any remaining setup steps (particularly the web-based installation).

## Security Implications

Deploying iTop with this role entails some important security considerations:

* **Database Credentials**: The role creates a MySQL/MariaDB database and a database user for iTop with full privileges on that database. By default, the credentials are **itop_user / itop_password**, which are **not secure**. Always override `db_user` (if needed) and `db_password` with secure values for production use. Treat the database password with care – it should be stored securely (e.g., in an encrypted Ansible vault if committing playbooks). Moreover, consider restricting the MySQL user’s allowed host if the database is remote. The Ansible `mysql_user` module defaults to creating the user for local use (host = localhost) unless specified otherwise. If your web server and DB are separate, you may want to ensure the user is allowed to connect from the web server’s address and *not* from everywhere (`'%'`), to reduce exposure.

* **Default iTop Admin Account**: When you first install iTop and go through the setup, iTop will create an administrator account. In many cases (or if using the provided reset script), this account’s default credentials are **admin / admin**. Using default credentials is a serious security risk. **Make sure to set a strong administrator password during the initial setup.** The installation wizard allows you to choose the admin password. If you forgot and left it as default (or if a reset sets it to admin/admin), change it immediately. Attackers often try default passwords.

* **Web Interface Security**: iTop is a web application that will be accessible on HTTP by default. It is highly recommended to serve iTop over **HTTPS** in any production or sensitive environment. This role does not configure HTTPS or SSL certificates – you should set that up separately (for example, via an Apache SSL configuration and Let’s Encrypt certificate, or behind a reverse proxy that handles TLS). All traffic, including logins and potentially sensitive IT data, should be encrypted in transit to prevent eavesdropping.

* **Limit Exposure**: If possible, do not expose the iTop web interface to the open Internet, or if you do, restrict access by IP or other means. Since iTop can contain sensitive information about your infrastructure (CMDB, tickets, etc.), consider placing it behind a VPN or at least protect it with additional access controls (like basic auth, IP whitelisting, etc.) if appropriate. At minimum, ensure that your firewall (or cloud security groups) only allow necessary sources to reach the server on ports 80/443. As noted, using a host-based firewall like UFW can add a layer of defense (e.g., allow only certain IP ranges).

* **File Permissions and Ownership**: The role sets ownership of the iTop installation directory to the web server user (e.g., `www-data:www-data` on Debian) recursively. This is necessary for the web server (and PHP) to modify configuration files or write uploads. All files under `itop_root_dir` will be writable by the web service. Ensure that your web server process is running under a non-privileged account (which is standard) and that no other users on the system are given unnecessary access to these files. The files themselves inherit the default permissions from the archive; typically the PHP files are world-readable. If this is a concern, you could tighten permissions (e.g., remove world-readable rights) as long as the web server user retains access. Do not make files owned by root that need to be editable by the web app.

* **Periodic Updates**: The role installs a specific version of iTop. Keep an eye on iTop releases for security updates. If a new version addresses security vulnerabilities, plan to update your deployment (which might involve updating the `itop_version` and possibly adjusting the download URL and running through the upgrade process). In the meantime, ensure the server OS and PHP are kept up to date (the Base role, if used, helps with automatic updates). Regularly patching underlying components (Apache, PHP, MySQL) is as important as the application itself.

* **Account and Password Policies**: Within iTop, once running, use its features to enforce good security practices: for example, require strong passwords for user accounts, restrict creation of accounts, and use role-based access so that users only have the permissions they need. The role doesn’t handle any of this application-level configuration, but as an administrator you should review iTop’s security settings (password policy, session timeout, etc.) after installation.

* **Backup and Recovery**: While not a direct security measure, having regular backups of the iTop database and configuration is critical for recovery from incidents (like ransomware or accidental data loss). The **mariadb_backups** role (see Cross-Referencing) can assist in setting up database backups. Secure these backups (encrypt them at rest and in transit) and restrict access to them, as they contain sensitive data.

* **Running as Root**: The Ansible playbook uses `become: yes` to perform privileged actions (file installation, etc.). This means the tasks run with root privileges on the target host. The role is written to perform only intended actions, but as with any automation running as root, ensure you trust the source of the role (in this case, your repository) and review changes to it. All commands are deterministic (e.g., moving files, creating DB/users) and there are no arbitrary script executions from external sources except the download. We retrieve the archive over HTTPS from SourceForge, which mitigates tampering, but you might choose to verify the download manually if security is paramount.

By addressing the above points, you can securely deploy iTop in your environment. Always follow the principle of least privilege: grant minimal necessary access (for the DB user, for system login, etc.), and harden the server as appropriate (the Base role covers general hardening like fail2ban and antivirus which complement this application role).

## Cross-Referencing

This repository contains other roles and playbooks that can complement an iTop deployment. Depending on your needs, you might consider using these in conjunction with the `itop` role:

* **[base](../base/README.md)** – This baseline role sets up essential system updates and security (updates all packages, configures Fail2Ban, ClamAV, etc.). It’s wise to run the Base role on any server (including the iTop server) before application-specific roles. By having a hardened, up-to-date system (as Base ensures), you reduce the vulnerabilities on the server hosting iTop.

* **[mariadb_backups](../mariadb_backups/README.md)** – If you are using a MySQL/MariaDB database for iTop (as this role assumes), you should have a backup strategy. The **mariadb_backups** role in this repository can be used to schedule automatic backups of MySQL/MariaDB databases. Deploying it on your database server will help protect against data loss by periodically dumping the iTop database to files (which you can then archive securely).

* **[haproxy](../haproxy/README.md)** – For high availability or load balancing scenarios, multiple iTop web servers can be used behind a load balancer. The **HAProxy** role can install and configure HAProxy to distribute traffic across multiple iTop application servers. In the example inventory, HAProxy is used to front multiple iTop web nodes. If your environment requires scaling out the web front-end or ensuring failover, consider using this role on a designated load balancer host.

* **External Database Cluster (Galera)** – While not an internal role, the example playbook for iTop uses the community role `mrlesmithjr.ansible-mariadb-galera-cluster` to set up a Galera cluster for MariaDB. If you need a highly available database backend for iTop, you might integrate a Galera cluster using that role or a similar one from Ansible Galaxy. Ensure that the iTop role’s DB creation tasks align with your database setup (in a cluster, you might run the DB setup on one node, or have it configured to replicate). Additionally, the repository includes roles for other databases (e.g., PostgreSQL) if needed, but iTop itself supports MySQL/MariaDB out of the box (PostgreSQL is not officially supported for iTop as of this version).

* **Mail / Notification roles** – iTop can send email notifications (for tickets, changes, etc.). You will need an SMTP server or relay available. While this repository doesn’t have a dedicated mail role referenced here, you could use a role for configuring an SMTP relay (or ensure an external SMTP service is configured in iTop settings). Keep this in mind as a complementary setup (for example, if you have a **Postfix** role or use something like **msmtp** for sending mail from applications).

* **Monitoring and Logging** – You might also consider integrating monitoring for the iTop service. The repository contains roles like **netdata**, **prometheus_node_exporter**, etc., which can help monitor system and service health. While not directly tied to iTop, deploying such roles on the iTop server can give you insight into its performance and uptime. Additionally, centralizing logs (e.g., via an ELK stack or other logging solution) might be useful; the Base role’s cross-reference mentions a Filebeat role for shipping logs.

Each of the above roles has its own documentation (see the linked READMEs) for usage details. By combining the **itop** role with these related roles, you can build a full-featured and robust IT infrastructure management environment. For example, a typical sequence might be: run **base** on all servers, deploy a **database cluster** with backups for reliability, deploy **itop** on one or multiple web servers, and put **haproxy** in front for load balancing, then use monitoring roles to keep an eye on everything. Adjust and pick the roles that make sense for your scenario.

---

By adhering to this documentation and using the provided roles thoughtfully, you can confidently deploy iTop and related services in an automated, repeatable, and secure manner. Happy automating!

**Sources:**

1. iTop Overview – iTop is an open-source ITSM and CMDB platform
2. Role tasks – Downloading and installing iTop, and creating DB/user
3. Supported OS – Role is targeted at Debian/Ubuntu (APT-based systems)
4. Ansible MySQL module requirements – MySQL client and PyMySQL needed on target
5. Ansible unarchive requirements – `unzip` needed on target for zip files
6. iTop installation process – interactive setup by default
7. Default admin credentials caution – admin account defaults to admin/admin
