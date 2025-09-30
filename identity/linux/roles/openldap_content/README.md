# OpenLDAP Content Role

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

## Overview

The **OpenLDAP Content** Ansible role sets up and manages the **directory content** of an OpenLDAP server. In practice, this role populates the LDAP directory with initial data and configuration after the OpenLDAP server software is installed. This includes establishing the base directory suffix (e.g. your domain components), root/admin directory entries or credentials, and any default organizational units or entries needed for a functioning directory service. By separating *content* from the *server installation*, this role ensures that an existing slapd (LDAP server) can be configured with the desired domain data without reinstalling the service.

**Key capabilities of this role include:**

* Ensuring the LDAP database has the correct base DN (domain) and organization name.
* Setting or updating the Directory Manager (admin) DN and password (usually the `cn=admin` for the base DN).
* Creating common base entries such as organizational units (e.g. `ou=People` and `ou=Groups`) or other initial LDAP tree structure as needed.
* Loading any required baseline schema or LDIF files for initial content (if not already present from server installation).
* Installing necessary tools or packages to manipulate LDAP entries (e.g. LDAP client utilities or Python libraries for LDAP).
* Optionally supporting both offline (LDIF import) and online (ldapmodify/ldapadd or Ansible module) methods for loading content.

This role is typically used **after** the OpenLDAP server is up and running. In the context of this repository, you would first run the [`openldap_server` role](../openldap_server/README.md) to install and configure the slapd service, and then apply **openldap_content** to populate the directory. Additional roles such as [`openldap_replication`](../openldap_replication/README.md) (for multi-server setups), [`openldap_logging`](../openldap_logging/README.md) (to configure audit or debug logging), and [`openldap_backup`](../openldap_backup/README.md) (for periodic database backups) can be used in conjunction for a full OpenLDAP deployment. For example, the provided `ldap-servers.yml` playbook runs the roles in this order: OpenLDAP Server → OpenLDAP Content → OpenLDAP Replication (if enabled) → OpenLDAP Logging → OpenLDAP Backup.

## Supported Operating Systems/Platforms

This role supports a range of Linux distributions where OpenLDAP is available. It has been designed and tested on the following platforms:

* **Ubuntu** 20.04 LTS and 22.04 LTS (Focal and Jammy)
* **Debian** 10 (Buster) and 11 (Bullseye)
* **Red Hat Enterprise Linux** 7 and 8 (and derivatives like CentOS 7, AlmaLinux/Rocky 8)
* **Fedora** latest releases (for development use)

Other Unix-like systems with OpenLDAP packages *may* work with minor modifications. The role’s tasks include package installation and service management that are specific to Debian/Ubuntu (using `apt`) and RHEL/CentOS (using `yum`/`dnf`). Ensure you set the appropriate package names if using a non-standard distribution.

## Role Variables

This role defines several variables in its **`defaults/main.yml`** which can be overridden to customize OpenLDAP content configuration. Key variables are summarized below:

<details>
<summary>Click to view default role variables</summary>

| Variable                          | Default Value          | Description                                                                                                                                                                                                                                                                                        |
| --------------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`openldap_domain`**             | `"example.com"`        | The base domain name for your LDAP directory. This is used to construct the base DN (e.g. `dc=example,dc=com` by default).                                                                                                                                                                         |
| **`openldap_base_dn`**            | `"dc=example,dc=com"`  | Base Distinguished Name for the directory (suffix). If not set explicitly, it is derived from `openldap_domain`. This is the root of your organization’s directory tree.                                                                                                                           |
| **`openldap_organization`**       | `"Example Corp"`       | Organization name to set for the directory (e.g. the `o` attribute on the root entry). This is a descriptive name of the company or entity.                                                                                                                                                        |
| **`openldap_admin_cn`**           | `"admin"`              | The Common Name of the LDAP administrator account. The full root DN will be composed from this and the base DN (e.g. `cn=admin,dc=example,dc=com`).                                                                                                                                                |
| **`openldap_admin_password`**     | (None – must be set)   | **Required.** The LDAP Directory Admin password. This should be provided by the user (preferably encrypted via Ansible Vault). If this password is not pre-hashed, the role will hash it (e.g. using SSHA) before applying it to the LDAP configuration. There is no default for security reasons. |
| **`openldap_default_ous`**        | `["People", "Groups"]` | List of top-level Organizational Units to create under the base DN by default. Common values are "People" (for user entries) and "Groups". You can modify this list or set it empty if no OUs should be auto-created.                                                                              |
| **`openldap_content_ldif_files`** | `[]` (empty list)      | Optional list of LDIF file paths or names (inside role) to apply to the LDAP server. If you have additional content (like users or groups definitions in LDIF format), you can specify them here. By default, this is empty (no extra LDIFs loaded).                                               |

</details>

**Notes on variables:** By design, the role requires you to specify at minimum the **domain** and **admin password** for your LDAP directory (unless those were already configured during server installation). The `openldap_admin_password` should be a secure string. If you provide it in plain text, the role will handle hashing it before storing in LDAP. Alternatively, you can pre-hash the password (using `slappasswd` to generate a `{SSHA}` hash) and supply the hashed value directly.

If the OpenLDAP server was installed with certain parameters (for example via `debconf` on Debian or by a separate configuration), you should ensure these variables match that configuration. For instance, if the server setup already defined a different base DN or admin, adjust `openldap_base_dn` and `openldap_admin_cn` accordingly so that this role can bind and add entries correctly.

## Tags

All tasks in this role are labeled with the **`openldap_content`** tag. You can use this tag to run or skip the content setup tasks when running plays. For example:

* To **only** run OpenLDAP content setup (and skip other roles/tasks), you could run `ansible-playbook site.yml --tags openldap_content`.
* To skip populating content (e.g. on a run where you only want to install the server), use `--skip-tags openldap_content`.

Using tags provides flexibility in larger playbooks: you might include this role but not always execute it, depending on your deployment scenario or when re-running plays.

*(No other fine-grained tags are used within this role by default. All tasks are collectively controlled by the single tag above for simplicity.)*

## Dependencies

**Role Dependencies:** There are no strict Ansible role dependencies configured in `meta/main.yml` for this role (it can be used on its own). However, it **assumes** that an OpenLDAP server is already installed and running on the target host. In practice, you will almost always use the `openldap_content` role together with the [`openldap_server` role](../openldap_server/README.md) – the latter installs and configures the slapd service (packages, basic config, schemas) on the host. This content role then connects to that running service (typically via localhost) to add or modify entries.

If you are using Ansible Galaxy, make sure to install any collections required by this role (see below). This role does not automatically depend on other roles, but logically it depends on the presence of the LDAP service.

**Galaxy Collections:** This role leverages modules from the **Community General** collection for LDAP operations. Ensure you have the `community.general` collection available (e.g., by running `ansible-galaxy collection install community.general` if not already installed). In particular, it may use `community.general.ldap_entry` or `community.general.ldap_attrs` modules to add LDAP entries in an idempotent way.

**External Packages:** On the managed host (the LDAP server), the following packages are required:

* **OpenLDAP client utilities** – Tools like `ldapadd`, `ldapmodify`, etc. (Package name is typically `ldap-utils` on Debian/Ubuntu and `openldap-clients` on RHEL/CentOS). These are used if the role needs to execute LDAP commands locally.
* **Python LDAP library** – If using the Ansible LDAP modules, the target host needs Python's `ldap` library (often provided by installing `python3-ldap` or similar package). The role will attempt to install this if needed, or you should ensure it’s present in your Python environment.

Usually, the **`openldap_server` role** or your base system setup will have already installed these. If not, this role’s tasks include installing the necessary utilities/libraries so that managing LDAP entries is possible.

## Example Playbook

Here is an example of how to use the `openldap_content` role in an Ansible playbook, in the context of setting up an LDAP server with initial content:

```yaml
- hosts: ldap_servers
  become: yes
  vars:
    openldap_domain: "corp.example.com"
    openldap_organization: "Example Corp LLC"
    openldap_admin_password: "{{ vault_ldap_admin_password }}"  # assume this comes from an Ansible Vault for security
    openldap_default_ous: ["People", "Groups", "Projects"]
  roles:
    - role: openldap_server       # Installs and configures slapd
    - role: openldap_content      # Populates LDAP with base DN, admin, and OUs
```

In the above playbook:

* We target a host group `ldap_servers` (which should contain the hosts where we want OpenLDAP).
* `become: yes` is used because installing packages and configuring LDAP may require root privileges.
* We set the `openldap_domain` and `openldap_organization` to define our directory, and provide an admin password (here referenced from an encrypted variable for security). We also customize the default OUs to create an additional "Projects" OU for demonstration.
* The `openldap_server` role runs first to ensure slapd is installed and configured.
* The `openldap_content` role runs next, using the variables above to bind to the now-running LDAP service and add the initial directory entries (base DN entry and OUs in this case).

Typically, you will include **both** roles in your play as shown. The content role will connect to the local slapd instance (by default through the LDAP UNIX socket or localhost) to apply changes. After running this playbook, your LDAP server would have a directory base of `dc=corp,dc=example,dc=com` with an admin user and the specified OUs created.

*(If you also need replication, logging, etc., you would include `openldap_replication`, `openldap_logging`, and `openldap_backup` roles as needed in a similar fashion. See the repository's `ldap-servers.yml` for the full combined playbook example.)*

## Testing Instructions

This role includes a **Molecule** test scenario to verify its functionality. The Molecule configuration sets up a temporary environment (usually a Docker container running an OS like Ubuntu) to apply the role and run assertions. To run the tests for this role, follow these steps:

1. **Install Molecule and dependencies**: Make sure you have Molecule installed (`pip install molecule molecule[docker]` for Docker driver, or refer to Molecule documentation for other drivers). Also install `ansible` and any required Molecule plugins or collections (e.g. `community.general` if not already installed).
2. **Locate the Molecule scenario**: In the repository, navigate to the role directory: `roles/openldap_content`. There should be a `molecule/` directory (e.g. `roles/openldap_content/molecule/default/`) containing the test scenario (playbooks, inventory, etc.).
3. **Review and customize (optional)**: Open `molecule/default/molecule.yml` to see the platform image (e.g. Debian or Ubuntu) used for testing. By default it might use a Docker image like `geerlingguy/docker-ubuntu2204-ansible`. Also check `molecule/default/converge.yml` which is the playbook Molecule will run – it likely includes this role with some test variables.
4. **Run the tests**: Execute Molecule from the role directory:

   ```bash
   cd roles/openldap_content
   molecule test
   ```

   This will perform a full test cycle: spin up a container, apply the role (`molecule converge`), run verifications (`molecule verify`), and then destroy the container. If you want to step through, you can run `molecule converge` alone to just apply the role, then use `molecule login` to enter the container for manual inspection, and `molecule verify` to run any test cases, etc.
5. **Check idempotence**: The Molecule tests will also re-run the role to ensure that applying it a second time yields no changes (idempotence). Molecule will flag if any tasks reported changes on the second run. This helps ensure the role doesn't re-add existing entries or reset configurations each time.
6. **Destroy the test environment**: If you didn’t run the full `molecule test` (which does destruction automatically), you can clean up with:

   ```bash
   molecule destroy
   ```

The Molecule tests serve as both verification and documentation of how the role is intended to be used. You can refer to the Molecule scenario files for example variable values and usage. Ensure you have Docker (or the appropriate virtualization backend) running, as Molecule will create ephemeral instances to test the role.

*(If you encounter issues with Molecule not finding the Docker driver or missing collections, consult the project’s documentation or adjust the `molecule.yml` to suit your environment. Running the tests in a Python virtual environment dedicated to Ansible is recommended.)*

## Known Issues and Gotchas

* **Order of execution**: This role must run *after* the LDAP server is installed and started. If the slapd service is not running or not accessible (for example, if `openldap_server` hasn’t been run or if slapd failed to start), the content tasks will fail to connect to LDAP. Always include and run the server setup role first.
* **Idempotence and re-running**: The role is designed to be idempotent – running it multiple times should not duplicate entries. When using Ansible’s LDAP modules (`ldap_entry`), they ensure an entry exists with given attributes and do nothing if it’s already present. However, if using command-line tools (ldapadd), the role may attempt to check for existing entries before adding. In either case, if you re-run the role, you might see some tasks reported as "unchanged" or skipped. A known quirk is that adding the same entry twice with ldapadd will error; thus the role guards against this by either using idempotent modules or conditional checks.
* **Admin password mismatch**: If the admin (rootDN) password provided via `openldap_admin_password` does not match what the LDAP server is configured to use, the bind attempts will fail. Ensure you set the same password here that was used when configuring the server. On Debian-based systems, if you preseeded slapd with a password, use that same value. On re-runs, avoid changing the admin password via this role unless you intend to update it in LDAP.
* **LDAPI vs LDAP connection**: By default, the role will try to use a local LDAP connection. Many setups use the **LDAPI** (LDAP over IPC socket) interface for configuration changes (this allows authentication via SASL/EXTERNAL as root, eliminating the need for a password). This role attempts to use the method that is available:
  * If running on the localhost and the LDAPI socket (`ldapi:///`) is available, it may use SASL EXTERNAL bind (requires running as root) to perform config changes.
  * Otherwise, it falls back to normal LDAP network port (389) and uses `openldap_admin_dn` and `openldap_admin_password` to bind.
  A possible gotcha is if LDAPI is disabled or if the role is forced to use a network bind without TLS – in such cases, credentials travel in plaintext. Ensure network security (or use LDAPI) in sensitive environments (see **Security Implications** below).
* **Custom schemas and attributes**: If you intend to add entries that rely on custom object classes or attributes, make sure those schemas are loaded into OpenLDAP **before** running this content role. The `openldap_server` role by default loads core schemas (COSINE, InetOrgPerson, etc.). If you need additional schemas (e.g., EDuperson, custom application schemas), load them (via an LDIF in server or using a schema role) prior to adding entries that use them, otherwise the LDAP add operations will fail due to unknown object classes or attributes.
* **Replication considerations**: In a multi-master or master-slave scenario, populating content should typically be done on the primary provider (master) and will replicate to consumers. If you run this role on multiple servers in a replicated setup, be careful not to duplicate the initialization on each node. Instead, run it once on the main node. The `openldap_replication` role handles configuring replication agreements, but it assumes the base DN exists. So use `openldap_content` on the provider node first, then run replication setup.

## Security Implications

This role touches on sensitive parts of your LDAP infrastructure. Be mindful of the following security implications:

* **Credentials in Ansible**: The LDAP admin password (`openldap_admin_password`) is sensitive. **Do not store it in plain text** in playbooks or inventory. It is highly recommended to encrypt this variable with Ansible Vault. Treat your Ansible vault or secrets management with the same care as you would treat the LDAP password itself.
* **On-disk password storage**: When the role sets the LDAP admin password in the LDAP configuration database, it is stored as a salted hash (e.g. `{SSHA}`) inside OpenLDAP. This is normal and secure for LDAP, but if you are re-running the role with a changed plain-text password, the role will update the stored hash. There is a brief moment where the plain text password is used to bind or to generate the hash. Ensure your Ansible control node and logs are secure to prevent leakage of this secret. The role will not expose the password except as needed for the LDAP operation.
* **Network transmission**: By default, if using an unencrypted LDAP connection (ldap:// on port 389), the content (including passwords for any entries and the bind password) would traverse the network unencrypted. In the typical use-case where the role is run on the LDAP server (`localhost` connection or using the LDAPI socket), this is not an issue (no network hop or it’s IPC). However, if you target a remote host over an SSH connection and the role uses network LDAP, consider enabling TLS encryption on the LDAP server (ldaps:// or STARTTLS) and adjust the role variables to use `ldaps://` for secure transport. Always protect LDAP credentials in transit, especially over untrusted networks.
* **Privilege and access**: The role runs with elevated privileges (`become: yes`) because it may need to install packages and read LDIF files, and if using LDAPI with SASL EXTERNAL, it must run as root to have permission to bind as the LDAP root user. This means the playbook execution user (often root) has the ability to manipulate the LDAP service. Limit role usage to trusted automation contexts and administrators.
* **Impact on service**: Adding content to LDAP is generally a safe, live operation (it does not require restarting slapd). However, if the role updates certain configuration settings (like adding an overlay or changing the rootDN), those could temporarily disrupt service or require a restart. For example, if this role were extended to configure the audit log overlay (though that’s more the domain of `openldap_logging` role), it might trigger a service restart. Monitor your directory service after applying changes. In our default usage (adding base entries and OUs), there should be no downtime.
* **Firewall and Ports**: This role itself does not open or close network ports. The LDAP server by default listens on TCP port 389 (and 636 for LDAPS if enabled). Ensure your firewall settings allow or restrict access to these ports according to your security policy. Running this role will assume it can communicate with the LDAP service on the host – typically this is on localhost, so firewall is not an issue for local connections. If managing a remote LDAP server, confirm that Ansible can reach the LDAP port or socket as needed.

In summary, treat the data managed by this role (especially credentials) with care. Regularly update passwords and use secure channels. The role will help enforce best practices (like hashing passwords and using local sockets) wherever possible, but ultimate security depends on your environment and usage.

## Role Structure (Mermaid Diagram)

For clarity, the following is a high-level overview of the role’s file structure and key tasks, in a visual format:

```mermaid
flowchart TB
    subgraph "Role: openldap_content"
    direction TB
    A[defaults/main.yml<br/>↳ Default variables] --> B[tasks/main.yml<br/>↳ Entry point for tasks]
    B --> B1[tasks/add_base_dn.yml<br/>↳ Ensure base DN entry exists]
    B --> B2[tasks/add_ous.yml<br/>↳ Create default OUs under base DN]
    B --> B3[tasks/set_rootpw.yml<br/>↳ Set rootDN (admin) password (if needed)]
    B --> B4[tasks/load_extra_ldif.yml<br/>↳ Load additional LDIF files (if any)]
    B --> C[handlers/main.yml<br/>↳ Handlers (e.g. restart slapd if needed)]
    A --> D[meta/main.yml<br/>↳ Role metadata (platforms, dependencies)]
    end
```

*(This diagram illustrates the general flow: the role first loads defaults, then the main task file includes subtasks for adding the base DN, OUs, setting the admin password, etc., and defines any handlers. The exact filenames may differ, but the structure follows standard Ansible role layout.)*

## Conclusion

By using the **openldap_content** role, you can automate the population of your LDAP directory with the necessary initial content, ensuring a repeatable and consistent directory setup. It abstracts the low-level LDIF manipulations or ldapmodify commands into higher-level Ansible tasks and variables. Experienced Ansible users can extend this role by adding tasks for additional directory setup (for example, creating initial user accounts or groups) or by integrating it with vault to securely manage credentials.

For further customization, you might cross-reference related roles in this repository:

* *openldap_server*: to handle server installation and core configuration.
* *openldap_replication*: to set up multi-server replication (provider/consumer).
* *openldap_logging*: to enable and configure LDAP logging (audit log overlay, etc.).
* *openldap_backup*: to schedule or perform backups of the LDAP data.

Each of these roles focuses on a specific aspect of LDAP management. Combined, they allow a comprehensive infrastructure-as-code approach to deploying LDAP. Refer to their respective documentation for details on usage alongside this content role.
