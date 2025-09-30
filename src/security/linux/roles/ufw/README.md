# Ansible Role: UFW

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
* [Cross-References](#cross-references)

## Overview

The **UFW** role installs and configures the Uncomplicated Firewall (**ufw**) on target Linux hosts. It provides a simple host-based firewall with a default deny-all inbound policy, allowing only explicitly permitted traffic. In practice, this role performs the following key actions:

* **Install UFW Package:** Ensures the UFW package is present on the system (using apt on Debian/Ubuntu).
* **Enable Logging:** Turns on UFW logging (`low` level by default, equivalent to "on") so that firewall events are recorded.
* **Allow SSH by Default:** Optionally allows incoming SSH (port 22, service **OpenSSH**) to prevent locking out remote access (enabled by default via `ufw_allow_ssh: true`).
* **Allow Additional Ports:** Allows any extra ports or port ranges defined in `ufw_allow_ports` (e.g. HTTP/80, HTTPS/443) for inbound traffic.
* **Allow Trusted Interfaces:** If any network interfaces are listed in `ufw_allow_interfaces`, permits **all** traffic in on those interfaces (useful for trusted internal or loopback traffic).
* **Enable Firewall with Deny Policy:** Activates UFW (ensuring it’s enabled on boot) and sets the default inbound policy to **deny**, blocking all unsolicited traffic not explicitly allowed.
* **Start UFW Service:** Starts and enables the UFW firewall service to enforce the rules immediately and persistently.

All tasks are designed to be **idempotent** – running the role multiple times should yield the same firewall state, only applying changes as needed. The role focuses on managing UFW’s state and rules; it does not modify kernel parameters or other firewall systems (like iptables directly). By applying this role, you can quickly impose a secure default firewall stance on your servers, only opening what you specify and closing everything else.

```mermaid
flowchart TD
    A[Install UFW package(s)] --> B[Enable UFW logging]
    B --> C{ufw_allow_ssh true?}
    C -- Yes --> D[Allow SSH (OpenSSH)]
    C -- No --> D
    D --> E[Allow each port in ufw_allow_ports]
    E --> F[Allow all traffic on each interface in ufw_allow_interfaces]
    F --> G[Enable UFW (deny inbound)]
    G --> H[Start & enable UFW service]
```

## Supported Operating Systems/Platforms

This role is tested on and intended for **Debian-family Linux distributions**, specifically:

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian/Ubuntu derivatives that use `apt` for package management will likely work as well. The role uses the `apt` module to install packages, so **Red Hat/CentOS, Fedora, or other non-APT-based systems are not supported** without modification. Ensure your target hosts are running a supported OS with the `ufw` package available in the repositories. Running the role on an unsupported OS (or without `apt`) will result in failures.

> **Note:** UFW (Uncomplicated Firewall) is primarily found on Debian-based systems. If you need a firewall on RHEL/CentOS, consider using roles for `firewalld` or `iptables` instead, as this role will not function on those systems.

## Role Variables

Below is a list of variables used by the role, along with default values (defined in **`defaults/main.yml`**) and descriptions:

<!-- markdownlint-disable MD033 -->

<details><summary>Role Variables (defaults)</summary>

| Variable                   | Default Value     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| -------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`ufw_packages`**         | `[ "ufw" ]`       | List of package(s) to install for UFW. By default, it includes only the **ufw** package, which provides the firewall on Debian/Ubuntu systems. You can override this list if you need to install additional related packages or a custom UFW version.                                                                                                                                                                                                                            |
| **`ufw_allow_ssh`**        | `true`            | Whether to allow SSH traffic (port 22, OpenSSH) through the firewall. If `true`, the role will create a rule to allow incoming SSH connections. It is highly recommended to keep this enabled (default) unless you have an alternate means of remote access, otherwise enabling the firewall could lock you out. Set to `false` only if you explicitly want to block SSH or if SSH is not needed on the host.                                                                    |
| **`ufw_allow_ports`**      | `[]` (empty list) | List of additional incoming ports (or port ranges) to allow. Each entry in the list should be a port number or range (e.g. `80` for HTTP or `6000:6100` for a range). The role will create an allow rule for each specified port (using TCP by default). This is useful for permitting application-specific ports (web, database, etc.). **Note:** Removing a port from this list will **not** automatically close that port if it was previously opened (see **Known Issues**). |
| **`ufw_allow_interfaces`** | `[]` (empty list) | List of network interface names from which to allow all traffic (incoming). If specified, the role will create allow rules for all incoming packets on each given interface. For example, you might include `lo` to ensure all loopback traffic is accepted, or an internal interface like `eth1` if you trust all traffic on that network. **Important:** Use actual interface identifiers (e.g. `"eth1"`, `"ens3"`, `"lo"`); do not list protocols (such as "tcp") here.       |

</details>

<!-- markdownlint-enable MD033 -->

You can override these variables in your playbook or inventory to customize the firewall configuration. For instance, to allow HTTP and HTTPS traffic you might set `ufw_allow_ports: [80, 443]`. If your SSH daemon runs on a non-standard port, set `ufw_allow_ssh: false` and add that port number to `ufw_allow_ports` so you don’t lose SSH access. All default values are defined in the role’s **defaults/main.yml** for easy reference.

## Tags

This role defines a minimal set of Ansible tags for selective execution of tasks:

* **`package`** – Applied to the task that installs the UFW package(s). Use this tag if you want to run *only* the installation step or, conversely, skip installing packages when the role executes (e.g., by using `--skip-tags package` if UFW is already installed).

No other custom tags are used within this role’s tasks. All configuration and enablement tasks will run by default when the role is invoked. (You may, however, apply your own tags at the play or role inclusion level if you need to group this role’s execution with other tasks.)

*Note:* You might notice a tag named **`usw`** in the role’s task file – this appears to be a minor typo and can be ignored. It does not correspond to any meaningful label and isn’t used elsewhere. The primary tag of interest is **`package`** as described above.

## Dependencies

**Collections:** This role relies on the **community.general** Ansible Collection for the `ufw` module it uses to manage firewall rules. Ensure that `community.general` (version 8.6.0 or higher) is installed before running the role (it is listed in the repository’s requirements.yml). You can install it via Ansible Galaxy if needed:

```bash
ansible-galaxy collection install community.general
```

**Roles:** There are no hard role dependencies defined in this role’s metadata – it does not require any other role to function. It can be used on its own. However, it is often used alongside a “base” role or other service roles (see [Cross-References](#cross-references)) to complete system setup.

**System Packages:** The UFW package itself is the only system requirement, and this role takes care of installing it. The target host should have a working package manager (APT) and internet access or a local repository to fetch the package. If running on a fresh system, it is advisable to update the APT cache (this role’s apt task includes `update_cache: true` to handle that automatically).

## Example Playbook

Here is a simple example of how to use the `ufw` role in a playbook, including some variable overrides to open common service ports:

```yaml
- hosts: webservers
  become: yes  # Ensure privilege escalation for firewall changes
  vars:
    ufw_allow_ports:
      - 80    # HTTP
      - 443   # HTTPS
  roles:
    - ufw
```

In the above example:

* We target a host group `webservers` and use `become: yes` because modifying firewall settings and installing packages require root privileges.
* We override `ufw_allow_ports` to include ports **80** and **443**, which will allow HTTP and HTTPS traffic through the firewall. (SSH is allowed by default via `ufw_allow_ssh`, so we don’t list port 22 here.)
* We then include the **ufw** role. This will install UFW (if not already installed), enable logging, allow SSH (default), allow the specified HTTP/HTTPS ports, set the default policy to deny other inbound traffic, and ensure the firewall is enabled and running.

You can adapt this pattern for other groups of hosts and ports. For example, database servers might open port 5432 for PostgreSQL, or you might disable `ufw_allow_ssh` on a bastion host that doesn’t need SSH access. Typically, you will include this role early in your playbook run (after basic system prep) so that the firewall is configured before or alongside deploying networked applications.

## Testing Instructions

This role includes a Molecule test scenario to verify its functionality using containers.

1. **Install Molecule and dependencies:** Make sure you have Molecule installed (`pip install molecule[docker]`) and Docker available on your system. You’ll also need **pytest** and **testinfra** (Molecule will use these for assertions). If not already set up, install them via pip as well.

2. **Prepare Ansible collections:** Ensure the required Ansible collections are installed, especially `community.general` for the UFW module (as noted in Dependencies). If you have this repository’s `requirements.yml`, run `ansible-galaxy collection install -r requirements.yml` to get dependencies. This step ensures the Molecule environment can use the `community.general.ufw` module.

3. **Run Molecule tests:** From the repository root (where the `molecule/` directory is located), execute the following command to run the UFW role’s test scenario:

   ```bash
   molecule test -s ufw
   ```

   This will launch the **ufw** Molecule scenario. Under the hood, Molecule will:

   * Build a fresh Docker container (typically using a Debian base image) with necessary dependencies.
   * Run the role inside the container (Molecule’s *converge* step), applying a test playbook that includes the `ufw` role with some test variables.
   * Execute verification steps (Molecule’s *verify* step) using **Testinfra**. These tests will check that UFW is installed, the service is enabled/active, and that the expected firewall rules are in effect (for example, that port 22 is allowed, that the default policy is denying other ports, etc.).
   * Finally, destroy the test container, unless you specify otherwise.

4. **Review results:** Check the output of the Molecule run. A successful test run should end with “**OK**” status for all assertions and report no failed tasks or tests. If a task fails or a test assertion is not met, the output will indicate what went wrong. In case of failures:

   * You can re-run the convergence step alone for debugging with `molecule converge -s ufw` (this applies the role without destroying the container, so you can inspect the state).
   * Use `molecule login -s ufw` to open a shell inside the test container. From there you might run commands like `ufw status` to manually verify the firewall status, or check logs, etc.
   * Adjust the role or test as needed, then repeat `molecule test -s ufw` until it passes.

Running the Molecule tests is a good way to ensure that changes to the role don’t break expected functionality. All contributors are encouraged to run these tests before committing changes. The Molecule scenario (configuration in `molecule/ufw/`) provides a reproducible environment to validate that the role works as intended on a clean system.

## Known Issues and Gotchas

* **Firewall rule removal is not automatic:** This role **only adds or enables rules**; it does not remove previously existing UFW rules that are no longer desired. For example, if you allowed a port (by including it in `ufw_allow_ports`) and later remove it from the list, UFW will still have that rule from the earlier run. Ansible’s UFW module does not automatically delete rules when they disappear from variables. To close a port that was once opened, you must either manually remove the rule (e.g. using `ufw delete allow <port>` or using the module with `delete: true`), or do a full reset of UFW rules. Plan accordingly if you change firewall requirements over time.

* **Default SSH rule and custom SSH ports:** By design, `ufw_allow_ssh: true` opens the standard SSH port 22 (using UFW’s predefined “OpenSSH” application profile). If your server’s SSH daemon listens on a non-standard port, the default rule won’t cover it. In that case, set `ufw_allow_ssh: false` and add your custom SSH port number to `ufw_allow_ports`. Otherwise, you could end up in a situation where UFW is enabled but your SSH port isn’t allowed – causing a lockout from the server. Always double-check that at least one management access method (SSH or other) is permitted by the firewall before enabling it on a remote host.

* **`ufw_allow_interfaces` usage:** Be careful to specify actual network interface names in `ufw_allow_interfaces`. This variable is intended to whitelist all traffic on given interfaces (e.g., `["lo"]` to allow all local loopback traffic, or an internal interface like `["eth1"]`). If you mistakenly put protocol names or other values here (for example, `"tcp"` is **not** an interface), the task will not fail but also will not do anything useful. Misconfiguration can lead to a false sense of security or openness. Use interface allows sparingly and only for interfaces that are fully trusted (as it opens them completely).

* **Ansible tag typo (`usw`):** As noted in the Tags section, the UFW package installation task is tagged `package` but also has an unintended tag `usw`. This appears to be a typo (likely meant to be `ufw`). This has no effect on the role’s operation unless you explicitly target tags. If running the role with tags, use `package` (or no tags) – do not use `usw` as it’s not an intended tag. This minor issue may be corrected in a future update of the role.

* **Concurrent firewalls or existing rules:** This role assumes UFW is the primary firewall mechanism on the host. If another firewall service (such as **firewalld** or custom iptables rules) is active, they may conflict with UFW. It’s recommended to use only one firewall service at a time. Before enabling UFW, ensure other firewall services are disabled or that you understand the interaction (in many cases, installing UFW on Debian/Ubuntu will disable **iptables-persistent** or other scripts, but it’s best to verify). Also, if UFW was previously enabled on the system with a different set of rules, this role will not purge those existing rules on its own (aside from resetting UFW if it’s completely uninstalled and re-installed). To start fresh, you might need to run `ufw reset` manually (be cautious: that will disable the firewall until re-enabled).

* **Use in containers or virtualization:** UFW manipulates low-level firewall settings (netfilter/iptables). Running this role inside Docker containers or unprivileged LXC containers might not work unless the container is privileged, as the UFW commands may require kernel capabilities that are restricted. In testing scenarios (e.g., Molecule’s Docker containers), the container is typically given necessary privileges or a custom image (with UFW pre-installed) is used. If you attempt to use this role in a lightweight container environment and encounter issues, this is likely why. Consider using network policies or host-level firewalls in those cases, or adjust the container security settings.

## Security Implications

Enabling UFW on your servers can significantly improve their security posture by reducing the attack surface, but it must be used thoughtfully:

* **Default-deny inbound:** By default, once this role enables UFW with a **deny** policy, any port not explicitly allowed will be blocked from incoming connections. This is a secure stance (closing unexpected access), but make sure you have allowed everything necessary for the system’s function. It’s wise to review all the services running on the host and ensure their ports are listed in `ufw_allow_ports` (or otherwise permitted) if they need to be reachable. Anything not allowed will be effectively cut off to external clients.

* **Maintaining access:** The most critical service to consider is SSH (or whichever method you use for remote administration). The role defaults to allowing SSH on port 22, which is crucial for not losing connectivity. If you change this (for example, disable `ufw_allow_ssh` or move SSH to a different port), double-check that you have an alternative way in or have added the new port. Whenever possible, apply firewall changes during a maintenance window or while you have console access, in case you need to revert quickly.

* **Limited outbound filtering:** UFW by default allows all outgoing traffic and this role does not alter that. That means services on the host can initiate connections to any external host. In most cases this is acceptable (e.g., for downloading updates, contacting APIs, etc.), but be aware that if the server is compromised, malware could freely connect out to an attacker’s system. If your security policy requires restricting egress (outgoing connections), you would need to manually add UFW rules to deny or limit outgoing traffic, or use additional tooling — this role focuses only on inbound access control.

* **Logging and auditing:** UFW’s logging (turned on by this role) will record blocked and allowed connections in syslog (typically under `/var/log/ufw.log` or `/var/log/kern.log` depending on setup). This is useful for auditing and intrusion detection – you can monitor these logs to see if someone is repeatedly probing your server on blocked ports. However, be mindful that in high-traffic scenarios, logging every blocked connection can generate a lot of log data. You may want to adjust UFW’s log level or ensure log rotation is in place. By default, the log level is set to “on” (which is low detail) by this role, which is a good balance for most uses.

* **Allowing entire interfaces:** If you use `ufw_allow_interfaces` to trust an interface, you are effectively disabling firewall restrictions on that interface. This can be convenient for internal network traffic (e.g., between backend servers on a private LAN or cluster interconnects), but it also means if that network is compromised, those packets aren’t filtered. Treat this like creating a “trusted network zone.” Only add interfaces that connect to networks you fully trust. For example, it’s common to allow all traffic on the loopback interface (`lo`) because it’s entirely local, and perhaps on an internal management interface that isn’t exposed publicly. Use this feature sparingly and with awareness of what’s on that network.

* **Application security still required:** UFW is a layer of defense, but it doesn’t secure the services themselves. Even if a port is allowed, ensure the service listening on that port has proper security (up-to-date patches, secure configuration, authentication where appropriate, etc.). For example, if you open port 3306 for MySQL, make sure MySQL itself has a strong root password and perhaps is configured to only accept certain hosts. Firewall rules can prevent opportunistic attacks, but any allowed traffic will go to the service – so that service must be configured securely as well.

* **Testing changes carefully:** Any time you adjust firewall rules, test connectivity to the allowed services from a client perspective. For instance, if you opened a new port, try connecting to it from another host to verify it’s reachable. Conversely, if you intended to block something, ensure it’s actually blocked. It’s easy to make a mistake in rule definitions, so validate in a staging environment or with safe commands. Keep in mind that UFW rules take effect immediately. Plan firewall activations for times when a misconfiguration will have minimal impact, and have a rollback plan (for example, an Ansible task to disable UFW in an emergency, or console access).

In summary, this role can significantly harden a host by limiting network access. It implements a classic firewall strategy: **“deny by default, allow by exception.”** This is a powerful approach, but requires that you explicitly define all needed access. When used carefully, it greatly reduces the exposure of services and helps protect against network-based threats. Just ensure to maintain the rules over time as the server’s role changes (adding new services or decommissioning old ones) so that the firewall policy always aligns with the host’s intended accessibility.

## Cross-References

The **ufw** role is often used in combination with other roles in this repository, especially those that set up networked services. Here are some relevant roles and how they relate:

* **Base role** – The base system hardening role (common setup) does **not** include firewall configuration. If you use the **base** role to update and secure your servers, consider adding the **ufw** role as well to enable a firewall layer. The Base role covers package updates, Fail2Ban, etc., but defers firewall tasks to a dedicated role for flexibility.

* **OpenLDAP Server role** – The OpenLDAP role installs an LDAP server which listens on ports 389 (LDAP) and 636 (LDAPS). By default, it does *not* open those ports in any firewall. The OpenLDAP documentation explicitly recommends using the **ufw** role to allow LDAP traffic. In practice, you can set `ufw_allow_ldap: true` and `ufw_allow_ldaps: true` in your inventory (as shown in the OpenLDAP group vars) and include this **ufw** role in your playbook. This will ensure ports 389 and 636 are permitted for LDAP clients. Without it, an enabled UFW would block LDAP, so pairing these roles is essential for an LDAP deployment with a firewall.

* **apt_mirror role** – This role sets up a local APT package mirror and typically serves content over HTTP (port 80). The apt_mirror role itself doesn’t configure any firewall rules. If you are running UFW on the mirror server, you should open port 80 (and 443 if you choose to serve via HTTPS) using this **ufw** role (e.g., set `ufw_allow_ports: [80, 443]` for that host or host group). This will allow your clients to reach the mirror. The apt_mirror documentation advises ensuring the mirror’s port is accessible through firewalls; the **ufw** role is the way to achieve that in this repository’s context.

* **Keycloak role** – The Keycloak identity server by default runs on port 8080 (HTTP). The Keycloak Ansible role does not manage firewall settings, so if UFW is enabled you must manually allow Keycloak’s port. Using this **ufw** role, you can open port 8080 by setting `ufw_allow_ports: [8080]` for the Keycloak host. This will let users access the Keycloak service. (In production, you might use a proxy and SSL on 443, but those ports too would need to be allowed.) The Keycloak documentation notes that you should ensure the service port is reachable through your firewall – again, the **ufw** role is how to implement that.

* **HAProxy role** – For load balancer setups, the HAProxy role installs HAProxy which typically listens on ports 80/443 (and possibly a stats port like 9000). Like others, it doesn’t open firewall ports for you. If you have UFW enabled on your load balancers, remember to allow the listening ports. For example, assign `ufw_allow_ports: [80, 443, 9000]` on those hosts when using the **ufw** role. This ensures that client traffic can reach HAProxy and that you can access the stats interface if needed (preferably binding the stats to localhost or securing it, as the HAProxy docs warn).

These are just a few examples. In general, whenever you use a role that exposes a network service (database, web application, cache, etc.), you should consider whether you need to open a port in the firewall for it. The **ufw** role can be included alongside those roles to centrally manage those openings. Many roles in this repository include notes in their READMEs about firewall considerations; you can search those for "UFW" or "firewall" to identify what ports might need opening. By combining the **ufw** role with your service roles, you ensure that each service is not only installed and configured, but also properly accessible (or restricted) at the network level according to your security needs.
