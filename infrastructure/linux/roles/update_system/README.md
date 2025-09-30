# Ansible Role: Update System

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

The **Update System** role ensures a server’s operating system packages are fully up-to-date. It refreshes the package index and upgrades **all system packages** to their latest available versions (essentially performing an apt full-upgrade on Debian/Ubuntu systems). By applying this role, you bring a host to the latest patch level, which is often one of the first steps in server provisioning or maintenance. This role is commonly included early in playbooks (with elevated privileges via `become: yes`) so that subsequent roles work on a patched, up-to-date system. It can be used independently for routine maintenance or as part of a larger setup (for example, the [Base](../base/README.md) role uses **Update System** as a dependency to handle OS package updates).

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian** and **Ubuntu** Linux distributions:

* **Debian**: 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu**: 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian-based systems similar to the above releases are likely compatible. The role relies on the `apt` package manager, so non-APT based systems (e.g., Red Hat Enterprise Linux, CentOS) are **not supported** without modifications. Ensure you run this role on a supported OS to avoid errors. (If you need a system update on RHEL/CentOS, consider using the `dnf`/`yum` modules or a different role specific to those platforms.)

## Role Variables

<details><summary>Click to see default role variables.</summary>

| Variable                         | Default Value | Description |
| -------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`update_system_upgrade_type`** | "full"      | Type of upgrade to perform. "full" (the default) will do a *dist-upgrade*, allowing installation or removal of packages if required (ensuring kernel and major updates are applied). You can set this to "safe" to do a conservative upgrade (no new packages or removals, equivalent to `apt upgrade`) if you wish to avoid kernel or core changes. |
| **`update_system_autoremove`**   | `false`       | Whether to automatically remove obsolete packages after the upgrade. If `true`, the role will run an `apt autoremove` to clear out packages that were installed as dependencies and are no longer needed. By default this is `false` to retain those packages (you may run cleanup later or use the **remove_unnecessary_packages** role separately). |

</details>

*Note:* Generally, no other variables need to be set for this role to run. The above defaults are defined in **`infrastructure/linux/roles/update_system/defaults/main.yml`** and can be overridden if necessary (e.g., in an inventory or playbook). Typically you would only change these if you have specific policies about the types of upgrades or post-upgrade cleanup.

## Tags

This role does not define any custom Ansible tags. All tasks run whenever the role is invoked (no tasks are skipped by default).

* **Required tags:** *None.* There are no mandatory tags attached to tasks in this role – it will execute in full whenever included in a play.
* **Optional tags:** *None specific to this role.* (You can, however, apply your own tags at the role inclusion level if you need to control when this role runs. For example, in a playbook you might include the role with a tag like `system_update` and then use `--tags system_update` or `--skip-tags system_update` as needed.)

## Dependencies

**No role dependencies.** This role is self-contained and does not require any other Ansible roles to function. It uses the built-in **`apt`** module to perform package management, which is part of Ansible’s core modules. There is no need for additional Ansible collections or Galaxy roles when using **Update System** on Debian/Ubuntu hosts.

However, the following prerequisites and considerations apply:

* **Package manager availability:** The target hosts must have the APT package manager (which is standard on Debian/Ubuntu). The role will fail on systems without apt.
* **Internet access:** Ensure the target host can reach its package repositories (internet or local mirror) to download updates. If the host is behind a proxy or offline, configure APT accordingly before running this role.
* **Privileges:** You should run this role with escalated privileges (`become: yes`), since updating system packages requires root permissions.

*(If using this role as part of a larger playbook, note that the repository’s base configuration might install some upstream roles or collections. For example, the Base role suggests use of `unattended-upgrades` via variables, and comments mention roles like **robertdebock.bootstrap** or **auto_update**, but those are optional and not strictly required for this role to run.)*

## Example Playbook

To use the **Update System** role in your playbook, include it in the roles list for the relevant hosts. A minimal example is below, which updates all packages on target hosts. In practice, you might run this during a maintenance window or at the start of a provisioning playbook:

```yaml
- hosts: all
  become: yes  # Ensure privilege escalation for system updates
  roles:
    - role: update_system
      vars:
        update_system_autoremove: true  # Optional: remove outdated packages after upgrade
```

**Usage notes:** In the above example, `become: yes` is used because installing packages requires root permissions. We override `update_system_autoremove` to `true` as an example, so that after upgrading packages, the system will clean up any orphaned dependencies. You can omit the `vars` section entirely if you’re happy with the defaults (which means perform a full upgrade and do not auto-remove packages). After running this role, it’s good practice to reboot the server if a kernel or low-level library was updated (since changes won’t fully take effect until reboot, see [Known Issues](#known-issues-and-gotchas)).

## Testing Instructions

This role includes a **Molecule** test scenario to verify its functionality in a containerized environment. You can run the tests to ensure the role works as expected on a fresh system. Follow these steps to test **Update System** using Molecule:

1. **Install Molecule and Docker:** Ensure you have Molecule installed (`pip install molecule[docker]`) and Docker running on your local machine. Molecule will use Docker containers to simulate target hosts. Also install testing frameworks if needed (`pip install pytest testinfra`) as Molecule uses them for verifications.

2. **Navigate to the repository root:** The Molecule scenarios are defined in the repository (under the `molecule/` directory). From the project’s root folder (where the `molecule/` directory is located), run the Molecule tests for this role.

3. **Run the Update System scenario:** Execute the following command to run the Molecule test scenario for this role:

   ```bash
   molecule test -s update_system
   ```

   This will build a temporary Docker container (using a Debian-based image such as Debian 12) and apply the **Update System** role inside it. Molecule will perform the following steps:

   * Launch a container and prepare it (if any additional setup is needed).
   * Apply the role’s tasks to the container (this is the **converge** phase, using a test playbook that includes the `update_system` role).
   * Run verification tests (using **Testinfra** or similar) to assert that the system has been updated. For example, it may check that no packages are marked as upgradeable after the role runs, indicating the system is fully updated.
   * Destroy the container.

4. **Check the results:** If the role ran successfully, Molecule will conclude with an "OK" status after running the checks, and then it will tear down the test container. If there were failures (e.g., the container still had pending updates, or a task exited with an error), Molecule will report which step failed. In case of failure, you can rerun `molecule converge -s update_system` to just apply the role and then use `molecule login -s update_system` to open a shell in the container for troubleshooting.

By testing with Molecule, you validate that updates install correctly in a clean environment and that the role doesn’t introduce errors. This is especially useful when modifying the role or applying it to new OS versions. (Each role in this repository is intended to be testable in isolation with Molecule, ensuring reliability across updates.)

## Known Issues and Gotchas

* **Full system upgrade impact:** This role upgrades **all** packages on the system to the latest versions. While this is usually desirable for security, be aware that on running servers it may trigger restarts of services or daemons (for example, upgrading the kernel, OpenSSL, or SSH may restart those services). It’s best to schedule this role’s execution during a maintenance window for production environments to avoid unexpected disruptions. Always verify critical services after running updates to ensure they restarted properly or to catch any configuration changes needed.

* **No automatic reboot by default:** The **Update System** role **does not** automatically reboot the server after applying updates. If a kernel or other critical system component was updated, you will need to reboot the machine manually (or as a separate step in your playbook) to fully apply those updates. In other words, the role will install a new kernel, but that new kernel won’t be in use until a reboot occurs. Plan for this in your workflow. If you desire automatic reboots after updates, you might combine this role with an explicit reboot task or use unattended-upgrades with its reboot feature enabled (note: by default, the repository’s Base configuration leaves automatic reboots off).

* **APT package prompts:** In rare cases, upgrading packages might prompt for user input (for example, if a new version of a package has a changed configuration file). The Ansible `apt` module by default runs apt in non-interactive mode with safe defaults (generally keeping existing configs), so manual intervention is typically not needed. Just be mindful if you have packages that normally require input during `apt upgrade` – test those scenarios or pre-seed debconf answers if necessary.

* **Use on correct OS families:** As noted, attempting to run this role on a non-Debian based system will fail (because the `apt` module won’t be available or appropriate). Ensure your inventory’s hosts are indeed Debian/Ubuntu family before including this role. You can guard the role with a condition like `when: ansible_os_family == "Debian"` if you run a heterogeneous environment.

* **Repository connectivity and locks:** The update process can fail if the package repository is unreachable or if another process is holding the apt database lock. If you encounter apt lock errors, ensure no other apt processes (like unattended-upgrades or manual apt runs) are running at the same time. For repository issues, verify network connectivity or mirror availability. It may be useful to run `apt-get update` manually to debug repository problems outside of Ansible.

## Security Implications

Keeping system packages updated is a fundamental security practice. Many software updates include patches for known vulnerabilities, so regularly applying updates significantly reduces the risk of compromise. By using this role to keep your servers current, you’re plugging security holes as fixes become available, which helps protect against exploits targeting outdated software.

That said, consider the following security-related points when using **Update System**:

* **Privileges and trust:** This role operates with root privileges (via `become`). It will make sweeping changes to the system’s software. It’s crucial to run it only on trusted hosts and with trusted playbooks. Also, ensure your package sources (APT repositories) are secure and official – you wouldn’t want to install updates from an untrusted source. Always maintain proper repository GPG keys and sources lists so that you only pull updates from vetted channels.

* **No new services or ports opened:** The role does not open any network ports, create new user accounts, or alter firewall settings. It strictly upgrades existing packages. Therefore, it does not directly introduce new network exposure. (Indirectly, however, upgraded services might change their behavior or default settings – it’s wise to review release notes of critical services when major updates occur.)

* **Post-update integrity:** After updates, especially large ones, verify that security services are still functioning as intended. For example, if you have intrusion detection or firewall software, ensure they are still enabled and rules intact post-upgrade. In general, updating should not disable any services (in fact, it often patches them), but a quick check can provide peace of mind.

In summary, applying system updates via this role **enhances security** by ensuring the latest fixes are applied, but it should be done in a controlled manner. Always test updates in a staging environment if possible, and monitor your systems after an update run. The act of updating is safe and recommended; just pair it with good operational practices (backups, maintenance windows, and post-update testing) to mitigate any unforeseen issues.

## Cross-Referencing

This role is often used in combination with other roles in the repository to form a complete system baseline. Notably:

* **[Base](../base/README.md)** – The Base role is a high-level role that includes **Update System** as a dependency (among others) to perform baseline setup. When you run the Base role, it will automatically call *update_system* to upgrade packages (as well as other tasks like removing junk packages, configuring security tools, etc.). In other words, Base orchestrates this role as the “apt upgrade” step of system hardening. If you are using the Base role, you usually do not need to run Update System separately (though you can, for maintenance tasks).

* **[remove_unnecessary_packages](../remove_unnecessary_packages/README.md)** – This complementary role removes unwanted or unnecessary packages from the system (for example, default games, old network utilities like telnet, etc.). It’s often run **before** updating the system, so that you aren’t upgrading packages you don’t need in the first place. In the Base role’s execution order, *remove_unnecessary_packages* is invoked prior to *update_system*. Using both roles together ensures you first clean out superfluous packages and then upgrade the remaining necessary packages to latest versions.

*(For completeness, you may also want to look at roles like **SSHD** for securing SSH settings, or a firewall role (UFW) for locking down ports, as these aspects are not handled by Update System. Those are covered by other roles and can further strengthen your system when used alongside keeping packages updated.)*

Each role in this repository has its own README documenting its purpose and variables. By combining **Update System** with the roles above (and others, such as security and application roles), you can achieve a robust and secure server configuration. Remember that **Update System** focuses solely on package updates – for a full hardened setup, consider it as one piece of the puzzle, to be used with baseline hardening (Base role), package removal, firewall rules, and so on as needed.
