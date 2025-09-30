# keepalived_setup Ansible Role

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
* [Mermaid Diagram](#mermaid-diagram)
* [Related Roles](#related-roles)

## Overview

The **keepalived_setup** role installs and configures **Keepalived** on a host to enable automatic failover of an IP address using VRRP (Virtual Router Redundancy Protocol). This allows a group of servers to share a **virtual IP** (VIP) such that one server is active at a time (MASTER) and others stand by (BACKUP) to take over the IP if the master fails. The role ensures that the keepalived service is installed, configured, and running with a basic VRRP setup. Key features include:

* **Automated Installation:** Installs the keepalived package from the OS repositories and enables the service to start on boot, requiring minimal manual setup.
* **Virtual IP Configuration:** Deploys a Keepalived configuration defining a single VRRP instance (one floating IP). One node will hold the VIP as MASTER, and if it becomes unavailable, a BACKUP node will automatically assume the VIP.
* **Configurable Parameters:** Allows customization of interface, virtual router ID, priority, and the virtual IP via role variables. These parameters control which network interface the VIP is tied to, the VRRP group ID, the election priority of the node, and the VIP address itself.
* **High Availability Use Cases:** Designed for HA scenarios such as two (or more) load balancer servers, database servers, or other critical services where an always-available IP address is needed. By using this role, you can achieve active-passive redundancy without specialized hardware or complex clustering software.

This role focuses on a simple, idempotent keepalived setup. It handles the common case of **one virtual IP failover group**. For more complex configurations (multiple VIPs, extensive health checks, etc.), see the notes in [Known Issues and Gotchas](#known-issues-and-gotchas) and [Related Roles](#related-roles).

## Supported Operating Systems/Platforms

This role is tested on and supported with the following Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** The target hosts must be Debian-based systems using the APT package manager. The tasks use the `apt` module for installation, so this role will **not** work on RPM-based distributions (e.g. RHEL, CentOS, AlmaLinux) unless you modify it to use `yum`/`dnf`. Ensure your Debian/Ubuntu hosts have network access to their package repositories for installing keepalived.

## Role Variables

Below is a list of the important variables for this role, along with their default values (defined in **`defaults/main.yml`**) and descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                           | Default Value   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`keepalived_setup_virtual_ip`**        | `192.168.1.100` | The Virtual IP address that Keepalived will manage. This IP will be floated between servers. The MASTER node will hold this IP and respond to traffic, and a BACKUP node will take over the IP if the master goes down. **This should be set to an appropriate free IP address in the subnet of your hosts.** (The default is a placeholder and must be changed for real use.) Keepalived’s configuration in this role does not explicitly specify a subnet mask, which means the VIP is treated as a /32 host address by default. |
| **`keepalived_setup_interface`**         | `eth0`          | Network interface on the target host that will carry the virtual IP. Typically this is the primary network interface (e.g. `eth0` or `ens160`). The VIP will be bound to this interface on the active node. Ensure all nodes in the failover group use the same interface name for the VIP.                                                                                                                                                                                                                                        |
| **`keepalived_setup_virtual_router_id`** | `51`            | The VRRP virtual router ID (VRID) number for the Keepalived instance. This is an identifier (1–255) that must be the same on all hosts participating in the same VRRP group. It distinguishes one VRRP group from another – use a unique VRID if you have multiple separate keepalived groups on the same network. The default `51` is arbitrary; you can change it if needed (e.g. to avoid conflict with another cluster using the same ID).                                                                                     |
| **`keepalived_setup_priority`**          | `100`           | The VRRP priority for this node. Higher values mean higher priority (the node most likely to be MASTER). In a two-node setup, you might assign a higher priority (e.g. 150) to the preferred primary node, and a lower value (e.g. 100) to the secondary. The node with the highest priority will become MASTER (or remain MASTER if it comes online), assuming other factors (like state and advert timing) are equal. If two nodes share the same priority, the one with the higher IP address typically becomes MASTER.         |

</details>

<!-- markdownlint-enable MD033 -->

Typically, you will override **`keepalived_setup_virtual_ip`** in your inventory or playbook, as the default is just an example. You should also ensure the `keepalived_setup_virtual_router_id` is consistent across all nodes in the cluster (usually you can use the default or any number, as long as it matches on every node). The **`keepalived_setup_priority`** can be left at default on all hosts if you intend to distinguish the primary via other means, but in practice you should set one host’s priority higher so that it will win the election and become MASTER. The **`keepalived_setup_interface`** usually corresponds to the primary network interface name on your servers; adjust it if your NIC is named differently (for example, on some systems it could be `ens33`, `enp0s8`, etc.).

**Additional variables:** This role does not expose some other Keepalived settings as variables (for example, the VRRP authentication password or advert interval). The provided configuration uses Keepalived’s default advert interval (1 second) and a default authentication password ("secret") baked into the template. See [Known Issues and Gotchas](#known-issues-and-gotchas) for implications of these defaults.

## Tags

This role does **not** define any Ansible task tags internally. All tasks will run by default whenever the role is applied. (You may still apply tags externally when including the role in a playbook if you want to control execution, but there are no built-in tags within this role requiring or skipping any tasks.)

## Dependencies

* **Ansible Version:** Requires Ansible **2.13** or higher. This role uses standard modules (e.g. `apt`, `template`, `service`) and syntax available in modern Ansible releases. It was developed and tested with Ansible 2.13+ for compatibility with other roles in the repository.
* **Collections:** None required beyond Ansible core. All modules used (`ansible.builtin.apt`, `ansible.builtin.template`, `ansible.builtin.service`) are part of the default Ansible distribution. You do not need any additional Galaxy collections to use this role.
* **External Roles:** None. This role is self-contained and does not depend on any other Ansible roles.
* **System Packages:** The role will install the **`keepalived`** package on the target host (using the OS package manager). Ensure that your package repositories are accessible. No other system service is strictly required for keepalived itself. (If you plan to use keepalived in conjunction with another service like HAProxy or Apache, those would be installed via their respective roles.) The keepalived service will be enabled and started automatically by this role.

## Example Playbook

Here is an example of how to use the `keepalived_setup` role in a playbook to configure two servers with a shared virtual IP. In this example, we assume an inventory group `loadbalancers` contains both nodes that should share the IP:

```yaml
- hosts: loadbalancers
  become: yes
  vars:
    keepalived_setup_virtual_ip: "10.0.0.50"       # The VIP that will float between the servers
    keepalived_setup_interface: "eth0"            # Interface on which to configure the VIP
    keepalived_setup_virtual_router_id: 50        # VRRP group identifier (must be same on both nodes)
    keepalived_setup_priority: 150                # Set a higher priority on the preferred master node
  roles:
    - keepalived_setup
```

*In the above play, we set the virtual IP to 10.0.0.50 and use `eth0` as the network interface. We choose `50` as the VRID (this must match on both servers). We’ve also set `keepalived_setup_priority: 150` in this playbook, which assumes this play is targeting the primary node. For the secondary node, you could run the same role with a lower priority (e.g. 100), or simply define `keepalived_setup_priority: 100` for the backup host in that host’s variables.*

Typically, you would achieve the above by setting host-specific variables in the inventory or host_vars: for example, in the inventory or host_vars for your secondary node, override `keepalived_setup_priority: 100` (while the primary gets 150) to ensure the primary is elected MASTER. All other variables (`keepalived_setup_virtual_ip`, `keepalived_setup_interface`, `keepalived_setup_virtual_router_id`) should be the same for both hosts in the cluster.

After running this playbook on both nodes, one node will come up as MASTER holding the IP 10.0.0.50, and the other will be BACKUP. You should then be able to use `10.0.0.50` to reach the service (e.g., HAProxy or whatever is running on those nodes) and it will automatically be served by the current MASTER.

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to ensure it works as expected before using it in a production environment. A basic testing workflow might be:

1. **Set up Molecule and Docker:** Install Molecule and the Docker driver on your development machine (for example, via pip: `pip install molecule[docker]`). Make sure you also have Docker installed and running.
2. **Initialize a test scenario (if needed):** If this role already includes a Molecule test scenario (e.g. in `molecule/default/` under the role directory), you can use that. If not, you can create one by running:

   ```bash
   molecule init scenario -r keepalived_setup -d docker
   ```

   This will create a `molecule/default` directory with a basic scenario configuration for Docker. You may need to edit `molecule/default/converge.yml` to include the `keepalived_setup` role and set required variables. For instance, you should set `keepalived_setup_virtual_ip` to a test value that the container can use (it could be a dummy IP like `10.0.0.50` as in the example above).
3. **Run the Molecule converge:** Execute the role in a Docker container by running:

   ```bash
   molecule converge -s default
   ```

   Molecule will launch a container (by default, often an Ubuntu image) and apply the `keepalived_setup` role inside it. The role should install keepalived and drop the config file in `/etc/keepalived/keepalived.conf`, then start the keepalived service.
4. **Verify the outcome:** After the converge, you can verify that keepalived was installed and configured. You can enter the container with `molecule login -s default` and then:

   * Check that `/etc/keepalived/keepalived.conf` exists and contains the expected configuration (VIP, interface, etc.).
   * Check that the keepalived service is running: e.g. `systemctl status keepalived` (you might need to install systemd or adjust the container init, since testing a service in a Docker container can be tricky; alternatively, run keepalived in foreground to test).
   * If the container has the necessary privileges, you could verify that the virtual IP is assigned (e.g. run `ip addr show eth0` inside the container to see if the VIP is present).
5. **Run idempotence test:** You can run `molecule converge` again (or use `molecule idempotence` if available) to ensure that a second run of the role makes no further changes (the role should be idempotent). If Molecule is configured with `molecule verify` tests (e.g., using Testinfra), run `molecule verify` to execute those. For example, a Testinfra test might check that the keepalived configuration file has the correct content or that the service is enabled.
6. **Cleanup:** When finished with testing, tear down the test container(s) with:

   ```bash
   molecule destroy -s default
   ```

   This will remove any containers created for the test. You can also run the full test sequence (create, converge, verify, destroy) in one step using `molecule test -s default`.

**Notes on testing environment:** Keepalived deals with networking (virtual IP assignment and VRRP multicast announcements). If you test inside a Docker container, be aware that:

* The container may need additional privileges to manipulate network interfaces and send VRRP packets. In some cases, you might have to run the container in privileged mode or with `--cap-add=NET_ADMIN` and possibly using `network_mode: host` for keepalived to function fully.
* Without special configuration, you might not be able to truly simulate two containers communicating via VRRP on the same host using multicast. For a more robust test of failover behavior, consider using a virtualization driver (like Vagrant with VirtualBox or libvirt) to run two VM instances, each running the keepalived_setup role, so they can exchange VRRP packets. In Docker-based tests, you will at least be able to verify installation and config file correctness, but testing actual failover might require more complex setups.

## Known Issues and Gotchas

* **Debian/Ubuntu Only:** As noted above, this role currently only supports Debian-based systems. Running it on other distributions will fail because it uses the `apt` module and expects the `keepalived` package name as provided in Debian/Ubuntu repositories. (On RHEL-based systems, the package and installation method would differ.) Ensure your inventory targets are using a supported OS.
* **VRRP Authentication Password:** The Keepalived configuration template provided by this role uses a hard-coded authentication password (`auth_pass`) of `"secret"`. This is a default placeholder and is **not recommended for production**. All nodes in a VRRP group must use the same password, and using a simple default increases the risk of misconfiguration or interference. Currently, the role does not expose this as a variable to easily change it. To use a custom password, you would need to edit the template (`keepalived.conf.j2`) or override it with your own template. (The more advanced **keepalived** role in this repo allows configuring the auth_pass via variable – see [Related Roles](#related-roles) below.)
* **Static State in Template:** In this role’s template, the `state` of the VRRP instance is set to `MASTER` unconditionally. Keepalived will start the service with that state on each node. Normally, one would configure the primary node’s instance as `MASTER` and the secondary’s as `BACKUP` in their respective configs. With this role’s simplistic approach, both nodes technically get a config stating `MASTER`. In practice, when two keepalived instances with the same VRID come online, the one with the higher priority will assume MASTER and the other will transition to BACKUP after hearing the master’s advertisements, even if its config file says `MASTER`. This behavior works due to the priority and advert mechanism, but it can be confusing and is not the conventional setup. **Gotcha:** Ensure that you do set different priorities so this election can happen correctly. Be aware that logs on the lower-priority node may show it initially claiming MASTER then yielding to the higher priority node. For a cleaner configuration that explicitly sets one node as BACKUP, consider using the **keepalived** role which templates the state based on a variable.
* **Single VIP Limitation:** The current role is designed to manage **one** virtual IP address (one `vrrp_instance`). If you require multiple virtual IPs or more complex failover scenarios (e.g., multiple instances or notifying scripts), this role would need to be adapted (e.g., additional config template entries and logic) or you might use multiple role invocations. The included template `keepalived.conf.j2` only defines a single `vrrp_instance VI_1`.
* **No Health-Check Script by Default:** This role’s configuration does not include any `vrrp_script` to monitor the health of a service (for example, checking if HAProxy or another service is up, and lowering priority if not). By default, failover will only occur if the keepalived service on the MASTER stops or the node itself goes down (link failure, power off, etc.). If you need to tie failover to a specific service’s health (e.g., have keepalived monitor an application and failover if it’s down), you will need to manually extend the configuration. This could involve adding a script on the nodes and modifying the keepalived.conf template to include a `track_script`. The base **keepalived_setup** role doesn’t handle this out of the box.
* **Firewall and Multicast Considerations:** Keepalived uses VRRP which sends multicast packets (IPv4 multicast to `224.0.0.18` by default, protocol number 112) to communicate between the MASTER and BACKUP. If a host-based firewall (e.g., UFW, iptables) is active, or if there are network firewalls separating the nodes, you **must allow VRRP traffic** between the participating servers. Otherwise, the backup node will not hear the master’s heartbeats and may wrongly assume the master is down (leading to IP conflicts or flapping). Ensure that protocol 112 (or UDP port 112 if your firewall needs a port specification for VRRP) is permitted between the HA nodes. In addition, ensure the network allows gratuitous ARP or neighbor announcements so that the MAC address change for the VIP is recognized by switches/routers when failover happens.
* **Unique Virtual IP:** This may be obvious, but the `keepalived_setup_virtual_ip` you configure should **not already be in use** in the network. Treat it as a virtual address that only keepalived will manage. If something else is using that IP, you’ll encounter IP conflicts. Also, all keepalived nodes should reside in the same subnet as that VIP (keepalived will add the VIP to the specified interface on the master node, and it should be able to ARP/respond on that subnet).
* **Cloud Environment Gotchas:** In some cloud environments, traditional VRRP may not work seamlessly. For example, certain cloud providers don’t support multicast or gratuitous ARP the same way a bare-metal network would. AWS, for instance, doesn’t natively allow multiple instances to claim the same IP address unless using specific features (like AWS Elastic IPs or network load balancers), and might block VRRP packets. If you plan to use keepalived in a cloud setting, research the cloud’s support for floating IPs or consider using provider-specific high-availability features. In private cloud or virtualized environments (OpenStack, etc.), ensure that the network is configured in **promiscuous mode** or allows MAC address changes if necessary, otherwise the VIP might not fail over correctly.
* **Troubleshooting Tip:** If failover isn’t working as expected, check the syslog or journal on both nodes for keepalived messages. Keepalived logs are very informative. Common issues include mismatched VRID (nodes not seeing each other at all), authentication mismatches (if you changed one node’s `auth_pass` but not the other’s, they’ll ignore each other’s packets), or firewall drops. Ensuring both nodes have identical VRRP configuration (except for state and priority) is key to a stable failover setup.

## Security Implications

* **Default Credentials in Config:** The role’s default configuration uses a generic authentication password `"secret"` for VRRP. This password is visible in the generated `/etc/keepalived/keepalived.conf` on the hosts. While VRRP authentication is not meant to be highly secure (it prevents accidental mix-ups more than determined attackers), using a default or common password is a bad practice. **Before deploying to sensitive environments, change the VRRP password** to a unique secret known only to your cluster. As noted, this role doesn’t provide a variable for it by default – you’ll need to customize the template or use the more advanced keepalived role. Failing to change the auth_pass means any other keepalived on the network using the default password and same VRID could potentially interfere with your cluster’s failover.
* **Running as Root:** Keepalived runs as a system service (typically as root or with root privileges for network manipulation). This is necessary for it to add/remove IP addresses and send low-level network traffic. The role doesn’t create any special user accounts or modify permissions on the system besides dropping the config and managing the service. Ensure that only trusted administrators run this role or have access to manage keepalived, because misconfiguration (intentional or accidental) could disrupt network operations (e.g., causing IP conflicts).
* **Exposure of the Virtual IP:** When a virtual IP is brought online on the MASTER node, that IP may start accepting traffic (for whatever service is listening on it, e.g., a load balancer or database). This doesn’t inherently open new ports by itself, but if you have firewall rules, you might need to account for the new IP. For example, if you restrict access by destination IP, you’ll need to add rules for the VIP. The role does not adjust firewall settings automatically. As a security measure, double-check that your firewall (network and host) rules are updated to either allow legitimate traffic to the VIP or block unwanted sources as appropriate.
* **VRRP Traffic Visibility:** VRRP advertisements are sent as multicast packets. These are not encrypted (even with authentication, the content can be observed on the LAN). An attacker on the same network segment could potentially sniff VRRP packets and learn the VRID and even the auth password hash. They could also attempt to send spoofed VRRP packets to disrupt the cluster (for example, claiming a higher priority to steal the VIP). To mitigate risks, use a unique auth_pass and, if possible, operate VRRP within a secured network segment (e.g., within a VLAN not accessible to untrusted systems). Some deployments use IPsec or other measures to protect such traffic if the threat model warrants it, but typically VRRP is used in trusted internal networks.
* **System Configuration Changes:** Keepalived will manipulate network interfaces (adding an IP address and responding to ARP for it). This is generally safe on a system meant for that purpose, but be aware if the host has other network security monitoring (IDS/IPS or ARP spoofing protection), you may need to whitelist this behavior. Similarly, if using SELinux or AppArmor, ensure that keepalived is allowed to perform its functions (most default policies do allow it, as it’s a common service).
* **Post-Failover Service Security:** After a failover, the new MASTER will start serving traffic on the VIP. Make sure that the services bound to the VIP are properly secured on both nodes (e.g., up-to-date patches, correct access controls) because whichever node is active will be receiving client traffic. The keepalived role itself doesn’t configure those services, but the overall security of your HA setup depends on each node being equally secure and prepared to take production traffic at any moment.

## Mermaid Diagram

The following diagram illustrates a simple two-node keepalived setup with a shared virtual IP. Node1 is configured with higher priority and will be the MASTER, while Node2 acts as BACKUP. Both nodes run keepalived and communicate using VRRP. The virtual IP (VIP) is owned by the MASTER and will switch over to the BACKUP if Node1 goes down:

```mermaid
flowchart TB
    VIP((Virtual IP 10.0.0.50/32))
    subgraph Keepalived Cluster
        Node1[Keepalived Node1<br/>(MASTER, prio 150)]
        Node2[Keepalived Node2<br/>(BACKUP, prio 100)]
    end
    Node1 -->|VRRP adverts| Node2
    Node1 -->|Active| VIP
    Node2 -->|Standby| VIP
```

In this diagram:

* **Node1** and **Node2** form a cluster managing the same VIP. Node1 has higher priority (150 vs 100) and thus becomes **MASTER**, bringing up the VIP `10.0.0.50` on its interface.
* Node2, as **BACKUP**, listens for advertisements. As long as it hears Node1 (the master) sending VRRP announcements, Node2 will not take over the IP.
* If Node1 fails (no VRRP adverts are received by Node2), Node2 will assume the MASTER role after a short timeout and bring up `10.0.0.50` on its own interface, thereby continuing service.
* When Node1 comes back online, since it has the higher priority, it will (by default) preempt and regain MASTER status, taking back the VIP. Keepalived handles this transition automatically.

This setup ensures that the IP `10.0.0.50` is always hosted by one of the two nodes, providing high availability for whatever service is reachable at that IP.

## Related Roles

* **keepalived (core keepalived role):** There is a related role named **`keepalived`** (without “_setup”) in this repository. It serves a similar purpose but offers a more elaborate configuration. The `keepalived` role supports additional variables such as `keepalived_state`, `keepalived_auth_pass`, and `keepalived_virtual_cidr`, allowing you to explicitly set MASTER/BACKUP per host, change the VRRP auth password via vars, and specify the netmask for the VIP. It may also handle installation on multiple OS families. If your use case requires those features or a cleaner multi-node config, consider using the more advanced keepalived role. (See the [keepalived role’s README](../keepalived/README.md) for details.)
* **haproxy (load balancer role):** The **haproxy** role in this repository can be combined with keepalived for high availability load balancing. A typical pattern is to have two HAProxy servers (configured with the `haproxy` role) and use `keepalived_setup` to give them a shared floating IP. Clients would connect to the VIP, and whichever HAProxy is MASTER will handle the traffic. If you are setting up an HA pair of load balancers, use this role to manage the failover IP alongside the haproxy configuration. (For reference, see the [haproxy role’s README](../haproxy/README.md).)
* **apt_mirror (APT repository mirror role):** The **apt_mirror** role optionally integrates with keepalived for an HA mirror setup. In a scenario where you have two Debian/Ubuntu package mirror servers (for redundancy), keepalived can manage a virtual IP that clients use to access the mirror. The apt_mirror role includes an option for “HA features” which, when enabled, expects keepalived to be configured with appropriate settings (VRID, VIP, etc.) on the mirror hosts. In such cases, you would apply `keepalived_setup` (or the more advanced keepalived role) to the two mirror nodes to handle the VIP. See the [apt_mirror role’s README](../apt_mirror/README.md) for details on setting up a high-availability APT mirror environment.
* **mariadb_galera_loadbalancer_install (Galera LB role):** In environments with a Galera cluster for MySQL/MariaDB, a load balancer (like GLB or HAProxy) is often used to distribute database traffic. If such a load balancer is deployed on multiple nodes for HA, keepalived can provide a single IP for database clients to connect to. While the specifics depend on your setup, you can use this keepalived role to manage a VIP for a pair of database load balancer nodes, similar to the HAProxy scenario. (Refer to the documentation or README of the `mariadb_galera_loadbalancer_install` role in this repo for context on how it might be used, and integrate keepalived accordingly.)

Each of the above roles addresses a different part of a high availability or infrastructure need, but keepalived often ties in by ensuring there's no single point of failure at the IP level. By cross-referencing these roles and their documentation, you can design a resilient system — for example, highly available load balancers with **haproxy+keepalived**, or a redundant package mirror with **apt_mirror+keepalived**. Always make sure that the variables between roles are consistent (e.g., the VIP and interface you set in keepalived should match what your other role’s configuration expects to use).

