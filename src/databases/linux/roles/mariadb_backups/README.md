# Ansible Role: MariaDB Backups

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

**MariaDB Backups** is an Ansible role that automates the backup of all databases on a MariaDB server. It installs the necessary client utilities and sets up a backup script and service to export the databases to compressed files on the host. The role’s approach is lightweight – using standard tools like **mysqldump** and **gzip** – making it easy to integrate with your existing scheduling or backup workflows. Key features include:

* **Full Database Dump:** Uses `mysqldump` to export *all* MariaDB databases into a single SQL dump file (via the `--all-databases` option). This captures the entire MariaDB instance (schemas and data) in one operation.
* **Compression:** The SQL dump is piped through `gzip` to produce a compressed `.sql.gz` file, significantly reducing storage space for backups.
* **Deploys Backup Script:** The role deploys a self-contained backup script (`mariadb-backup.sh`) to the target host (by default to **`/usr/local/bin`**). This script encapsulates the backup logic (dumping and compressing the databases) and can be run manually or via an automated service.
* **Systemd Integration:** Installs a Systemd service unit (`mariadb-backup.service`) to execute the backup script. The service is enabled and started during role execution, triggering an immediate backup run. This setup can be paired with a Systemd timer or external scheduler if regular automated backups are desired (the role itself does **not** include a timer).
* **Minimal Dependencies:** No heavy external software is required – the role ensures the necessary OS packages (MariaDB client for `mysqldump` and `gzip`) are present. There are no persistent daemons introduced; the backup runs on-demand, making it suitable for cron jobs, Ansible Automation Platform jobs, or other orchestrated scheduling.

```mermaid
flowchart LR
    subgraph MariaDB_Backup_Role["MariaDB Backups Role Execution"]
        step1([Dump all MariaDB databases using mysqldump]) --> step2([Compress the SQL dump (gzip)])
        step2 --> step3([Store backup file in target directory])
        step3 --> opt_transfer{Offsite transfer?}
        step3 --> opt_prune{Retention cleanup?}
        opt_transfer -- "Yes" --> step4([Upload/copy backup to remote storage])
        opt_transfer -- "No" --> step4b([Keep backup locally only])
        opt_prune -- "Yes" --> step5([Purge older backups from local storage])
        opt_prune -- "No" --> step5b([Retain all backups on host])
    end
    classDef optional fill:#ffe,stroke:#666,stroke-width:1;
    opt_transfer, opt_prune class optional;
    style opt_transfer stroke-dasharray: 5 5;
    style opt_prune stroke-dasharray: 5 5;
```

*(Diagram: MariaDB backup process – the role dumps all databases to a compressed file in a local directory. Offsite transfer and old backup pruning are **optional** steps handled outside this role.)*

## Supported Operating Systems/Platforms

This role is tested on and supported with the following Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** The role is tailored for Debian/Ubuntu-based systems (it uses APT for package installation and expects Debian/Ubuntu default paths). Other Linux distributions (Red Hat, CentOS, etc.) are not officially tested and may require adjustments (e.g. using `yum`/`dnf` instead of APT, different package names for MariaDB client, or different service management). Use on non-Debian systems with caution and test accordingly.

## Role Variables

Below is a list of important variables for this role, along with their default values (defined in **`defaults/main.yml`**) and descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                 | Default Value                                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------ | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`backup_script_path`** | `"/usr/local/bin/mariadb-backup.sh"`           | Filesystem path where the backup script will be installed on the target host. In most cases the default (`/usr/local/bin/mariadb-backup.sh`) is appropriate, placing the script in the system’s `$PATH`. You can change this if you need the script in a custom location (the systemd service will use this path).                                                                                                                                           |
| **`service_file_path`**  | `"/etc/systemd/system/mariadb-backup.service"` | Filesystem path for the Systemd service unit file. The default is `/etc/systemd/system/mariadb-backup.service`, which is where custom service definitions are typically placed. You usually wouldn’t need to change this unless you have a non-standard init system or want the unit file in a different location.                                                                                                                                           |
| **`mariadb_username`**   | `"backup_user"`                                | MariaDB username that the backup script will use to connect to the database server. This user should have permission to read *all* databases (e.g., global SELECT privileges, and preferably lock/flush privileges for consistent dumps). **Ensure this database user is created beforehand** with the necessary privileges. The default `"backup_user"` is a placeholder; in production you will likely set this to an existing backup or replication user. |
| **`mariadb_password`**   | `"backup_password"`                            | Password for the above **mariadb_username**. **This should be set to a secure value** in your inventory or vault – the default `"backup_password"` is **not** a real password and only a placeholder. The password will be stored in the backup script (for use by `mysqldump`), so treat it carefully (see **Security Implications** below).                                                                                                               |
| **`backup_location`**    | `"/path/to/backup"`                            | Target directory where backup files will be stored. **Important:** This directory must exist on the target host (the role does *not* create it automatically) and should have appropriate permissions. For example, you might set this to a path like `/var/backups/mariadb` or a mounted backup volume. Ensure the directory is writable by the user running the backup (root by default) and is secured from unauthorized access.                          |

</details>
<!-- markdownlint-enable MD033 -->

**Notes:** Generally, you will override `mariadb_username`, `mariadb_password`, and `backup_location` to match your environment. For instance, you might use an Ansible Vault to supply `mariadb_password`, and choose a backup directory that fits your system’s backup policy (e.g. a secure, dedicated backup folder). The default values above are provided as examples and **must** be reviewed before running the role in production. The `backup_script_path` and `service_file_path` usually do not need changing unless you have a custom filesystem layout.

## Tags

This role does **not define any Ansible tags** in its tasks. All tasks will run whenever the role is invoked. (You can still apply tags externally when including the role in a play if you need to control when this role runs, but within the role itself, no tasks are tagged.)

## Dependencies

* **Ansible Version:** This role has been used with Ansible **2.13+**. It relies only on built-in modules like `apt`, `template`, `copy`, and `systemd`, so it doesn’t require very new Ansible features, but using a relatively recent Ansible release (2.12 or later) is recommended to ensure full compatibility.
* **Collections:** No special Ansible collections are required. All tasks use modules from Ansible’s built-in arsenal (such as **`apt`** for package installation and **`ansible.builtin.systemd`** for service management). As long as you have the standard Ansible modules, you’re covered.
* **External Packages:** The role will install necessary OS packages on the target node:

  * **MariaDB client tools:** The Debian/Ubuntu package **`mariadb-client`** is installed to provide the `mysqldump` utility. (If you are using a different distribution, ensure an equivalent package is present that provides `mysqldump`.)
  * **Compression tool:** The **`gzip`** package is installed (if not already present) for compressing the dumps.
    These installations require internet access or an available package repository on the target.
* **Target Environment:** A running **MariaDB server** (or Galera cluster) is assumed to exist. This role **does not install MariaDB server software or create databases** – it only handles backups. You should provision your database server separately (e.g., using another role or manual setup). For example, in this repository a MariaDB Galera cluster is set up using the **mrlesmithjr.mariadb_galera_cluster** role prior to running `mariadb_backups`.
* **Database User:** As noted above, a MariaDB user with adequate privileges to perform the dump must exist. Creating that user (and granting it proper permissions) is outside the scope of this role. Typically, you would create a user (e.g. `backup_user`) on the database server with at least SELECT on all databases (or the *BackupAdmin* privilege in MariaDB 10.3+), and use those credentials for the backup.
* **OS Services:** Systemd is expected on the target host (the role drops a unit file into `/etc/systemd/system` and uses the `systemd` module). This role won’t work on systems without Systemd as-is (you’d need to adapt it for other init systems if necessary).
* **Prior Roles/Tasks:** No direct role dependencies are specified in meta, but it’s logical to run this role **after** the database is installed and configured. For instance, in a playbook you might include your MariaDB installation role (or tasks) first, then include `mariadb_backups` to set up backups. In a clustered environment, you may target one node or run on all nodes in sequence (see **Known Issues and Gotchas** about clustering considerations).

## Example Playbook

Below is an example of how to use the `mariadb_backups` role in an Ansible playbook. In this example, we assume a group of database hosts (`db_servers`) which are running MariaDB. We will run the role on those hosts to install the backup components and trigger an immediate backup. We also override some defaults to provide the correct credentials and backup path:

```yaml
- hosts: db_servers
  become: yes  # Ensure we have root privileges to install packages and configure services
  vars:
    mariadb_username: "backup_user"
    mariadb_password: "{{ vault_mariadb_backup_password }}"  # secure password from Ansible Vault
    backup_location: "/var/backups/mariadb"  # ensure this directory exists or create it beforehand
  roles:
    - mariadb_backups
```

In the above play, we target the `db_servers` group (adjust to your inventory). We provide the required variables such as the backup user credentials and desired backup directory. When this role runs, it will:

1. **Install Tools:** Use apt to install the MariaDB client and gzip packages on the host (if they are not already installed).
2. **Deploy Script:** Place the `mariadb-backup.sh` script into `/usr/local/bin/` (or your configured `backup_script_path`) with proper permissions. This script contains the mysqldump command with the provided credentials and writes out a compressed dump file.
3. **Install Service:** Copy a Systemd service unit file to `/etc/systemd/system/mariadb-backup.service` (or your configured `service_file_path`). This service is configured to run the backup script.
4. **Run Backup:** Enable and start the `mariadb-backup` service immediately. Starting the service triggers the backup script to execute once (dumping all databases and writing the `.sql.gz` file to the backup directory). The service will then exit after completing the backup.
5. **Persist on Boot:** Because the service is enabled, it will also run on boot by default. This means if the server reboots, the backup script will execute once after startup (you can disable this if not desired, or use a timer for a specific schedule instead).

After running the playbook, you should find a new backup file in `/var/backups/mariadb` on each target host. The file name will be a timestamp ending in `.sql.gz` (for example, `20250531101050.sql.gz` if the backup ran on May 31, 2025 at 10:10:50). Each run of the role (or start of the service) produces a new file. Typically, you would **not** hard-code sensitive values like the database password in the playbook; instead we used an encrypted variable `vault_mariadb_backup_password` in this example. In practice, these variables might also be set via group or host variables in your inventory (so that you can simply include the role without having to specify them every time in the playbook).

**Usage in Practice:** You can integrate this role into a larger workflow. For instance, you might schedule it to run nightly via Ansible AWX/Controller or a cron job (invoking the playbook). In a clustered scenario, you might run the backup on one node at a time – e.g., using `serial: 1` in your play to avoid all nodes dumping simultaneously. (This repository’s playbooks, for example, include the Galera cluster setup role followed by `mariadb_backups` on the database hosts, potentially with a serial execution to reduce load.)

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to ensure it works correctly in an isolated environment. Follow these steps:

1. **Install Molecule and Docker:** On your development machine, install Molecule and its Docker support (for example, via pip: `pip install molecule[docker]`). Also ensure you have Docker installed and running.
2. **Prepare a Test Scenario:** If a Molecule scenario is provided with this role (e.g. under `roles/mariadb_backups/molecule/`), you can use that. If not, you can initialize a new scenario for this role by running:

   ```bash
   molecule init scenario -r mariadb_backups -d docker
   ```

   This will create a `molecule/` directory with a default scenario (by default named “default”) for the `mariadb_backups` role.
3. **Configure the Scenario:** Edit the generated Molecule configuration (`molecule/default/molecule.yml`) and playbook (`molecule/default/converge.yml`) as needed:

   * Use a Docker image that matches one of the supported OS (e.g. Docker image for Debian 11 or Ubuntu 22.04) for the instances.
   * In the converge playbook, you will need to simulate a MariaDB environment. This can be as simple as installing MariaDB server on the container and ensuring it’s running. You can add tasks in the playbook to install `mariadb-server` (and perhaps `expect` or some method to set a root password in the container), or use an existing container image that has MariaDB running.
   * Also ensure a **backup user** exists in the test database. For example, you might add an Ansible task to create a MySQL user and grant it privileges, or use the root user credentials for a quick test. Update the `mariadb_username`/`mariadb_password` variables in the scenario’s play or inventory to match your test setup.
   * Set a suitable `backup_location` that exists in the container. For instance, you could use `/tmp/mariadb_backups` and add a task to create this directory (with proper ownership/perms) before the role runs.
4. **Run the Molecule test:** Execute `molecule converge` to apply the role in the Docker container. Molecule will launch the container, run the converge playbook which includes the `mariadb_backups` role, and report any task failures. Watch the output for errors, especially around the database dump task. If everything goes well, the role should complete with no errors.
5. **Verify the Results:** After convergence, verify that the backup was created inside the container:

   ```bash
   docker exec -it <container_id> ls -l /tmp/mariadb_backups
   ```

   (Replace `/tmp/mariadb_backups` with whatever path you set as `backup_location`.) You should see at least one `.sql.gz` file with a timestamp. You can also exec into the container (`docker exec -it <id> /bin/bash`) and inspect the file, e.g., running `gunzip -c 20250531101050.sql.gz | head -20` to see the SQL dump header. If the role includes any embedded tests (such as Ansible asserts or a `molecule verify` step with Testinfra), run `molecule verify` to execute those. Otherwise, manual verification of the backup file’s existence and contents is sufficient.
6. **Cleanup:** When done, run `molecule destroy` to tear down the test container. This ensures no leftover containers consume resources.

By following these steps, you can confidently iterate on the role in a safe environment. Adjust the scenario as needed to mimic your production setup (for example, you could test on multiple containers to simulate running on a cluster node vs. another host).

## Known Issues and Gotchas

* **Backup Directory Must Exist:** The role does **not** create the `backup_location` directory for you. If the directory specified by `backup_location` does not exist on the target host, the backup script will fail (the `mysqldump` will be unable to open the output file path). To avoid this, pre-create the directory (e.g., via an Ansible task or through provisioning) with appropriate ownership and permissions. For security, it’s wise to restrict this directory to the root user (or whichever user will run the backup) so that backup files are not accessible to others.
* **Database User and Permissions:** Ensure the MySQL/MariaDB user you configure for backups (`mariadb_username`) exists and has adequate privileges. The role will not create or grant permissions to this user. At minimum, the user should have SELECT on all databases and the ability to lock tables or run FLUSH commands if needed for consistency. If using a recent MariaDB version, consider giving the user the `BACKUP_ADMIN` privilege which is designed for backup operations. If the user lacks privileges, `mysqldump` may fail to read certain databases/tables without obvious errors.
* **No Automatic Scheduling:** The role sets up the backup as a one-time service execution. There is **no built-in scheduling** (no cron job or systemd timer included). This is by design, to give you flexibility. You must arrange a schedule to run backups regularly. Options include: scheduling the Ansible playbook itself (via AWX/Automation Controller or cron on your control machine), creating a Systemd Timer unit to trigger the provided service on a schedule, or using cron on the target host to call the backup script directly. Pick a method that fits your operations. If you do create a `mariadb-backup.timer` (systemd) or a cron entry, ensure it runs as root (or the appropriate user) so that it can invoke the backup properly.
* **Service Behavior:** The installed `mariadb-backup.service` unit is a simple one-shot service that runs the backup script and then exits. It is enabled to run at boot (which may or may not be desirable in your scenario). Be aware that on a reboot, it will execute and then likely show as “inactive (dead)” after successful completion. This is normal for one-shot services. If you prefer not to run on boot automatically, you can disable the service after the initial run and manage invocation via other means.
* **Clustering Considerations:** In a multi-node MariaDB Galera cluster, avoid running backups on all nodes at the exact same time, as this can put significant load on the cluster and possibly impact performance. A common approach is to run the backup on one designated node or stagger the backups. You can use Ansible’s `serial: 1` when running this role across a group of DB servers, which will run the role on one node at a time. Alternatively, pick a specific host (e.g., the primary or a dedicated replica) to perform backups. Also note that `--all-databases` dump on each node will produce identical data for a Galera cluster – so running it on one node is usually sufficient, unless you want redundancy in backup files.
* **Large Databases and Performance:** For very large databases, a full `mysqldump` can be time-consuming and resource-intensive. During the dump, there may be increased load on the database and potential locking (especially if using MyISAM tables). By default, the script does **not** use options like `--single-transaction` or `--quick`, which means it will lock tables as it dumps them. If your databases are mostly InnoDB and you require an online, less-locking backup, you might consider enabling the `--single-transaction` option. This can be done by editing the template script or overriding it with your own. Keep in mind that `--single-transaction` works only for InnoDB tables and you must not perform schema changes during the dump. Another alternative for large datasets is to use physical backup tools (like MariaDB’s `mariabackup` or Percona XtraBackup), which are beyond the scope of this role but might be more suitable for high-volume production environments.
* **Backup Retention:** This role does not automatically prune or rotate old backups. If you run it regularly, backup files will accumulate in the `backup_location`. Plan for a retention strategy – for example, you might have another job to remove backups older than X days, or incorporate that logic into a wrapper playbook. Be mindful of disk space on the backup target; large or frequent dumps can fill up storage over time.
* **Restoration Process:** While not exactly an “issue,” it’s worth noting that restoration from these backups is a manual process. To restore, you would transfer the desired `.sql.gz` file to a MySQL/MariaDB instance and import it (gunzip the file and use the MySQL client to execute the SQL). Always practice your restore procedure to ensure the backups are valid. The role doesn’t provide restore automation, so have documentation or scripts on hand for recovery.
* **Security of Credentials:** The database password is inserted into the backup script in plain text. The script file is chmod `0700` (accessible only by root) which is good, but whenever the backup runs, the password might be visible in the process list (e.g., via `ps`) since `mysqldump` is invoked with `-p<password>`. On a secure server this may be an acceptable risk, but it’s something to consider. To mitigate this, you could modify the approach to read the password from a secured file or environment variable rather than command-line. For example, using a MySQL option file (`~/.my.cnf` for root with a dedicated section for the backup user’s credentials) would allow running `mysqldump` without specifying the password in the command. This is an advanced customization not currently in the role, but keep it in mind if process security is a concern in your environment.

## Security Implications

Running database backups touches on security in multiple ways. Here are the main considerations and recommendations when using this role:

* **Database Credentials:** The role requires a database username and password with broad read access. **Protect these secrets.** Use Ansible Vault or another secrets management solution to store the `mariadb_password`. Do not expose it in plain text in playbooks or version control. Remember that the password is stored in the backup script on the server. By default the script is only readable/executable by root – do not loosen these permissions. If other users on the system need to run the backup, consider adding them to a privileged group rather than making the script world-readable.
* **Backup File Sensitivity:** The dumps produced contain all data from your MariaDB databases, which often includes sensitive information. Treat the backup files as sensitive assets. The backup directory should have restricted permissions (e.g., owned by root and not accessible by regular users). If you copy these files off the host, ensure the transfer is secure (use scp/rsync over SSH, or a secure backup service). At rest, consider encrypting backups or storing them in an encrypted filesystem if they contain highly sensitive data.
* **Principle of Least Privilege:** The MariaDB **backup user** should be limited to what’s necessary. It’s not recommended to use the root MySQL user for backups. Instead, create a user that has just the needed privileges (e.g., global SELECT, LOCK TABLES, SHOW VIEW, and possibly RELOAD for flush or the BACKUPADMIN role) but not permissions to modify or delete data. This way, if the backup credentials are compromised, the impact on the database is limited (read-only access).
* **Running as Root:** The role and its systemd service run the backup as the root user (by virtue of how Ansible and systemd are invoked, since no alternate user is specified in the service). Running the `mysqldump` as root is typically fine (root on the OS doesn’t equate to DB admin unless the DB allows socket root login), and it ensures the process can write to any directory. Just be aware that with root execution comes the responsibility to secure the script and output as mentioned. If you need to run as a different user, you’d have to adjust file paths, ownership, and possibly the systemd unit (`User=` setting) accordingly, and ensure that user can perform the dump.
* **Exposure in Transit:** If you are copying backup files to a central location, avoid insecure channels. Do not, for example, email the SQL dumps or copy them over plain FTP. Use SSH/SFTP, a secure API, or an encrypted transfer method. Similarly, if using network storage (NFS, SMB) as the backup location, consider the security of that medium (e.g., restrict access to the share, use encryption if available).
* **Integrity and Verification:** A security aspect often overlooked is verifying backups. A corrupted or partial backup is a risk to data integrity. While not handled by this role, you should implement checks (like periodically testing a restore, or at least running `mysqlcheck` on the dumped SQL) to ensure the backup files are valid. Storing checksums or using tools that verify the backup can be useful.
* **System Resource Usage:** A backup, especially a full dump, can be resource-intensive (CPU, disk I/O, memory). While this is more of a performance concern, note that an overloaded system could impact other services and potentially become a security issue if it causes outages. Mitigate this by scheduling backups during off-peak hours and monitoring system performance. If necessary, nice/ionice the backup process (requires customizing the script or service unit).
* **Cleaning Up Credentials:** If at some point you remove this role or no longer need the backup, remember to also remove or disable the backup user in the database if it’s no longer needed, and remove the script/service from the host to eliminate any leftover credentials on disk.

In summary, **safeguard your backup credentials and files**. The role provides the mechanism to create backups, but it’s up to you to enforce policies around who can access the backups, how they are stored, and to ensure the backup process does not inadvertently open any security holes.

## Cross-Referencing

This **mariadb_backups** role is part of a suite of roles intended to manage infrastructure in this repository. Here are some related roles and references that might be useful:

* **MariaDB Galera Cluster Setup:** Our playbooks utilize the external role **mrlesmithjr.mariadb_galera_cluster** to install and configure a multi-node MariaDB Galera cluster (a highly-available MariaDB setup). If you are looking to set up the database servers themselves, consider using that role or a similar one (e.g., geerlingguy.mysql for single-instance MariaDB). The `mariadb_backups` role is typically run after the database is up and running.
* **MariaDB Galera Load Balancer:** If you are deploying a Galera cluster, you might also be interested in the **`mariadb_galera_loadbalancer_install`** role (in this repository) which helps set up a load balancer or proxy (such as HAProxy or ProxySQL) in front of the Galera cluster. This can distribute database traffic among the nodes and handle failovers. While not directly related to backups, it’s part of the MariaDB ecosystem in our configuration.
* **PostgreSQL Backup Role:** For environments that use PostgreSQL, see the **`postgres_backup`** role in this repository. It serves a similar purpose for PostgreSQL databases (dumping databases to files). The implementation is analogous (it uses `pg_dump` and optional compression). If your stack includes multiple database types, having both `mariadb_backups` and `postgres_backup` roles ensures consistent backup strategies across them.
* **Application-Specific Backups:** We also have roles for backing up specific applications. For example, **`backup_netbox`** is a role that backs up the NetBox application (including its PostgreSQL database and media files). Similarly, **`jenkins_backup`** handles backups of a Jenkins server (its configuration and data). While these are outside the scope of MariaDB, they are part of the broader backup practices in this repository. Studying them can provide ideas on how to extend backup roles (e.g., handling not just databases but also associated files, or implementing retention policies).
* **Base/System Roles:** Don’t forget general roles like **`base`** (which prepares a server with common baseline configuration) if you are setting up a new host for backups. For instance, ensuring that basic utilities, correct time synchronization, and security hardening from the base role are applied can make your backup process more reliable.

Each of these roles can be found in this repository (see their respective README documentation for details). They complement the `mariadb_backups` role to round out our infrastructure management. Depending on your scenario, you might use several of them together. For example, a full deployment for a web application might involve a database role (to set up MariaDB), a backup role (like this one), and perhaps a role to manage web servers, etc. The modular design allows you to pick and choose what’s needed.

---

By following this documentation and the role’s guidelines, you should be able to confidently incorporate **MariaDB Backups** into your playbooks, ensuring that your MariaDB databases are safely backed up. Always test your backups and restoration procedures regularly, and adapt the configuration to fit your operational requirements. Happy backing up!
