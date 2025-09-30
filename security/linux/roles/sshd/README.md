# Ansible Role: Sshd

*Ansible role to install and harden the OpenSSH server (sshd) on Linux hosts.*

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

The **SSHD** role installs and configures the OpenSSH daemon on target servers. It ensures that the SSH service is present, running, and configured according to recommended settings for secure remote access. By applying this role, you can enforce consistent SSH configuration across your hosts – for example, controlling which network interface and port the daemon listens on, whether password logins are permitted, and other security-related options. This helps standardize SSH setups and reduce the risk of misconfiguration or weak defaults.

In practice, this role performs a few key actions to set up SSH on a host:

* **Install OpenSSH Server:** Ensures the OpenSSH server package (`openssh-server`) is installed via the system package manager (APT on Debian/Ubuntu).
* **Deploy Secure Config:** Templates a hardened SSH **server configuration** at `/etc/ssh/sshd_config`, applying settings defined by role variables (e.g. listen address, authentication methods).
* **Restart SSH Service:** Restarts (or reloads) the `sshd` service to apply the new configuration (via an Ansible handler).

```mermaid
flowchart TD
    subgraph "SSHD Role Tasks"
    A[Install OpenSSH Server<br/>(openssh-server package)] --> B[Apply sshd_config Template<br/>(with secure settings)]
    B --> C[Restart sshd Service<br/>(apply new config)]
    end
```

This role focuses on **SSH server configuration** rather than user management. It will not create users or manage SSH keys – those should be handled separately. Typically, you would include **SSHD** in your playbooks to harden SSH **after** basic system prep. For example, you might run a base setup role (updating packages, adding users) first, then apply **SSHD** to lock down SSH settings to your desired security level. This role can be used to implement policies such as disabling direct root login, changing the default SSH port, or restricting cryptographic ciphers/MACs for compliance requirements.

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian**-family Linux distributions. It uses the APT package manager, so only Debian/Ubuntu and their derivatives are supported out-of-the-box. Specifically, the role has been used on the following OS versions:

* **Debian**: 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu**: 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian/Ubuntu-like systems are likely compatible, since the tasks use standard Debian conventions. **Non-APT based systems (e.g., RHEL, CentOS, Fedora)** are *not supported* without modification. The role’s tasks assume the presence of the `apt` module and Debian-style paths; running on an unsupported OS will result in failures or incorrect behavior. Ensure your target hosts run one of the above supported versions before applying this role.

> **Note:** The OpenSSH server (`openssh-server`) package must be available via APT on the target system. All listed Debian/Ubuntu releases include this package in their default repositories.

## Role Variables

<details><summary>Click to see default role variables.</summary>

| Variable                  | Default Value                                        | Description                                                                                                                                                                                                                                                                                                                                         |
| ------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`sshd_listen_address`** | `{{ hostvars[inventory_hostname]['ansible_host'] }}` | IP address that SSHD should listen on. By default, this is set to the host’s primary IP as known to Ansible (the `ansible_host` for the inventory). This effectively binds the SSH daemon to that network interface only. Override this if you need a different bind address (e.g., `0.0.0.0` to listen on all interfaces, or another specific IP). |

</details>

If you need to customize additional SSH settings, you can override them via inventory variables or playbook `vars`. For example, the role looks at a dictionary `sshd` for certain settings (defined in group variables). By default, **password authentication is enabled** (`sshd.PasswordAuthentication: true` in the sample inventory) to allow SSH password logins. You can set `sshd.PasswordAuthentication: false` to disable password-based login and enforce key-based authentication (see **Security Implications** below). Similarly, other SSHD config options like `PermitRootLogin` or ciphers/MACs can be added to this dictionary or the template as needed (the role does not set these by default, so SSH will use upstream defaults or existing config for those).

## Tags

This role does not define any custom Ansible tags of its own. All tasks in **SSHD** run whenever the role is invoked (no tasks are tagged for selective execution). In other words, you don’t need to specify any special tags to include or skip parts of this role – its tasks will always run by default.

*(For consistency with your playbook’s tagging scheme, you may manually tag the role invocation in a play if needed. But internally, the role’s tasks are untagged.)*

## Dependencies

**None.** This role has no dependent roles and relies only on Ansible built-in modules. It uses core modules like `apt` (for package installation), `template`, and `systemd` – all of which are included in Ansible’s standard distribution. No external Ansible Galaxy roles are required.

**Ansible Collections:** No special collections are needed beyond the default **ansible.builtin**. (All tasks use either ansible-core modules or fully-qualified module names that come with Ansible by default.) Ensure you have a relatively modern version of Ansible that includes the `ansible.builtin` modules for apt and systemd.

**System Packages:** The role will install the **OpenSSH server** package (`openssh-server`) if it is not already present, using the system package manager (APT). The target hosts should have access to the appropriate package repository (e.g., internet or a mirror) so this installation can succeed. If the package is already installed, the role will skip the install step and simply manage the configuration.

## Example Playbook

Here is an example of how to use the `sshd` role in a playbook:

```yaml
- hosts: all
  become: yes  # Ensure privilege escalation for installing packages and editing /etc/ssh
  roles:
    - role: sshd
      vars:
        sshd_listen_address: "0.0.0.0"            # (Optional) Listen on all interfaces instead of a specific IP
        sshd:
          PasswordAuthentication: false           # Disable password authentication for SSH (keys only)
```

In the above playbook, the **SSHD** role is applied to all hosts. We elevate privileges with `become: yes` because modifying SSH configuration and restarting services requires root access. The example also demonstrates overriding two settings:

* Setting `sshd_listen_address: "0.0.0.0"` to make SSH listen on all network interfaces (by default it listens only on the primary interface IP).
* Setting `sshd.PasswordAuthentication: false` to disallow password logins, requiring SSH keys for all users.

These overrides will be applied when the role runs, resulting in an `/etc/ssh/sshd_config` that reflects the new values. If you omit the `vars` section, the role will use its defaults (listening on the inventory host IP and allowing password auth).

## Testing Instructions

This role includes a **Molecule** test scenario to verify its functionality in a containerized environment. We use Molecule with the Docker driver and **Testinfra** (Python-based server testing) for assertions. To run the tests for the **SSHD** role:

1. **Install Molecule and dependencies:** Make sure you have Molecule installed on your system (`pip install molecule[docker]`) along with Docker. You will also need `pytest` and `testinfra` for running tests. (Installing Molecule with the `[docker]` extra should pull in these dependencies, but you can `pip install pytest testinfra` if needed.)
2. **Provision role dependencies (if any):** The Molecule scenario will use the role as defined in this repository. There are no external role dependencies for **SSHD**, so you mainly need to have the repository content available. If the repository’s `requirements.yml` includes collections like `community.general`, install them before testing to avoid missing module errors (though the **SSHD** tasks themselves do not require those).
3. **Run Molecule tests:** From the repository root (where the `molecule/` directory is located), execute the following command:

   ```bash
   molecule test -s sshd
   ```

   This will launch the Molecule test sequence for the **SSHD** role. Under the hood, Molecule will:

   * Build a fresh Docker container (using a Debian-based image, e.g. Debian 12) to serve as a dummy target host.
   * Apply a test playbook that includes the **sshd** role to the container (the converge step). This will install OpenSSH and apply our sshd_config in the container.
   * Execute verification steps (using Testinfra) to validate that the role did what we expect. For example, the tests likely check that the `/etc/ssh/sshd_config` file exists and contains the configured directives (matching the default or overridden variables), that the SSH daemon is running and listening on the specified port, and that certain security settings are in effect (e.g., password authentication setting is as expected).
   * Finally, destroy the test container.
4. **Review results:** Observe Molecule’s output for any failures. A successful run will end with `OK` status for converge and verify steps and then clean up the container. If a test fails (for instance, if a configuration line was not applied correctly), you can use Molecule for debugging:

   * Run `molecule converge -s sshd` to just apply the role in the test container and leave it running. This lets you inspect the container manually.
   * Use `molecule login -s sshd` to open a shell inside the container. You can then check `/etc/ssh/sshd_config` or the status of the `sshd` service to diagnose issues.
   * Adjust the role or variables as needed, then re-run the tests until they pass.

The Molecule tests provide a safety net to ensure that changes to the **SSHD** role don’t break the expected behavior. Contributors should run these tests before committing changes to the role. The Molecule configuration for this role is defined in the repository (e.g. in `molecule/sshd/` scenario directory), which uses a Debian Docker image and basic Testinfra checks for SSH functionality.

## Known Issues and Gotchas

* **SSH Connection Loss During Changes:** Be cautious when applying this role to a system over SSH, especially if you are changing SSH settings that could cut off your connection. For example, if you **change the SSH port or disable root login/password authentication**, the current SSH session (and thus the Ansible run) might be interrupted when the SSH service restarts. Ansible will typically apply all tasks and then trigger the restart via a handler at the end, but the next time it needs to connect, it could fail if you haven’t adjusted your inventory or authentication. To avoid lockouts, plan such changes carefully:

  * If changing the port, update your inventory to use the new port **after** the playbook run, and ensure firewalls allow the new port (see below).
  * If disabling root login, **create and test a non-root user with sudo** (and key access) *before* applying the role. Switch your Ansible connection to use that user for subsequent runs.
  * If disabling password auth, make sure all necessary SSH keys are in place on the server beforehand. Losing access due to misconfiguration can require console or out-of-band access to fix.

* **Firewall Considerations (SSH Port):** If you use a firewall (e.g., the UFW role) on the host, remember that changing the SSH listening port means you must adjust firewall rules. The **UFW** role, for instance, by default allows port 22 (SSH). If you switch SSH to a non-standard port, you’ll need to allow that port in UFW or your firewall role, or you risk locking yourself out. Always coordinate port changes with firewall configuration updates.

* **Single-Interface Bind:** By default, the role’s configuration binds SSH to a single interface (the IP defined in `sshd_listen_address`). On multi-homed servers, this could mean SSH is *not* listening on other network interfaces. This is often desirable (to limit exposure), but it can be a gotcha if you expected access on multiple IPs. If your server has multiple network interfaces (e.g., private and public) and you want SSH available on all of them, set `sshd_listen_address: "0.0.0.0"` (or add additional `ListenAddress` lines via custom config) to ensure SSH listens on all addresses. Otherwise, the default behavior might unintentionally restrict SSH to one network.

* **IPv6 Not Enabled by Default:** The provided template sets `AddressFamily inet`, which restricts SSH to IPv4 only. This means the SSH daemon will **not listen on IPv6** addresses. If your environment requires IPv6 connectivity, you should adjust this setting (e.g., change it to `any` to support both IPv4 and IPv6, or specifically `inet6` for IPv6 only). Not enabling IPv6 by default is a conservative choice, but in a dual-stack network you’ll want to modify that or add a `ListenAddress` for `::0` as needed.

* **PermitRootLogin and Root Access:** The role’s default configuration does **not explicitly set** `PermitRootLogin` in the SSH config. Many Linux distributions default this to “prohibit-password” (permit root login only with keys) or “yes” in their stock SSH config. Since our template may replace the config entirely, omitting this directive means the SSH daemon might fall back to its compiled default (which could be permissive). Be aware of this if you need to guarantee root login is disabled. As a best practice, consider setting `PermitRootLogin no` for production systems (you can add this to the template or through an override). However, ensure you have an alternative admin user ready (as noted above) before disabling root access.

* **Overriding Defaults:** If you have previously modified the SSH configuration on a host manually, this role will overwrite `/etc/ssh/sshd_config` with the template. Any manual changes or OS default settings not captured by the template will be lost. This is expected behavior (infrastructure as code means we enforce a known config), but keep it in mind. If there are distribution-specific settings or banner text, etc., that you want to preserve, you should incorporate them via this role’s variables or template rather than editing the file manually after running the role.

* **Service Restart Caution:** Restarting SSHD will momentarily disconnect active SSH sessions. In automated runs, this is usually fine (Ansible will reconnect if possible). However, if the new SSH config has issues (e.g., a syntax error or unsupported option), the SSH daemon might fail to start. This would lock out SSH access entirely. While the Molecule tests help catch template syntax errors, it’s wise to roll out SSH changes in a controlled manner. Consider using `molecule` or a staging environment to test changes, and have an out-of-band method to access the server (cloud console, IPMI, etc.) in case the SSH service doesn’t come back up.

## Security Implications

Configuring SSH is a sensitive operation with direct security consequences. This role is aimed at strengthening the security of your SSH daemon, but how you choose to configure it will determine the actual security posture. Below are some important security considerations when using the **SSHD** role:

* **SSH Port Changes:** Changing the default SSH port (22) to a non-standard port can reduce automated attack noise (many bots target port 22). The role allows you to do this by editing the template or using a different listen port. However, **security through obscurity** has limits: determined attackers can scan all ports. If you do change the port, remember to inform all users/administrators of the new port, update any monitoring or management tools, and adjust firewall rules to allow traffic on the new port. *Never remove port 22 from the firewall allow-list until you have confirmed the new port works*, to avoid accidental lockout.

* **Password Authentication:** Allowing SSH password logins (`PasswordAuthentication yes`) is convenient but risky. It opens the door to brute-force attacks on user passwords. By default, this role leaves password authentication **enabled** (assuming you might need it initially), but for hardened security you should consider disabling it (`PasswordAuthentication no`) once you have set up SSH keys. Using key-based authentication vastly improves security, as keys are not susceptible to guessing in the way passwords are. If you disable password auth via this role’s variables, ensure every user who needs access has their public key installed on the server; otherwise they will be unable to log in.

* **Root Login:** Permitting direct SSH login as root is generally a bad practice. It’s better to require admins to log in as a normal user and then escalate (with sudo) – this provides accountability and an extra layer of protection. As noted, the role doesn’t override `PermitRootLogin` by default, so it may remain at the system default (which on many systems still effectively allows root login with keys). For improved security, you can set `PermitRootLogin no` (prevent root SSH login entirely) or `PermitRootLogin prohibit-password` (allow root with key only) in the SSH config. Implement this by adjusting the template or adding an extra line via this role. Keep in mind that if you disable root login, you **must** have an alternative way to become root (typically an admin user with sudo privileges). This change, when combined with disabling password auth, means root cannot log in via SSH at all – even with a password – which is often desirable in production.

* **SSH Ciphers and MACs:** By default, OpenSSH has a set of ciphers, key exchange algorithms, and MACs (message authentication codes) that it considers secure. The role’s template does not explicitly restrict these, meaning the system will use OpenSSH’s defaults. In some environments (due to compliance or policy), you might need to allow or disallow specific algorithms (for example, disabling older ciphers or enabling FIPS-approved ciphers only). If that’s the case, you should customize the sshd_config via this role to specify the `Ciphers`, `KexAlgorithms`, and `MACs` lines according to your requirements. This role can accommodate those settings (you could add variables and template entries), but be careful: removing too many algorithms could prevent some clients from connecting. Always test after making such changes.

* **Fail2Ban Integration:** While not part of this role, it’s worth noting that if you use the **Base** role in this repository, Fail2Ban is installed and configured to monitor SSH login attempts. Fail2Ban will ban IPs that have too many failed SSH logins, which greatly helps mitigate brute-force attacks if password auth is on (or even to protect against key-based auth guessing or other SSH exploitation attempts). Ensure that the SSH settings you apply via **SSHD** align with Fail2Ban’s expectations (by default, Fail2Ban watches auth logs for “Failed password” messages on port 22 – if you change the port or auth method, Fail2Ban should still catch failures, but you might need to adjust its jail configuration in advanced scenarios). Also, as mentioned in Base role docs, be cautious not to ban yourself – consider whitelisting your Ansible control machine’s IP in Fail2Ban ignore list if you do many login attempts.

In summary, **any change to SSH configuration can have major security (and accessibility) implications**. This role gives you a controlled way to implement those changes via code. Always review the settings you deploy, test them in a safe environment, and proceed gradually for critical systems. The default configuration provided by the role is a reasonable starting point for general use, but you should adjust it to meet your organization’s security policies.

## Cross-Referencing

This repository contains other roles that complement or relate to **SSHD** and overall SSH security. Depending on your needs, you may want to use these in conjunction with the **SSHD** role:

* **[base](../base/README.md)** – The Base role sets up general security baseline on servers. Notably, it installs Fail2Ban for SSH and other services (to prevent brute-force attacks), but it does **not** change SSH configuration itself. Pairing Base with **SSHD** is a common approach: Base will handle updates and intrusion prevention, while **SSHD** locks down the SSH settings (authentication, ports, etc.).

* **[ufw](../ufw/README.md)** – Configures the Uncomplicated Firewall. If you are restricting SSH to certain ports or networks, the UFW role can enforce those rules at the host firewall level. For example, UFW by default allows port 22 for SSH; if you move SSH to a different port or want to allow SSH only from specific IPs, you would adjust variables in the UFW role accordingly. Using **SSHD** in tandem with **UFW** helps ensure that your SSH service is not just configured securely, but also properly firewalled.

* **User Account Roles** – While this repository might manage users in an ad-hoc way (or via other roles), consider how you provision user accounts and SSH keys. Disabling root login and password auth (via **SSHD**) is most effective when each admin has their own user account with a public key. If you have a role or tasks for creating users and distributing authorized keys, run those **before** applying **SSHD** to avoid locking out administrators. (For example, you might first apply a “users” role that ensures an admin user exists with a key, then apply **SSHD** to turn off root login.)

* **Logging and Monitoring** – The Base role’s cross-references mention a *Filebeat* role for shipping logs. If you have central logging, including auth.log, it can complement **SSHD** by giving visibility into SSH access attempts across your fleet. Similarly, you might integrate with an IDS/IPS system or SIEM. While not directly part of **SSHD**, these integrations can enhance your security posture around SSH by alerting on suspicious login attempts or configuration changes.

Each of the above roles has its own documentation. Refer to those README files for details on usage and configuration. In practice, combining **SSHD** with the Base security role and a firewall role (and proper user management) will yield a much more secure SSH setup than defaults. This role is one piece of a broader security strategy – it specifically ensures the SSH daemon’s settings are as you intend them to be, and it should be used alongside other measures for defense in depth.
