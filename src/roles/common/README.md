# Ansible Role: Common

*Ansible role for basic system setup on Debian/Ubuntu systems, focusing on package management prerequisites.*

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

The **Common** role ensures a host has essential base packages and updates needed for other roles to run smoothly. It primarily updates the system’s package index (APT cache) and installs a set of common system utilities and libraries. This includes Python tooling (like **python3-venv** and **python3-pip**) and packages required for secure package management (such as **apt-transport-https**, **ca-certificates**, and **gnupg**). By doing so, the Common role prepares the system for operations like adding new APT repositories or installing Python packages in later roles.

In practice, you would include this role at the beginning of your playbooks to bootstrap a server with fundamental capabilities. For example, updating the APT cache ensures the latest package information is available (so subsequent package installations won’t fail due to missing index data). Installing pip and venv means other roles can reliably use Python package modules or create virtual environments. In short, **Common** provides a minimal baseline, enabling other specialized roles to assume these basic tools are present.

## Supported Operating Systems/Platforms

This role is designed for **Debian-based** Linux distributions, particularly recent Debian and Ubuntu releases. It uses the APT package manager, so only systems with APT are supported. The role has been used on the following OS versions (matching those tested in this repository):

* **Debian**: 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu**: 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian/Ubuntu-derived distributions are likely compatible, since the tasks are generic. **Non-APT systems (e.g., Red Hat/CentOS)** are not supported by this role without modification. The tasks assume the presence of the `apt` module and Debian-family packaging; on those other systems the role will fail. Ensure your inventory targets are running one of the supported Debian/Ubuntu versions to use Common.

## Role Variables

<details><summary>Click to see default role variables.</summary>

*(None defined)* – This role does not define any default variables in `defaults/main.yml`. All operations (APT cache update and package list) are hard-coded for simplicity. There are no user-configurable knobs provided by this role out-of-the-box.

</details>

## Tags

This role does not define any custom Ansible tags. All tasks in **Common** run whenever the role is invoked (they are not tagged for selective runs). In other words, there is no need to specify tags to trigger or skip parts of this role – its two tasks always execute by default.

## Dependencies

**None.** The Common role has no external role dependencies and relies only on Ansible built-in modules. It uses the core `apt` module for package management, which is part of Ansible’s default battery (no additional collections or Galaxy roles are required). As long as you have Ansible’s standard modules and a Debian-based OS, you can run this role without any special setup.

*(For completeness: the repository’s `requirements.yml` does list some collections like `community.general`, but those are not specifically needed for Common. This role’s functionality is fully self-contained.)*

## Example Playbook

Here is a minimal example of how to use the `common` role in a playbook to prepare all hosts:

```yaml
- hosts: all
  become: yes  # Run with privilege escalation to perform package installs
  roles:
    - common
```


In the above example, we run **Common** on **all hosts** with `become: yes` because updating packages requires root privileges. No additional variables are set because the role operates with its built-in defaults. Simply including the role will update the APT package cache and install the common dependencies on each target host. Typically, you would run this role at the start of a play, before roles that configure specific applications, to ensure the system is ready for them.

## Testing Instructions

This role comes with a Molecule test scenario to verify its functionality in a containerized environment. We use **Molecule** (with the Docker driver) and **Testinfra** for assertions. To test the Common role:

1. **Install Molecule and prerequisites:** Ensure you have Molecule and its dependencies installed on your control machine. For example, use pip: `pip install molecule[docker]`. Also install Docker (for running containers), and Python testing tools like `pytest` and `testinfra` (Molecule will leverage these for verification).

2. **Prepare environment (dependencies):** The Common role has no external role dependencies, so you don’t need to install any Galaxy roles for it. However, it’s good practice to install required Ansible collections for the repository if you haven’t already (e.g. run `ansible-galaxy collection install -r requirements.yml` to cover any needed collections). This ensures all modules used elsewhere are available. (For Common itself, all needed modules are built-in, so this step is mostly informative.)

3. **Run Molecule tests:** From the repository root (where the `molecule/` directory is located), execute Molecule with the Common scenario:

   ```bash
   molecule test -s common
   ```

   This will launch the Common role’s Molecule test sequence. Under the hood, Molecule will:

   * Spin up a fresh Docker container (using a Debian-based image, e.g. Debian 12) as the test instance.
   * Apply a test playbook that includes the **common** role (converge step). This will run the role tasks inside the container.
   * Verify the results using Testinfra. For example, it will check that the expected packages (python3-venv, pip, apt-transport-https, etc.) were successfully installed on the container, and that the apt cache was updated. (Testinfra might do this by querying package managers or checking versions.)
   * Finally, destroy the test container, cleaning up the environment.

4. **Review outcomes:** Check the Molecule output for any failures. A successful run should end with a message indicating all assertions passed (e.g., “OK” or similar) and no tasks failed. If something did fail – for instance, if a package wasn’t found or a task had an error – you can rerun in debug mode. Use `molecule converge -s common` to apply the role without destroying the container (so you can inspect it), and/or `molecule verify -s common` to run the tests again on an existing converge. You can even enter the container with `molecule login -s common` to troubleshoot interactively.

Running these tests helps ensure that changes to the role don’t break expected behavior. Contributors should run the Common role’s Molecule test scenario after making modifications to confirm everything still works as intended.

## Known Issues and Gotchas

* **Debian/Ubuntu only:** As noted, this role will fail on systems that don’t use APT. If you accidentally target a RedHat-based host (or anything without apt), the tasks will not execute properly. Ensure your inventory is filtered to Debian-family hosts when using Common.

* **Internet access required:** The Common role expects to reach package repositories to update and install packages. If your servers have no internet access, make sure you have an internal package mirror or proxy configured (and that the apt sources list is pointed to it). Without access to a valid APT repository, the tasks in this role will hang or fail.

* **Apt cache is time-limited:** The **Update apt cache** task uses a cache validity period of 3600 seconds (1 hour). This means if the apt cache was refreshed less than an hour ago, Ansible will skip downloading indexes again. Generally this is fine (it reduces unnecessary network calls), but be aware that re-running the role within an hour may not fetch new package lists. If you need to force an update sooner, you might have to run `apt-get update` manually or wait until the cache time expires.

* **No package upgrades performed:** Common does **not** upgrade existing packages; it only installs the specific packages listed. Any available updates for other packages on the system are just fetched to the cache, not applied. This is by design – the role is kept lightweight. However, it means your system could still have outdated packages after running Common. For comprehensive patching, consider running the **Base** role or another update mechanism. Don’t assume a system is fully up-to-date security-wise just because Common ran (it only updated the package index).

* **Python interpreter requirement:** The target hosts need to have Python 3 available for Ansible to run the **apt** module. In most Debian/Ubuntu installations Python is present, but on minimal base images (or containers) it might not be. If Ansible cannot find a Python interpreter on the host, it will fail before Common can do anything. In such cases, you may need to bootstrap Python on the host (for example, by using the `raw` module to install `python3`). The **Base** role includes an automatic Python installation step (using `robertdebock.bootstrap`), so using Base is one way to handle this. If you are only using Common, ensure Python is installed or use a bootstrap step beforehand.

* **APT daily auto-updates conflict:** On Ubuntu/Debian, the system’s unattended-upgrades or apt-daily service might run in the background and lock the apt database. If you run the Common role at the same time, you could occasionally see apt tasks fail due to a lock. A workaround is to either disable those automatic apt timers when running Ansible or simply retry after a short wait. This is a rare timing issue, but worth noting if you encounter apt lock errors.

## Security Implications

Security-wise, the Common role makes minimal changes to the system, mostly positive or neutral:

* **No new network services:** This role does not start any persistent services or open any ports. It installs packages like Python venv and pip, which are tools and libraries, not network daemons. There is no impact on firewall or listening services after running Common.

* **Credential and user management:** Common does not create or alter user accounts, groups, or credentials. It doesn’t touch SSH configuration or sudoers. Your system’s user access policies remain unchanged by this role (aside from the requirement to run it as root for installation tasks).

* **Secure package installation:** By ensuring **apt-transport-https** and **ca-certificates** are present, the role enables the system to fetch packages over HTTPS and to validate TLS certificates for package repositories. This is a security improvement, as it helps protect against man-in-the-middle attacks on package downloads. Similarly, installing **gnupg** means the host can import and use GPG keys to verify package signatures. In summary, Common readies the system for **secure APT operations** (which is important when you add external repositories or keys in subsequent roles).

* **Software source trust:** The role itself only installs packages from your configured apt sources. It’s assumed those sources are official or trusted repositories. The installed packages (pip, venv, etc.) are standard components from the OS vendor. Ensure your apt sources list is pointing to legitimate repositories (e.g., official Debian/Ubuntu mirrors). The Common role will implicitly trust those sources when updating the cache and installing packages.

* **Pip availability:** Having **pip** on the system can be a double-edged sword: it’s a powerful tool that can install any Python package, including potentially unvetted third-party software. Simply installing pip doesn’t pose a direct security risk, but **usage** of pip should be done cautiously (e.g., install packages from trusted indexes only). In the context of this role, pip is provided for convenience and for other roles to use; it does not auto-install any Python packages on its own. Make sure that any subsequent Ansible roles or users that invoke pip adhere to your organization’s security guidelines for software installation.

In conclusion, the Common role by itself does not harden or weaken the system appreciably – it mostly sets the stage for other roles. It improves the ability to securely manage packages (HTTPS and signature verification for APT) and ensures essential tools are present. There are no known negative security impacts from running it. Administrators should still follow up by applying actual security patches (upgrades) and other hardening (firewall, user restrictions) via appropriate roles or playbooks, since Common doesn’t address those areas.

## Cross-Referencing

This repository contains other roles that relate to baseline system setup, which you may consider using alongside or instead of **Common** depending on your needs:

* **[Base](../base/README.md)** – A comprehensive initialization role that goes beyond Common. The Base role performs full system upgrades, removes bloat, and configures security features (automatic updates, Fail2Ban, ClamAV, etc.). If you desire a hardened and fully updated system, you might use Base rather than Common (or even run Base after Common in some cases). Base includes its own prerequisites handling (like ensuring Python is installed) and might make running Common unnecessary, though Common can still be used to guarantee pip and other tools are in place. See the Base role’s documentation for a complete overview of system hardening tasks it performs.

* **[remove_unnecessary_packages](../remove_unnecessary_packages/README.md)** – *(Internal dependency of Base)* This role removes predefined unnecessary packages (games, obsolete utilities, etc.) from the system to reduce attack surface. Common does not remove any packages, so if you are not using the full Base role but still want to clean out junk, you can run this role separately. It’s a simple way to ensure legacy or unused packages (like **telnet** or **ftp** clients) are purged from your servers.

* **[update_system](../update_system/README.md)** – *(Internal dependency of Base)* This role handles upgrading all system packages to the latest versions (essentially an `apt upgrade`). If you want to apply outstanding updates to your OS packages, consider using this role. Common by itself only updates the package index, but **update_system** will actually install the available upgrades. This can be run periodically or as needed to keep servers patched, in scenarios where you don’t run the full Base role.

* **[sshd](../sshd/README.md)** – This role configures SSH server settings for better security (for example, disabling root login, enforcing strong ciphers/MACs, etc.). The Common role does not touch SSH configuration at all. If you need to harden SSH on your hosts, use the SSHD role in addition to Common. In the Base role scenario, Fail2Ban is used to protect SSH, but SSHD goes a step further by locking down the SSH daemon’s settings. It’s a recommended role to apply for production environments requiring strict SSH policies.

* **[apt_mirror](../apt_mirror/README.md)** and **[apt_mirror_client_setup](../apt_mirror_client_setup/README.md)** – These roles help manage local APT package mirrors. If your environment restricts direct internet access, you can use **apt_mirror** to create an internal mirror of Debian/Ubuntu repositories, and **apt_mirror_client_setup** to point servers to that mirror. Common will benefit from this because the `apt update` and package installs will then draw from your local mirror. In offline or high-security environments, combining Common with the apt_mirror roles allows package management to work without external connectivity.

*Other roles in this repository* – After preparing the system with Common (or Base), you would typically run application-specific roles (database, web server, etc.). For instance, roles like **PostgreSQL**, **Minio**, **Apache NiFi**, **Vault**, **Amundsen** (and many more here) assume the system has basic tools installed and updated. The Common role ensures that foundation is in place. Always refer to each role’s README for any additional assumptions or requirements. Using Common as the first step helps unify those prerequisites across all your servers.
