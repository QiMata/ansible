# Ansible Role: Remove Unnecessary Packages

*Ansible role to remove unnecessary default packages from Debian/Ubuntu systems as part of system hardening and baseline cleanup.*

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

The **Remove Unnecessary Packages** role purges predefined, unwanted packages from a system to minimize bloat and potential security risks. It targets legacy or insecure utilities – by default **“games,” “ftp,” and “telnet”** – which are generally not needed on servers. Removing these extraneous packages helps reduce the server’s attack surface and enforces a leaner OS installation appropriate for production environments. This role is typically run early in a setup or hardening process (often as part of a base configuration) to perform an initial cleanup of the system.

In practice, this role simply uses the system package manager to **uninstall the specified packages**. On Debian/Ubuntu hosts, it will iterate over the list of unnecessary packages and remove each one via apt. By eliminating utilities like FTP and Telnet (which transmit data in plaintext and are considered insecure), the role ensures such tools aren’t accidentally left available on your servers. The result is a cleaner baseline – any software not explicitly required is removed, so you can start with a minimal, hardened system before adding your necessary services.

## Supported Operating Systems/Platforms

This role is designed for **Debian**-family Linux distributions and has been tested on the following platforms:

* **Debian**: 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu**: 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian/Ubuntu-derived releases are likely compatible as long as they use the APT package manager. The role uses the Ansible `apt` module for package management, so **non-APT based systems (e.g., RHEL, CentOS)** are **not supported** without modification. Attempting to run this role on a Red Hat or other yum/dnf-based OS will fail, since the tasks assume an apt environment. Ensure your inventory targets are running a supported Debian/Ubuntu version to use this role successfully.

## Role Variables

The **`remove_unnecessary_packages_list`** variable defines which packages will be removed. This is a list that can be customized as needed. By default it includes “games”, “ftp”, and “telnet.” You can override this list to add or remove package names based on your environment’s needs (for example, to purge GUI utilities on a server or other unwanted packages).

| Variable                               | Default Value                | Description                                                                                                                                    |
| -------------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **`remove_unnecessary_packages_list`** | `["games", "ftp", "telnet"]` | List of packages to remove during initial cleanup. By default, it removes legacy or insecure utilities (games, ftp, telnet) that are generally not needed on servers. |

*(See the role’s `defaults/main.yml` for the source of these defaults. You can override this variable in your playbook or inventory to change which packages get purged.)*

## Tags

This role does not define any custom Ansible tags for its tasks – all tasks will run whenever the role is invoked (they are not selectively tagged). In other words, there are no built-in tags to include or skip parts of this role.

* **Required tags:** None (all tasks run unconditionally when you run the role).
* **Optional tags:** None (the role’s tasks are not subdivided by tags, though you may apply your own tags at the role include level if needed).

## Dependencies

**None.** This role has **no external dependencies** on other roles or collections. It relies only on Ansible built-in functionality (specifically the core `apt` module) to perform package removals. As long as you have Ansible’s standard modules available and are targeting a Debian-based system, you can use this role without any additional Galaxy role installs or collection requirements.

*(For reference: the repository’s global `requirements.yml` does list some community collections like `community.general`, but **none** are needed or used by this particular role. The tasks here are fully self-contained.)*

## Example Playbook

Here is a simple example of how to use the `remove_unnecessary_packages` role in a playbook to clean up a host:

```yaml
- hosts: all
  become: yes  # Ensure privilege escalation to remove packages
  roles:
    - remove_unnecessary_packages
```

In the above example, we run **Remove Unnecessary Packages** on **all hosts** with `become: yes` because uninstalling packages requires root privileges. No additional variables are set here, so the role will use its default package list (removing “games”, “ftp”, and “telnet”). Simply including the role as shown will attempt to purge those packages on each target host. Typically you would run this early in your play (for example, right after basic host preparation) to make sure any default bloatware or insecure utilities are gone.

*If you need to customize the removal list, you can override `remove_unnecessary_packages_list` in your play or inventory. For instance, you might add other packages that are unwanted in your environment. This role can be extended to remove any package you consider unnecessary – e.g., you could include desktop GUI packages when provisioning a server with a GUI pre-installed.*

## Testing Instructions

This role comes with a **Molecule** test scenario to verify its functionality in a containerized environment. We use Molecule (with the Docker driver) and **Testinfra** for assertions. To test the Remove Unnecessary Packages role, follow these steps:

1. **Install Molecule and prerequisites:** Ensure you have Molecule and its dependencies installed on your control machine. For example, use pip: `pip install molecule[docker]`. You will also need Docker installed (since the tests use containers), and Python testing tools like **pytest** and **testinfra** (Molecule will invoke these for verification).

2. **Prepare the environment:** This role has no external Galaxy role dependencies, so you don’t need to install any additional roles. However, it’s recommended to install the required Ansible collections for this repository if you haven’t already (for example, run `ansible-galaxy collection install -r requirements.yml` to ensure all needed modules are available). While the Remove Unnecessary Packages role itself only uses built-in modules, having the collections from `requirements.yml` installed ensures a consistent test environment for any shared library needs.

3. **Run Molecule tests:** From the root of the repository (where the `molecule/` directory is located), execute the role’s Molecule test scenario with the following command:

   ```bash
   molecule test -s remove_unnecessary_packages
   ```

   This will launch the Molecule test sequence for the **remove_unnecessary_packages** scenario. Under the hood, Molecule will:

   * **Spin up a container:** It will create a fresh Docker container (using a Debian-based image, e.g. Debian 12) as the test instance.
   * **Apply the role (converge):** Molecule runs a test playbook that includes the **remove_unnecessary_packages** role, applying all of its tasks inside the container.
   * **Verify results:** After convergence, Molecule (via Testinfra) will check that the expected changes occurred. For example, it will ensure that the packages listed in `remove_unnecessary_packages_list` (e.g. **telnet** and **ftp**) have indeed been removed from the container. The verification may involve checking that those packages are no longer installed (e.g., using `dpkg` queries or ensuring the binaries are absent).
   * **Destroy the container:** Finally, Molecule will clean up by destroying the test container, returning the environment to its initial state.

4. **Review outcomes:** Observe Molecule’s output for any failures. A successful run should end with all tests passing (look for output indicating something like “OK” or no failed assertions) and no Ansible task failures. If something does fail – for example, if a package wasn’t removed as expected or an apt operation error occurred – you can troubleshoot using Molecule’s debug capabilities. Run `molecule converge -s remove_unnecessary_packages` to rerun the role without tearing down the container (allowing you to inspect the container’s state), and then `molecule verify -s remove_unnecessary_packages` to re-run the tests on the existing container. You can also use `molecule login -s remove_unnecessary_packages` to open a shell inside the container for manual investigation.

Running these tests helps ensure that changes to the role (or updates to the environment) don’t break the expected behavior. Contributors should execute the Remove Unnecessary Packages Molecule test scenario after making modifications to the role, to confirm everything still works as intended.

## Known Issues and Gotchas

* **Debian/Ubuntu only:** As noted above, this role will **fail on systems that don’t use APT**. If you accidentally target a Red Hat/CentOS or another non-Debian host, the tasks will not run properly (the `apt` module won’t be available). Always ensure your inventory for this role consists of Debian-based hosts. If you need similar functionality on other distributions, you would have to modify the role to use the appropriate package manager (e.g., `yum`/`dnf` for RHEL systems).
* **APT lock contention:** The role’s apt removal task is wrapped in a retry loop to handle cases where the apt database is locked by another process. For example, if unattended upgrades or apt daily maintenance is running, the initial removal attempt might fail due to a lock. The role will retry up to 10 times with a short delay, which usually allows time for the lock to clear. However, if another process holds the lock for an extended period (or hangs), the role may still ultimately fail after all retries. In such cases, you may see an error on the final attempt. Ensure that no long-running apt processes (or package managers like `dpkg`) are active when running this role, or consider temporarily disabling auto-updates during provisioning to avoid conflicts.
* **Valid package names:** Be careful when customizing `remove_unnecessary_packages_list` to include additional packages. All names in the list should correspond to real packages in the OS’s package index. If you specify a package name that **does not exist** or is misspelled, apt will error out (“Unable to locate package X”) and the role will fail. Similarly, if a package name exists but isn’t applicable to your OS version, the apt task could fail. Double-check package names (using commands like `apt-cache search` or consulting documentation) before adding them to the list. Using the defaults provided (games, ftp, telnet) on supported OS versions should not produce errors, as those are known package names on Debian/Ubuntu.
* **Minimal installations (no packages to remove):** On a minimal base image of Debian/Ubuntu, it’s possible that none of the default packages (games, ftp, telnet) are installed in the first place. In such a case, this role will effectively do nothing (apt will report that there is “nothing to remove” or that those packages are not installed). This is normal – the role will simply complete with zero changes. If you find that to be the case and you still want to use this role, you can repurpose it by overriding the `remove_unnecessary_packages_list` with packages that *are* present and unwanted in your environment. For example, on a server that accidentally has some GUI or extras installed, you might list those here to purge them. The role is safe to run even if the list is already absent; it will just skip removals that aren’t needed.

## Security Implications

* **Reduces attack surface:** Removing obsolete clients like **Telnet** and **FTP** has positive security benefits. These protocols transmit data (including credentials) in plaintext and are considered unsafe on modern systems. By purging them (and other unnecessary packages), this role helps ensure that administrators or users won’t inadvertently use insecure tools, and it eliminates software that could be potential vectors for exploits. In short, fewer unnecessary services/binaries on the system means fewer avenues for attackers to target.
* **No new services or ports opened:** This role **does not install or start any services**, nor does it open any network ports. In fact, it may indirectly *close* potential avenues of attack (for instance, if an FTP or Telnet server package were installed and running, removing it would also stop that service). The role makes only removals, so it doesn’t introduce new network-facing components or persistent processes. This keeps the security posture either neutral or improved – there are no additional services that would require monitoring or patching.
* **Privilege requirements:** The role’s tasks run with **elevated privileges** (`become: yes`), since uninstalling packages touches the system state and requires root access. This is expected for any system maintenance action. Ensure that only trusted automation or users run this role with sudo/become rights, as with any Ansible role that makes system changes. The role itself does not create or modify user accounts, credentials, or file permissions – it strictly removes software – so there are no direct changes to account security or permissions on the system beyond the removal of the packages themselves.

## Cross-Referencing

This repository contains other roles that are related to system baseline management and can complement **Remove Unnecessary Packages** in your playbooks:

* **[Base](../base/README.md)** – *(Meta-role for baseline setup)* The Base role is a comprehensive initialization role that **calls the Remove Unnecessary Packages role as its first step** during system provisioning. Base goes beyond just removing packages – it performs full system upgrades, configures security tools (like unattended upgrades, Fail2Ban, ClamAV), and sets other baseline settings. If you use the Base role, you don’t need to run *remove_unnecessary_packages* explicitly (Base will include it automatically). See the Base role’s documentation for a complete overview of the baseline hardening tasks it performs.
* **[Update System](../update_system/README.md)** – *(Internal dependency of Base)* This role handles upgrading all system packages to their latest versions (essentially performing an `apt upgrade` on the host). It is typically run immediately *after* Remove Unnecessary Packages as part of the base hardening sequence. You can use **update_system** on its own to apply OS package updates during maintenance windows or in playbooks where you want to ensure the system is fully patched. (In the Base role, this runs automatically following the removal of unnecessary packages.)
* **[Common](../common/README.md)** – This role installs fundamental packages and updates the package index on Debian/Ubuntu systems, preparing a host for further configuration. Unlike the Base role, **Common** is a lightweight bootstrap: it updates APT caches and installs basic tools (like Python 3, `apt-transport-https`, CA certificates, etc.) but **does not remove** any packages or perform upgrades. If you choose not to use the full Base role, you might use Common to do initial setup and then run *remove_unnecessary_packages* separately to strip out unwanted packages (since Common by itself leaves them untouched). In summary, Common ensures the system has the prerequisites and package index updated, while Remove Unnecessary Packages can be run alongside it to clean the system of default bloat. (You may then follow with Update System to apply upgrades, if needed.)

Each of the above roles has its own documentation in this repository. Refer to those READMEs for more details on usage and how they interact with the baseline configuration. By combining the **Remove Unnecessary Packages** role with these related roles (or using the Base role which encompasses them), you can achieve a robust and secure initialization of your servers, setting the stage for application-specific roles to be applied on a clean, up-to-date system.

