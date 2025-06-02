# Ansible Role: Base

*Ansible role for baseline system configuration and hardening on Linux servers.*

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

The **Base** role sets up essential system configuration and security measures on a fresh server. It performs initial cleanup of unnecessary packages, fully updates the operating system, and configures basic security tools like automatic updates, Fail2Ban (intrusion prevention), and ClamAV antivirus. By applying this role, you ensure all servers have a consistent baseline (packages up-to-date, common vulnerabilities mitigated, and baseline services configured) before layering on additional application-specific roles.

In practice, this role orchestrates several component roles in sequence to prepare the system:

```mermaid
flowchart TD
    subgraph "Base Role Execution"
    RUP[Remove Unnecessary Packages] --> US[Update System] --> RB[Bootstrap (robertdebock.bootstrap)] --> AU[Auto Update (robertdebock.auto_update)] --> F2B[Fail2Ban (robertdebock.fail2ban)] --> CL[ClamAV (geerlingguy.clamav)]
    end
```

The **Base** role is typically run early in your playbook (often on all hosts) with elevated privileges (`become: yes`). It assumes internet access for package installation and updates. No application-specific configurations are made here – only generic system hardening and preparation tasks. This provides a solid foundation for subsequent roles (database, webserver, etc.) to build upon.

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian** and **Ubuntu** Linux distributions:

* **Debian**: 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu**: 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian-based systems similar to the above releases are likely compatible. The role uses `apt` for package management, so Red Hat/CentOS or other non-APT-based systems are **not supported** without modifications. Ensure you are running a supported OS version to prevent any compatibility issues.

## Role Variables

<details><summary>Click to see default role variables.</summary>

| Variable                           | Default Value                 | Description                                                                                                                                                                                                                |
| ---------------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`remove_unnecessary_packages_list`**         | `["games", "ftp", "telnet"]`  | List of packages to remove during initial cleanup. By default, it removes legacy or insecure utilities (games, ftp, telnet) that are generally not needed on servers.                                                      |
| **`auto_update_download_updates`** | `yes`                         | Whether to automatically **download** package updates when they become available. (Part of unattended-upgrades configuration.)                                                                                             |
| **`auto_update_apply_updates`**    | `no`                          | Whether to automatically **apply** downloaded updates. By default this is off (updates are downloaded but not installed automatically). Set to `yes` to enable fully unattended upgrades (use with caution in production). |
| **`auto_update_random_sleep`**     | `360`                         | Maximum random delay (in seconds) before the auto-update service runs. Staggering update checks helps avoid all systems updating at exactly the same time.                                                                 |
| **`fail2ban_loglevel`**            | `"INFO"`                      | Logging level for Fail2Ban. Controls verbosity of Fail2Ban logs (INFO is default).                                                                                                                                         |
| **`fail2ban_logtarget`**           | `"/var/log/fail2ban.log"`     | Log file path for Fail2Ban. Fail2Ban will write its log messages here.                                                                                                                                                     |
| **`fail2ban_ignoreself`**          | `"true"`                      | Instructs Fail2Ban to ignore the server’s own IP (localhost) when monitoring for failures. Typically should remain true to prevent self-bans.                                                                              |
| **`fail2ban_ignoreips`**           | `["127.0.0.1/8", "::1"]`      | List of IP addresses or networks that Fail2Ban should never ban. By default, localhost IPv4/IPv6 are whitelisted. Add your trusted IPs here if needed.                                                                     |
| **`fail2ban_bantime`**             | `600`                         | Ban duration in seconds for banned IPs (default 10 minutes). After this period, the IP is automatically unbanned.                                                                                                          |
| **`fail2ban_findtime`**            | `600`                         | Monitoring window in seconds. Fail2Ban counts failed login attempts within this timeframe to decide if a ban should occur.                                                                                                 |
| **`fail2ban_maxretry`**            | `5`                           | Maximum failed login attempts before an IP is banned. (e.g., 5 failed SSH login attempts within the findtime window triggers a ban.)                                                                                       |
| **`fail2ban_destemail`**           | `"admin+fail2ban@qimata.net"` | Destination email for Fail2Ban alerts. Fail2Ban will send ban notification emails to this address (if mailing is configured).                                                                                              |
| **`fail2ban_sender`**              | `"admin@<server_fqdn>"`       | Sender address for Fail2Ban emails. By default, uses “admin@” with the server’s FQDN. Adjust if your mail setup requires a specific sender.                                                                                |

</details>

Most defaults are defined in **`roles/base/defaults/main.yml`** or inherited from included roles. You can override these in your inventory or playbook as needed. For example, to change Fail2Ban’s ban time or enable auto-upgrades, set the corresponding variables in your playbook or host/group vars.

## Tags

This role does not define any custom Ansible tags of its own. All tasks in the Base role (and its dependency roles) run by default.

* **Required tags:** None (the role’s tasks run unconditionally when the role is invoked).
* **Optional tags:** You may leverage tags from the included dependency roles if they have any. For instance, the **Geerlingguy.clamav** role’s tasks might be tagged as `clamav`, and **robertdebock.fail2ban** tasks might use a `fail2ban` tag. While running playbooks, you can use `--tags fail2ban` or `--skip-tags clamav` to selectively run or skip parts, *provided those tags are defined in the sub-role*. (The Base role itself doesn’t apply a blanket tag to all its sub-tasks.)

Generally, you will include the entire Base role in your play, so fine-grained tagging is usually not necessary. If you need to skip a component (say you don’t want ClamAV on a particular host), it’s often clearer to disable it via variables or omit that dependency rather than using tags.

## Dependencies

**External role dependencies:** The Base role relies on several Ansible Galaxy roles for specific tasks. These dependencies are automatically invoked via this role’s metadata, but **they must be available** on your system (installed via `ansible-galaxy`) before you run the Base role. The required roles are:

* **robertdebock.bootstrap** – Prepares a fresh system for Ansible by installing Python (using raw SSH) and ensuring basic tools (like `sudo`) are present.
* **robertdebock.auto_update** – Configures unattended package updates (for Debian/Ubuntu, sets up `unattended-upgrades`).
* **robertdebock.fail2ban** – Installs Fail2Ban and sets up jail configurations to ban malicious IPs after repeated failures.
* **geerlingguy.clamav** – Installs the ClamAV antivirus service and optionally configures scheduled scans (default is an on-demand scanner and freshclam updater).

These Galaxy roles should be installed in advance. If you use the provided **`src/requirements.yml`** (in the repository), you may need to add the above roles to it (if not already listed) and run `ansible-galaxy install -r requirements.yml`. Otherwise, install them individually, for example:

```bash
ansible-galaxy install robertdebock.bootstrap robertdebock.auto_update robertdebock.fail2ban geerlingguy.clamav
```

**Internal role dependencies:** In addition to external roles, Base includes some internal roles (from this same repository) that run automatically:

* **`remove_unnecessary_packages`** – Removes predefined unnecessary packages (games, legacy tools, etc.) to slim down the system and eliminate potential security risks.
* **`update_system`** – Updates all system packages to the latest available versions (essentially running an apt upgrade). This ensures the server starts in a fully patched state.

These internal roles are part of the repository and are invoked automatically; you do not need to call them separately. There are no other external system requirements (such as specific Python libraries on the control node) beyond a recent Ansible release (Ansible 2.13+ recommended to ensure all modules used are available).

## Example Playbook

Here is a simple example of how to use the `base` role in a playbook, including some variable overrides to customize its behavior:

```yaml
- hosts: all
  become: yes  # Ensure privilege escalation for system tasks
  vars:
    auto_update_apply_updates: yes       # Enable auto-install of updates (override default)
    fail2ban_ignoreips:                  # Add a trusted network to Fail2Ban whitelist
      - 127.0.0.1/8
      - ::1
      - 192.168.1.0/24
  roles:
    - base
```

In the above example:

* We run the role on **all hosts** and use `become: yes` because the tasks need root privileges.
* We override `auto_update_apply_updates` to `yes` to automatically apply updates (whereas the default is to only download them).
* We add a local LAN network to `fail2ban_ignoreips` so that Fail2Ban will never ban IPs from `192.168.1.0/24`.
* Then we simply include the `base` role. All of the baseline tasks (cleanup, updates, Fail2Ban, ClamAV, etc.) will run in order on the target hosts.

You can also set these variables in your inventory (`group_vars` or `host_vars`) instead of in the playbook. After running this play, your servers will be up-to-date, and the security measures will be in place.

## Testing Instructions

This role is equipped with **Molecule** tests to verify its functionality in a containerized environment. We use Molecule with the Docker driver and Testinfra for assertions. To run the tests for the Base role:

1. **Install Molecule and dependencies:** Make sure you have Molecule installed (`pip install molecule[docker]`) and Docker available on your system. Also install `pytest` and `testinfra` if not already present (Molecule will use these for verification).

2. **Obtain role dependencies:** The Molecule scenario will automatically use the role dependencies. Ensure you have run `ansible-galaxy install` for the roles mentioned in the Dependencies section above, so that Molecule can find them.

3. **Run Molecule tests:** From the repository root (where the `molecule/` directory is located), execute:

   ```bash
   molecule test -s base
   ```

   This will launch the **Base** role’s Molecule scenario. Under the hood, Molecule will:

   * Build a fresh Docker container (using a Debian-based image, e.g. Debian 12) for testing.
   * Run a converge step that applies the `base` role inside the container (this uses a test playbook similar to the example above).
   * Execute verification steps (via Testinfra) to ensure that expected changes have taken place (for example, checking that Fail2Ban is installed and running, ClamAV service is present, etc.).
   * Finally, destroy the test container.

4. **Review results:** Check the output for any failed tasks or failed tests. A successful run will end with "*** OK ***" after the verify phase and then clean up the container. If something fails (e.g., the role didn’t configure as expected), you can use `molecule converge -s base` to just apply the role and then manually inspect the container, or `molecule login -s base` to open a shell inside the test container for debugging.

The Molecule tests provide a quick way to validate changes to the role. Contributors should run these tests before submitting changes. The Molecule configuration for this role is defined in `molecule/base/default/molecule.yml` (with the Docker platform and a basic scenario).

## Known Issues and Gotchas

* **Full system upgrade impact:** This role will upgrade all packages on the system to the latest version. While this is usually desirable for security, be mindful that on running systems it may trigger restarts of services (e.g., upgrading the kernel or OpenSSL). It’s best to schedule the Base role (or any play including it) during maintenance windows for production environments. Always verify critical services after the upgrade.

* **No automatic reboot by default:** Unlike some hardening roles, Base (via `update_system`) does **not** automatically reboot the server after upgrading packages. If a kernel or critical library was updated, you might need to reboot manually to apply changes fully. You can combine this role with a planned reboot task or consider enabling unattended-upgrades’ reboot feature if automatic reboots are desired (not enabled by default here).

* **Role dependency availability:** Ensure all dependent roles are installed before running `base`. If any of the Galaxy roles (bootstrap, auto_update, fail2ban, clamav) are missing, Ansible will throw an error like "role not found". Install them via Galaxy or add them to your requirements file. (The Base role’s own tasks will not run until dependencies are resolved.)

* **ClamAV resource usage:** ClamAV can be memory and CPU intensive during virus database updates (freshclam) and scans. On smaller servers or containers, you might notice high resource usage. By default, the role installs ClamAV but does not schedule any heavy recurring scans. If you don’t need antivirus on a particular server, you can disable or remove the ClamAV installation by commenting out or removing that dependency (or by not running the Base role on that host). If you keep ClamAV, ensure there is adequate memory (freshclam updates can use a few hundred MB of RAM) and consider tuning ClamAV scan settings for your environment.

* **Fail2Ban lockout prevention:** Fail2Ban is configured to protect SSH (and possibly other services) out-of-the-box. Be careful not to lock yourself out. The default ignore list includes localhost but **not** other private IPs. If you run Ansible from a remote IP or jump host, consider adding it to `fail2ban_ignoreips` before applying the role. In case you get locked out (because Fail2Ban banned your IP), you’ll need console or out-of-band access to remove the ban. Always verify the `ignoreips` and ban settings in a staging environment.

* **Firewall not automatically configured:** This Base role does **not** enable or configure a firewall by default. It installs Fail2Ban (which uses firewall rules internally to ban IPs) but it does not set up general firewall rules for open/closed ports. If you require a firewall (e.g., UFW or firewalld) you should apply a separate role or manual tasks for that. (There was an option to include an UFW role, but it is left disabled in this role’s dependencies.) So, don’t assume ports are blocked just by using Base—set up a firewall explicitly if needed.

* **Initial connectivity and Python**: When running on a brand new server that lacks Python, the included `robertdebock.bootstrap` role will attempt to install Python using the raw module. This requires either direct root SSH access or a user able to `sudo` without a pre-existing Python interpreter. In practice, you should run the Base role with `become: yes` and an account that has root privileges. The bootstrap process will handle Python installation. If your Ansible control user cannot escalate to root, the bootstrap step (and thus the Base role) will fail. Ensure your inventory is set up to allow bootstrapping (e.g., `ansible_user=root` for new machines or a proper `ansible_become` configuration).

* **Mail setup for alerts:** The Base role (via Fail2Ban and possibly other services) is configured to send email alerts (e.g., Fail2Ban bans to `admin+fail2ban@qimata.net`). For these emails to actually get delivered, the server needs an operational mail transfer agent (MTA) or relay setup. The Base role itself does *not* configure an MTA. If you want to receive Fail2Ban emails, ensure an SMTP server or relay is configured on the host or adjust the notification settings to use an external email service.

## Security Implications

Running the Base role significantly improves the security posture of a server, but it’s important to understand what changes are being made:

* **Package Removal (Attack Surface Reduction):** By removing unnecessary packages (like `telnet` and `ftp` clients, games, etc.), the role reduces the potential attack surface. These packages are often outdated or not needed on servers. Security-wise, this means fewer binaries that could have vulnerabilities. The flip side is to verify none of your legitimate workflows needed those tools (usually they do not on production systems).

* **System Updates (Patching):** Applying all package updates ensures the latest security patches are in place. This is a fundamental security measure (mitigating known vulnerabilities in the OS and software). However, updates can sometimes change system behavior; ensure you trust the update sources and test if possible. Regular patching greatly lowers risk of compromise.

* **Unattended Upgrades:** The configuration for unattended upgrades (if enabled) means the system will continue to apply security (or all) updates automatically. This improves security long-term by ensuring new vulnerabilities get patched in a timely manner without waiting for manual intervention. The security trade-off is the potential for an unexpected change or reboot. With `auto_update_apply_updates: no` (default), the role only downloads updates and leaves installation to the administrator, which is a safer default in terms of change control. If you enable auto-apply, be aware that critical updates could trigger automatic restarts (for example, if you configure unattended-upgrades to reboot when needed). Always monitor and possibly use tooling (like needrestart or OS-provided notifications) to know when a manual reboot is required after updates.

* **Fail2Ban Intrusion Prevention:** Fail2Ban will actively monitor logins (by default, SSH auth failures) and ban offending IPs by modifying firewall rules (in Debian/Ubuntu, this typically means inserting iptables/nftables rules). This dramatically improves security against brute-force attacks. The security implication is mostly positive: malicious actors get locked out after a few attempts. But misconfiguration can lead to *accidental DoS* of legitimate users (including yourself). It’s crucial to maintain the whitelist (`ignoreips`) for admin or monitoring addresses. Also, consider that Fail2Ban’s banning uses firewall rules – if your server relies on a specific firewall setup, ensure Fail2Ban’s actions align with it (by default it uses its own chain and doesn’t conflict with UFW or firewalld, but it’s something to keep in mind).

* **ClamAV Antivirus:** Installing ClamAV adds malware scanning capability to the server. This can catch viruses or malware in files (for example, on file servers or user upload directories). The ClamAV daemon (if enabled) will run with elevated privileges to read files, and regularly update signature databases. Security considerations: ClamAV itself runs under a dedicated low-privilege user (`clamav`) for scanning, and its signatures are updated securely from the ClamAV servers. There’s minimal risk introduced by ClamAV, but be aware that if ClamAV finds infected files, you need a process to handle those alerts/quarantine. Also, an outdated ClamAV (if not kept updated) could give a false sense of security – the role ensures freshclam is installed so definitions stay current. ClamAV does open a local socket (for clamd service) but it is not exposed to external network by default.

* **User Accounts and Access:** The Base role itself does **not create or remove user accounts** (aside from the system accounts created by package installations like `clamav` and `Debian-exim` for mail if any). It does not modify SSH authorized keys or sudoers aside from what the bootstrap role ensures (installing sudo). So it doesn’t directly alter user access. However, note that the separate **SSHD role** (if you choose to use it in conjunction) *would* harden SSH (e.g., disable root login, etc.). By default Base leaves SSH settings unchanged. If you require root login to be disabled or other SSH hardening, refer to the SSHD role (see below) or configure those settings in your sshd config outside of this role.

* **No Firewall by Default:** As noted, Base doesn’t turn on a firewall. This means all ports that are open pre-role remain open post-role. Security-wise, this role doesn’t restrict network access (beyond Fail2Ban blocking certain IPs). It’s recommended to implement firewall rules (manually or via an Ansible role) to complement the Base role for a defense-in-depth strategy. The commented dependency on UFW indicates that it was considered, but it’s not active; thus, ensure your server’s ports are managed according to your organization’s security policy.

In summary, the Base role is geared towards **reinforcing security** (through updates, hardening measures, and monitoring) while maintaining system stability. Always review the changes, especially on sensitive systems, and adjust variables (like whitelists or update behaviors) to align with your security requirements.

## Cross-Referencing

This repository contains other roles that complement or relate to the Base role. Depending on your needs, you might want to use or consider these in conjunction with Base:

* **[remove_unnecessary_packages](../remove_unnecessary_packages/README.md)** – *(Dependency of Base)* This role is called by Base to purge unneeded packages. It can be run independently if you want to customize the package removal list for your environment. (For example, you might extend it to remove GUI packages on a server.)

* **[update_system](../update_system/README.md)** – *(Dependency of Base)* Handles updating all system packages. This is essentially the “apt upgrade” step. It’s included in Base, but you could use it separately for maintenance tasks or adjust its behavior (it could be extended to reboot if needed).

* **[sshd](../sshd/README.md)** – This role configures the OpenSSH daemon. While the Base role installs Fail2Ban for SSH protection, it does not alter SSH settings themselves. The **SSHD** role can be used to harden SSH configuration (for example, disable root login, change SSH port, restrict ciphers/MACs, etc.). Use this role alongside Base if you require custom SSH server settings.

* **[configure_filebeat_os](../configure_filebeat_os/README.md)** – This optional role sets up Filebeat to ship system logs to an external Elasticsearch/ELK stack. It’s not enabled by default in Base, but if you have a central logging system, you can apply this role to forward auth logs, syslog, etc. (Base ensures your logs are there and Fail2Ban monitors them, but this would get them off the box for analysis).

* **UFW (Uncomplicated Firewall)** – *Note:* While not currently an active role in the repository (it was planned via `oefenweb.ufw` but commented out), if you need host-based firewalling, consider enabling a UFW role or another firewall role from Ansible Galaxy. This would complement Base’s security by restricting network ports as needed. (For instance, you might allow SSH and HTTP/HTTPS and deny all else.)

* **Other application roles** – After the Base role has been applied, you would proceed with roles like **PostgreSQL**, **Apache NiFi**, **Minio**, etc. (all present in this repository). The Base role’s state (up-to-date system with basic security) is assumed by those roles. For example, [postgresql](../postgresql/README.md) will rely on the OS being prepared (and it even can leverage `postgresql_configure_firewall` if you integrate with a firewall role). Check each role’s documentation for any assumptions; Base is usually a prerequisite for them in a full playbook run.

Each of the above roles has its own README and documentation. Refer to those links for details on usage and how they interact with the Base role. By combining the Base role with these specialized roles, you can achieve a robust, secure, and maintainable infrastructure playbook.

