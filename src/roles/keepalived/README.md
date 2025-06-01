# keepalived Ansible Role

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
* [Related Roles](#related-roles)

## Overview

This role installs and configures **Keepalived**, a service that provides high availability by using the Virtual Router Redundancy Protocol (VRRP) on Linux systems. In practice, Keepalived allows a group of servers to share a **virtual IP address** (VIP) so that if the primary server (Master) fails, a backup server can automatically take over the VIP, ensuring continued service availability. This role is typically used to create a highly available cluster of nodes for critical services (for example, a pair of load balancers using a floating IP).

When applied, the role will perform the following main functions:

* **Package Installation:** Installs the Keepalived software package on the target host (using APT for Debian-based systems).
* **Configuration:** Deploys a templated `/etc/keepalived/keepalived.conf` defining one VRRP instance. The configuration includes the virtual IP, network interface, VRRP router ID, priority, and authentication key as specified by role variables.
* **Service Management:** Ensures the `keepalived` service is enabled to start at boot and is currently running (and reloads/restarts the service if the configuration changes).

This role is designed to be **idempotent**. Running it multiple times will not change the system after the first run, unless you modify variables (for example, changing the virtual IP or interface will update the config and trigger a service restart via handler).

Below is a conceptual diagram of a two-node HA setup using Keepalived for failover:

```mermaid
flowchart LR
    subgraph Keepalived_VRRP_Cluster [Keepalived VRRP Cluster]
      direction TB
      A[Primary Server\n(MASTER)]
      B[Secondary Server\n(BACKUP)]
      A -- "VRRP Heartbeat" --> B
      B -- "VRRP Heartbeat" --> A
    end
    VIP[Virtual IP (Floating)]
    C[Clients]
    A == Holds VIP ==> VIP
    B -. Standby .- VIP
    C --> VIP
    %% The MASTER node owns the VIP and handles client traffic. If the MASTER fails, the BACKUP becomes MASTER and takes over the VIP.
```

In the diagram, the **Master** node (A) owns the **VIP** and handles traffic from clients. The **Backup** node (B) listens for VRRP heartbeats from the Master. If the Master goes down (heartbeats stop), B will assume the VIP and become the new Master, so clients continue to be served without changing the IP they contact.

## Supported Operating Systems/Platforms

This role is tested on and supported with the following Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** The target hosts must be Debian-based (APT package manager available). The role’s tasks use `apt` and are not currently designed for RedHat/CentOS or other non-Debian platforms. If you need to use Keepalived on those systems, you would have to extend this role (e.g. add `yum`/`dnf` tasks) or use a different role that supports them.

## Role Variables

Below is a list of important variables for this role, along with default values (defined in **`defaults/main.yml`**) and their descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                      | Default Value    | Description |
| ----------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`keepalived_package_name`** | `keepalived`     | Name of the OS package to install for Keepalived. In most cases this should remain `"keepalived"` (the official package in Debian/Ubuntu repositories). Change this only if you need a custom package name or a different version. |
| **`keepalived_service_name`** | `keepalived`     | Name of the Keepalived service (for managing with `service`/`systemctl`). This is typically `"keepalived"` on Debian/Ubuntu. It should match the service name provided by the OS package if it differs. |
| **`keepalived_state`**        | `BACKUP`         | Initial VRRP state of this node. Should be `"MASTER"` for the primary node and `"BACKUP"` for secondary/standby nodes. The MASTER node will own the virtual IP when healthy, while BACKUP nodes wait to take over if the master fails. **Default is BACKUP**, so you will typically override this to `"MASTER"` on one node in the cluster. |
| **`keepalived_priority`**     | `100`            | VRRP priority for this node (0-255). A higher number means higher priority to become or remain the MASTER. Ensure the intended MASTER has the highest priority value. By default this is 100 (suitable for a backup if the master is set higher, e.g. 150). Two nodes must not share the same priority if both are MASTER, to avoid ties. |
| **`keepalived_interface`**    | `eth0`           | Network interface on which to run VRRP. The virtual IP will be attached to this interface on the MASTER node. Default is `eth0`. **Change this to the appropriate interface name** on your servers (e.g. `"ens160"`, `"bond0"`, etc.) if not using eth0. |
| **`keepalived_router_id`**    | `51`             | Virtual Router ID (VRID) for the VRRP group. This is an identifier (0-255) that must be the same on all nodes in this Keepalived cluster. It **must be unique per network segment** – do not use a VRID that another cluster or device is using on the same VLAN. The default (51) is an example; you should set an ID that does not conflict with other VRRP deployments in your environment. |
| **`keepalived_virtual_ip`**   | `192.168.50.100` | The Virtual IP address that will be shared by the cluster. This IP will float to whichever node is MASTER. **Change this to the IP address you want to use for your service’s HA endpoint.** It should be in the same subnet as the `keepalived_interface` and not already in use. The default is a placeholder example. |
| **`keepalived_virtual_cidr`** | `32`             | CIDR prefix length for the virtual IP. This defines the netmask of the VIP. Default `32` means a single host address. For most use cases, `/32` is correct (the VIP is an individual address on an existing subnet). If your network requires a specific netmask (for example, if using an address in a /24 network and you prefer to configure it as such), you can adjust this. |
| **`keepalived_auth_pass`**    | `vrrp_secret`    | Authentication password for VRRP. Keepalived uses a simple clear-text password (auth type `PASS`) in its configuration by default. **You should override this with your own secret** in production. All nodes in the cluster must use the same password. The default `"vrrp_secret"` is not secure if left unchanged. *(Note: PASS authentication is meant to prevent accidental misconfiguration or unauthorized takeover in a shared network, but it is not encrypted traffic. For stronger security, Keepalived supports using IPSEC (AH) with an MD5 key, but that is beyond this role’s default setup.)* |

</details>

<!-- markdownlint-enable MD033 -->

## Tags

This role does **not define any Ansible tags** in its tasks. All tasks will run by default when the role is invoked. (You may still apply tags externally when including the role, if desired, to control when it runs as part of a larger playbook.)

## Dependencies

* **Ansible Version:** Requires Ansible **2.13** or higher. (The playbooks use updated Ansible idioms like `ansible_facts` and rely on modules available in modern Ansible releases.)
* **Collections:** None. All modules used (e.g. `apt`, `template`, `service`) are part of Ansible’s built-in modules. No external Ansible collections are required for this role.
* **External Packages:** No other Ansible roles or Galaxy collections are required. The Keepalived system package will be installed on the target host by this role. The target host needs to have a functioning package manager (APT) and network access to the package repositories. The role will automatically install the `keepalived` package (and its dependencies). Ensure that if you have a firewall or security policy, the host is allowed to install packages and later to exchange VRRP traffic (VRRP uses IP protocol 112 and multicast address 224.0.0.18 on the local network). There are no additional system services installed besides Keepalived itself.

## Example Playbook

Here is an example of how to use the `keepalived` role in a playbook for a two-node load balancer cluster. This playbook applies the role to all hosts in the `loadbalancers` inventory group. It sets a custom virtual IP and other parameters via variables (you could also put these in group_vars), and assumes you will mark one host as MASTER in its host-specific vars.

```yaml
- hosts: loadbalancers
  become: yes
  vars:
    keepalived_virtual_ip: "10.0.0.50"
    keepalived_virtual_cidr: 32
    keepalived_interface: "eth0"
    keepalived_router_id: 50
    keepalived_auth_pass: "mySuperSecretPass"
    # Note: Set keepalived_state and keepalived_priority in host_vars for each server:
    # e.g., host1 vars: keepalived_state: MASTER, keepalived_priority: 150
    #       host2 vars: keepalived_state: BACKUP, keepalived_priority: 100
  roles:
    - keepalived
```

In the above play, we configure Keepalived to use the virtual IP 10.0.0.50/32 on interface eth0 for all nodes in the `loadbalancers` group. We would designate one of those nodes as the MASTER by overriding `keepalived_state: MASTER` (and a higher `keepalived_priority`) for that host in the inventory or host_vars, while the other node(s) remain BACKUP with lower priority. This ensures the host marked MASTER will claim the IP, and the backup will take over if the master fails. The role will install keepalived and write the config accordingly on each node.

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to verify it works as expected before deploying to production:

1. **Install Molecule** and Docker on your development machine (e.g., `pip install molecule[docker]`). Ensure that Docker is running.
2. **Prepare a test scenario:** If a Molecule scenario is provided with this role (e.g. in `molecule/default/`), you can use that. Otherwise, you can initialize a new scenario for this role with:

   ```shell
   molecule init scenario -r keepalived -d docker
   ```

   This will create a default Molecule configuration using Docker containers.
3. **Run the role in a container:** Execute `molecule converge` to spin up a Docker container (by default using a Debian/Ubuntu base image) and apply the `keepalived` role to it. Molecule will run the playbook in `molecule/default/converge.yml` (or the scenario’s playbook) which should include this role.
4. **Verify the results:** After the converge step, check inside the container to ensure Keepalived was installed and configured. You can do:

   ```shell
   docker exec -it <container_id> /bin/bash
   ```

   Once inside, verify that `/etc/keepalived/keepalived.conf` exists and contains the expected settings (e.g. the virtual IP and router ID from your test vars). Also check that the Keepalived service is running: `systemctl status keepalived` (or `service keepalived status`) should show it as active. You can run `ip addr show <interface>` to see if the virtual IP has been assigned to the interface (if the container was the MASTER). If the role includes automated tests (e.g., with Inspec or Testinfra in a `verify.yml`), you can run `molecule verify` to execute those.
5. **Cleanup:** Run `molecule destroy` to tear down the test container when you are done testing. This will remove any containers and networks that were created for the test. (You can also run `molecule test` to perform the full cycle: create, converge, verify, destroy in one command.)

**Note:** When testing Keepalived in Docker, you may need to adjust the container privileges. Keepalived requires the ability to manipulate network interfaces to add the virtual IP. By default, Docker containers might not allow this. If you encounter errors adding the VIP, consider modifying the Molecule scenario to run the container in privileged mode or with NET_ADMIN capabilities (e.g., in `molecule.yml` set `privileged: true` for the instance, or add `cap_add: ["NET_ADMIN"]`). This will allow Keepalived inside the container to bind the VIP for testing purposes.

Using Molecule with Docker helps ensure the role is idempotent and works on a fresh system. During testing, you can adjust variables (like using a test virtual IP that is appropriate for the Docker network). Also, if testing a cluster scenario, you might use multiple containers or iterative converge runs to simulate MASTER/BACKUP nodes. Always destroy test environments after use to avoid interfering with your host or network.

## Known Issues and Gotchas

* **VRRP Traffic & Firewalls:** Keepalived uses VRRP which communicates via multicast and a dedicated IP protocol (number **112**). By default, VRRP advertises to the multicast address 224.0.0.18 on the local network. If your hosts have a firewall (e.g., ufw or iptables) or network policies, ensure that VRRP packets are allowed through. You may need to allow protocol 112 (and possibly multicast traffic on 224.0.0.0/24). If VRRP advertisements are blocked, the backup nodes will not receive heartbeats and may falsely assume the master is down, causing unexpected failover behavior.

* **Unique VRID Required:** The `keepalived_router_id` (VRID) must be unique per broadcast domain. Using the same VRID for two different clusters on the same VLAN will cause conflicts. For example, if another device or cluster is using VRID 50 on the same network and you also use 50, the two VRRP groups will interfere with each other’s elections and ARP announcements. Always choose a VRID that is not in use elsewhere on that network. (You can have up to 255 distinct VRRP groups in one LAN, numbered 0-255, but they all must have distinct IDs and VIPs.)

* **Initial State and Priority:** By default, this role sets nodes as BACKUP with priority 100. It’s important to configure one node to be MASTER (with a higher priority) for each VIP. If all nodes are left as BACKUP with equal priority, they will still elect a master among themselves (typically the one with the highest IP address or lowest MAC will become master if priorities tie), but this is not deterministic or intended. Ensure you explicitly set a primary node with a higher priority to control which node is master. Also note that Keepalived’s default behavior is **preemptive** – meaning if a higher-priority node (e.g., the intended master) comes online or recovers, it will take over as master again. This can cause the VIP to shift back after a failover. This is normal VRRP operation, but if you prefer non-preemptive failover (to avoid flapping, so that a backup that has taken over remains master), you would need to add `nopreempt` in the config manually – the provided template does not include that option by default.

* **Multiple VIPs or Instances:** This role’s template defines a single `vrrp_instance` (one virtual router/VIP). If you require multiple VIPs on the same hosts, the role would need modification (e.g., to allow defining multiple instances or running the role multiple times with different variables). As is, the role handles one HA virtual IP address. For most HA use-cases (like a single API endpoint or single service VIP) this is sufficient. If you need to advertise several IPs, consider either extending the template or creating additional VRRP instances with different IDs and config.

* **Multicast in Cloud Environments:** Some cloud networks and virtualized environments do not support multicast traffic, which VRRP relies on by default. For example, certain AWS, Azure, or OpenStack setups may drop multicast packets, preventing Keepalived from working out-of-the-box. In such cases, you may need to configure Keepalived in unicast peer mode (specifying the peer IPs instead of multicast). This role does **not** currently auto-configure unicast mode. If deploying in an environment where multicast VRRP is not viable, be prepared to customize the Keepalived configuration (e.g., by supplying a custom template that sets `unicast_peer` directives) or ensure your network can be configured to permit VRRP multicast between the instances.

* **Container/VM Networking:** If you run Keepalived inside containers or VMs, be aware of networking constraints. In containerized tests (as noted above), lack of NET_ADMIN capabilities can prevent adding the VIP. Similarly, in virtual machines or cloud instances, you might need to enable promiscuous mode or specific network permissions for the VIP to be moved or for ARP announcements to be honored by the hypervisor’s switch. For example, VMware and some cloud providers may require special settings to allow an instance to claim an IP address that is not its primary IP. This is not a limitation of the role per se, but a deployment consideration. Check your platform’s requirements for “floating IP” or “VIP” support.

## Security Implications

* **Root Privileges and Network Changes:** The Keepalived service runs with root privileges because it needs low-level access to networking. It will add or remove IP addresses on the interface and handle ARP announcements. Misconfiguration can therefore have network-wide effects. For instance, if an incorrect virtual IP is configured (one that conflicts with another device’s IP), Keepalived could cause IP address conflicts on the LAN. Similarly, using a VRID that another cluster uses could disrupt that cluster’s traffic. Always double-check that the VIP and VRID you configure are unique and correct for your network to avoid disrupting other systems.

* **VRRP Advertisements on the Network:** Keepalived will broadcast VRRP announcements (multicast) on your network. These advertisements include the VRRP group information and are sent periodically (by default every 1 second). In a normally trusted internal network, this is fine, but in an untrusted network segment, a malicious actor could potentially attempt to spoof these messages or become part of the VRRP election. The role’s configuration uses a password (simple authentication) to mitigate unauthorized takeover – only nodes with the correct `keepalived_auth_pass` will be accepted in the VRRP group. **However, note that this password is sent in plaintext within VRRP packets.** It is not encrypted or hashed in transit (it is just used to verify that messages come from a member of the group). This means an attacker sniffing the network could see the password if they can capture VRRP packets. For environments where security is a concern, consider using additional protections: for example, placing HA nodes in a dedicated VLAN that untrusted devices cannot access, or using IPSEC AH authentication for VRRP (Keepalived supports MD5 authentication for VRRP which provides cryptographic verification of messages). By default, this role does not enable the IPSEC/MD5 option.

* **Use of Default Credentials:** The default `keepalived_auth_pass` provided by this role (`vrrp_secret`) is meant as an example. **Do not use the default password in production.** If multiple clusters or devices accidentally use the same password and VRID on the same network, they could join each other’s VRRP group, which is dangerous. Always set a unique, hard-to-guess password for each HA cluster, especially if multiple teams or systems share a network.

* **Service Availability and Failover:** Introducing a virtual IP that moves between hosts can have security implications for client access. Ensure that any security groups, ACLs, or firewall rules account for the use of the VIP. For example, if the service behind the VIP (e.g., a web service via HAProxy) has firewall rules, those rules may need to allow traffic on the VIP address in addition to the real interface IPs. Also, if using stateful firewalls or cloud security groups, ensure both potential hosts of the VIP are allowed to send/receive traffic for that IP. From a security standpoint, treat the VIP as an alias of the primary node; any port that needs to be open on the primary should also be allowed on the secondary when it holds the VIP.

* **System Hardening and Reliability:** Running Keepalived means a new root-level daemon on your servers. As with any such service, keep it updated to receive security patches. The role installs Keepalived from the OS repository, which is generally maintained (for example, Debian/Ubuntu security updates). There are no known major security vulnerabilities in Keepalived in recent versions, but it’s good practice to monitor advisories. Additionally, restrict access to your servers such that only authorized users can modify Keepalived’s config or stop the service. Disrupting Keepalived (accidentally or maliciously) could cause a failover or loss of the VIP, impacting service availability.

In summary, while Keepalived greatly enhances availability, it must be configured thoughtfully. Proper network isolation, unique IDs/passwords, and monitoring of the HA setup will help ensure a secure and stable high-availability configuration.

## Related Roles

* **`haproxy`** – Typically used in conjunction with Keepalived for load balancing. For instance, you might deploy two HAProxy nodes with a virtual IP managed by Keepalived to achieve a highly available load balancer setup. (This repository includes a **haproxy** role that can be paired with Keepalived in this manner.)
* **`apt_mirror`** – This role (for setting up an APT package mirror) has an optional high-availability mode which utilizes Keepalived. When HA features are enabled in the **apt_mirror** role, it expects a Virtual IP to be configured so that two mirror servers can fail over. The Keepalived role can be used to provide that capability. (Refer to the apt_mirror role’s documentation for the `ha_features_enabled` option and how it integrates with Keepalived.)
* **Other roles in this repository** – While **Keepalived** is a generic HA tool, you may find references to it in other roles or playbooks whenever a floating IP is needed for high availability (e.g., database clusters or other services). Keepalived can be considered a building block to complement many services that require failover. Check the documentation of those specific roles to see if they recommend using Keepalived for HA, or if they have any special integration.
