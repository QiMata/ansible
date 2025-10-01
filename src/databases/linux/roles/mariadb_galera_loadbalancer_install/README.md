# Ansible Role: MariaDB Galera Load Balancer (GLB)

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

**MariaDB Galera Load Balancer (GLB)** is an Ansible role that installs and configures a **Galera Load Balancer** in front of a MariaDB Galera Cluster. Its purpose is to provide a single **load-balanced endpoint** for database clients, distributing incoming connections across multiple MariaDB nodes in the cluster for improved availability and scalability. The role automates the entire setup of GLB, which is a lightweight TCP load balancer tailored for Galera clusters:

* **Source Build and Installation:** The role clones the official GLB source from GitHub and compiles it on the target host. This ensures you get the latest GLB binaries even if no OS package is available. It then installs the GLB daemon (`glbd`) and associated scripts on the system.
* **Service Configuration:** It deploys an init script (`glbd.sh`) and a configuration file for GLB, and registers GLB as a service to start on boot. The service will be started immediately after installation, so the load balancer begins accepting connections right away.
* **Galera-Aware Load Balancing:** By default, GLB is configured to listen on the **MySQL port (3306)** and forward client connections to the defined Galera cluster nodes. It operates at the TCP level, balancing incoming connections (not individual queries) using efficient algorithms suitable for database workloads. All Galera cluster nodes can handle reads/writes (multi-primary replication), and GLB helps distribute the connection load among them.
* **Configurable Parameters:** You can easily customize listening address/port, control port, backend server list, and threading via role variables. This allows integration into various environments – from a single proxy node to a highly-available pair of proxy nodes with failover. The role defaults are sensible for a typical deployment, but you should review and override them to match your infrastructure (see **Role Variables** below).

In practice, you would use this role on one or more **load balancer nodes** sitting in front of your MariaDB Galera Cluster. Clients connect to the GLB node(s) instead of directly to MySQL. In a multi-node GLB setup, it’s common to combine this with a virtual IP (using Keepalived) so that if one GLB node fails, another can take over (see **Mermaid Diagram** and **Related Roles** for details). By using GLB, applications get a single database endpoint while the actual traffic is spread across all healthy database nodes.

## Supported Operating Systems/Platforms

This role is tested on and supports **Debian** and **Ubuntu** Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** The role’s tasks are designed around Debian/Ubuntu conventions (using APT for package management and assuming systemd or SysV init is present). Other Linux distributions (e.g. RHEL, CentOS, AlmaLinux) are **not officially tested**. In theory, GLB can run on any modern Linux, but using this role on non-Debian systems may require adjustments (for example, installing development tools via `yum`/`dnf` and adapting file paths for init scripts). Proceed with caution and test if you plan to use this role on a non-Debian OS. Also ensure the target system has network access to clone the GLB repository and install build dependencies.

## Role Variables

Below is a list of important variables for this role, along with their default values (defined in **`defaults/main.yml`**) and descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                 | Default Value | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`glb_listen_address`** | `"0.0.0.0"`   | The network address that GLB will bind to for accepting MariaDB client connections. **`"0.0.0.0"` (all interfaces) is the default**, meaning GLB listens on all network interfaces of the host. You can set this to a specific IP address to restrict it (e.g., `"192.168.10.10"` to listen only on a particular interface). If you plan to use Keepalived with a VIP, you might set this to the VIP address so GLB only listens on the floating IP.                                                                                                                                                                                                                                                                                                                    |
| **`glb_listen_port`**    | `"3306"`      | The TCP port that GLB will listen on for incoming database connections. By default this is `3306`, the standard MySQL/MariaDB port, so that clients can connect as if to a normal MySQL server port. You may change this if needed (for example, if 3306 is already in use on the host, or if you want to run GLB on a different port for testing). Make sure clients are aware of the port if you use a non-default value.                                                                                                                                                                                                                                                                             |
| **`glb_control_port`**   | `"8010"`      | The TCP control port for GLB’s admin interface. GLB can open a separate port to accept administrative commands or provide usage statistics. By default this is set to **8010**. If this parameter is defined, GLB will listen on the specified port (on the same address as `glb_listen_address`) for control commands. If you do **not** want a control interface, you can set this to an empty value or omit it, in which case GLB will not open a control socket. **Note:** Exposing the control port on a public interface is not recommended; see **Security Implications** below.                                                                                                                 |
| **`glb_servers`**        | `[]`          | The list of Galera cluster backend servers (database nodes) that GLB should forward connections to. Each entry should be in the format `"host:port"` (usually port 3306 for MySQL/MariaDB). **No default servers are provided** – you must specify your cluster nodes. For example, you might define `glb_servers` in your inventory or playbook as:<br>`glb_servers: ["db-node1:3306", "db-node2:3306", "db-node3:3306"]`.<br>You can also generate this list dynamically using group inventory. In the repository’s example configuration, it’s constructed via an expression (e.g., using an inventory group named `nodes`). Ensure that every listed host is a running MariaDB node in the cluster. |
| **`glb_threads`**        | `"4"`         | Number of threads for the GLB daemon to use for handling connections. GLB is multi-threaded; increasing this can improve throughput on multi-core systems by allowing more parallel handling of connections. The default is **4**, which is suitable for many scenarios. You may adjust this based on the number of CPU cores and expected load (for example, set to the number of cores in the server for maximum concurrency). Keep in mind that beyond a certain point, more threads may yield diminishing returns due to locking in the load balancer.                                                                                                                                              |

</details>
<!-- markdownlint-enable MD033 -->

**Notes:** Typically, you will *override* several of the above variables in your inventory or playbooks:

* **`glb_servers`** has no default list – you **must** provide the addresses of your database nodes. It’s often convenient to generate this from your inventory groups. For example, if your Ansible inventory group for database nodes is `galera_nodes`, you could set:

  ```yaml
  glb_servers: "{{ groups['galera_nodes'] | map('concat', ':3306') | list }}"
  ```

  This Jinja2 expression takes all hosts in `galera_nodes` and appends `:3306` to each, producing the list of host\:port strings. Use whatever method ensures the list is correct for your environment.
* **`glb_listen_address`** and **`glb_listen_port`** usually can remain at defaults (all interfaces, port 3306) unless you have a specific reason to change them (e.g., running GLB on the database nodes themselves – see **Known Issues** – or avoiding port conflicts).
* **`glb_control_port`** is optional. The default (8010) is provided for convenience, but you can disable the control interface by removing or blanking this variable. If you do use it, consider limiting it to localhost or firewalling it off, since it can be used to query or modify GLB’s state.
* **`glb_threads`** may be tuned according to the hardware. If the GLB host has many cores and will handle a high volume of connections, you might increase this number. If unsure, the default of 4 is a reasonable starting point.

## Tags

This role does **not** define any Ansible task tags internally. All tasks will run whenever the role is invoked (every time you include the role in a play, it performs the full setup). You can still use tags *externally* when including the role if you need to control when it runs (for example, tagging the role invocation in a playbook), but there are no built-in tags within the role to selectively skip or run specific tasks.

## Dependencies

* **Ansible Version:** This role requires Ansible **2.13** or higher. It uses standard modules and syntax available in modern Ansible, and was developed/tested with Ansible 2.13+. Earlier versions of Ansible (2.9, 2.10) may not support some of the collection usage or module features used here. It’s recommended to run this role with a relatively recent Ansible to ensure compatibility.
* **Collections:** The role uses the **community.general** Ansible Collection for certain modules. In particular, it calls the `community.general.make` module to build the software from source. Make sure you have this collection installed (e.g., run `ansible-galaxy collection install community.general` if your Ansible installation doesn’t include it by default). Other modules used, such as `ansible.builtin.git`, `ansible.builtin.template`, `ansible.builtin.copy`, and `ansible.builtin.service`, are part of Ansible core.
* **External Packages/Tools:** The target host **must have development tools** available to compile GLB from source. This role **does not automatically install build dependencies**, so ensure the following are present on the node before running the role:

  * **Git:** Required to clone the GLB repository. Install via apt (`git` package) if not already installed.

  * **Build Essentials:** A C/C++ compiler and related tools. On Debian/Ubuntu, installing the `build-essential` package will provide gcc, g++ and make. These are needed to compile the GLB source (which is written in C++).

  * **Autotools:** GLB’s build uses an autoconf/automake toolchain. Ensure packages like `autoconf`, `automake`, `libtool`, and `pkg-config` are installed. The role runs `./bootstrap.sh` and `./configure` scripts, which rely on these tools to prepare the build system.

  * **Libraries:** GLB doesn’t have many external library requirements, but it may depend on standard C libraries and possibly development headers (for example, it uses `pthread` for threads and might use libevent/epoll for networking). On Debian/Ubuntu, having the basic system libraries (which `build-essential` and autotools packages pull in) is typically sufficient. There is no need for MySQL client libraries because GLB works at the TCP connection level.

  > *If the target system is a minimal install, you might need to install the above packages manually or via another role before applying this role.* If you skip this and the required tools are missing, the role will fail during the compile steps.
* **Galaxy Roles:** No external Ansible Galaxy roles are required by this role. It is self-contained (it does not list any dependencies in its meta). However, it is often used alongside other roles (see **Related Roles** below) to set up a complete HA database environment.
* **Target Environment:** A running **MariaDB Galera Cluster** is assumed to exist. **This role does *not* install MariaDB or configure the database cluster itself.** You should set up your Galera cluster beforehand (for example, using the `mrlesmithjr.mariadb_galera_cluster` role or another method) so that GLB has multiple backend nodes to connect to. Without a database cluster, the load balancer has no real purpose. Ensure that the MySQL/MariaDB instances on those nodes are accessible (firewall open on port 3306 within your network, etc.).
* **High Availability (Optional):** If you require the load balancer itself to be highly available (no single point of failure), you will need at least two GLB nodes **and an approach to failover**. This typically means using Keepalived (VRRP) to maintain a floating virtual IP that is always hosted by one of the GLB nodes. This role does not configure keepalived by itself; use the accompanying `keepalived_setup` role to achieve this. (See **Mermaid Diagram** and **Related Roles** for more info on combining GLB with Keepalived.)
* **Firewall Considerations:** The role does not manage firewall rules. If your GLB host has a firewall (e.g., UFW or firewalld), you must allow the GLB listen port (e.g., 3306) and, if needed, the GLB control port (e.g., 8010) for the appropriate source ranges (e.g., application servers). Additionally, the GLB host needs to be able to reach all Galera nodes on their MySQL port. Ensure internal firewalls or security groups allow the GLB node to connect to port 3306 on each database node.

## Example Playbook

Below is an example of how to use the `mariadb_galera_loadbalancer_install` role in an Ansible playbook. In this scenario, we assume a group of hosts (e.g., **`galera_loadbalancer`**) that will act as our load balancer nodes, and another group (e.g., **`galera_cluster`**) for the actual MariaDB Galera database nodes. We will apply the GLB role to the load balancer hosts. We also provide the necessary variables to configure GLB to point to our database cluster:

```yaml
- hosts: galera_loadbalancer
  become: yes  # ensure we have privileges to install packages and configure services
  vars:
    glb_listen_address: "0.0.0.0"        # Listen on all interfaces (could also use the VIP here if one is set up)
    glb_listen_port: "3306"             # Listen on the default MySQL port
    glb_control_port: "8010"            # Enable control port (could omit if not needed)
    glb_threads: 4                     # Use 4 threads for glbd
    glb_servers:                       # Define the Galera backend nodes (host:port for each)
      - "db-node1:3306"
      - "db-node2:3306"
      - "db-node3:3306"
  roles:
    - mariadb_galera_loadbalancer_install
```

**How this works:** The play targets the **`galera_loadbalancer`** group (you should replace this with the actual inventory group or host names for your load balancer machine(s)). We elevate to root (`become: yes`) because installing software and adding services require root privileges. In `vars`, we explicitly set the GLB configuration:

* We keep `glb_listen_address` at `0.0.0.0` so the service listens on all network interfaces (for instance, if this host gets a floating VIP later, it will still accept connections on it).
* `glb_listen_port` is left at 3306, meaning clients can connect without specifying a non-standard port.
* `glb_control_port` is set to 8010 to enable the admin interface (for demonstration here; in production you might disable it or firewall it).
* `glb_threads` is set to 4 (this could be omitted since 4 is the default, but we include it for clarity).
* `glb_servers` is the critical part: we list the three database node addresses (replace `"db-node1"`, etc., with your actual hostnames or IPs that the GLB host can resolve/reach). Each is suffixed with `:3306` because that’s the MySQL service port on those nodes.

When this play runs, the role will:

1. Clone and build the GLB software on each host in `galera_loadbalancer`.
2. Install the GLB init script and config file using the variables provided.
3. Start and enable the `glb` service. At this point, the GLB daemon will be running and listening on **port 3306** on each load balancer host, proxying connections to the specified `glb_servers`.

Clients (for example, your application or web servers) should then be configured to connect to the **load balancer host(s)** (ideally via a VIP if you configured one) on port 3306, instead of connecting directly to the database nodes. This way, GLB will distribute their connections among the cluster nodes.

## Testing Instructions

It is highly recommended to test this role in an isolated environment (using **Molecule** with Docker) before using it in production. Molecule allows you to run the role on a disposable container and verify that it converges correctly. Below is a suggested testing workflow:

1. **Set up Molecule and Docker:** Install Molecule and its Docker driver on your development machine (e.g. via pip: `pip install molecule[docker]`). Ensure you have Docker installed and running as well.
2. **Initialize a test scenario:** If this role already contains a Molecule scenario (check for a `molecule/` directory in the role), you can reuse it. If not, create a new scenario for this role by running:

   ```bash
   molecule init scenario -r mariadb_galera_loadbalancer_install -d docker
   ```

   This will create a `molecule/default/` directory with a basic scenario configuration. You may need to edit `molecule/default/molecule.yml` to adjust the Docker image (use an image for one of the supported OS, e.g., Debian 12 or Ubuntu 22.04). Also edit `molecule/default/converge.yml` to include this role and set the required variables (like `glb_servers`) for the test.
3. **Prepare the test host environment:** In a real deployment, GLB needs backend DB servers to connect to. For testing, you have a couple of options:

   * **Single-container test:** You can install a MariaDB server *inside the same container* and have GLB forward to it on localhost (using a different port to avoid conflicts). For example, in the Molecule converge playbook, you might install `mariadb-server` on the container and set `glb_servers: ["127.0.0.1:3306"]` but change GLB to listen on a different port (say 13306) so that the local MySQL can keep 3306. This way, GLB is balancing “across” one local server (not a real balance, but a functional test of connectivity).
   * **Multi-container test:** A more robust test is to use two containers – one acting as a database node, and one as the GLB node. You can define multiple instances in the Molecule config. For example, one container `db1` running MariaDB, and another `glb1` running this role. Set `glb_servers` in the GLB container’s inventory to point to `db1:3306`. This simulates a real-world scenario with separate nodes. After converge, the GLB container should be proxying to the DB container.

   Choose the approach that fits your comfort level. The single-container method is simpler but a bit contrived; the multi-container approach more closely mirrors a real deployment but requires a more advanced Molecule configuration.
4. **Run Molecule converge:** Execute the role in the Docker container(s) by running:

   ```bash
   molecule converge
   ```

   Molecule will build the container(s) and apply the `mariadb_galera_loadbalancer_install` role. Watch the output for any errors. The role should complete with no failures. It will clone the GLB repo, build it, and attempt to start the `glb` service inside the container.
5. **Verify the outcome:** Once converge finishes, verify that GLB is installed and running:

   * **Login to the container:** `molecule login` (for a single container scenario) or `molecule login -h glb1` (if you named a container). Once inside, check the service status. Since this is a container environment, Systemd might not be fully running; however, the role’s final task attempts to start `glb` via the init script. You can manually run `/etc/init.d/glb status` or use `ps -ef | grep glbd` to see if the daemon is running.
   * **Configuration files:** Check that `/etc/sysconfig/glbd.cfg` exists (this is the config file the role templates). It should contain lines reflecting your test variables (listen address, ports, backend servers, threads). Also, `/etc/init.d/glb` should exist and be executable.
   * **Ports listening:** Even if the service status is tricky in a container, you can verify GLB is listening by using `netstat` or similar. For example, install net-tools (`apt-get install net-tools`) in the container if not present, then run `netstat -tnlp`. You should see a process (glbd) listening on the configured `glb_listen_port` (e.g., 3306 or 13306 in your test) and on the `glb_control_port` (e.g., 8010) if enabled. This confirms the load balancer is running.
   * **End-to-end test:** If you have a MariaDB running in the test (either in the same container or another), try connecting through GLB. For instance, on the GLB host container execute: `mysql -h 127.0.0.1 -P 13306 -u root -p` (adjust host/port/user as needed for your test setup). If GLB is working, you should be able to connect (and you’d actually be hitting the backend MySQL). Alternatively, use `nc` (netcat) to ensure the port is open: `nc -z 127.0.0.1 13306` (exit code 0 indicates the port is listening).
6. **Idempotence test:** Run the converge again (`molecule converge` a second time) or use `molecule idempotence`. The role should ideally make no changes on the second run (meaning it’s idempotent). No changes would indicate that all actions were either already done or properly check for existing state. If you see tasks reporting “changed” on the second run, double-check if that’s expected or if the role could be improved (for example, the `git` clone might pull updates if the repo changed, which is acceptable, but most tasks should be idempotent).
7. **Cleanup:** After testing, destroy the test container(s) with `molecule destroy`. This will remove any containers that were created for the scenario. You can also run `molecule test` to run the full cycle (create, converge, verify, destroy) in one go once you have your scenario configured.

Following these steps will give you confidence that the role works as expected in a controlled environment. It’s much easier to catch and fix issues in Molecule/Docker than on live servers. Additionally, you can adapt the Molecule scenario to simulate different scenarios (e.g., adding multiple database nodes, or testing on different OS versions) as needed.

## Known Issues and Gotchas

* **Build Dependencies Are Required:** As noted, this role builds GLB from source. If the target host lacks compilers or other build tools, the role will fail. A common pitfall is running this role on a fresh minimal server without installing `build-essential`, `git`, etc. Make sure to install those prerequisites (either manually, via a “base” role, or by customizing this role) *before* applying this role. If you see errors during the `bootstrap.sh` or `make` steps, it’s likely due to missing development tools.
* **No Default Backend Servers:** The role cannot function without defining `glb_servers`. By default (unless you override via inventory), `glb_servers` is an empty list `[]`, which means GLB would have no target nodes and thus won’t be able to forward any connections. Always set `glb_servers` to at least one actual database node. If this is not provided, the GLB service may still start, but it won’t accept any client connections (it might immediately close them because no backends are configured). This is a configuration mistake to avoid – double-check that your inventory or playbook supplies the list of backend DB hosts.
* **Running GLB on a DB Node (Port Conflicts):** In some setups, you might be tempted to run GLB on the database nodes themselves (to avoid having separate load balancer VMs). This is possible, **but you must adjust ports**. GLB by default uses port 3306 – which is the same port MariaDB uses. If you install GLB on a DB server without changing `glb_listen_port`, it will conflict with the database service. In such a case, consider using a different port for GLB (e.g., have GLB listen on 3307 and still point to the local MySQL on 3306). Alternatively, bind GLB to a different IP (if the DB server has multiple NICs or you assign a separate VIP to GLB on that host). Generally, it’s cleaner to run GLB on separate host(s) to avoid this complexity, but it’s something to be aware of.
* **Lack of Advanced Health Checks:** GLB’s balancing is at the TCP connection level and it does not perform detailed health checks on the database nodes (it will detect if a node is not accepting connections, but it’s not as health-check-rich as something like HAProxy or ProxySQL). This means if a database node is up but not actually functioning correctly at the SQL layer (for example, it’s alive but hitting errors), GLB has no built-in way to know that – it will continue to send connections to that node. In practice, GLB will stop using a node only if the TCP connection outright fails. This is usually fine in Galera clusters (since node failures are typically network-level or the node is removed from cluster), but it’s a **gotcha** compared to more advanced proxies. If you need robust health checks or query-level routing (e.g., directing SELECTs differently from DML, or automatically removing lagging nodes), consider using **HAProxy** or **ProxySQL** instead of GLB (see **Related Roles**).
* **Control Port Accessibility:** If you enable the `glb_control_port`, note that by default it will listen on the same address as `glb_listen_address`. If that is 0.0.0.0, the control port is accessible from any network interface as well. This can be dangerous because GLB’s control interface can potentially alter load balancing behavior or divulge stats. The role does not set any authentication for using the control port. Treat it like an admin port – ideally, bind it to `127.0.0.1` only or firewall it so that only administrators can reach it. In the provided defaults, we did not specify a separate control bind address, so it’s effectively 0.0.0.0:8010. This is something you should change or protect in production (see **Security Implications** below).
* **Service Management in Containers:** If you test this role inside a Docker container (as discussed in Testing), be aware that the `service` startup might not work seamlessly since many Docker base images don’t run a full init system. The role’s use of an init script means on a system with Systemd, the service should be properly registered and enabled. On a vanilla Docker container, you might not have Systemd running; the role will still place the script and attempt to start it. You may need to start `glb` manually for testing in that context. In a full VM or metal server, this is not an issue – the role will integrate with Systemd or SysV as appropriate.
* **Idempotence of Git Pull:** By default, the `ansible.builtin.git` task will update the GLB repository to the latest commit on each run (unless a specific version/tag is checked out). We have not pinned a version of GLB in this role, so whenever you run the play, it may pull in the newest changes from the GLB GitHub repo. This could lead to the role compiling a new version of GLB if there have been updates, causing changes on what might otherwise be an idempotent run. This isn’t exactly a bug – but be aware that GLB’s code could update over time. For a stable production environment, you might want to fork or snapshot a known-good version of GLB or specify a commit hash/tag in the git task to avoid unexpected changes. Currently, the role always tracks the latest master branch.
* **Log Files and Monitoring:** GLB doesn’t automatically create a detailed log file by default (it may log to syslog). If you’re troubleshooting, check `/var/log/syslog` or `/var/log/messages` for GLB entries (or wherever your system logs daemon output). The init script provided doesn’t rotate logs or create a dedicated log file. Over time, if GLB outputs a lot (it’s generally quiet except for errors), ensure your syslog is managed. Also consider monitoring the GLB process – if it crashes or is accidentally stopped, you’d lose the load balancing function until it’s restarted (the role enables it on boot, but no further monitoring). Using a tool or configuring systemd (if you create a systemd unit) for restart on failure could be beneficial.
* **Galera Cluster Behavior:** Remember that GLB is just distributing connections; it does not mitigate the need to properly configure and monitor your Galera cluster. All nodes listed in `glb_servers` should be part of the same Galera cluster and in sync. If a node goes down or desyncs, GLB won’t automatically remove it (unless the TCP connections fail). Ideally, you’d integrate GLB with a cluster monitoring system or remove failed nodes from `glb_servers` (and restart GLB) if a node is known to be out. Some advanced setups use scripts (via the control port or external registries) to dynamically update load balancer backends, but that’s beyond the scope of this simple role. The takeaway: ensure your cluster is healthy; GLB will blindly send connections to whatever hosts you configured.

## Security Implications

Deploying a load balancer for your database introduces some security considerations. Below are the main points to keep in mind when using this role:

* **Root Privileges and Service Execution:** The GLB service (glbd) runs as root by default (since it’s started via an init script with no user drop specified). This is common for system daemons that bind to low-numbered ports (3306) and need broad access. However, it means that any compromise of the GLB process could potentially lead to root-level access on the system. Mitigate this by running GLB on dedicated hosts that have a minimal attack surface and by keeping the system and GLB up to date. If desired, you could modify the init script or create a systemd unit to run glbd as a non-root user with `CAP_NET_BIND_SERVICE` (to allow binding to 3306) – this role does not do that by default.
* **Exposed Ports:** After applying this role, your load balancer host will have **port 3306/TCP open** (or whatever `glb_listen_port` you set). Ensure that this port is only accessible to the appropriate clients (e.g., your application servers or web servers) and not the entire internet, unless absolutely necessary. Typically, database endpoints should be in a private network. Use host-based firewalls or security groups to restrict access. Similarly, if the control port (8010 by default) is enabled, treat it as an admin-only port – ideally bind it to localhost or block it from untrusted sources. In the example group vars, port 3306 is allowed through UFW and the control port is not listed, implying only the DB traffic is expected externally.
* **No Authentication on GLB:** GLB itself does not perform any authentication or encryption. It’s a TCP proxy. This means any client that can reach GLB’s port can attempt to initiate a MySQL connection to the backend. Authentication is still enforced by MySQL on the backend nodes (so you must have proper MySQL users/passwords, etc.), but GLB won’t add any extra layer of security like requiring its own credentials. Also, GLB does not encrypt traffic – if you need TLS/SSL encryption between clients and the database, GLB will just pass through whatever the client initiates. (You could terminate TLS at GLB if GLB supported it, but it doesn’t modify the stream – it’s not an SSL terminator. So typically you’d use end-to-end SSL from client through GLB to MySQL, or keep it all internal).
* **Control Interface Risks:** If `glb_control_port` is set and accessible, an attacker who can connect to it might be able to run administrative commands (GLB’s control interface allows things like checking status and possibly adding/removing backends on the fly). By default, GLB’s control has **no authentication**. In production, you should seriously consider disabling the control port or locking it down (e.g., only allow from 127.0.0.1 or a jump box). As mentioned, GLB will not even open a control socket unless you configure one. Our defaults explicitly configure one on 8010 for demonstration, so take steps to secure it (or remove it if not needed).
* **Data Sensitivity:** The GLB node will handle all your database traffic, which likely includes sensitive data. While GLB doesn’t log the content of queries, someone with root access on the GLB host could potentially sniff traffic or capture queries. Treat the security of the GLB host as you would a database server. Limit who can log into it, keep it patched, and monitor it. The role itself doesn’t change any system security settings except opening the ports for GLB’s service – but it’s up to you to ensure that’s done in a safe environment.
* **Inbound vs. Outbound Rules:** GLB will make outbound connections to the database nodes on their MySQL port. This means the GLB host needs network access to all `glb_servers` addresses on port 3306. Ensure that any firewalls on the database side allow connections from the GLB host. It’s easy to overlook outbound access; if GLB can’t reach a backend, clients will hang or fail to connect when routed to that backend.
* **Keepalived and VIP (if used):** If you set up a virtual IP with Keepalived for HA, note that the VIP will often be handled by root-owned network changes (via Keepalived) and ARP announcements. The keepalived roles by default use a simple password for VRRP (`"secret"` in the basic role). You should change that in a production environment to prevent malicious VRRP packets from disrupting your cluster. While this is more on Keepalived than GLB, it’s part of the overall security of your load-balanced setup.
* **Securing the Source Code (Supply Chain):** This role pulls code from an external GitHub repository (Codership’s GLB). While this is the official source, it does mean you’re fetching code at deploy time. In high-security environments, outbound internet access or running arbitrary latest code might be a concern. Consider vendoring the code or pinning to a specific release of GLB. At the very least, use reputable sources and check the integrity (the role doesn’t do a signature check – it just clones). Keep this in mind if your servers are in a restricted network; you might need to whitelist GitHub or host the code internally.
* **Auditing and Compliance:** Since GLB doesn’t create a new user or have its own auth, your focus should be on MySQL/MariaDB user security and host firewall rules. Ensure default MySQL accounts (like root with no password, etc.) are secured on the backend nodes. GLB will happily forward any login attempts to the DB – it doesn’t know if an attempt is malicious or legitimate. Use MySQL’s usual security measures (strong passwords, TLS, user grants limited by source host, etc.) in conjunction with GLB.

In summary, **treat the GLB node as part of your database trust zone**. Secure it like a database server: minimal services running, locked-down network access, and up-to-date patches. Restrict who can access the GLB host and its ports. By itself, this role doesn’t expose any more than a MySQL server would (port 3306) plus an optional admin port, but the presence of a proxy means you have one more component to secure and monitor in your database architecture.

## Mermaid Diagram

The following diagram illustrates a typical **HA deployment** of the Galera Load Balancer in front of a MariaDB Galera cluster. In this setup, two GLB nodes are configured with Keepalived to share a floating Virtual IP (VIP). One GLB node is active (MASTER) at any time, holding the VIP, while the other is on standby (BACKUP). Client applications connect to the VIP, and GLB forwards those connections to one of the database nodes in the Galera cluster:

```mermaid
flowchart TB
    client((Client Application))
    VIP{{Virtual IP (floating)}}
    subgraph GLB_Load_Balancers [GLB Load Balancer Nodes]
        LB1[GLB Node 1\n(MASTER – has VIP)]
        LB2[GLB Node 2\n(BACKUP)]
    end
    subgraph Galera_Cluster [MariaDB Galera Cluster]
        DB1[DB Node 1]
        DB2[DB Node 2]
        DB3[DB Node 3]
    end

    client -->|connects to| VIP
    VIP -->|active| LB1
    VIP -->|standby| LB2
    LB1 -->|forwards to| DB1
    LB1 --> DB2
    LB1 --> DB3
    LB2 -->|forwards to| DB1
    LB2 --> DB2
    LB2 --> DB3
```

In this diagram:

* **Client Application** – This represents one or more application servers or end-users that need to connect to the database. They are configured to use the **Virtual IP** for database connections (instead of addressing a specific DB node).
* **Virtual IP (VIP)** – A floating IP address managed by Keepalived (VRRP). At any given time, this IP is assigned to the MASTER GLB node. Clients always connect to this IP. If the MASTER fails, the BACKUP will take over this IP, so connectivity continues. (In the example group_vars, the VIP was `10.80.6.69` with VRID 51, but yours will vary.)
* **GLB Load Balancer Nodes** – Two (or more) servers running this role (GLB).

  * *GLB Node 1 (MASTER)* is currently holding the VIP and actively accepting client connections on port 3306.
  * *GLB Node 2 (BACKUP)* is running GLB as well, but clients aren’t reaching it because it does not have the VIP while in standby. It’s essentially idle, waiting for failover.
* **MariaDB Galera Cluster** – Three database nodes (the number can be 3 or more for Galera). All nodes are part of a Galera cluster, replicating data to each other (multi-master). Each node runs MariaDB and listens on port 3306. They are depicted as DB1, DB2, DB3.
* **Connection flow (normal operation)**: The client connects to the VIP. VIP directs traffic to GLB Node1 (since it’s the one holding the VIP). GLB Node1 then forwards the connection to one of the DB nodes (DB1/DB2/DB3) based on its load balancing algorithm (e.g., least connections). Subsequent client connections may go to different DB nodes, but all through GLB Node1.
* **Failover scenario**: If GLB Node1 goes down (or is removed for maintenance), Keepalived will trigger the VIP to move to GLB Node2. GLB Node2 becomes MASTER and starts receiving client connections (clients continue to use the same VIP IP, unaware of the change). GLB Node2 forwards connections to the DB cluster in the same way. This ensures that even if one load balancer node fails, database service continues via the other node.
* **Galera cluster handling**: Because Galera allows any node to accept writes, the load balancer doesn’t need to distinguish read vs write – it can treat all nodes equally. The cluster syncs writes across nodes. If one DB node fails, from GLB’s perspective, connections to it will fail and GLB will stop sending new connections to that node (if it cannot connect). In a failure, the remaining DB nodes still handle the traffic.

This HA architecture eliminates any single point of failure at the load balancer level: clients have a consistent endpoint (the VIP), and GLB + Keepalived ensure that endpoint is always served by an active node. Meanwhile, GLB distributes the load across the database nodes, preventing any one DB server from becoming a bottleneck under multi-connection workloads.

## Related Roles

* **keepalived_setup (VRRP for VIP):** To achieve high availability for the load balancer, use the **`keepalived_setup`** role in this repository. It installs and configures Keepalived to manage a floating IP address between multiple servers. When combined with `mariadb_galera_loadbalancer_install`, you would run Keepalived on the two (or more) GLB nodes so that one holds the VIP (Virtual IP) at a time. Clients connect to the VIP, and Keepalived handles failover if the primary node goes down. See the [keepalived_setup role README](../keepalived_setup/README.md) for usage details and ensure you set the same `virtual_router_id`, interface, VIP address, and priority on your GLB hosts accordingly.
* **haproxy (alternative load balancer):** The **haproxy** role provides an alternative approach to database load balancing. HAProxy is a widely-used TCP/HTTP load balancer that can also proxy MySQL traffic. It offers advanced features like health checks, detailed logging, and even read-write splitting (with some manual configuration or via ProxySQL in front). If your environment could benefit from these features or you prefer using a more familiar proxy, consider the [haproxy role’s README](../haproxy/README.md) for guidance. In a typical setup, two HAProxy instances can be deployed with Keepalived (similar to the GLB scenario) to provide HA. Keep in mind HAProxy introduces a bit more latency and complexity compared to GLB’s lightweight approach, but it’s very robust and configurable.
* **Galera Cluster Deployment:** While not a role within this repository, it’s worth mentioning that to set up the Galera cluster nodes themselves you might use a role like **`mrlesmithjr.mariadb_galera_cluster`** (which our playbook example references). Ensure the database cluster is configured and healthy *before* adding the load balancer on top. The GLB role assumes the cluster is up. In this repository’s context, the Galera cluster nodes are set up with an external role, and then `mariadb_galera_loadbalancer_install` is run to provide the proxy layer.
* **mariadb_backups:** If you are deploying a Galera cluster, you should also consider how to back up your databases. The **`mariadb_backups`** role (in this repository) can be used on one or more nodes of the cluster to perform SQL dumps of all databases. It’s not directly related to GLB, but it’s part of a complete database management strategy. Load balancing ensures high availability, and backups ensure data durability – both are important. See the `mariadb_backups` role for more information on setting up automated backups of the Galera cluster’s data.

Each of these roles and tools complements the `mariadb_galera_loadbalancer_install` role to build a reliable, production-ready database service:

* **GLB + Keepalived** for high availability and distribution of traffic.
* **HAProxy (or ProxySQL)** as alternative strategies if more complex load balancing or routing is needed.
* **Galera Cluster setup** to actually provide the multi-master database.
* **Backups and other maintenance** roles to round out the solution.

Using the above roles together, you can create a fully automated deployment of a highly available MariaDB Galera Cluster with robust failover, load balancing, and maintenance routines. Always refer to each role’s documentation for specifics and tune the configurations to your environment’s needs.
