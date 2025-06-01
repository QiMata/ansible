# Ansible Role: Backup NetBox

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

**Backup NetBox** is an Ansible role that automates backing up of a NetBox application’s data. It dumps the NetBox PostgreSQL database and archives the NetBox media files (attachments), storing them on the target host for safekeeping. The role ensures a designated backup directory exists with secure permissions (by default `/var/backups/netbox`, owned by root). You can run this role on a regular schedule (e.g. via Ansible AWX/Controller, cron, or Jenkins) to maintain up-to-date backups of NetBox. Key features include:

* **Database Dump:** Uses PostgreSQL tools (via Ansible modules) to export the NetBox PostgreSQL database to a timestamped SQL file. This captures all NetBox data and schema.
* **Media Archive:** Compresses the NetBox media files directory (where uploaded images/attachments are stored) into a timestamped tarball, ensuring that file uploads are backed up alongside the database.
* **Backup Directory Management:** Creates and manages the backup folder (default `/var/backups/netbox`) on the target system with appropriate ownership and permissions (root:root, `0750`). This protects the backups from unauthorized access on the host.
* **Lightweight Integration:** The role focuses on backup tasks and does not install heavy additional software. It can be combined with your existing scheduling/orchestration tools for regular execution. (No persistent services or daemons are set up by this role by default.)

The backup process is designed to minimize impact on the running NetBox service. In most cases, NetBox can remain online during the backup; the role runs quickly (database dumps are typically consistent if taken during off-peak usage, though an exclusive lock is not enforced). For maximum safety in critical environments, you may choose to briefly stop NetBox while this role runs – see **Known Issues and Gotchas** for details on consistency considerations.

```mermaid
flowchart LR
    subgraph Backup_NetBox_Role ["Backup NetBox Role Execution"]
        step1([Dump NetBox PostgreSQL DB]) --> step2([Archive NetBox media files])
        step2 --> step3([Store backup files in /var/backups/netbox])
        step3 --> opt_transfer{Offsite transfer?}
        step3 --> opt_prune{Retention cleanup?}
        opt_transfer -- "Yes" --> step4([SFTP/Upload backups to remote storage])
        opt_transfer -- "No" --> step5([Keep backups locally])
        opt_prune -- "Yes" --> step6([Delete old backups])
    end
    classDef optional fill:#ffe,stroke:#999;
    opt_transfer, opt_prune class optional;
    style opt_transfer stroke-dasharray: 5 5,stroke:#333;
    style opt_prune stroke-dasharray: 5 5,stroke:#333;
```

*(Diagram: Backup role flow – the role dumps the database and media to local files. Offsite transfer and old backup cleanup are **optional** steps that can be implemented externally.)*

## Supported Operating Systems/Platforms

This role is tested on and supported with the following Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** These Debian/Ubuntu-based systems are the primary targets for this role. The tasks leverage Debian/Ubuntu defaults (such as the `postgres` user and standard file paths). Other Unix-like systems (RedHat, CentOS, etc.) are not officially tested and may require minor adjustments.

## Role Variables

Below is a list of important variables for this role, along with default values (defined in **`defaults/main.yml`** or expected from inventory) and their descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                | Default Value                                                             | Description                                                                                                                                                                                                                                                                                                                                                                                |
| ----------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`postgres_host`**     | `"localhost"`                                                             | Hostname or address of the PostgreSQL server hosting the NetBox database. Defaults to `"localhost"` (assuming NetBox DB is local). In a distributed setup, set this to the DB server’s address (e.g. an inventory group target).                                                                                                                                                           |
| **`postgres_port`**     | `5432`                                                                    | TCP port for PostgreSQL connection (default `5432`). Change if your Postgres instance listens on a non-standard port.                                                                                                                                                                                                                                                                      |
| **`postgres_db`**       | `"netbox"`                                                                | Name of the NetBox PostgreSQL database to back up. The default is `"netbox"`.                                                                                                                                                                                                                                                                                                              |
| **`postgres_user`**     | `"netbox"`                                                                | PostgreSQL username with access to the NetBox database. By default `"netbox"` (the typical NetBox DB user). This user should have permission to read the entire database for dumping.                                                                                                                                                                                                      |
| **`postgres_password`** | *Not set* (required)                                                      | Password for the above PostgreSQL user. **This must be provided by the user**, as no default is stored in the role (for security). For example, in an inventory you might supply this via Ansible Vault. The backup task will use this password to authenticate when dumping the database.                                                                                                 |
| **`netbox_media_root`** | `{{ netbox_install_dir }}/netbox/media` (e.g. `/opt/netbox/netbox/media`) | Filesystem path to NetBox’s media files directory (where uploaded media/attachments are stored). By default, it uses the standard NetBox installation path: concatenating `netbox_install_dir` (which defaults to `/opt/netbox`) with `/netbox/media`. If your NetBox’s media files reside in a custom location, set this variable accordingly so the role archives the correct directory. |

</details>
<!-- markdownlint-enable MD033 -->

**Notes:** In many cases, these variables (especially `postgres_*` and `netbox_media_root`) are defined in your inventory or set by the NetBox installation role. For instance, this repository’s **production inventory** provides the NetBox DB connection info and installation path via group variables. The defaults above assume a typical single-host NetBox deployment. If your setup differs (e.g. remote DB server, custom install paths), adjust the variables as needed.

## Tags

This role does **not define any Ansible tags** in its tasks. All tasks will run by default whenever the role is invoked. (You may still apply tags externally when including the role in a play, if you wish to control execution of this role along with other tasks.)

## Dependencies

* **Ansible Version:** Requires Ansible **2.13** or higher to run properly (due to use of newer modules/collections and syntax).
* **Collections:** Ensure the **`community.postgresql`** collection is installed on the control machine, as this role uses the `postgresql_db` module from that collection for database dumps. You can install it via: `ansible-galaxy collection install community.postgresql`.
* **Python Libraries:** The target host (NetBox server/DB server) needs the PostgreSQL client library (Python `psycopg2` or equivalent) available for Ansible’s PostgreSQL modules to work. The NetBox database server should already have this if PostgreSQL is installed. If not, you may need to install the PostgreSQL client packages (e.g. `postgresql-client`) on the target.
* **External Roles/Software:** This role assumes a running PostgreSQL database (and if applicable, a running NetBox instance). Provisioning of PostgreSQL itself is outside the scope of this role. (For example, in this repository the database setup is handled by the **geerlingguy.postgresql** role before using `backup_netbox`.)

## Example Playbook

Below is an example of how to use the `backup_netbox` role in an Ansible playbook. In this example, we assume a single server is running both NetBox and its database (adjust the hosts/group as needed for your inventory):

```yaml
- hosts: netbox_server
  become: yes  # Ensure we have root privileges for backup tasks
  vars:
    postgres_host: "localhost"
    postgres_port: 5432
    postgres_db: "netbox"
    postgres_user: "netbox"
    postgres_password: "{{ vault_netbox_db_password }}"  # retrieve from Vault or inventory
    netbox_media_root: "/opt/netbox/netbox/media"
  roles:
    - backup_netbox
```

In the above play, we target the `netbox_server` host (replace with your actual host or group name). We provide the required variables such as database credentials and the media path. The role will then:

1. Connect to the PostgreSQL service on `localhost` as user **netbox** (using the provided password) and dump the **netbox** database to a file.
2. Archive the NetBox media files located in `/opt/netbox/netbox/media` into a tarball.
3. Place the resulting `.sql` dump and `.tgz` archive in `/var/backups/netbox` on the target host.

Typically, you would not hard-code the database password in the playbook as shown above. Instead, store it securely (for example, in an Ansible Vault or a secrets manager). In this repository’s inventory, for instance, the NetBox DB password is pulled from HashiCorp Vault. The example is kept simple for illustration.

**Usage in Practice:** In a real scenario, these variables might already be set via group variables. For example, the provided `netbox-backup.yml` playbook in this repository runs the role on the **netbox_db_servers[0]** host with `become: true`, while the inventory supplies the `postgres_*` and `netbox_install_dir` values. You can adapt the above playbook or simply include this role in your site playbook wherever you need to trigger a NetBox backup.

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to ensure it works correctly in an isolated environment. Follow these steps:

1. **Install Molecule and Docker:** On your development machine, install Molecule and the Docker backend (e.g. via pip: `pip install molecule[docker]`). Ensure Docker is installed and running.
2. **Prepare a test scenario:** If a Molecule scenario is provided with this role (e.g. under `roles/backup_netbox/molecule/default/`), you can use it. Otherwise, you can initialize a new scenario with:

   ```bash
   molecule init scenario -r backup_netbox -d docker
   ```

   This will create a `molecule/` directory with a default configuration for testing the role.
3. **Configure the scenario (if needed):** Edit the Molecule config (`molecule.yml`) or the playbook (`converge.yml`) to suit the test. Typically, you’ll want to use a Docker image based on Debian or Ubuntu (matching the supported OS). You may also need to install PostgreSQL server in the container and populate a dummy NetBox database for a realistic test (or at least ensure the `postgresql` service is running with a `netbox` database that the role can dump).
4. **Run the role in a container:** Execute `molecule converge`. Molecule will launch a fresh container and apply the `backup_netbox` role to it (using the `converge.yml` playbook in the scenario). Watch the output for any task failures. After this, the container should contain the backup artifacts.
5. **Verify the results:** You can manually inspect the container to ensure the backup ran as expected. For example:

   ```bash
   docker exec -it <container_id> ls -l /var/backups/netbox
   ```

   You should see files like `netbox_<timestamp>.sql` and `netbox_media_<timestamp>.tgz` in that directory. If the role includes automated tests (e.g. with Testinfra or Ansible asserts), you can run `molecule verify` to execute those. Otherwise, manual verification of the backup files (and possibly contents) is advised.
6. **Cleanup:** Once testing is done, tear down the test container with `molecule destroy`. *(Or use `molecule test` to run the full cycle: create, converge, verify, destroy in one go.)*

Using Molecule ensures the role runs idempotently and can be safely executed on a clean system. It also helps catch any platform-specific issues. During testing, you might use a smaller database or dummy data to speed up the process. Ensure that any sensitive variables (like `postgres_password`) are provided to Molecule (for example, via `group_vars` in the scenario or passing through environment secrets) so that the role can run non-interactively.

## Known Issues and Gotchas

* **Data Consistency vs Service Uptime:** By default, this role does *not* stop the NetBox service when performing the backup. This means the database dump is taken “online.” In practice, brief writes during the dump may not significantly corrupt the backup, but there is a small chance of capturing in-flight changes. For most installations, this is acceptable and the backup will be consistent enough. However, if you require a transaction-consistent snapshot (no changes during backup), consider scheduling a short maintenance window. For example, you could manually stop the NetBox service or put the application in read-only mode during the backup. (The official NetBox Enterprise backup procedure stops the NetBox service during backup to ensure integrity.) Balancing downtime vs. consistency is a decision for your environment; this role leaves that to the user to manage as needed.
* **Backup Retention:** The role **does not automatically purge old backups** from `/var/backups/netbox`. Every run will create new files, so you need to implement a retention policy. Over time, backup files can accumulate and consume significant disk space. It’s recommended to periodically delete backups older than a certain age (e.g. keep the last 7 or 14 days of backups). You can achieve this via a cron job or an additional Ansible task. For example, a simple approach is to run a find command to remove files older than *N* days:

  ```bash
  find /var/backups/netbox -type f -mtime +14 -delete
  ```

  (This would delete files older than 14 days.) In an enterprise setup, backup retention and pruning should be part of your strategy – the upstream documentation suggests managing retention as a key part of the backup process. Always ensure you have enough recent backups to meet your recovery point objectives, while cleaning up outdated files.
* **Offsite Storage of Backups:** Copies of the backup files are **not automatically transferred offsite** by this role. The dumps and archives remain on the NetBox host in `/var/backups/netbox`. It is **critical** to move backups to secure external storage (another server, cloud storage, etc.) to protect against server loss. You can accomplish this with additional tasks or external tools – for example, using `ansible.builtin.fetch` to retrieve the files to the control node, or a follow-up role/task to SCP/SFTP the files to a backup server. The NetBox Enterprise guide includes an optional step to SFTP the backup files to a remote server for safekeeping. Implement a solution that fits your environment (ensuring that transfers are secure and automated).
* **Backup Size and Duration:** Be mindful of the size of your NetBox database and media when planning backups. Large databases or many uploaded files will result in large backup files and longer execution times. Ensure the **`/var/backups/netbox`** directory is on a filesystem with sufficient space. If your NetBox is several gigabytes in size, the `.sql` dump could be correspondingly large. Consider compressing the SQL dump (this role doesn’t compress the `.sql` by default, though you could pipe it through gzip by customizing the tasks). Running the backup during off-peak hours (late night or early morning) is advisable to minimize any performance impact on the NetBox server.
* **Restore Procedure:** Remember, a backup is only as good as your ability to restore it. This role does not provide an automated restore playbook, so you should practice the restore process manually to verify your backups. To restore, you would typically stop NetBox, create a fresh database (or drop the existing one), load the SQL dump (e.g. `psql netbox < netbox_<date>.sql`), and unpack the media tarball back into the NetBox media directory. Verify that NetBox starts up and the data is intact. Performing test restores periodically (for example, on a staging environment) will give you confidence that the backups are valid and complete.

## Security Implications

* **Privilege Use:** This role performs actions with elevated privileges. It runs as **root** on the target system (via `become: true`) and even switches to the **postgres** system user when dumping the database. These privileges are necessary to read all data and files. Ensure that only trusted administrators run this role, and limit access to your Ansible inventory and vaults containing the DB credentials.
* **Credentials Management:** You must provide the database password (`postgres_password`) for the NetBox DB user to allow the dump. Storing this secret securely is crucial. **Do not hard-code passwords in plain text** in playbooks or in Git. Instead, use Ansible Vault or another secrets management solution. In our inventory example, the NetBox DB password is fetched from HashiCorp Vault rather than being stored in the repository. This approach keeps sensitive credentials out of source control. Follow similar practices for your environment.
* **Backup File Sensitivity:** The backup files produced (SQL dumps and media archives) contain all the information in your NetBox instance – including potentially sensitive data like IP schemas, device inventories, user account data, and secrets stored in NetBox (if any). Treat these files as sensitive assets. By default, the role restricts the backup directory to `root:root` ownership with permission `0750` (only root and its group can access). This is a good security measure to prevent local non-privileged users from reading the backups. Maintain these strict permissions. If you need non-root processes to handle the backups (for example, a backup agent that runs as its own user), consider adjusting group ownership or using a secure copy method rather than loosening the permissions.
* **Encryption of Backups:** The backups generated by this role are **not encrypted** at rest. They are plain text (for the SQL file) and tarball (for media). If the backup files might be stored in less secure locations or transferred over networks, you should encrypt them. This could be done by modifying the role or adding steps to encrypt the files with a tool like GPG or OpenSSL after creation. (For instance, you could use **`community.crypto.openssl_encrypt`** or GPG to encrypt the `.sql` and `.tgz` files with a public key.) The official NetBox backup guidance emphasizes encrypting backup files as part of the process. Failing to do so could expose sensitive data if the backups are obtained by unauthorized parties. Always weigh the security requirements of your organization – for highly sensitive environments, enabling encryption and secure key management for backups is strongly recommended.
* **Network Exposure:** This role itself does not open any network ports or start any network services on the host. All operations are local (database connection is local or over the existing DB port, and file archiving). However, if you implement remote backup transfers (e.g. via SFTP in a follow-up step), ensure you use secure protocols and keys. For example, favor SSH key authentication for SFTP/SSH transfers of backups, rather than embedding passwords. If you plan to serve or download backups via an API or web server, put proper authentication in place. Essentially, treat the backup files with the same security as you would the live NetBox data.
* **System Integrity:** No new system users or software are installed by this role. It leverages existing system utilities (PostgreSQL and tar). This means the role’s footprint is small. Nevertheless, always review the tasks if you modify the role – accidental misconfiguration (like pointing `netbox_media_root` to `"/"` by mistake) could archive more than intended. The role defaults are safe, but with great power (root access) comes responsibility.

By understanding and addressing these considerations, you can safely incorporate `backup_netbox` into your NetBox maintenance routine with minimal risk.

## Cross-Referencing

This role is part of a suite of Ansible roles for managing NetBox and related infrastructure. You may find the following roles (in the same repository) useful in conjunction with **`backup_netbox`**:

* **`netbox` role** – Installs and configures the NetBox application itself (web UI, background services, etc.). Use the `netbox` role to set up your NetBox server initially, and then use `backup_netbox` to safeguard its data. (See the [`netbox` role README](../netbox/README.md) for details on installation variables and setup.) The two roles are designed to work together – for example, `netbox` defines the `netbox_install_dir` and database settings that `backup_netbox` uses.
* **`postgres_backup` role** – A more general PostgreSQL backup role included in this repository. Whereas `backup_netbox` is specific to NetBox’s database (and media files), **`postgres_backup`** can be used to back up PostgreSQL databases in a broader context (e.g., other applications’ databases or an entire database cluster). If you have additional Postgres databases to protect (outside of NetBox), you might apply `postgres_backup` for those. It uses a similar mechanism (dumping databases to files) but is not NetBox-specific. Refer to the [`postgres_backup` role documentation](../postgres_backup/README.md) for usage and how it differs (if at all) from `backup_netbox`. Typically, you would use `postgres_backup` on database servers and `backup_netbox` on the NetBox application server (if those are separate). Both roles rely on the **community.postgresql** collection for Postgres operations.

Lastly, if you are using NetBox in a production environment, consider complementing this backup role with monitoring and maintenance tasks. For example, verifying that backups succeed (perhaps via Nagios/Sensu checks on file age), using the **`netbox` role’s** variables to tune performance, and employing roles like **`postgresql`** (or the external **geerlingguy.postgresql**) to properly configure the database. Each role plays a part in a robust NetBox deployment: **`backup_netbox`** focuses on data safety, while other roles handle installation, configuration, and maintenance. By using them together, you can achieve a well-managed and resilient NetBox installation.
