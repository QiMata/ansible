# OpenLDAP Server Role

## Table of Contents

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Cross-References](#cross-references)

## Overview

The **OpenLDAP Server** role installs and configures an OpenLDAP directory server (**slapd**) on target hosts. It provides the foundation for an LDAP service by handling the installation of required packages and applying initial server configuration. In practice, this role will:

* **Install OpenLDAP** server packages (`slapd`) and client utilities (`ldap-utils`) via the system package manager.
* **Pre-configure the Directory Suffix and Admin**: Preseed the installation with a base **domain name** and **admin password** so that the slapd service initializes with the correct suffix (e.g. `dc=example,dc=com`) and an administrator account (typically **cn=admin,<base DN>**).
* **Ensure Service Is Running**: Enable the `slapd` service to start on boot and verify that it is running after installation.
* **Configure Logging Level**: Set the OpenLDAP log verbosity (the **olcLogLevel** in `cn=config`) to a desired level (default **256**, which corresponds to “stats” level logging).
* **Optional TLS Support**: If TLS is enabled, deploy the provided SSL/TLS certificate, private key, and CA certificate files to the server, and update the LDAP config to use them (setting `olcTLSCertificateFile`, `olcTLSCertificateKeyFile`, etc.). This prepares the server for secure LDAPS (LDAP over SSL) or StartTLS operation.
* **Idempotent Configuration**: The role can be re-run on a host to ensure configuration drifts are corrected (it will re-apply the log level or TLS settings as needed). Most tasks are only applied when changes are needed, making repeated runs safe in principle.

By separating the *server installation* from *directory content population*, this role focuses on getting the LDAP service up and running with a baseline configuration. **It does not load any directory entries or schemas beyond defaults** – for adding organizational units, users, groups, or additional schema, see the complementary **openldap_content** role. Likewise, advanced features like replication or custom access controls are handled by dedicated roles (e.g. **openldap_replication** for multi-master setups). In summary, use **openldap_server** to provision a functioning LDAP server instance, then layer other roles to customize and extend its functionality.

```mermaid
flowchart TD
    A[Preseed debconf: domain & admin password] --> B[Install slapd & ldap-utils (APT)]
    B --> C[Enable & start slapd service]
    C --> D[Set olcLogLevel = 256 (stats logging)]
    D --> E{TLS enabled?}
    E -- Yes --> F[Copy TLS cert/key/CA & update olcTLS settings]
    F --> G[Notify slapd service restart]
    E -- No --> G[--]
    G[slapd running with configuration applied]
```

## Supported Operating Systems/Platforms

This role is designed and tested on **Debian-based Linux distributions** (Debian and Ubuntu). It installs packages using **APT**, and thus assumes the target is running an apt-compatible OS. Specifically, the following platforms are supported:

* **Ubuntu** – tested on LTS releases (20.04 Focal, 22.04 Jammy, etc.).
* **Debian** – tested on Debian 10 (Buster), 11 (Bullseye), and 12 (Bookworm), and likely compatible with newer versions.

> **Note:** Because the role uses Debian/Ubuntu-specific package names and debconf settings (e.g. package **slapd**, **ldap-utils**), it will **not work on Red Hat Enterprise Linux, CentOS, AlmaLinux/Rocky, or other RPM-based systems without modification**. In particular, on RHEL systems the equivalent packages (like `openldap-servers`, `openldap-clients`) and configuration methods differ. Adapting this role to RHEL would require switching to `yum`/`dnf` for package installation and adjusting service setup. Ensure your targets are running a supported Debian/Ubuntu OS before using this role.

## Role Variables

Below is a list of default variables for the role, defined in **`defaults/main.yml`**, along with their default values and descriptions. You can override these in your inventory or playbook as needed. Variables marked **(required)** should be set, as the defaults are mostly placeholders or examples.

<!-- markdownlint-disable MD033 -->

<details><summary>Click to view default role variables</summary>

| Variable                  | Default Value                                   | Description |
| ------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`ldap_domain`**         | `"example.com"`                                 | **Base domain name** for the LDAP directory. This is used during installation to configure the directory suffix. For example, if set to `"example.com"`, the resulting base DN will be `dc=example,dc=com`. In a Debian-based install, this value is preseeded to the slapd installer (debconf) as the LDAP domain. Typically, you should set this to your organization’s domain name (e.g., `"company.org"`). |
| **`ldap_base_dn`**        | `"dc=example,dc=com"`                           | **Base Distinguished Name** (suffix) of the LDAP directory. This should correspond to your `ldap_domain`. By default it’s simply `dc=example,dc=com`, which matches the example domain above. **Important:** If you change `ldap_domain`, you should also update this to the proper calculated DN (the role does **not** automatically derive it). For instance, for `ldap_domain: "school.edu"`, set `ldap_base_dn: "dc=school,dc=edu"`. This DN will be the root of your LDAP directory tree. |
| **`ldap_organization`**   | `"Example Corp"`                                | **Organization name** to associate with the directory. This is a human-readable name for your company or group, used in the top-level LDAP entry (often as the `o` attribute). In Debian’s automated setup, this would correspond to the “organization” value in slapd configuration. By default it’s a placeholder "Example Corp". You can change it to your organization’s full name (e.g., `"Acme, Inc."`). |
| **`ldap_admin_password`** | *none* (uses `{{ vault_ldap_admin_password }}`) | **Admin password for LDAP root** (the **Directory Manager** account). **(Required)** – there is no hard-coded default password for security reasons. You must provide this, preferably via an Ansible Vault variable (as shown by the default referencing `vault_ldap_admin_password`). This password will be set as the LDAP directory’s admin (root) password during installation. You may supply it in plain text or as an **already hashed** value (SSHA hash, etc.). If provided in plain text, it will be stored as such in the LDAP config (which is a security risk – see notes in Security Implications). Supplying a pre-hashed password (e.g. `{SSHA}...`) is recommended for better security. |
| **`ldap_use_tls`**        | `false`                                         | Whether to **enable TLS/SSL** for the LDAP server. If `true`, the role will attempt to configure slapd for secure connections (LDAPS on port 636, and/or StartTLS on 389). Specifically, it will copy your certificate files and set the appropriate TLS attributes in the LDAP config (olcTLSCertificateFile, olcTLSCertificateKeyFile, olcTLSCACertificateFile). Note that simply enabling this flag is not sufficient; you must also provide valid certificate and key files (see below), and ensure the slapd service is configured to listen on LDAPS (the default init script will listen on ldapi:/// and ldap:// by default; with TLS enabled, you may need to adjust it to add ldaps:// – see **Known Issues**). |
| **`ldap_tls_cert`**       | `"/etc/ldap/ssl/ldap.crt"`                      | Path to the **LDAP server’s SSL/TLS certificate** file. This should be an accessible path on the Ansible **control machine** (or a file distributed with your playbook/role) pointing to the public certificate for your LDAP server. When `ldap_use_tls: true`, this file will be copied to the target host at `/etc/ldap/ssl/ldap.crt` (the location used in slapd configuration). By default, it’s set to `/etc/ldap/ssl/ldap.crt`, assuming you might place the cert there locally; you should override this to the actual certificate file path if different. |
| **`ldap_tls_key`**        | `"/etc/ldap/ssl/ldap.key"`                      | Path to the **LDAP server’s private key** file. This should be the private key corresponding to the LDAP certificate. It is used only if TLS is enabled. The file at this path will be copied to the target as `/etc/ldap/ssl/ldap.key`. **Ensure this key is kept secure** (on both control and target machines), as it grants the ability to impersonate the LDAP server if compromised. |
| **`ldap_tls_ca`**         | `"/etc/ldap/ssl/ca.crt"`                        | Path to the **Certificate Authority (CA) certificate** to trust for LDAP. If your LDAP server’s certificate is signed by a private or internal CA (or it’s self-signed), provide the CA cert here. The role will copy it to `/etc/ldap/ssl/ca.crt` on the server and configure slapd to trust this CA for TLS connections. If using a certificate from a well-known public CA, this may not be necessary (clients will trust it via their system CA store), but providing it does not harm. |
| **`ldap_log_level`**      | `256`                                           | Numeric **log level** for the LDAP server. This sets how verbose OpenLDAP’s logging should be. The default 256 corresponds to “stats” logging, which records high-level operations (connections, bind attempts, searches, etc.). Other common values: 0 for no logging, 128 for minimal, 256 for stats, 256+128=384 for stats+packets, and higher values for debug levels. Adjust this as needed for troubleshooting or verbosity. The role applies this by updating the `olcLogLevel` in the config database (`cn=config`). |
| **`ldap_extra_schema`**   | `[]` (empty list)                               | **Additional LDAP schemas** to load. This can be a list of schema LDIF file names or paths that you want to ensure are added to the LDAP server. By default, it’s empty (no extra schemas). The OpenLDAP package already includes core schemas (e.g. *core*, *cosine*, *nis*, *inetorgperson* are typically loaded by default on Debian). If you need to add other schemas (perhaps custom or less common ones), you can list them here and provide the LDIF files via this role or other means. *Note:* At present, this role does not automatically import the files even if listed – you would need to handle the loading (for example, by using the **openldap_content** role or additional tasks) unless this functionality is implemented in the future. |

</details>
<!-- markdownlint-enable MD033 -->

**Notes on variables:** It’s strongly recommended to **override** at least `ldap_domain`, `ldap_base_dn`, and `ldap_admin_password` for your deployment (the defaults are example values). The admin password should be stored securely (e.g., in an Ansible Vault) and ideally provided as a pre-hashed string for security. If using TLS, ensure the certificate/key file paths are correct and the files exist on the control host (or are included in the role/files). The role will not generate certificates for you. Also, double-check that `ldap_base_dn` matches the domain components of `ldap_domain` – the role does not auto-calculate `ldap_base_dn` from `ldap_domain`.

## Tags

This role does **not define any custom Ansible tags** for its tasks. All tasks will run by default when the role is included. There are no built-in tags to selectively skip or run portions of this role (every task is unconditionally executed unless you apply your own conditionals).

*Usage:* If you need to control execution, you can apply tags at the playbook level when including the role (for example, in a playbook you might include the role with `tags: ['ldap','openldap']` to group it). Otherwise, by design, every task in **openldap_server** runs whenever the role is invoked.

## Dependencies

This role has **no hard dependencies on other Ansible roles**; it can be used on its own to set up an OpenLDAP server (the role’s `meta/main.yml` does not list any required roles). However, in a typical environment you will use it alongside other roles (for example, to configure firewall rules, or to load initial LDAP data). See the **Cross-References** section for complementary roles in this repository.

**Requirements and Prerequisites:**

* **Ansible Version:** It is recommended to use Ansible **2.14+** (Ansible Core 2.14 or newer) with this role. The role utilizes newer features and modules (via collections) that are available in modern Ansible versions.

* **Collections:** This role relies on the **community.general** Ansible collection for certain modules (notably the LDAP utilities). In particular, it uses `community.general.debconf` during installation and `community.general.ldap_attrs` to apply settings in the LDAP configuration database. Ensure this collection is installed on your control machine before running the role. You can install it with:

  ```bash
  ansible-galaxy collection install community.general
  ```

* **Python LDAP library on target:** The managed node (target server) needs to have the **Python LDAP** library installed for Ansible’s LDAP modules to function. On Debian/Ubuntu, this is provided by the package **python3-ldap**. (If you are using the system Python on the target, installing `python3-ldap` via apt is sufficient.) The older version of this role ensured that package was installed; currently, you should verify that **python3-ldap** is present on the LDAP server host. Without it, tasks using `ldap_attrs` may fail. Typically, the `python3-ldap` package can be installed alongside slapd (it may not be pulled in by default, so consider installing it in advance or via an extra task).

* **Privileges:** You must run this role with **privilege escalation** (`become: yes`). Installing packages, modifying system files, and updating the slapd configuration database all require root permissions. Notably, the LDAP configuration changes are applied via a **ldapi:/// (SASL EXTERNAL)** bind, which only works as root (the role uses the EXTERNAL bind on the local LDAP socket). Ensure your play or inventory allows sudo/become for the target host.

* **External Dependencies:**

  * **OpenLDAP packages:** The role will install the necessary packages (`slapd`, `ldap-utils`) from the OS repositories. Internet access or an internal package mirror is required for this step.
  * **No additional roles required:** As mentioned, the role doesn’t depend on other roles. It will install packages and configure slapd on its own. (It is often used with others like firewall or content-loading roles, but those are optional and not automatically invoked.)

In summary, before running **openldap_server**, make sure you have the **community.general** collection installed on the control node and that your target system is prepared (proper OS, network access to package repos, and privileges set). After that, you can run this role independently to set up the LDAP server.

## Example Playbook

Here is an example of how to use the **openldap_server** role in a playbook:

```yaml
- hosts: ldap_servers
  become: yes
  vars:
    ldap_domain: "corp.example.com"
    ldap_base_dn: "dc=corp,dc=example,dc=com"
    ldap_admin_password: "{{ vault_ldap_admin_password }}"  # Assume this is defined via Ansible Vault
  roles:
    - role: openldap_server
      # Optionally enable TLS:
      # ldap_use_tls: true
      # ldap_tls_cert: "/path/to/corp_example_com.crt"   # Path on control machine to LDAP server cert
      # ldap_tls_key: "/path/to/corp_example_com.key"   # Path on control machine to LDAP server key
      # ldap_tls_ca:  "/path/to/my_ca.crt"             # Path to CA cert if using self-signed or internal CA
```

**Explanation:** This playbook targets hosts in the `ldap_servers` group and runs the openldap_server role on them. We elevate privileges with `become: yes` because package installation and config changes need root rights. In `vars`, we specify our domain and base DN (`corp.example.com` -> `dc=corp,dc=example,dc=com`) and supply an admin password (here referenced from an encrypted Vault variable). The role will install OpenLDAP on each host, initialize it with the domain “corp.example.com” (creating the suffix `dc=corp,dc=example,dc=com` and an admin user `cn=admin,dc=corp,dc=example,dc=com`), and set the admin password.

If we wanted to enable TLS/LDAPS in this setup, we’d set `ldap_use_tls: true` and provide the paths to the certificate and key files for the server (as shown in the commented lines). These files must be accessible to Ansible on the control side; the role will copy them into `/etc/ldap/ssl/` on the target host. After running this play, the LDAP service (slapd) will be running on each host, ready to accept connections (on port 389 by default, and port 636 if TLS was configured).

## Testing Instructions

It is highly recommended to test this role with **Molecule** (using Docker or another driver) to verify its behavior before using it in a production environment. A Molecule test can ensure that the role converges correctly on a fresh system and is idempotent.

If a Molecule scenario is provided with this role (e.g. under `molecule/` directory of `roles/openldap_server`), you can use it directly. If not, you can create one easily. Below are general steps to test:

1. **Install Molecule and dependencies**: On your development machine, install Molecule and the Docker driver, as well as testing tools:

   ```bash
   pip install "molecule[docker]" pytest testinfra
   ```

   Ensure Docker is installed and running (if using the Docker driver).

2. **Prepare a Molecule scenario**: If the role already includes a Molecule scenario (check for a `roles/openldap_server/molecule/` folder), navigate to it. Otherwise, initialize a default scenario:

   ```bash
   molecule init scenario -r openldap_server -d docker
   ```

   This will create a `molecule/default` scenario with a basic config.

3. **Configure the test scenario (if needed)**: Edit `molecule/default/molecule.yml` to choose an OS image (e.g., use a Debian/Ubuntu Docker image). Also edit `molecule/default/converge.yml` – it should include the `openldap_server` role. Set necessary variables in that play (at minimum, define `ldap_domain`, `ldap_base_dn`, and a `ldap_admin_password`, since the role requires those).

4. **Run Molecule converge**: From the role directory, run:

   ```bash
   molecule converge
   ```

   Molecule will create a container and apply the role. Watch the output for any errors. After convergence, you can use `molecule login` to enter the container and manually inspect the LDAP server (e.g., check that `slapd` is running, see if the configuration is as expected).

5. **Verify functionality**: Within the Molecule container, you might run some basic checks:

   * Ensure the slapd process is running: `ps -ef | grep slapd` (or `systemctl status slapd` if systemd is available in the container).
   * Verify LDAP is listening on the expected port(s): e.g., `ss -ltn | grep 389` for LDAP. If TLS was enabled, check `ss -ltn | grep 636` for LDAPS.
   * Perform a simple LDAP query. For example, using ldapsearch (installed via ldap-utils):

     ```bash
     ldapsearch -x -H ldap://localhost -b "dc=corp,dc=example,dc=com" -D "cn=admin,dc=corp,dc=example,dc=com" -w '<admin_password>' -s base "(objectclass=*)"
     ```

     This should retrieve the base DN entry if the server is configured (replace the base DN and password as appropriate for your test). If you get results with `dc=corp,dc=example,dc=com` attributes, the server is functioning.
   * If TLS is enabled in the test, you can test an LDAPS connection. For example:

     ```bash
     ldapsearch -x -H ldaps://localhost -b "dc=corp,dc=example,dc=com" -D "cn=admin,dc=corp,dc=example,dc=com" -w '<admin_password>' -LLL
     ```

     Or use `openssl s_client -connect localhost:636` to check the certificate handshake.

6. **Idempotence test**: Run `molecule converge` again (or `molecule idempotence`) to ensure that running the role a second time results in "OK" for all tasks (no changes). Molecule does this automatically in the `molecule test` sequence. If any task reports "changed" on the second run, it indicates a potential idempotence issue that should be fixed.

7. **Full test cycle**: Finally, run the full test suite with:

   ```bash
   molecule test
   ```

   This will recreate the container, apply the role, run any verification steps, and then destroy the container. It’s a one-command way to do steps 4–6 in one go.

By following these steps, you can confidently validate that the **openldap_server** role works as expected on a fresh system and doesn’t introduce unexpected changes on repeated runs. Always test with Molecule (or a manual VM) before deploying to production servers.

## Known Issues and Gotchas

* **Debian-specific Implementation:** As noted, this role currently targets Debian/Ubuntu environments. Attempting to run it unmodified on RedHat/CentOS systems will fail or produce incorrect results (due to missing apt, debconf, etc.). If you require RHEL support, you must modify the tasks for yum/dnf and adjust service names and paths.

* **Admin Password in Plain Text:** The LDAP admin password (`ldap_admin_password`) is applied as given. The role does **not hash or encrypt the password before storing it in LDAP**. That means if you provide it in plain text, it will be stored **as plain text (or a trivially Base64-encoded form)** in the LDAP configuration database (`cn=config`). This is a security concern because anyone with read access to the config (which is typically root-only) could see the admin password. It’s recommended to pre-hash the password using a tool like `slappasswd` (which generates a `{SSHA}` or other hash) and use that value for `ldap_admin_password`. Alternatively, ensure strong protections on the config database and use Ansible Vault to avoid exposing the cleartext in playbooks.

* **TLS/SSL Configuration Considerations:** While this role will configure TLS settings if `ldap_use_tls: true`, there are a couple of caveats:

  * **Service Listener:** Simply configuring TLS does not automatically make slapd listen on port 636 for LDAPS. On Debian systems, slapd’s default startup options (in `/etc/default/slapd`) may need to include `ldaps:///` to actually enable the LDAPS listener. The role itself does **not** modify the default listener configuration. If you find that after enabling TLS the server is not listening on 636, you may need to adjust the slapd service options manually (or use the **openldap_logging** role or a custom task to set the `SLAPD_SERVICES` environment variable to include ldaps://). Alternatively, clients can use StartTLS on the standard port 389, which the server will support if TLS is configured.
  * **Certificate File Permissions:** After copying the certificate and key to `/etc/ldap/ssl/`, the files are owned by root (with the key file set to mode 0600 by default). However, the slapd process runs as the `openldap` user, which means **openldap will not be able to read the key file by default**. This is a known issue – if left unaddressed, slapd will fail to start TLS or LDAPS because it cannot access the private key. You must ensure the `openldap` user can read the key. There are a few ways to handle this:

    * Change the ownership of the key to `openldap` (and perhaps group `openldap`) and set mode 640.
    * Add the `openldap` user to a group that owns the key (and adjust file group and mode accordingly). Debian’s default approach is sometimes to add `openldap` to the `ssl-cert` group if keys are placed there. In our role’s context, one workaround is adding `openldap` to the `root` group (not ideal security-wise).
    * Run a custom task after this role to `chmod` or `chown` the `/etc/ldap/ssl/ldap.key` file appropriately.

  The key point is: **ensure the slapd process can access the TLS key file.** The role doesn’t currently fix the permissions, so without manual intervention you might encounter startup errors. For example, you can add a task in your playbook like:

  ```yaml
  - name: Adjust permissions on LDAP key
    file:
      path: /etc/ldap/ssl/ldap.key
      owner: openldap
      group: openldap
      mode: '0640'
    when: ldap_use_tls
  ```

  This would give the OpenLDAP server user read access to the key while still protecting it from others.

* **Firewall Ports Not Opened:** This role **does not manage firewall settings**. If your servers have a firewall enabled (UFW, iptables, firewalld, etc.), you must open the LDAP ports yourself. By default, slapd listens on TCP port **389** for LDAP (and 636 for LDAPS if enabled). Ensure these are permitted through the firewall to your client hosts. (In this repository, there is a separate **ufw** role; if you use it and set `ufw_allow_ldap: true` and `ufw_allow_ldaps: true` in your inventory, it will open those ports. But unless you run that role, no changes to firewall will be made.)

* **Re-running the Role on an Existing Server:** The role is primarily intended for initial setup of a new LDAP server. If you run it on a system that already has OpenLDAP configured, be cautious:

  * **Base DN and Admin**: The debconf preseeding will not reconfigure an existing slapd installation (it runs only during package install). The role does not explicitly handle changing an existing directory suffix or admin DN. So if the system was set up with different values, re-running the role won’t change them (aside from possibly altering the admin password via debconf, which may not take effect on an already-initialized DB).
  * **Idempotence of LDAP changes**: The tasks that use `ldap_attrs` (for loglevel and TLS) use `state: present`. If a value is already set, these tasks usually won’t duplicate it, but they will ensure it exists. Generally, they are idempotent (setting the same log level twice is fine). However, if you intentionally change `ldap_log_level` or toggle `ldap_use_tls` between runs, the role will apply those changes to the running config (e.g. updating olcLogLevel or adding/removing TLS settings). This could potentially override manual changes made outside Ansible.

  In summary, you can safely re-run the role to enforce the configured state (it will ensure the service is installed and the config settings remain as specified). But if you need to change fundamental settings like the base DN or admin user after the initial setup, those require manual intervention or specialized steps (not handled by the role automatically). Always review what changes a rerun would make (e.g., check if `ldap_domain`/`ldap_base_dn` match the current server state) to avoid unintentional alterations.

* **Extra Schemas Not Loaded Automatically:** The `ldap_extra_schema` variable is provided for completeness, but the role by itself doesn’t yet implement tasks to load those schema files. OpenLDAP on Debian comes with certain schemas already loaded (like cosine, nis, inetorgperson). If you listed others (or custom schemas) in `ldap_extra_schema`, you would need to apply them using another method (for example, the **openldap_content** role or a manual `ldapadd` command). Failing to load a needed schema could prevent you from adding certain attributes or objectClasses to LDAP. Keep this in mind if your directory structure needs additional schemas – ensure they are loaded either via a different role or an extension of this one.

## Security Implications

Deploying an LDAP directory service involves several security considerations. This role sets up a basic but functional configuration; you should review and adjust settings to meet your security requirements. Key points:

* **Service Account and Privileges:** OpenLDAP (slapd) does **not run as root**; it uses a dedicated user account **`openldap`** created by the package. This is a security best practice to limit the damage if the service is compromised. All LDAP database files and configs under `/etc/ldap` and `/var/lib/ldap` are owned by `openldap`. One implication of this is file permissions for TLS keys (as discussed). By default, our role does *not* change the group membership of the `openldap` user. In Debian’s default setup, the slapd process runs as `openldap:openldap`. If you place certificates under `/etc/ldap/ssl` owned by root, you either need to adjust those file permissions or (less ideally) add `openldap` to a group that can read them (some setups use the `ssl-cert` group for this purpose). Adding `openldap` to the `root` group (as the older setup role did) is generally not recommended, as it grants that user broad read access. A safer approach is to restrict the certificate files’ ownership to `openldap` or a specific group with minimal membership. In any case, ensure the slapd process can only access what it needs and nothing more.

* **Network Exposure:** After this role, the LDAP server listens on **LDAP port 389** (and possibly **LDAPS port 636** if configured). The role does not restrict access to these ports. You should control network access using firewalls or security groups to allow only trusted hosts to communicate with LDAP. Also consider the sensitivity of the data: if anonymous binds can read your directory (see next point), having the LDAP port open to the world could leak information. Best practice: run LDAP within a protected network or VPN, or at least firewall it to permitted clients.

* **Anonymous Access & ACLs:** By default, the LDAP server (as configured by the standard slapd package) allows **anonymous read access** to most entries, while restricting certain sensitive attributes like passwords. In other words, anyone who can connect can query public fields in the directory (this is the out-of-the-box behavior unless you change the access rules). This role *itself* does not modify the default access control list (ACL). The default ACL on Debian typically includes rules like *"by anonymous read"* for the entire suffix and *"by self write"* for userPassword, etc. This means **userPassword attributes are protected (only the user or authenticated binds can check them), but general directory information (names, emails, etc.) may be readable by anyone**. Depending on your use case, this might be acceptable (e.g., a public address book), or it might be a security risk. If you need to tighten access, you should introduce custom ACLs. You can do this via the **openldap_content** role or manually using `ldapmodify` on `cn=config` to adjust `olcAccess` rules. For instance, you could require authentication for any read access, or limit reads to certain bind DN groups. Always design your ACLs to principle of least privilege for your environment.

* **LDAP Admin Credentials:** The **LDAP Root DN** (admin user) has full control over the directory. Protect its credentials:

  * Use an unpredictable, strong password (and change it periodically if possible).
  * **Do not store the admin password in plain text** in any source control or inventory. Always use Ansible Vault or another secret management mechanism to supply `ldap_admin_password`.
  * As mentioned, consider hashing the admin password. If you set `ldap_admin_password` to a hash (like `{SSHA}...`), the LDAP config will store that hash and require that the admin bind password matches it. This way, even if someone sees the config, they cannot easily reverse the hash to get the plaintext. You can generate such a hash with the `slappasswd` utility.
  * Limit how the admin account is used. Typically, `cn=admin,<base>` should only be used for administrative tasks – not by applications. Create less-privileged bind users for applications if needed, with specific ACL rights.

* **Encryption (TLS):** By default (if `ldap_use_tls` is false), the LDAP server accepts unencrypted connections on port 389. This means any credentials or sensitive data sent via LDAP are transmitted in clear text over the network. In a secure, isolated network, this might be tolerable, but it’s generally advisable to enable encryption:

  * Enabling **LDAPS (TCP 636)** or **StartTLS on 389** ensures that LDAP traffic is encrypted in transit, protecting against eavesdropping.
  * If you enable TLS via this role, make sure clients are configured to trust the certificate. If you used a self-signed or internal CA cert, deploy that CA to your clients (so they don’t refuse the connection). The role configures the server side, but client side trust is up to you.
  * If you cannot use TLS, consider tunneling LDAP traffic over a VPN or SSH tunnel when crossing untrusted networks.
  * Reminder: The role configures TLS but does not force clients to use it. If both 389 and 636 are open, clients could still bind without encryption unless you enforce policies. Some organizations choose to allow only LDAPS and close port 389 entirely.

* **Data Confidentiality in Backups:** (Though backup is handled by another role, it’s worth noting.) If you use **openldap_backup** to dump directory contents, those LDIF files may contain sensitive data (including password hashes). Protect the backups – they should be stored securely and access to them should be restricted. The backup role by default keeps them locally on the server with root-only access. Ensure any off-host transfer or long-term storage of those archives is done securely (encryption, etc.).

* **Monitoring and Logs:** The `ldap_log_level` is set to a moderate level (256, stats). This will log operations but not their detailed content. For security auditing, you might increase logging to record binds and queries, or use the **openldap_logging** role to set up specific audit logging. Be mindful that higher log levels can expose sensitive info in logs (like search filters or even data). Balance the need for auditing with privacy.

* **Physical Security:** Ensure the server hosting LDAP is secure (as with any critical infrastructure). LDAP often holds identity information that could be sensitive (employee data, authentication info if not using Kerberos, etc.). Standard host security measures (patching, minimal services, secure configuration) apply here too.

In summary, the **openldap_server** role gets you a running LDAP server with a basic configuration. You should review the default settings (especially ACLs and network exposure) and adjust according to your organization's security policies. Use encryption for authentication, protect the admin account, and restrict access to the service to only what is necessary. The other roles in this suite (like logging or client configuration) can further enhance security by providing auditing and ensuring proper client usage of the directory. Always test configuration changes in a safe environment to understand their impact on security and functionality.

## Cross-References

The **openldap_server** role is one part of a suite of roles in this repository for managing an OpenLDAP ecosystem. Related roles that you might use in conjunction include:

* **openldap_content** – After the server is up, this role can populate the directory with initial entries and structure (base DN entry, default OUs like People and Groups, test users, etc.). It ensures your LDAP database has the required organizational content.
* **openldap_replication** – If you need a multi-server setup (for redundancy or load-balancing), this role sets up replication between a primary LDAP server and secondary server(s) using **syncrepl**. Use it to configure master/master or master/slave replication without manually editing config; it pairs with openldap_server to extend the deployment to multiple nodes.
* **openldap_logging** – Configures enhanced logging for OpenLDAP. This might adjust the log level (beyond what this role sets by default) and potentially integrate with system logging (rsyslog) to route LDAP logs to a specific file or service. Useful for audit trails and debugging LDAP operations.
* **openldap_backup** – Automates backups of the LDAP data. It can dump the LDAP directory (and `cn=config`) to LDIF on a schedule (e.g., nightly) and optionally rotate those backups. This role is crucial for disaster recovery; it assumes you have openldap_server already set up (since it uses tools like `slapcat` which come from the `ldap-utils` installed by openldap_server).
* **openldap_client** – Configures Linux systems to use LDAP for authentication (often in combination with Kerberos). While not directly modifying the LDAP server, it’s included here as part of the ecosystem: use openldap_client on your application or user machines to point them to your LDAP server for centralized auth. It sets up SSSD or similar and ties into the LDAP directory and (optionally) Kerberos for password verification.
* **Firewall (ufw)** – The repository includes a UFW role (if applicable) to manage firewall settings. As mentioned, the `group_vars/openldap.yml` in this repo suggests enabling LDAP ports in UFW. If you include that role in your playbook, it will read those vars and open ports 389 and 636 to allow LDAP traffic. This is recommended if your servers have UFW enabled, to ensure the directory service is reachable by clients.
* **Example Playbook:** For a complete example of how these roles work together, refer to the provided playbook [**ldap-servers.yml**][ldap-servers.yml]. In that playbook, hosts in group `ldap_servers` are assigned the roles in a sequence: first **openldap_server** (this role) to install slapd, then **openldap_content** to add directory entries, followed by **openldap_replication** (conditional on a variable) to enable replication, and then **openldap_logging** and **openldap_backup** for additional functionality. This layered approach is the recommended way to use the roles: each role focuses on one aspect, and together they deliver a full LDAP server setup.

[ldap-servers.yml]: https://github.com/QiMata/ansible/blob/main/src/playbooks/ldap-servers.yml "Example LDAP servers playbook"

Using these roles in combination allows you to build a robust LDAP infrastructure. For example, you might run **openldap_server** and **openldap_content** on two servers to set them up, then run **openldap_replication** to link them, ensuring both have the same data. **openldap_backup** would be applied to each master to regularly export data, and **openldap_logging** could be used to increase verbosity or send logs to a SIEM. Meanwhile, on client machines (web servers, etc.), you’d use **openldap_client** to make them query the LDAP server for user authentication. Each role has its own README detailing usage and variables (similar in structure to this one). Be sure to consult those for deeper information on specific functionality.

---

**Maintainer Note:** This documentation is generated to assist users of the `openldap_server` role. It consolidates role-specific details and best practices from the role implementation and related knowledge. For general OpenLDAP administration or troubleshooting outside the scope of the role, refer to official OpenLDAP documentation and community resources. Always test changes in a controlled environment before applying to production servers. Enjoy your LDAP deployment!
