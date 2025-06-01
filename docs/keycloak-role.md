# Keycloak Role

## Overview

The **Keycloak** Ansible role installs and configures [Keycloak](https://www.keycloak.org/) (an open-source Identity and Access Management server) on a target host and sets it up as a systemd service. It handles the following tasks:

* **System Requirements:** Ensures necessary system packages (e.g. `unzip`, `curl`, OpenJDK 17) are present on the host.
* **User Setup:** Creates a dedicated system user (default **`keycloak`**) with a non-login shell to run the Keycloak service.
* **Installation:** Downloads the specified Keycloak server tarball (by default, version **24.0.1**) and unpacks it into the installation directory. The install path is version-specific (e.g. `/var/lib/keycloak/keycloak-24.0.1` by default).
* **Configuration:** Deploys a Keycloak configuration file (`keycloak.conf`) and a systemd service unit for Keycloak from Jinja2 templates. The configuration sets Keycloak to use an external **PostgreSQL** database (via `KC_DB=postgres` and related env vars) and defines the host name and ports.
* **Service Management:** Registers the Keycloak service with systemd, ensuring it is enabled to start on boot and is currently running. A handler will reload systemd to pick up the new unit file and restart Keycloak when configuration changes.

In summary, applying this role results in a running Keycloak server connected to a PostgreSQL database, with Keycloak running under a limited system account as a persistent service.

## Supported Operating Systems/Platforms

This role is currently designed for **Debian-based Linux distributions**. It uses the APT package manager in its tasks, so it has been tested and verified on:

* **Debian 12 (Bookworm)** – *Tested via Molecule* (Docker container image).
* **Ubuntu LTS** (e.g. 20.04, 22.04) – *Likely supported*, given similar package names and availability of OpenJDK 17 on these releases.
* *Other Debian/Ubuntu derivatives* that use `apt` should also work with little or no modification.

**Not supported out-of-the-box:** Red Hat Enterprise Linux, CentOS, AlmaLinux, etc. (no `yum/dnf` tasks are included). Adapting the role to RHEL-based systems would require adding equivalent YUM tasks for installing packages and possibly adjusting package names (e.g. OpenJDK 17 package on RHEL) and paths. The role also assumes a systemd-based OS for service management, so non-systemd environments would need modifications.

## Role Variables

Below is a list of variables available for this role, along with default values (if set) and descriptions. Most defaults are defined in the role’s **defaults/main.yml**, while a few must be provided by the user (noted as “required”).

<details><summary>Role Variables (click to expand)</summary>

| Variable                | Default Value                                                                                                            | Description |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `keycloak_version`      | "24.0.1"                                                                                                               | Version of Keycloak to install. This should match an official Keycloak release version. It is used to construct the download URL and installation directory. |
| `keycloak_user`         | "keycloak"                                                                                                             | System username under which Keycloak will run. The role will create this user (if not present) as a system account with no login shell. |
| `keycloak_home`         | "/var/lib/keycloak"                                                                                                    | Base home directory for Keycloak. The default path is used to store Keycloak application files. |
| `keycloak_install_dir`  | `{{ keycloak_home }}/keycloak-{{ keycloak_version }}`                                                                    | Directory where Keycloak will be installed. By default, this is a subfolder of `keycloak_home` that includes the version (e.g. `/var/lib/keycloak/keycloak-24.0.1`). **Note:** Changing `keycloak_version` will alter this path (the role does not remove old version directories). |
| `keycloak_download_url` | "https://github.com/keycloak/keycloak/releases/download/{{ keycloak_version }}/keycloak-{{ keycloak_version }}.tar.gz" | URL to download the Keycloak server archive. By default it points to Keycloak’s official GitHub releases. In offline environments, you can override this to a local mirror or file path. |
| `keycloak_http_port`    | 8080                                                                                                                     | HTTP port on which Keycloak will listen for requests. This is used in the Keycloak config file as `KC_HTTP_PORT`. Default is **8080** (for HTTPS, see **Security** section). |
| `keycloak_packages`     | *List:* `['unzip', 'curl', 'openjdk-17-jre-headless']`                                                                   | List of OS packages the role will install to support Keycloak. By default: **unzip** (to extract the archive), **curl** (generally useful, e.g. health checks), and **OpenJDK 17** (headless JRE for running Keycloak). You may extend or modify this list if additional packages are required. |
| `keycloak_db_host`      | *(required)*                                                                                                             | **PostgreSQL host** for Keycloak’s database. This should be an accessible hostname or IP where a PostgreSQL server is running. **No default** is provided – you must define this in your inventory or playbook. |
| `keycloak_db_name`      | "keycloak"                                                                                                             | PostgreSQL database name that Keycloak will use. Defaults to “keycloak”. The database must exist on the `keycloak_db_host` (the role does **not** create the DB). |
| `keycloak_db_user`      | "keycloak"                                                                                                             | PostgreSQL username that Keycloak will use when connecting to the database. Defaults to “keycloak”. This user must be present in the database with appropriate privileges (the role does **not** create the DB user). |
| `keycloak_db_password`  | *(required)*                                                                                                             | Password for the Keycloak database user. No default is set for security reasons. You should supply this (preferably via an Ansible Vault variable for safety). The password will be stored in the Keycloak config file (`keycloak.conf`). |
| `keycloak_hostname`     | *inventory hostname*                                                                                                     | External hostname for the Keycloak server. By default, it uses Ansible’s `inventory_hostname` of the target (if you don’t set `keycloak_hostname`, the role will fall back to the host’s name). This is used to configure Keycloak’s `KC_HOSTNAME` setting, which should be the public host/domain users will access. If you plan to use a custom domain or load balancer, set this variable accordingly. |

</details>

**Note:** In addition to the above, the role’s template uses a fixed PostgreSQL port `5432` in the JDBC URL. If your database is running on a non-standard port, you will need to override the template or adjust the role (there is no `keycloak_db_port` variable in the role defaults). Also, ensure that `keycloak_db_host`, `keycloak_db_name`, `keycloak_db_user`, and `keycloak_db_password` are correctly set – the role will fail to start Keycloak if these are missing or incorrect, since Keycloak will not be able to connect to its database.

## Tags

This role does not define any task tags. All tasks will run by default when the role is invoked. (You cannot skip or limit the role’s tasks via Ansible tags at this time.)

## Dependencies

**Role Dependencies:** The Keycloak role itself does not depend on any other Ansible roles. No dependencies are listed in its metadata, and all modules used are part of standard Ansible (e.g. `apt`, `get_url`, `unarchive`, `template`, `systemd`). You do not need additional Ansible collections or Galaxy roles for this role to function.

However, **Keycloak has external service requirements** that should be met for a successful deployment:

* **PostgreSQL Database:** Keycloak is configured (via environment variables) to use PostgreSQL as its database. **This role does not install or configure PostgreSQL**; you must provision a PostgreSQL server separately. Ensure a PostgreSQL database is available at `keycloak_db_host` with the specified name, user, and password before or shortly after running this role. You may use a database role from this repository or an external role (e.g. *geerlingguy.postgresql*) to set up the database. At minimum, create a database and user for Keycloak and grant the user appropriate rights.
* **Java Runtime:** The role will install OpenJDK 17 by default as part of `keycloak_packages`. Ensure your target system can install this (internet access or appropriate package repositories are needed). In offline scenarios, adjust the package installation or pre-install Java.
* **Internet Access:** By default, the role downloads the Keycloak tarball from the official GitHub releases URL. The target host needs internet connectivity (or specifically, access to `github.com`) to fetch this file. If the host is in a closed network, you should provide an alternative `keycloak_download_url` pointing to an internally hosted file, or manually transfer the Keycloak archive to the host and adjust the role variables.
* **Systemd:** The target system must have systemd as the init system (the role uses the `systemd` module to manage the service). Nearly all modern Debian/Ubuntu systems use systemd, so this is usually not an issue. (If you needed to run on a system without systemd, the role’s service setup would need reworking.)

The role does not configure firewalls or proxy servers. If your environment has a firewall, you may need to open port 8080 (or whichever `keycloak_http_port` you use) for Keycloak, or adjust as appropriate.

## Example Playbook

Below is an example of how to use the `keycloak` role in a playbook. This example assumes you have a host (or group) in your inventory named **`keycloak`**, and that you have already set up a PostgreSQL database for Keycloak (or will do so separately):

```yaml
- hosts: keycloak
  become: true  # Run with privilege escalation to install packages and configure system
  vars:
    keycloak_db_host: "db.example.com"         # Hostname of the PostgreSQL server
    keycloak_db_name: "keycloak"              # Database name for Keycloak (defaults to 'keycloak')
    keycloak_db_user: "keycloak"              # Database user for Keycloak (defaults to 'keycloak')
    keycloak_db_password: "{{ vault_keycloak_db_password }}"  # Database password (use Vault for safety)
    # keycloak_hostname: "sso.example.com"    # Optionally set the external hostname if different from inventory name
    # keycloak_version: "24.0.4"             # Optionally override the Keycloak version to install
  roles:
    - role: keycloak
```

**Notes:**

* We recommend storing sensitive values like `keycloak_db_password` in an **Ansible Vault** (as shown above) or in a protected variable store, rather than plain text.
* The playbook above will install Keycloak using default settings (HTTP on port 8080, no TLS). In a production setting, you might put Keycloak behind a reverse proxy (see **Cross-Referencing** below) for TLS termination or use Keycloak’s HTTPS support (requires additional configuration not covered by this role).
* Ensure that the database host (`db.example.com` in this example) is reachable from the Keycloak host, and that the database and user are prepared.

There is also a provided playbook `playbooks/keycloak.yml` in this repository which simply includes this role for the *keycloak* host group. You can use that playbook as a quick start (adjusting inventory and group vars as needed).

## Testing Instructions

This role includes a **Molecule** test scenario for automated testing. Molecule is used to verify that the role can converge on a fresh system and that Keycloak starts correctly. To test this role locally using Molecule (with Docker):

1. **Install Molecule and dependencies**: Make sure you have Python and Docker installed. Install Molecule and its Docker driver, for example:

   ```bash
   pip install molecule molecule[docker] docker-py testinfra
   ```

   *This will install Molecule and Testinfra (for verifications). Docker must be running on your system to launch test containers.*
2. **Navigate to the scenario directory**:
   Go to the Molecule scenario for the keycloak role:

   ```bash
   cd src/roles/keycloak/molecule/default
   ```

   (This is the default test scenario for the Keycloak role.)
3. **Run the Molecule test**:
   Execute Molecule to run the full test cycle (create, converge, verify, destroy):

   ```bash
   molecule test
   ```

   Molecule will pull a Docker container (by default Debian 12) and apply the role inside it. The scenario’s converge playbook will use `playbooks/keycloak.yml` to apply the role. After convergence, Molecule will run **Testinfra** tests (if any are defined) to verify Keycloak is installed and running, then destroy the container.
4. **Observe results**:
   Ensure the playbook ran without errors. The Testinfra verification (if configured) might check that the Keycloak service is active and listening on the expected port, etc. You can review the output for assertions. (If no explicit tests are present, you can manually verify by logging into the container.)
5. *(Optional)* **Debug/Iterate**:
   During development or troubleshooting, you can run steps separately:

   * `molecule create` to create the container,
   * `molecule converge` to apply the role,
   * `molecule verify` to run tests,
   * `molecule login` to drop into an SSH shell in the container (for manual checks),
   * `molecule destroy` to clean up.

   This allows you to inspect the system if something fails. For example, after `molecule converge`, you might use `molecule login` and then check `systemctl status keycloak` or view logs.

The Molecule configuration for this role indicates the use of the **geerlingguy/docker-debian12-ansible** image (Debian 12 with Ansible), so the tests simulate a Debian 12 environment. Ensure you have a good internet connection on first run (to pull the container). All role defaults will be in effect during the test, but you can customize the scenario to test different variables if needed.

## Known Issues and Gotchas

* **Debian/Ubuntu Only:** As noted, the role currently only supports Debian-based systems using APT. Running it on a RedHat-based system will fail at the package installation step. If you require CentOS/RHEL support, you’ll need to add YUM/DNF tasks or use a different role.
* **External Database Requirement:** The role **does not** set up the PostgreSQL database or user. If the database is not ready or the connection details are wrong, Keycloak will fail to start. Symptoms include the systemd service continually restarting or errors in Keycloak logs about database connectivity. Ensure `keycloak_db_host`, `keycloak_db_name`, `keycloak_db_user`, and `keycloak_db_password` are correct and that the database is reachable from the Keycloak host (network/firewall open, credentials valid).
* **Database Port is Hard-Coded:** The JDBC URL in the Keycloak configuration template uses port **5432** by default. There is no variable to change this in the current role version. If your PostgreSQL is running on a non-default port, you must modify the template (`roles/keycloak/templates/keycloak.conf.j2`) or provide a custom template to use the alternate port.
* **Initial Admin User Not Created:** Out of the box, Keycloak requires an initial admin account to be set up (usually via `KEYCLOAK_ADMIN` and `KEYCLOAK_ADMIN_PASSWORD` environment variables, or through a manual `kc.sh add-user` command). This role **does not currently automate the creation of the Keycloak admin user**. Although variables `keycloak_admin_user` and `keycloak_admin_password` are present in some example inventories, the role’s tasks and templates do *not* use them (the `keycloak.conf` template has no entries for these). This means after installation, you will need to create an admin user. **Workaround:** You can manually export `KEYCLOAK_ADMIN` and `KEYCLOAK_ADMIN_PASSWORD` before the Keycloak service first starts, or modify the `keycloak.conf.j2` template to include these env vars. Failing to create an admin will leave you unable to log into the Keycloak admin console, which is a configuration step that must be addressed. (This is a known gap in the role – future updates might incorporate admin user setup.)
* **Clustering Not Fully Automated:** The role is capable of installing Keycloak on multiple hosts (see inventory with multiple `keycloak` hosts), but it does not itself configure clustering beyond using a shared database. For true Keycloak clustering (HA), additional steps are needed (e.g. setting up a discovery protocol or configuring JGroups/infinispan cache). The role provides some variables like `keycloak_cluster` and `keycloak_cache_stack` in examples, but currently **these are not utilized in the tasks**. If `keycloak_cluster: true` is set, you are expected to handle the cluster configuration manually (for example, ensuring all nodes use the same database and adding any needed environment vars for caching). Similarly, load-balancing is not handled by this role (see **HAProxy** in Cross-Referencing).
* **Upgrading Keycloak:** To upgrade to a new Keycloak version, you would change `keycloak_version` and run the role again. The role will download and install the new version into a new directory and update the service to point to it. However, it will **not remove the old version’s files**. Over time, you may accumulate outdated Keycloak directories under `keycloak_home`. This is by design (to avoid accidentally deleting data or config), but be aware you might need to clean up old versions manually. Always back up your Keycloak data (database and any custom configuration/themes) before upgrading. Also, review Keycloak’s upgrade guide for any steps needed between versions (the role doesn’t perform DB migration or other upgrade tasks aside from installing the new binaries).
* **No Built-in TLS/HTTPS:** The role configures Keycloak to run on HTTP (port 8080) by default. It does set `KC_PROXY=edge` in the config, which is appropriate if Keycloak is behind a TLS-terminating proxy. If you require HTTPS directly on Keycloak, you’ll need to configure SSL separately (e.g. generate certificates and adjust Keycloak settings for HTTPS). This role does not handle certificate provisioning or HTTPS enablement. A common approach is to use a reverse proxy (like HAProxy or Nginx) in front of Keycloak for TLS – see the **Cross-Referencing** section below for the HAProxy role.
* **Firewall and SELinux Considerations:** This role doesn’t configure firewall rules. On Debian/Ubuntu, if you use **UFW** or another firewall, you must open port 8080 (or your chosen `keycloak_http_port`) to allow access to Keycloak. On systems with SELinux (not typically Debian, but if adapted to RHEL), you’d need to ensure the SELinux context allows Keycloak to bind to the port and access necessary files. These aspects are outside the scope of the role and must be handled in your system security configuration.

## Security Implications

Deploying Keycloak has important security considerations. This role attempts to follow best practices (like running under a separate user), but you should be aware of the following:

* **System User & Permissions:** The role creates a system user account **`keycloak`** for running the service. The Keycloak process will run as this unprivileged user, **not** as root, which is a security best practice. The systemd unit file explicitly sets the service to run as user `keycloak` (and group `keycloak`). This limits the impact of any Keycloak compromise to that user’s privileges. The home directory and installation files are owned by `keycloak` as well.
* **Configuration File Protection:** Sensitive configuration (such as the database password, and potentially admin credentials if you add them) is stored in `/conf/keycloak.conf` which the role creates with restrictive permissions (owner `keycloak`, group `keycloak`, mode **0640**). This means only the Keycloak service account and system administrators (root) can read the file. Ensure you do not loosen these permissions. Avoid placing secrets in world-readable files.
* **Network Exposure:** By default Keycloak listens on **port 8080** for HTTP. If this port is open to the internet or untrusted networks, your Keycloak admin console and authentication endpoints will be accessible without encryption. **It is highly recommended** to put Keycloak behind an HTTPS reverse proxy or enable TLS on Keycloak itself in production. At a minimum, if running HTTP, limit access (e.g. within a private network or via firewall rules) to mitigate eavesdropping and man-in-the-middle risks. The `KC_PROXY=edge` setting is configured anticipating that Keycloak may be behind a proxy that handles HTTPS – adjust this if your deployment differs (e.g. use `KC_PROXY=passthrough` for end-to-end TLS).
* **Initial Admin Setup:** As noted, the role doesn’t auto-create an admin user. From a security standpoint, **you must create an admin account** promptly after installation (or during installation via env vars) to prevent being locked out. Use a strong password for the admin account. If you add the `KEYCLOAK_ADMIN` and `KEYCLOAK_ADMIN_PASSWORD` in the environment, treat those like secrets (do not commit them to plaintext config in version control; use Vault or an env injection strategy).
* **Patching and Updates:** Keep the `keycloak_version` up to date with the latest stable release to ensure you have the latest security fixes. Keycloak updates often include important security patches. This role makes it easy to deploy a new version, but it’s up to you to trigger that update via changing the version and rerunning, and to perform any necessary post-upgrade steps (database migrations, etc. per Keycloak’s documentation).
* **Data Security:** All Keycloak data (users, credentials, configs) is stored in the external PostgreSQL database. Secure that database properly: use strong passwords (as enforced by `keycloak_db_password`), restrict access so only Keycloak and DB admins can connect, and enable SSL for DB connections if possible. The role does not configure the JDBC connection with SSL or other security options by default – consider adjusting the Keycloak configuration if your DB requires or supports encrypted connections.
* **Underlying OS Security:** Since Keycloak is a network-exposed service, ensure the host system is hardened. Apply regular OS updates, firewall rules (if needed), and monitor the Keycloak service. The role itself doesn’t implement monitoring or logging beyond what Keycloak does by default (logging to stdout/stderr captured by systemd). You might want to set up log forwarding, health checks, etc., depending on your operational requirements.

By following these guidelines and using the role as a starting point, you can maintain a secure Keycloak installation. Always refer to the [Keycloak security documentation](https://www.keycloak.org/docs/latest/server_admin/#security-hardening) for further hardening steps that may be outside the scope of this Ansible role.

## Cross-Referencing Related Roles

Within this repository, there are several other roles that can complement or be used in conjunction with the Keycloak role:

* **PostgreSQL Database Role** – Deploy a PostgreSQL server for Keycloak. If your infrastructure doesn’t already provide a PostgreSQL instance, you can use the repository’s PostgreSQL role (if available) or a community role to set one up. This would handle installing PostgreSQL and creating the `keycloak` database and user. Keycloak’s role can then be pointed at this database. (In the repository’s inventory, a separate DB host can be configured for Keycloak; ensure to run the DB role on that host.)
* **HAProxy Role** – The repository includes a role for **HAProxy**, a load balancer. This is useful if you are running Keycloak in a **cluster** (multiple Keycloak instances) or if you want to **terminate TLS** in front of Keycloak. For example, you could deploy two Keycloak nodes (using this role on two hosts) and then use the **haproxy** role to distribute traffic between them on port 8443/443 with an SSL certificate. The HAProxy role can be configured to forward requests to Keycloak’s internal 8080 port. (See the HAProxy role documentation for setup details.)
* **OpenLDAP Role** – If you plan to integrate Keycloak with an LDAP directory for user federation, the **openldap** server role can be used to set up an OpenLDAP server within your environment. While configuring Keycloak to connect to LDAP is done within Keycloak (e.g. via the admin console or Keycloak’s API/CLI), having an OpenLDAP directory ready (courtesy of the **openldap_server** role) can be part of your overall identity management deployment. The repository’s roles include OpenLDAP (and corresponding client configurations).
* **Step CA Role** – The **Step CA** role sets up a private Certificate Authority (using Smallstep’s CA). This can be useful if you need to issue certificates for Keycloak or its proxy. For instance, you could use Step CA to generate an internal TLS certificate for the Keycloak server or for HAProxy. While not directly integrated with the Keycloak role, it’s a relevant piece if your deployment requires internal PKI. (E.g., issue a certificate for `keycloak_hostname` to enable HTTPS on Keycloak or the proxy.)
* **Base/Hardening Roles** – Depending on your environment, you might have a **base** role that ensures firewall (UFW) is configured, system updates are applied, etc. The repository contains roles such as **ufw** (firewall) and others for general setup. Consider using those to harden the system where Keycloak runs, e.g., enabling the firewall and allowing only necessary ports.
* **Other Application Roles** – Keycloak often works alongside other services (for example, a frontend that uses Keycloak for SSO, or other tools like **NetBox**, **Jenkins**, etc.). This repository has roles for many such services. While not directly related to Keycloak’s operation, you might deploy Keycloak as part of a larger stack using multiple roles from this repo. The provided **playbooks** (e.g., `site.yml` or environment-specific playbooks) show examples of how roles can be combined.

Each role mentioned has its own documentation and defaults. Refer to those roles’ READMEs or defaults for configuration details. By leveraging multiple roles, you can orchestrate a full environment (for instance, standing up a database with the Postgres role, deploying Keycloak with this role, and fronting it with HAProxy for high availability and TLS).

