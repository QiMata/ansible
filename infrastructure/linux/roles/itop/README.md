# Ansible Role: iTop

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

The **iTop** role installs and prepares the iTop application on a target server. **iTop (IT Operations Portal)** is an open-source, web-based IT service management (ITSM) and configuration management database (CMDB) platform, designed to streamline IT operations and adhere to ITIL best practices. This role automates the deployment of iTop by downloading the specified version, placing the web application files into the web server directory, adjusting file ownership, and setting up the MySQL/MariaDB database and user required by iTop. By applying this role, you can quickly provision an iTop server as part of your infrastructure.

Typically, you will run this role on a host that already has a **LAMP stack** (Linux, Apache, MySQL/MariaDB, PHP) available. The role does **not** install Apache or PHP itself; it assumes the web server and PHP runtime (with necessary extensions) are already in place. After running the role, the iTop application files will reside in the configured web root (default `/var/www/html/itop`), owned by the web server user (e.g. **www-data** on Debian/Ubuntu). The role will also ensure a MySQL database is created (default name `itop_db`) and a database user is created with full privileges on that database (default user `itop_user`).

> **Note:** By default, the role installs **iTop version 2.7.5**. You can adjust the `itop_version` variable to deploy a different version (see [Role Variables](#role-variables)), but be aware of version-specific file names (the download URL includes an internal build number tied to the version, as noted in [Known Issues](#known-issues-and-gotchas)). Also, additional manual or automated steps are required to finalize the iTop installation via its setup wizard – this role handles the file and database setup, but not the interactive configuration step.

```mermaid
flowchart LR
    A[Client Browser] -- HTTP/HTTPS --> B{Apache HTTP Server<br/>(with iTop PHP Application)}
    B -- MySQL queries --> C[(MySQL/MariaDB Database)]
    subgraph "Optional High-Availability"
      LB[HAProxy Load Balancer] -.-> B
      B2[Apache+iTop (Additional Web Node)] -.-> C
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

Here is a simple example of how to use the `itop` role in a playbook, including some variable overrides to customize the deployment:

```yaml
- hosts: itop_web_servers
  become: yes  # Ensure we have root privileges to install files and create DB
  vars:
    itop_version: "2.7.5"         # iTop version to install (optional override, default is 2.7.5)
    itop_root_dir: "/var/www/html/itop"  # Install path for iTop (using default here)
    db_name: "itop_production"    # Example custom DB name
    db_user: "itop_app_user"      # Example custom DB username
    db_password: "S3cur3P@ssw0rd" # Set a strong DB user password for iTop
  roles:
    - itop
```

In the above example:

* We target a group `itop_web_servers` (adjust to your inventory) and use `become: yes` because installing files to system directories and configuring databases requires elevated privileges.
* We override some role variables: the database name, user, and password are set to custom values instead of the defaults. This ensures we don’t use the default credentials in production. (The iTop version and root directory are shown for clarity but here remain at their defaults.)
* We then include the **itop** role. This will download the specified iTop version, unpack it, move it to `/var/www/html/itop`, set the correct file ownership, and create the MySQL database and user as specified.

**Important:** This playbook assumes that Apache and PHP are already installed on the hosts in `itop_web_servers`, and that a MySQL/MariaDB server is accessible (if on the same hosts, it should be running; if on separate hosts, ensure connectivity and appropriate permissions). You might run additional roles before `itop` to set up the web and database servers. For instance, you could apply a role to install MariaDB on a database host, or ensure your Apache/PHP configuration is in place on the web host. Once this play completes, you should be able to navigate to the iTop web interface (e.g., `http://<hostname>/itop`) to perform the initial configuration via the setup wizard.

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
