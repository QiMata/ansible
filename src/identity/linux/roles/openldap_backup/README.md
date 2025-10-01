# Ansible Role: Openldap Backup

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

The **Openldap Backup** role automates nightly backups of an OpenLDAP server’s data and configuration. It deploys a backup script and a cron job to export the LDAP directory to LDIF files and archive them, ensuring you have point-in-time snapshots of your directory service. Specifically, this role backs up both the **OpenLDAP configuration database** (`cn=config`) and the main **directory database** (your LDAP directory base DN) using the `slapcat` utility, then packages them into a compressed tarball. By default, backups are retained for 30 days on the host. This approach provides an easy recovery path in case of data loss or corruption – you can restore the LDIF to recover the directory state.

```mermaid
flowchart TD
    subgraph "Nightly OpenLDAP Backup Process"
    C[Cron (2:00 AM)] --> S[ldap_backup.sh script (root)]
    S --> E1[Export cn=config via slapcat]
    S --> E2[Export directory ({{ ldap_base_dn }}) via slapcat]
    S --> A[Archive exports into tar.gz]
    S --> D[Delete exports (LDIF files)]
    S --> R[Remove archives older than 30 days]
    end
```

In practical use, you will include this role on OpenLDAP server hosts **after** the OpenLDAP service is installed and configured. The backup script runs non-intrusively (it does not stop the `slapd` service) and uses read-only operations to dump the database. Restoration is not automated by this role, but the resulting LDIF files and archives can be used to manually restore the LDAP directory if needed. This role helps maintain regular offline backups of your LDAP data for disaster recovery or migration purposes.

## Supported Operating Systems/Platforms

This role is tested on and intended for **Debian-based Linux** systems (64-bit), specifically modern Debian and Ubuntu releases:

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal) and 22.04 LTS (Jammy)

> **Note:** The OpenLDAP roles in this repository use Debian/Ubuntu conventions (e.g. apt package manager). For example, the OpenLDAP server role uses `debconf` preseeding and `apt` to install `slapd`. As such, these roles will **not work on RHEL/CentOS or other non-APT-based systems** without modifications. Ensure your target hosts are running a supported Debian/Ubuntu version. The backup script itself relies on the `slapcat` command, which is provided by the OpenLDAP utilities package on Debian/Ubuntu.

## Role Variables

Below is a list of variables relevant to this role, along with default values (defined in **`defaults/main.yml`**) and descriptions:

<!-- markdownlint-disable MD033 -->

<details><summary>Click to see default role variables.</summary>

| Variable           | Default Value         | Description |
| ------------------ | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`ldap_base_dn`** | "dc=example,dc=com" | **Base Distinguished Name** for the main LDAP directory. This is the suffix of your directory (e.g., `dc=company,dc=com`) that will be backed up. The backup script uses this DN to export the directory contents. **You must set this to match your environment** (it should correspond to your LDAP domain name or top-level DN). |

</details>
<!-- markdownlint-enable MD033 -->

*Note:* The above default is a placeholder. In practice, this role expects `ldap_base_dn` to be defined (for example, via the OpenLDAP server role or your inventory) to match your actual directory suffix. If it is not provided, the backup script will not know which database to export.

This role has a fixed backup schedule and retention policy (see Tasks section) – there are no additional tunable variables for schedule timing or retention in the defaults. The backup behavior (cron timing, backup directory, retention days) is set in the script itself (see **Known Issues and Gotchas** below for details on adjusting these if necessary).

## Tags

This role does not define any custom Ansible tags. All tasks in **openldap_backup** run by default whenever the role is included.

* **Required tags:** None (the tasks execute unconditionally when the role runs).
* **Optional tags:** None specific to this role. You can apply your own tags at the play or role level if you need to include or skip the entire backup role in larger playbooks. By default, the nightly backup setup is always applied to ensure backups are configured.

## Dependencies

**OpenLDAP installation:** This role assumes that an OpenLDAP server (`slapd`) is already installed and configured on the target host. It does *not* install OpenLDAP itself. Typically, you would run the **openldap_server** role (and related roles like **openldap_content**) before this role to set up the LDAP service. The presence of the `slapcat` utility is required for backups – on Debian/Ubuntu this is provided by the `ldap-utils` package (which is usually installed alongside `slapd`). If your environment does not have `ldap-utils`, ensure it is installed so that `slapcat` is available.

**Ansible collections:** No special Ansible collections are required by this role’s tasks. It uses only built-in modules (`ansible.builtin.copy` and `ansible.builtin.cron`). (The broader OpenLDAP setup may use the **community.general** collection for certain LDAP modules, but **openldap_backup** itself does not.)

**External dependencies:** None. The backup script uses standard system tools (`bash`, `slapcat`, `tar`, `find`) that are expected to be present on a typical Linux system with OpenLDAP. There are no external services or internet connectivity required for the backup process.

## Example Playbook

Here is an example of how to use the **openldap_backup** role in a playbook. In this example, we assume the OpenLDAP server has already been configured on the hosts (using other roles or tasks), and we simply include the backup role to schedule nightly backups:

```yaml
- hosts: ldap_servers
  become: yes
  vars:
    ldap_base_dn: "dc=example,dc=com"  # ensure this is set to your directory's base DN
  roles:
    - openldap_server       # (assumes this role sets up slapd and base DN)
    - openldap_content      # (loads initial LDAP entries, optional)
    - openldap_backup       # schedule backups for the LDAP data
```

In the above play, the **openldap_backup** role is included after the LDAP server is up and configured. The `ldap_base_dn` variable is provided (either earlier by the openldap_server role or explicitly as shown) so that the backup script knows which database to dump. By applying this role, a script `/usr/local/sbin/ldap_backup.sh` will be installed and a cron job scheduled to run it nightly. No further manual intervention is needed to produce daily backup files.

## Testing Instructions

This role comes with a **Molecule** test scenario to verify its functionality in a containerized environment. Molecule (with the Docker driver) is used alongside Testinfra to ensure the backup setup works as expected. To run the tests for the **openldap_backup** role, follow these steps:

1. **Install Molecule and dependencies:** Ensure you have Molecule and Docker installed on your control machine. Install Molecule and its Docker plugin with pip (e.g. `pip install molecule[docker]`), and make sure you have `pytest` and `testinfra` as well (Molecule will use these for assertions). Docker must be running to provide containers for testing.

2. **Prepare role dependencies (if any):** The test scenario for openldap_backup might include the OpenLDAP server setup to provide a realistic environment. Make sure the required roles (such as `openldap_server`) are present or installable. If using a `requirements.yml`, include any dependent roles and run `ansible-galaxy install -r requirements.yml` before testing. (For example, to test this role, the test playbook may call the openldap_server role to install slapd inside the container.)

3. **Run the Molecule test:** From the repository root (where the `molecule/` directory is located), execute the following command:

   ```bash
   molecule test -s openldap_backup
   ```

   This will launch the Molecule scenario named "openldap_backup". Molecule will perform the following actions:

   * Spin up a fresh Docker container (based on a supported OS like Debian) for the test environment.
   * Run a converge step: apply a test playbook that includes the **openldap_backup** role (and likely the OpenLDAP server role to set up `slapd` and provide an `ldap_base_dn` for the test).
   * Execute verification steps (via Testinfra) to check that the role’s tasks had the intended effect. For example, it will verify that the `/usr/local/sbin/ldap_backup.sh` script exists and is executable, that a cron job is installed for root at 2:00 AM, and possibly that running the script produces an archive in `/var/backups/ldap`.
   * Destroy the test container after testing, cleaning up the environment.

4. **Review the test results:** Check the output of the Molecule run. A successful test run should end with an "OK" state and no failed assertions. If a failure occurs (e.g., the script was not found, or backup files were not created as expected), you can debug by rerunning specific stages: use `molecule converge -s openldap_backup` to just apply the role in the container (leaving it running for inspection), and/or `molecule verify -s openldap_backup` to rerun tests. You can also use `molecule login -s openldap_backup` to get an interactive shell inside the test container for manual troubleshooting.

Running these tests ensures that changes to the role do not break its functionality. Contributors should run Molecule tests before submitting changes to verify that the backup script and cron setup work on a clean system.

## Known Issues and Gotchas

* **Base DN must be correct:** The backup will fail if the `ldap_base_dn` is not set to the correct value for your LDAP directory. The slapcat command will exit with an error if given a base DN that doesn’t exist on the LDAP server. Make sure you define `ldap_base_dn` appropriately (matching your OpenLDAP suffix). This is often provided by the **openldap_server** or **openldap_content** role; otherwise you must set it in your inventory or playbook. If you see no `data-*.ldif` being generated, double-check this variable.

* **Backup schedule and retention are fixed (by default):** Currently, the cron job is hard-coded to run daily at **02:00 (2:00 AM)** system time, and the script purges archives older than **30 days**. These values are not exposed as role variables. If you need to adjust the schedule or retention:

  * To change the time or frequency of backups, you would have to modify the task that creates the cron job (or override it by editing the cron entry after playbook runs). For example, adjust `hour:` or `minute:` in the role’s tasks or use an Ansible task in your playbook to alter the cron schedule.
  * To change retention period (30 days by default), you would need to modify the script content. The `find ... -mtime +30 -delete` command is what enforces the 30-day retention. You could maintain a custom version of the script via another task or fork the role to make retention configurable. Similarly, the backup directory (`/var/backups/ldap`) is currently fixed in the script.

  These limitations are by design for simplicity. In most cases, a 2 AM daily backup with 30-day retention is reasonable. But be aware that changing these requires code changes. Future enhancements to the role might externalize these parameters for easier customization.

* **Disk space and storage considerations:** The backups are stored locally under `/var/backups/ldap` by default. Over time, these archives can consume significant disk space (especially if your directory is large). Monitor the available space on the volume holding `/var/backups`. If space is a concern, consider offloading older archives to external storage before the 30-day deletion, or reduce retention (which, as noted, requires editing the script). Also ensure that the host has enough space for at least 30 days of LDAP data growth.

* **Backup contains sensitive data:** The LDIF files and resulting tar archives include the entire LDAP database contents (including user entries, group entries, and any hashed passwords or sensitive attributes stored in LDAP). Handle these backup files with care. By default, the backup tarballs are owned by root and stored in a directory only root can write, but the directory creation may default to world-readable permissions (depending on system umask). It’s advisable to restrict access to the backup files:

  * Verify that `/var/backups/ldap` is not world-accessible. Adjust its permissions to `700` (owner=root) if necessary, so that only root can list or read files in it.
  * If you require additional security, consider moving the backups to an encrypted storage or use additional tools to encrypt the tarballs. This role does not do encryption – it’s up to the administrator to secure the backup archives as needed.

* **No automatic offsite backup:** This role keeps backups on the local machine. If the entire host fails, you could lose both the server and its backups. For true disaster recovery, you should regularly transfer the backup archives to a remote location or storage service. You can complement this role by adding tasks to copy the `ldap-backup-*.tar.gz` files to an external backup server or cloud storage (e.g., via rsync, S3 upload, etc.) as part of your backup strategy. Similarly, implement monitoring or alerts if a backup fails (e.g., parse cron's output emails or log files) to ensure the backups are running as expected.

* **Concurrent modifications during backup:** The `slapcat` utility is used while the LDAP server is running. In general, `slapcat` on a live `slapd` database is safe and produces a consistent snapshot because it reads the database files directly. However, if your directory is under heavy write load at 2 AM, there’s a slight chance that the backup could capture a state in between transactions (OpenLDAP’s HDB/MDB handles this gracefully with transactions, so it’s usually not a problem). Just be aware that the backup is essentially a point-in-time snapshot; any writes that complete after the `slapcat` start won’t be in the backup for that night. This is usually acceptable, but in highly dynamic directories you might want to schedule backups during a low-activity period.

## Security Implications

Running this role affects system security in the following ways:

* **Creates root-owned script and cron job:** The role deploys a script at `/usr/local/sbin/ldap_backup.sh` with permissions **0700** (only root can read/execute) and registers a cron job to run as **root**. This means the backup process runs with full privileges. The script itself is simple and read-only in nature (it dumps data and writes files), but as with any cron job as root, ensure you trust the content of the script (this role provides a vetted default script). Avoid modifying the script in ways that could be exploited, and limit access to the script file. The cron entry is named "OpenLDAP nightly backup" for clarity.

* **Storage of sensitive directory data:** As noted, the backups contain all LDAP data including potentially sensitive information (user credentials, personal data, etc., albeit passwords are typically hashed). The security of this data now depends on the filesystem protections of the backup location. By default, the archive files (e.g., `ldap-backup-<DATE>.tar.gz`) will likely be world-readable (mode 0644) unless your system umask is stricter. This is a security risk because non-privileged users on the system could read the backup archive. It is strongly recommended to tighten permissions:

  * Set the backup directory (`/var/backups/ldap`) to `chmod 700` (only accessible by root).
  * Consider setting a stricter file creation mask or manually adjusting file permissions after creation to ensure backups are not world-readable.
  * Only users with root (or sudo) privileges should be able to access the backup contents. Audit who has access to the server and those privileges.

* **No network exposure:** This role does not open any network ports or alter firewall settings. The backup process is entirely local. Thus, it does not directly increase the attack surface in terms of network services. (Contrast this with, say, enabling an LDAP replication listener or a new service – this role does none of that.)

* **Potential impact on LDAP performance:** The backup script will momentarily consume system resources: CPU and disk I/O for `slapcat` and compression. If your LDAP server is large, the compression step could be CPU-intensive and the disk I/O could impact database performance. There is a minor security consideration here: if the server is resource-constrained, backup processes might slow down authentication or other LDAP operations, which could be seen as a availability concern. In extreme cases, if backup timing overlaps with peak usage and slows down LDAP responses, it might be considered a form of self-induced DoS. Mitigate this by scheduling backups during off-peak hours and ensuring the host has adequate resources.

* **Restore procedure caution:** While not directly part of this role, if you use these backups to restore data, you would typically stop the LDAP service and re-import the LDIF. Ensure that during such a procedure, proper precautions are taken (e.g., correct file ownerships, apparmor/SELinux contexts if applicable, disabling external access until restore is complete, etc.). The security implication is to avoid partial restores or inconsistent states that could confuse clients or leave the service in an insecure state. Always follow official OpenLDAP restore guidelines when using the LDIF from these backups.

In summary, the **openldap_backup** role slightly increases local data security risk (by creating sensitive archives) but significantly improves operational security by providing a recovery mechanism. Treat the backup files as you would any secret data: protect them with filesystem permissions or encryption and include them in your security audits. The automated backups help ensure that in the event of a failure or breach, you can recover directory data to a known state, which is a critical part of overall security posture.

## Cross-Referencing

The OpenLDAP backup role is one component in a suite of roles for LDAP management. You may want to use or be aware of the following related roles in this repository:

* **[openldap_server](../openldap_server/README.md)** – *OpenLDAP Server Installation & Config*: Installs and configures the core OpenLDAP server (`slapd`). This sets up the LDAP service, initial domain configuration (base DN), and admin user. It should be applied before running the backup role, since it provides the running LDAP instance and foundational settings that the backup will use.

* **[openldap_content](../openldap_content/README.md)** – *Initial LDAP Content Loader*: Populates the LDAP directory with initial entries (e.g., base organizational units, default users/groups, or application-specific LDAP data). This role can be used to bootstrap the directory content after the server is set up. Running backups after this role ensures that any seeded content is captured in the backup archives.

* **[openldap_replication](../openldap_replication/README.md)** – *LDAP Replication Setup*: Configures multi-master or master-slave replication between OpenLDAP servers (if you have more than one LDAP node for high availability). Backups on each server are still recommended even in a replicated scenario (each node can backup its own data, which should be equivalent). This backup role does not configure or alter replication – it simply dumps the local DB, which in a replication setup would contain the same data as its peers.

* **[openldap_logging](../openldap_logging/README.md)** – *Enhanced LDAP Logging*: This optional role sets up log forwarding or specialized logging for OpenLDAP. For instance, it might configure **Filebeat** or other log shippers to send LDAP logs to a central log system (ELK stack, etc.). Using openldap_logging ensures that not only is data backed up, but LDAP operation logs are preserved externally. While not directly related to backups, having centralized logs can be invaluable when investigating issues that might require a restore (you can correlate restore points with events in the logs).

Each of these roles complements **openldap_backup** by addressing different aspects of an OpenLDAP deployment (installation, data seeding, replication, monitoring). In a typical playbook (like **ldap-servers.yml** in this repo), you might include *openldap_server*, *openldap_content*, *openldap_replication*, *openldap_logging*, and *openldap_backup* together to build a complete LDAP server setup. Refer to each role’s documentation for details on usage and configuration. By combining them, you achieve a robust and maintainable LDAP infrastructure with automated setup, consistent backups, and integrated logging.
