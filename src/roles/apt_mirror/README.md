# apt_mirror Ansible Role

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

## Overview

This role installs and configures a local APT package mirror on a Debian/Ubuntu server using the **apt-mirror** utility and serves the mirrored repositories via Apache HTTP. It is designed to be **idempotent** and flexible, allowing you to maintain an in-house mirror of Debian/Ubuntu repositories for faster and controlled package installs. Key features include:

* Support for mirroring multiple distributions (e.g. Ubuntu, Debian releases), components (main, universe, etc.), and CPU architectures.
* Automatic regular synchronization via cron (daily by default) to keep the mirror up to date.
* Automatic pruning of outdated packages after each sync to free up storage.
* Optional integration with an ELK stack for shipping mirror logs or metrics to a central logging system.
* Optional high-availability support (HA stubs) using a Virtual IP (Keepalived) to failover between mirror servers.
* Optional weekly backup of mirror metadata (indexes) for disaster recovery (DR) purposes.
* Two deployment profiles: **simple** (default) for basic standalone mirrors, and **complex** for production setups enabling the above optional features via a single switch.

By default, the role operates in "simple" mode. Setting `deployment_profile: "complex"` will turn on advanced features (ELK integration, DR backups, and allow HA) automatically. This role focuses on the server-side mirror. To configure client machines to use the new mirror, see the companion **`apt_mirror_client_setup`** role in this repository.

## Supported Operating Systems/Platforms

This role is tested on and supported with the following Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** The target hosts must be Debian/Ubuntu systems because the `apt-mirror` package is specific to Debian-based package management.

## Role Variables

Below is a list of important variables for this role, along with default values (defined in **`defaults/main.yml`**) and their descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                         | Default Value           | Description |
| -------------------------------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`apt_mirror_base_path`**       | `/var/spool/apt-mirror` | Base directory on the mirror server where all mirrored packages and metadata are stored. This directory will be created if it does not exist, and must have sufficient space for the repositories you mirror. |
| **`apt_mirror_mirrors`**         | *Empty list* `[]`       | List of mirror sources to sync. **This must be provided by the user**, since no default mirrors are set (an empty list means nothing will be mirrored). Each list item is a dictionary defining an upstream repo with keys: <br>`name`: an identifier for the mirror (used for Apache alias) <br>`base_url`: the base URL of the upstream archive (e.g. `http://archive.ubuntu.com/ubuntu`) <br>`distributions`: list of distribution releases to mirror (e.g. `["jammy", "jammy-updates", "jammy-security"]`) <br>`components`: list of repository components (e.g. `["main", "restricted", "universe", "multiverse"]`). |
| **`apt_mirror_architectures`**   | `["amd64"]`             | List of CPU architectures to mirror. By default only 64-bit packages (`amd64`) are mirrored. You can include additional architectures (e.g. `"i386"`) in this list. If more than one architecture is specified, the role will enable multi-architecture mode (creates a separate symlink for multi-arch content). |
| **`apt_mirror_include_sources`** | `false`                 | Whether to include source packages (`deb-src`) in the mirror. When set to `true`, the apt-mirror config will include source repositories so that source .deb packages are mirrored as well. (Note: Setting `deployment_profile: "complex"` also enables source mirroring by default). |
| **`apt_mirror_cron_enabled`**    | `true`                  | Whether to schedule an automatic cron job for syncing the mirror. If `true`, a cron entry will be installed to run `apt-mirror` on the defined schedule (below) as the **apt-mirror** user. Disable this if you prefer to sync manually. |
| **`apt_mirror_cron_schedule`**   | `"0 4 * * *"`           | The cron schedule for mirror synchronization, in crontab format (minute, hour, day, month, weekday). By default this is `"0 4 * * *"`, meaning daily at 04:00 (4 AM). Adjust this schedule as needed for your environment. |
| **`elk_integration_enabled`**    | `false`                 | Whether to enable ELK (Elastic Stack) integration. If `true` (or if `deployment_profile` is set to "complex"), the role will include tasks to ship apt-mirror logs or metrics to your ELK stack. This may involve installing and configuring a log forwarder (e.g. Filebeat) to send the mirror’s log (`cron.log`) to a central server. |
| **`ha_features_enabled`**        | `false`                 | Whether to enable high-availability features. If set to `true` **and** `deployment_profile: "complex"`, the role will configure HA-related tasks. Typically this means setting up a Virtual IP address via Keepalived so that two or more mirror servers can fail over. Additional configuration (such as specifying `keepalived_router_info`) is required for this to work properly. |
| **`dr_backup_enabled`**          | `true`                  | Whether to enable weekly backup of mirror metadata for disaster recovery. If `true`, a cron job will be installed to archive the apt-mirror metadata (index files) on a weekly basis (every Sunday at 2:00 AM by default). These backups (tarballs in `/var/backups/apt-mirror/`) can help rebuild the mirror or analyze its state in case of issues. |
| **`apt_mirror_prune`**           | `true`                  | Whether to run apt-mirror’s **clean** step after each sync. The clean process removes packages that are no longer present upstream (prunes outdated files) to save space. It is **highly recommended** to keep this enabled to avoid unlimited growth of the mirror storage. Set to `false` only if you have a specific reason to retain all historical packages. |

</details>
<!-- markdownlint-enable MD033 -->

In addition to the above, you can use `deployment_profile` (string) to quickly toggle groups of features. By default it is `"simple"`. Setting `deployment_profile: "complex"` will effectively set `elk_integration_enabled` to true and allow HA features (while still requiring `ha_features_enabled: true` to fully activate HA). You can also directly toggle each feature via its variable as shown in the table.

## Tags

This role does **not define any Ansible tags** in its tasks. All tasks will run by default when the role is invoked. (You may still apply tags externally when including the role, if desired.)

## Dependencies

* **Ansible Version:** Requires Ansible **2.13** or higher (utilizes newer syntax and modules).
* **Collections:** The role uses the `apache2_module` Ansible module to enable Apache mods, which is part of the **community.general** collection (not in ansible-core). Ensure you have `community.general` installed (e.g. via `ansible-galaxy collection install community.general`) before running this role.
* **External Packages:** No external Ansible roles are needed (all necessary setup is done within this role). However, the target host must have access to install the following system packages:

  * **apt-mirror:** The main tool that synchronizes APT repositories (installed via apt).
  * **apache2:** Web server used to serve the mirrored files over HTTP.
  * **python3-apt:** Python bindings for APT, required by some apt-related modules and scripts.
    These packages will be automatically installed by the role on the target machine. Ensure the host’s package manager is functional and the default package repositories are available.

## Example Playbook

Here is an example of how to use the `apt_mirror` role in a playbook. This will set up a simple mirror for Ubuntu 22.04 (Jammy) packages:

```yaml
- hosts: mirrors
  become: yes
  vars:
    apt_mirror_mirrors:
      - name: "ubuntu_official"
        base_url: "http://archive.ubuntu.com/ubuntu"
        distributions: ["jammy", "jammy-updates", "jammy-security"]
        components: ["main", "restricted", "universe", "multiverse"]
    apt_mirror_include_sources: false    # do not include source packages in mirror
    # apt_mirror_architectures: ["amd64"]  # (default is ["amd64"]; adjust if needed)
  roles:
    - apt_mirror
```

In the above play, we define one mirror source (`ubuntu_official`) for Ubuntu 22.04 and use default settings for architecture (amd64 only) and cron schedule (daily 4 AM). Run this playbook against your mirror server host to set up the mirror.

For a more advanced production setup, you could set `deployment_profile: "complex"` and toggle other variables (e.g. `elk_integration_enabled: true`, `ha_features_enabled: true`) in your inventory or playbook. This would enable log shipping and high-availability features in addition to the basic mirror setup.

After deploying the mirror server, you can use the **`apt_mirror_client_setup`** role on your client machines to reconfigure their `apt` sources to use the new mirror (for example, pointing to `http://<your-mirror-server>/mirror/…` instead of the official URLs).

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to ensure everything works as expected before applying to production:

1. **Install Molecule** and Docker on your development machine (e.g. `pip install molecule[docker]`). Ensure Docker is running.
2. **Prepare a test scenario:** If a Molecule scenario is provided with this role (usually in `molecule/default/`), use that. Otherwise, you can initialize one with `molecule init scenario -r apt_mirror -d docker` (this creates a default Molecule config for the role).
3. **Run the role in a container:** Execute `molecule converge` to create a Docker container (based on a Debian/Ubuntu image) and apply the `apt_mirror` role to it. Molecule will use the playbook in `molecule/default/converge.yml` (or equivalent) to run the role.
4. **Verify the results:** After converge, you can shell into the container (e.g. `docker exec -it <container_id> /bin/bash`) to check that `/var/spool/apt-mirror` is populated, Apache is running, and the config files are in place. If the role includes automated tests (e.g. with Inspec or Testinfra in `molecule/`), run `molecule verify` to execute them.
5. **Cleanup:** Run `molecule destroy` to tear down the test container when done. Or use `molecule test` to run the entire sequence (create, converge, verify, destroy) in one command.

Using Molecule ensures that the role is idempotent and works on a fresh system. During testing, you might want to adjust `apt_mirror_mirrors` to a smaller repository or use caching to avoid lengthy downloads. Also, consider setting `apt_mirror_cron_enabled: false` during tests to skip cron setup (since the container might not have a functioning cron service by default).

## Known Issues and Gotchas

* **Initial Sync Time & Storage:** The first run of apt-mirror can be time-consuming and will download a large amount of data, depending on how many distributions/architectures you configured. Ensure the `apt_mirror_base_path` location has sufficient disk space and a reliable network connection to upstream mirrors. Subsequent runs (via cron) will be incremental.
* **Running Sync Manually:** The cron job is configured to run as the `apt-mirror` system user. If you need to run `apt-mirror` manually, run it under the `apt-mirror` user (e.g., `sudo -u apt-mirror apt-mirror`) to avoid permission issues. Running it as root can create root-owned files in the mirror directory, which will prevent the normal sync (running as apt-mirror) from updating those files later.
* **Multi-Architecture Mirrors:** Apt-mirror does not natively segregate files by architecture in separate directories. In this role, if you enable multiple architectures (e.g. `"amd64"` and `"i386"`), all packages will be mirrored under the same `mirror` directory. The role automatically creates a symlink `mirror_arch` pointing to the `mirror` directory for compatibility. This is used internally to serve multi-arch content, so you generally don’t need to worry about it – just ensure your clients have multi-arch enabled if they require packages of different architectures.
* **Pruning Behavior:** Be aware that if you disable `apt_mirror_prune`, the mirror will keep **all** retrieved packages, even those outdated upstream. This will consume increasing storage over time. Only disable pruning if you intend to maintain an archive of all packages. By default, pruning is on and apt-mirror’s `clean.sh` is run after each sync to delete files not referenced by the current mirror config.
* **APT GPG Keys:** This role does **not** manage APT GPG keys for the mirrored repositories. The mirror is essentially a copy of the upstream packages and indexes; clients using the mirror will still need to trust the same repository signing keys as they would when using the official mirror. (For official Ubuntu/Debian mirrors, clients typically already have the necessary keys installed via `ubuntu-keyring` or `debian-archive-keyring`.) If you mirror a custom or third-party repo, ensure clients import the appropriate GPG key for that repository manually.
* **Firewall and Access:** The mirror is served over HTTP on port 80 by default. The role does not automatically configure firewall rules. If your server has a firewall (e.g. UFW or others), make sure to allow inbound traffic on port 80 to let clients access the mirror. Optionally, you could serve the mirror behind an HTTPS reverse proxy for encryption or require VPN/ssh-tunnel for access if security is a concern (since HTTP is plaintext).
* **High Availability Setup:** If you enable HA features (`ha_features_enabled: true` with complex profile), the role will attempt to configure Keepalived for a virtual IP address. This assumes you have at least two mirror hosts in the inventory group and have provided the necessary Keepalived settings (like `keepalived_router_info`) in your vars. Make sure the **keepalived** service is allowed to communicate (VRRP uses protocol 112) and that both primary and secondary mirror servers are configured consistently. You may refer to the **`keepalived`** role in this repository for a more controlled setup of VRRP if needed. The HA setup ensures that if the primary mirror goes down, the secondary can take over the IP and continue serving packages.
* **ELK Integration Expectations:** When `elk_integration_enabled` is true, the role will include tasks to forward logs to your ELK stack. Ensure that your environment has an ELK endpoint (e.g. Logstash or Elasticsearch ingestion API) reachable, and adjust any variables (if provided) for log shipping. Typically, this integration might install a tool like Filebeat to ship `/var/spool/apt-mirror/var/cron.log` (which contains sync logs) to the ELK server. Verify that the log shipping is working and consider security implications (the logs are not sensitive, but network connectivity to ELK is required). If you do not have an ELK setup ready, leave this disabled to avoid unnecessary package installation or errors.

## Security Implications

* **System User:** The installation of **apt-mirror** creates an `apt-mirror` system user on the server. This role makes use of that user account for running sync jobs (via cron). The mirror files in `apt_mirror_base_path` are owned by `apt-mirror:apt-mirror` with permissions 0755 (world-readable). This ensures the Apache web server (running as `www-data`) can read the files. The `apt-mirror` user has no interactive login by default, and its permissions are limited to the mirror directory, which is good for security isolation.
* **Network Ports:** By default, the mirror is served over **HTTP on port 80**. The Apache configuration allows open access (`Require all granted`) to the mirror content, meaning anyone who can reach the server can fetch packages. There is no authentication or encryption on this port by default. If this mirror is for internal use, ensure the network is segmented or firewalled appropriately. If exposure to the public internet is needed, consider adding HTTPS (e.g., via a reverse proxy or enabling Apache SSL) and possibly basic authentication to restrict usage.
* **File/Directory Permissions:** The role ensures the mirror directory (`apt_mirror_base_path`) and its subdirectories are created with correct permissions (owned by apt-mirror user, mode 0755). This strikes a balance between access (Apache and others can read files) and security (only the apt-mirror user can write into the mirror area). The backup directory for DR (`/var/backups/apt-mirror`) is created root-owned (mode 0755) and stores compressed metadata – these files should be accessible only to admins.
* **Cron Jobs:** A cron job is installed (under `/etc/cron.d/` or the user’s crontab) to sync the mirror daily. This job runs as the apt-mirror user and redirects output to a log file (`cron.log` in the mirror var directory). Ensure that this log file is rotated or monitored as needed. The weekly backup cron (if enabled) runs as root (via the system cron) to create tar archives of metadata. Both cron jobs are non-interactive and have limited scope, but they do consume network bandwidth and disk I/O; consider timing (4 AM default) to avoid interfering with peak usage hours.
* **High Availability (Keepalived):** If HA is enabled, the role (or accompanying setup) will configure Keepalived. Keepalived runs with root privileges and manipulates network interfaces to add a virtual IP. It will send multicast VRRP advertisements on your network. While Keepalived is a standard tool, be aware that misconfiguration (e.g., overlapping VRRP IDs or VIPs) could disrupt network addressing. Use secure passwords for VRRP instances if your network is untrusted (to prevent malicious takeover of the VIP). The Keepalived configuration in this role uses settings you provide (like interface name, virtual IP address, etc.) – review them carefully.
* **ELK/Logging Agents:** Enabling ELK integration may install a log forwarding agent (such as Filebeat) on the mirror server. Such an agent typically runs as root or a dedicated service account and will have read access to apt-mirror’s log files. It will also establish outgoing connections to send data to the ELK stack. Ensure your firewall allows this egress and that the credentials/keys for the ELK endpoint (if any) are kept secure. Also, consider that any logs sent to ELK will be accessible to whoever has access to your ELK system – though apt-mirror logs are generally not sensitive (mostly a list of packages synced or any errors).
* **Package Authenticity:** The mirror server synchronizes packages but does not alter them. Clients will use their own apt verification (GPG signatures) when installing from the mirror. As long as clients trust the official keys, using the mirror does not introduce additional risk of tampering, provided your mirror server itself is secure. Keep the server patched and limit access to it. The Apache directory listing is enabled for convenience, but directory indexes could expose the list of packages to unauthenticated users – this is usually fine for public repo data. If you mirror any private repository, you should restrict access to the mirror (e.g., via Apache auth or network controls) accordingly.
