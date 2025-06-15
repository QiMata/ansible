# ha_proxy_load_balancer_setup Ansible Role

*Ansible role for installing and configuring an HAProxy load balancer on Linux servers.*

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

The **ha_proxy_load_balancer_setup** role sets up the HAProxy service to load balance network traffic across multiple backend servers. It automates the installation of the HAProxy package and deploys a basic configuration with one frontend listening for client requests and one backend pool containing your servers. After running this role, HAProxy will be installed, configured with your specified backend servers, and running as a system service.

Key features of this role include:

* **Package Installation:** Ensures the latest **HAProxy** package is installed via the system package manager (APT) and that the HAProxy service is enabled and started on boot.
* **Automated Configuration:** Deploys an `/etc/haproxy/haproxy.cfg` configuration file based on template and variables. By default it defines a frontend on port 80 and a backend group of servers, using round-robin balancing (with optional sticky sessions).
* **Custom Error Pages:** Copies custom HTTP error pages (for codes 400, 403, 408, 500, 502, 503, 504) to `/etc/haproxy/errors/`, which HAProxy will serve for those HTTP error responses. This allows more user-friendly error messages than the HAProxy defaults.
* **Sticky Sessions (Optional):** Supports enabling **sticky sessions** for HTTP applications. When `ha_proxy_load_balancer_setup_sticky_sessions` is set to "yes", the role configures HAProxy to insert a cookie and use source IP hashing so that a client will consistently be served by the same backend server.
* **Idempotent and Minimal:** Running the role again will update the config if variables changed (or do nothing if no changes) and ensure HAProxy remains running. It makes only the necessary changes (installing HAProxy if not present, updating the config, etc.) and leaves other system settings untouched.

Typical use cases for this role include load balancing web servers, API servers, or other services where you want to distribute incoming traffic across multiple hosts. For high-availability setups, this role can be used on multiple load balancer nodes in conjunction with a virtual IP failover (see **keepalived** in this repository under [Known Issues and Gotchas](#known-issues-and-gotchas) for HA considerations). The role should be run with elevated privileges (`become: yes`), as it installs packages and writes to system directories.

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian**-family Linux distributions, specifically:

* **Debian**: 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu**: 20.04 LTS (Focal) and 22.04 LTS (Jammy)

> **Note:** The target hosts must be Debian/Ubuntu (or derivatives) because the role uses the APT package manager (`apt` module) to install HAProxy. Red Hat, CentOS, Alpine, or other non-APT-based systems are **not supported** without modifying the role (e.g. to use `yum` or another package module). Ensure you run this role on a supported OS to avoid package installation failures.

## Role Variables

Below is a list of the key variables for this role, along with their default values (defined in **`defaults/main.yml`**) and descriptions:

<!-- markdownlint-disable MD033 -->

<details><summary>Click to see default role variables.</summary>

| Variable                      | Default Value                                                                                                                  | Description |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`ha_proxy_load_balancer_setup_frontend_name`**   | `"http_frontend"`                                                                                                              | Name of the HAProxy frontend. This is an identifier used internally in the HAProxy configuration. It appears in the config and logs to label the frontend. |
| **`ha_proxy_load_balancer_setup_frontend_bind`**   | `"*:80"`                                                                                                                       | The address and port on which HAProxy will listen for incoming traffic. The default `"*:80"` binds to all network interfaces on port 80 (HTTP). Adjust this if you want HAProxy to listen on a specific interface or a different port. |
| **`ha_proxy_load_balancer_setup_backend_name`**    | `"http_backend"`                                                                                                               | Name of the HAProxy backend group. This identifier labels the backend pool of servers. The frontend will direct traffic to this backend. |
| **`ha_proxy_load_balancer_setup_backend_servers`** | *List of 2 servers* (`[ { name: "server1", address: "192.168.1.101:80" }, { name: "server2", address: "192.168.1.102:80" } ]`) | List of backend servers that HAProxy should load balance across. **Each list item** is a dictionary with: <br>`name` – a unique name for the server (used in HAProxy stats/logs). <br>`address` – the host/IP and port of the server (e.g. `"10.0.0.5:80"`). <br>All servers listed here will be included in the HAProxy config under the backend. By default two example servers are provided as placeholders – you should override this list with the actual servers in your inventory. |
| **`ha_proxy_load_balancer_setup_sticky_sessions`** | `no` (boolean false)                                                                                                           | Whether to enable sticky sessions (session persistence) for the backend. If set to `"yes"` (or true), HAProxy will add a persistence cookie and use the client's source IP to consistently route each client to the same backend server. By default it is `no`, meaning load balancing is purely round-robin with no session stickiness. |

</details>
<!-- markdownlint-enable MD033 -->

You can override any of these variables in your playbook or inventory to customize the HAProxy configuration. For example, to change the listening port to 8080 or to add more backend servers, set `ha_proxy_load_balancer_setup_frontend_bind: "*:8080"` or define your own `ha_proxy_load_balancer_setup_backend_servers` list in your host/group variables. Refer to the defaults above as a guide for proper structure and expected values.

## Tags

This role does not define any specific Ansible tags for its tasks. All tasks will run whenever the role is invoked. If you wish to control execution of this role via tags, you can tag the role in your playbook or apply your own tags when including the role. For example, in a playbook:

```yaml
- hosts: loadbalancers
  roles:
    - role: ha_proxy_load_balancer_setup
      tags: ['haproxy','loadbalancer']
```

In the above case, you could run `ansible-playbook play.yml -t haproxy` to execute only this role. By default, however, no tags are required to run **ha_proxy_load_balancer_setup** and all its tasks will always execute (assuming the role is included).

## Dependencies

**Ansible Collections:** None. This role uses only modules from the built-in Ansible distribution (e.g. `apt`, `template`, `copy`, `service` from **ansible.builtin**), so no additional Galaxy collections are needed.

**System Packages:** None that need to be pre-installed. The role will automatically install the required package **haproxy** on the target host using the system package manager. Make sure the target hosts have internet access to package repositories (or have an internal apt mirror configured) so that the installation can succeed. There are no other external software dependencies; everything needed to run HAProxy (and manage it as a service) is handled by the role.

**Role Dependencies:** None. This role is self-contained and does not depend on any other Ansible roles. It can be run on a host independently. (However, it is often used alongside other roles as part of a larger deployment – see the **Known Issues and Gotchas** and **Security Implications** for suggestions on complementary roles and configurations.)

## Example Playbook

To use this role, include it in a play targeting your load balancer host(s). Below is a minimal example of how to apply **ha_proxy_load_balancer_setup** in a playbook:

```yaml
- hosts: loadbalancers
  become: yes  # Ensure privilege escalation, since installing packages and editing /etc require root
  vars:
    ha_proxy_load_balancer_setup_frontend_bind: "*:80"            # Listen on port 80 (default; can be omitted if unchanged)
    ha_proxy_load_balancer_setup_backend_servers:                # Define the backend servers to load balance
      - name: web1
        address: 10.0.1.101:80
      - name: web2
        address: 10.0.1.102:80
    ha_proxy_load_balancer_setup_sticky_sessions: "yes"          # Enable sticky sessions (optional)
  roles:
    - ha_proxy_load_balancer_setup
```

**Explanation:** This play runs on the host group `loadbalancers` (which should contain your HAProxy server(s)). It elevates to root (`become: yes`) because the role needs administrative privileges. We override some role defaults in `vars`:

* We explicitly set `ha_proxy_load_balancer_setup_frontend_bind` to "*:80" (which is the default in this case, listening on port 80 on all interfaces).
* We define two backend servers (web1 and web2 with their IPs and ports) that HAProxy will distribute traffic to. In a real scenario, replace these with the actual IP addresses (or hostnames) and ports of your application servers.
* We enable `ha_proxy_load_balancer_setup_sticky_sessions` to demonstrate sticky session usage. With this on, HAProxy will ensure each unique client sticks to one backend (useful for stateful web sessions). If you prefer pure load balancing without session affinity, leave this at default "no".

After running this playbook, HAProxy will be installed on the target host, listening on port 80, and forwarding traffic to `web1` and `web2`. You can adjust or add variables as needed (for example, changing ports or adding more servers). For a more complex scenario (such as also listening on HTTPS/443 or load balancing multiple services), additional customization or a more advanced role might be required (see **Known Issues and Gotchas**).

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to verify that it works as expected in a controlled environment before deploying to production. The basic steps to test **ha_proxy_load_balancer_setup** with Molecule are:

1. **Install Molecule and dependencies:** Ensure you have Molecule installed on your development machine, along with Docker. For example, use pip to install: `pip install molecule[docker]` (this installs Molecule and the Docker support). Also, have Docker running, as Molecule will create test containers.
2. **Prepare a test scenario:** If this role comes with a predefined Molecule scenario (check for a `molecule/` directory in the role), you can use that. Otherwise, you can initialize a new scenario for this role by running:

   ```bash
   molecule init scenario -r ha_proxy_load_balancer_setup -d docker
   ```

   This will create a `molecule/default` scenario using Docker. You can customize the `molecule.yml` (to specify a base image, e.g., an Ubuntu image) and the `converge.yml` playbook if needed. By default, the converge playbook will apply this role to a container.
3. **Run the Molecule test sequence:** Execute `molecule converge` to create a Docker container and apply the role inside it. Molecule will use the playbook in `molecule/default/converge.yml` (or the scenario you set up) to run **ha_proxy_load_balancer_setup** on the container. This step performs the actual role tasks in a clean environment.
4. **Verify the outcomes:** After convergence, you can verify that the role did its job. For example:

   * Run `molecule login` (or `docker exec -it <container_id> /bin/bash`) to open a shell in the test container.
   * Check that HAProxy is installed by running `haproxy -v` (it should show the HAProxy version) and that the service is running (`systemctl status haproxy` or `service haproxy status`).
   * Examine the generated config file `/etc/haproxy/haproxy.cfg` inside the container to ensure the frontend and backend settings match your expectations (e.g., the backend servers list, sticky setting if enabled, etc.).
   * If you have a simple web service running on one of the backend addresses (for testing), you could try sending a test HTTP request through HAProxy (for example, `curl http://localhost` inside the container) and observe if HAProxy forwards it (in a basic test without real backends, HAProxy may return a 503 if backends are down – which is expected in that case).
   * (Optional) If the role or scenario includes automated tests (e.g., with Testinfra or Inspec in a `verify.yml`), run `molecule verify` to execute those tests.
5. **Cleanup:** Once testing is done, use `molecule destroy` to tear down the test container and free resources. You can also run the full test cycle (create, converge, verify, destroy) in one step with `molecule test`.

Using Molecule helps ensure that the role is **idempotent** (running it twice yields no changes if the system is already configured) and that it works on a fresh system of the target OS. During testing, you may customize variables to simulate different scenarios. For instance, you could change `ha_proxy_load_balancer_setup_backend_servers` to point to a reachable dummy service or adjust `ha_proxy_load_balancer_setup_frontend_bind` to another port to ensure those settings apply correctly. Always verify that applying the role multiple times does not produce changes on the second run (which indicates idempotence).

## Known Issues and Gotchas

When using the **ha_proxy_load_balancer_setup** role, keep in mind the following points, caveats, and common pitfalls:

* **Debian/Ubuntu Only:** As noted, this role is hard-coded to use the APT package manager. Attempting to run it on a Red Hat/CentOS system (or others without apt) will fail during the package installation task. Use it only on Debian-based systems or modify the package installation step to suit your OS if needed.
* **Default Backend Servers are Placeholders:** The default `ha_proxy_load_balancer_setup_backend_servers` list in this role is an example with IPs `192.168.1.101` and `192.168.1.102`. These are **not** meant to be real servers in your environment. If you do not override this variable, HAProxy will be configured with those dummy addresses, which likely do not exist in your network. HAProxy will still start (and mark those servers as down), but it won't actually forward traffic to any real service. **Solution:** Always set `ha_proxy_load_balancer_setup_backend_servers` to the actual backend hosts/ports you intend to load balance. This is typically done in your inventory group_vars or playbook (as shown in the example).
* **Single Frontend/Backend Configuration:** This role is designed to set up one frontend and one backend group. All traffic hitting the specified frontend port will be directed to the configured list of backend servers. If you require multiple frontends or more complex routing (e.g., HTTP vs HTTPS, or multiple services on different ports), you will need to adjust the HAProxy configuration template or use a more advanced role. In this repository, the **haproxy** role (if available) or a custom HAProxy configuration might be more suitable for complex scenarios. Out of the box, **ha_proxy_load_balancer_setup** aims for a simple, common use-case configuration.
* **No HTTPS/SSL Termination by Default:** This role’s default config listens on port 80 (HTTP) and does not include HTTPS termination. If you need HAProxy to handle TLS/SSL, you will have to obtain certificates (e.g., via Let’s Encrypt or your CA) and modify the HAProxy configuration accordingly (for example, binding to `*:443` with the `ssl crt` option). The role does not manage TLS certificates or keys. You may consider using a companion role or manual steps to set up SSL. For instance, you could use a role like **letsencrypt_godaddy** (present in this repository) to get a certificate, then adjust this role’s variables or template to reference that certificate in the bind line. Not addressing TLS means traffic is unencrypted; in secure environments, plan accordingly.
* **Firewall Considerations:** The role itself does not configure any firewall. If your servers have an active firewall (iptables, ufw, firewalld, etc.), you must ensure that the HAProxy listening port (e.g., 80, and 443 if used) is allowed through. For example, if using Ubuntu's UFW, open port 80 for the load balancer. In the context of this repository, the **Base** role or a planned **UFW** role might handle general firewall settings. Just remember that after running this role, HAProxy will expect to receive traffic on the frontend port – if a firewall blocks it, clients won’t be able to reach the service.
* **Ensure Sufficient Privileges:** All tasks in this role assume they are run with root privileges. Failing to run with `become: yes` can lead to permission denied errors (e.g., when installing packages or writing to `/etc/haproxy/haproxy.cfg`). Always run the role with the appropriate privilege escalation. In most cases, your playbook should include `become: yes` for the hosts targeted by this role (see the example playbook above).
* **HAProxy Config Overwrites:** This role will overwrite the `/etc/haproxy/haproxy.cfg` file on each run with the template-driven configuration. If you manually modify that file on the system, those changes will be lost next time the role runs. Treat the role variables (and template) as the source of truth for HAProxy’s config. If you need to add custom HAProxy settings not exposed via role variables, you might incorporate them into the template or use a separate task/role to manage those after this role runs.
* **Reload vs Restart:** The role uses a handler to restart HAProxy whenever the config changes. A full restart will briefly interrupt traffic. In many cases, HAProxy can reload configurations with minimal downtime (using `reload` instead of `restart`), but this role opts for a simple restart. For most small setups this is fine (restarts are quick). If you require zero-downtime reloads, you may need to modify the handler to use `state: reloaded` or a more complex approach.
* **High Availability (HA) Setup:** By itself, a single HAProxy instance is a potential single point of failure. This role doesn’t set up multiple HAProxy nodes or any failover mechanism. If you need a highly available load balancer, consider running HAProxy on two or more nodes and using a tool like Keepalived for failover. This repository provides a **[keepalived](../keepalived/README.md)** role that can be used to create a virtual IP address shared by multiple HAProxy servers. Using keepalived, if the primary load balancer goes down, the secondary can take over the VIP, ensuring continued service. Keep in mind you’d run this HAProxy role on both nodes (pointing to the same backends) and then apply the keepalived role to manage the failover IP. HAProxy itself is stateless (especially with sticky sessions off), so active-passive failover is generally straightforward.
* **Backend Health and Monitoring:** HAProxy will automatically mark a backend server as down if it fails health checks (it uses a simple TCP check by default on each server as configured in this role). The role’s configuration uses the default check settings. If a backend is down at the time of role execution, HAProxy will log it and not send traffic to it. Ensure your backends are reachable (ping/connection) from the HAProxy server. If needed, you can adjust health check settings (e.g., using `option httpchk` for HTTP services or modifying check intervals) by customizing the template.
* **Sticky Sessions Caveat:** When `ha_proxy_load_balancer_setup_sticky_sessions` is enabled, HAProxy inserts a cookie named `SERVERID` and uses a source IP hash for balancing. This means all requests from a given client will go to the same backend server as long as that cookie persists. Be aware that if clients are behind a NAT or proxy, many clients could share one source IP and thus all go to the same backend (potentially uneven distribution). Also, if a backend goes down, those sessions will be lost and HAProxy will send clients to a different server (by design). In short, use sticky sessions only if necessary (e.g., your application requires session affinity), and understand the trade-offs. If not needed, keep it `no` for true load balancing rotation.

## Security Implications

Deploying an HAProxy load balancer with this role has a few security considerations to keep in mind:

* **Open Ports:** By default HAProxy will listen on port **80/tcp** on all network interfaces. This means the server will accept HTTP traffic from anywhere (unless restricted by external means). If this server is in a DMZ or exposed to the internet, ensure that this is intended. You might want to restrict listening to a specific interface/IP (by changing `ha_proxy_load_balancer_setup_frontend_bind`) if the server has multiple network interfaces or if you only want to allow internal traffic. Additionally, consider using firewall rules to limit who can access port 80 (e.g., allow only certain IP ranges).
* **No Encryption (HTTP Only):** Traffic through the load balancer is not encrypted by default (it's HTTP). If you are load balancing sensitive data or internet-facing applications, not using HTTPS is a security risk (data can be intercepted or modified in transit). As noted in **Known Issues**, this role doesn’t configure SSL termination. The recommendation is to implement TLS – either by offloading SSL at HAProxy (obtaining and configuring a certificate on HAProxy) or by having another component handle TLS (e.g., a reverse proxy in front of HAProxy, or TLS on the backend servers). If you add SSL to HAProxy, ensure that private keys are stored securely (HAProxy will need access to the certificate and key file) and consider using strong ciphers.
* **HAProxy Process Security:** The HAProxy service, as configured by this role, drops privileges and runs as a non-root user for improved security. In the generated config, HAProxy is set to run as user **haproxy** and group **haproxy**, and to chroot to `/var/lib/haproxy`. These settings (which come from the template’s global section) help limit the impact of any compromise: running as a low-privilege user and within a chroot jail means that if HAProxy were exploited, the damage is contained to the `/var/lib/haproxy` directory and the haproxy user’s privileges. This is a security best practice and is enabled by default in this role's configuration.
* **Local Admin Socket:** The HAProxy configuration includes a local UNIX domain socket for administrative commands: `/run/haproxy/admin.sock` with permissions 660 and level admin. This socket allows admin-level control of HAProxy (e.g., to dynamically change server states or get stats) but is only accessible by root or users in the **haproxy** group. By default, only root and the haproxy user itself are in that group. This is fairly secure, but you should be aware of it. Do not add untrusted users to the haproxy group. If your security policy requires, you can disable the admin socket or restrict it further. On the flip side, if you need to use the socket (for monitoring or control via scripts), ensure your processes have the appropriate permissions.
* **Service Enablement:** This role enables the haproxy service to start on boot. From a security perspective, this means that whenever the server reboots, HAProxy will automatically come up and listen on the configured port. Ensure that is acceptable in your deployment scenario (usually it is, since you want the load balancer to be persistent). If for some reason you do not want HAProxy to auto-start, you would need to override this behavior (e.g., by disabling the service after provisioning).
* **User Accounts:** The installation of HAProxy via the package manager will typically create a system user account called `haproxy`. This account is used to run the HAProxy process (as mentioned above). It is not an interactive login account. You should ensure this account remains a system account (no shell or login) and is not used for other purposes. The role does not manipulate this user beyond relying on it in the config.
* **Log Data:** HAProxy will log requests and errors via the local syslog (using facilities local0 and local1). Ensure your system’s rsyslog or journald is configured to handle these logs. Logs can contain client IPs and URLs, which are sensitive information. Treat the log files with care (standard practice: they are usually in `/var/log/haproxy.log` or integrated into syslog). Make sure log permissions and rotation policies meet your security requirements. If shipping logs to a central system, consider who can access them.
* **Backend Server Security:** While not directly controlled by this role, remember that HAProxy is routing traffic to your backend servers. Ensure that those backend systems are secured (they might be on an internal network, but if HAProxy is internet-facing, the backends will now indirectly receive internet traffic). Harden the backend servers and ensure only HAProxy (and intended clients) can reach them. If the traffic is internal, maybe restrict backend service firewall to only accept connections from the HAProxy host.
* **Upstream Trust:** HAProxy by default does not do any application-layer filtering – it simply proxies requests. If you need to enforce HTTPS to the backend or perform any deep packet inspection or WAF (Web Application Firewall) functions, those are beyond the scope of this role. Consider additional security layers or more advanced HAProxy configurations if needed.

In summary, the **ha_proxy_load_balancer_setup** role will introduce a publicly reachable service on your host (by default, HTTP on port 80) and run a privileged network proxy (HAProxy) with reduced privileges. Follow best practices by restricting network access where appropriate, enabling TLS if handling sensitive traffic, and keeping your system and HAProxy updated. By default, the role’s configuration aligns with secure defaults (non-root user, chroot jail, no open admin ports), but you must operate it in a secure environment and context. Regularly review HAProxy’s access logs and monitor for any suspicious activity, as you would for any public-facing service.
