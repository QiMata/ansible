# Ansible Role: HAProxy

*Advanced Ansible role to install and configure the **HAProxy** load balancer on Linux servers with comprehensive enterprise features.*

**Table of Contents**

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Advanced Features](#advanced-features)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)

## Overview

The **HAProxy** role sets up the HAProxy load balancing service on a target host with enterprise-grade features. It installs HAProxy using the system package manager and deploys a comprehensive configuration to handle client traffic with advanced capabilities. This role is designed to be **idempotent** and supports complex production scenarios. Key features include:

### Core Features
* Installation of the HAProxy package (via apt on Debian/Ubuntu or yum/dnf on RHEL/CentOS) and automatic enabling/start of the HAProxy service.
* Template-driven configuration for HAProxy with support for multiple frontends and backends
* **SSL termination** support with multiple certificate management and SNI support
* **Statistics web interface** with comprehensive monitoring capabilities
* Configurable load balancing algorithms and health check behavior

### Advanced Features
* **Multiple frontends/backends**: Support for complex multi-service architectures
* **ACL support**: Advanced Access Control Lists for traffic routing and security
* **Content switching**: Route traffic based on URL paths, headers, and other criteria
* **Advanced health checks**: Customizable HTTP, TCP, and external monitoring integration
* **Rate limiting and DDoS protection**: Connection throttling and request rate limiting
* **Compression**: Built-in gzip/deflate compression support
* **Caching**: Integrated caching mechanisms for improved performance
* **SSL/TLS security**: Advanced cipher suite configuration and security headers
* **HSTS support**: HTTP Strict Transport Security implementation
* **SSL redirect**: Automatic HTTP to HTTPS redirection
* **Prometheus metrics**: Native metrics export for monitoring
* **Custom logging**: Flexible logging configuration with header capture
* **Peer synchronization**: Stick-table synchronization between HAProxy instances
* **Weighted load balancing**: Server weight configuration and backup server support
* **IP restrictions**: Whitelist/blacklist functionality with ACL-based access control
* **Request filtering**: Protection against malicious requests and method blocking
* **Zero-downtime deployments**: Seamless configuration updates and graceful reloads
* **Runtime API**: Dynamic server management and configuration updates
* **Configuration validation**: Pre-deployment validation and automatic backup/restore

### Operational Excellence
* **Configuration backup**: Automatic configuration backup before changes
* **Health check validation**: Post-deployment validation and monitoring
* **Error page customization**: Custom error pages for better user experience
* **Firewall integration**: Automatic firewall rule configuration
* **Log management**: Advanced logging with rsyslog integration

By default, the role maintains backward compatibility with existing configurations while providing access to advanced features through additional variable configuration.

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian**-family and **Red Hat**-family Linux distributions, specifically:

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal), 22.04 LTS (Jammy), and 24.04 LTS (Noble)
* **Red Hat Enterprise Linux** – 8 and 9
* **CentOS** – 8 and 9 (Stream)
* **Rocky Linux** – 8 and 9
* **AlmaLinux** – 8 and 9

The role automatically detects the OS family and uses the appropriate package manager (`apt` for Debian-based systems, `yum`/`dnf` for Red Hat-based systems). Ensure you run this role on a supported OS to avoid issues.

## Role Variables

Below is a list of important variables for this role, along with their default values (defined in **`defaults/main.yml`**) and descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                              | Default Value                                        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`haproxy_package_name`**            | "haproxy"                                          | Name of the HAProxy package to install via the OS package manager. In most cases the default "haproxy" is correct (installs the distribution-provided HAProxy package). Override this only if you need a custom package name or specific version.                                                                                                                                                                                                                                                                                                                                                                                                   |
| **`haproxy_service_name`**            | "haproxy"                                          | Name of the HAProxy service. Used when controlling the service (enable/start/reload). Usually "haproxy"; change only if your OS uses a different service name.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **`haproxy_frontend_name`**           | "hafrontend"                                       | Identifier for the frontend in the HAProxy configuration. This becomes the label of the `frontend` section in haproxy.cfg. Mostly cosmetic, used in logs and stats output.                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **`haproxy_frontend_bind_address`**   | "*"                                                | Address on which HAProxy will bind for the frontend listener. "*" means all network interfaces. You can specify an IP (e.g., `0.0.0.0` for all IPv4, or a specific interface IP) to restrict listening.                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **`haproxy_frontend_port`**           | 80                                                 | Port number for the frontend listener. Default is 80 (HTTP). Change this to 443 for HTTPS or any other port as needed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **`haproxy_frontend_mode`**           | "http"                                             | Mode of traffic handling on the frontend. Common values are "http" for HTTP(s) traffic (layer 7) or "tcp" for raw TCP (layer 4) load balancing. This should match the type of service you are load balancing.                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **`haproxy_backend_name`**            | "habackend"                                        | Identifier for the backend server pool. This becomes the label of the `backend` section in haproxy.cfg.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **`haproxy_backend_mode`**            | {{ haproxy_frontend_mode }} (defaults to "http") | Mode for connections to backend servers. By default, it inherits the same mode as the frontend. Typically this should be left as-is (HTTP mode if frontend is HTTP, or TCP if frontend is TCP) to maintain consistency in how traffic is handled.                                                                                                                                                                                                                                                                                                                                                                                                     |
| **`haproxy_backend_balance_method`**  | "roundrobin"                                       | Load balancing algorithm for distributing traffic among backend servers. Default is "roundrobin" (rotate evenly). Other common options include "leastconn" (least connections) or "source" (source IP hash) depending on your requirements.                                                                                                                                                                                                                                                                                                                                                                                                     |

</details>

## Advanced Features

This role now includes comprehensive enterprise-grade features for production deployments:

### Multiple Frontends and Backends

Configure multiple frontends and backends for complex architectures:

```yaml
haproxy_frontends:
  - name: web_frontend
    bind_address: "*"
    port: 80
    mode: "http"
    default_backend: web_backend
    ssl_redirect: true
  - name: api_frontend
    bind_address: "*"
    port: 443
    mode: "http"
    ssl_certificate: "/etc/haproxy/certs/api.pem"
    default_backend: api_backend

haproxy_backends:
  - name: web_backend
    mode: "http"
    balance_method: "roundrobin"
    servers:
      - name: web1
        address: "192.168.1.10:80"
        weight: 100
      - name: web2
        address: "192.168.1.11:80"
        weight: 100
  - name: api_backend
    mode: "http"
    balance_method: "leastconn"
    servers:
      - name: api1
        address: "192.168.1.20:8080"
        backup: false
      - name: api2
        address: "192.168.1.21:8080"
        backup: true
```

### Access Control Lists (ACLs) and Content Switching

Route traffic based on various criteria:

```yaml
haproxy_acls:
  - name: "is_api"
    condition: "path_beg /api/"
  - name: "is_admin"
    condition: "path_beg /admin/"
  - name: "trusted_ips"
    condition: "src 192.168.1.0/24 10.0.0.0/8"

haproxy_use_backends:
  - condition: "is_api"
    backend: "api_backend"
  - condition: "is_admin"
    backend: "admin_backend"
```

### SSL/TLS Security Enhancements

Configure advanced SSL settings:

```yaml
haproxy_global_ssl_default_bind_ciphers: "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!SHA1:!AESCCM"
haproxy_global_ssl_default_bind_options: "ssl-min-ver TLSv1.2 no-tls-tickets"

haproxy_ssl_certificates:
  - path: "/etc/haproxy/certs/example.com.pem"
    content: "{{ vault_example_com_cert }}"
  - path: "/etc/haproxy/certs/api.example.com.pem"
    content: "{{ vault_api_example_com_cert }}"

haproxy_hsts:
  enable: true
  max_age: 31536000
  include_subdomains: true

haproxy_ssl_redirect:
  enable: true
  redirect_code: 301
```

### Rate Limiting and DDoS Protection

Protect against abuse:

```yaml
haproxy_rate_limiting:
  enable: true
  stick_table_type: "ip"
  stick_table_size: "100k"
  stick_table_expire: "30s"
  http_req_rate: 20
  http_req_burst: 50
  tarpit_timeout: "10s"

haproxy_ip_restrictions:
  whitelist:
    - "192.168.1.0/24"
    - "10.0.0.0/8"
  blacklist:
    - "1.2.3.4"
    - "5.6.7.0/24"
```

### Advanced Health Checks

Configure comprehensive health monitoring:

```yaml
haproxy_health_checks:
  - name: "http_check"
    type: "http"
    uri: "/health"
    expect: "string ok"
  - name: "tcp_check"
    type: "tcp"

haproxy_external_monitoring:
  enable: true
  agent_check: true
  agent_port: 9999
```

### Compression and Caching

Optimize performance:

```yaml
haproxy_compression:
  enable: true
  algorithms: ["gzip", "deflate"]
  types: ["text/html", "text/plain", "text/css", "application/javascript"]

haproxy_caching:
  enable: true
  caches:
    - name: "web_cache"
      total_max_size: "256m"
      max_object_size: "10m"
      max_age: "3600s"
```

### Prometheus Metrics

Enable monitoring integration:

```yaml
haproxy_prometheus:
  enable: true
  bind_address: "127.0.0.1"
  port: 9101
  uri: "/metrics"
```

### Zero-Downtime Deployments

Enable seamless updates:

```yaml
haproxy_zero_downtime:
  enable: true
  graceful_reload: true
  reload_timeout: "30s"
```

### Runtime API Management

Dynamic server management:

```yaml
haproxy_runtime_api:
  enable: true
  socket_path: "/run/haproxy/admin.sock"
  socket_mode: "660"
  socket_level: "admin"
```

### Peer Synchronization

Synchronize stick tables between HAProxy instances:

```yaml
haproxy_peers:
  enable: true
  peers:
    - name: "haproxy1"
      address: "192.168.1.10:1024"
    - name: "haproxy2"
      address: "192.168.1.11:1024"
```
| **`haproxy_backend_httpchk`**         | *Empty string* ""                                  | HTTP health check request for backend servers. If set (e.g., "GET /healthz" or a full HTTP request line), HAProxy will periodically perform HTTP checks to determine backend health. Leave this empty to disable HTTP health checks (HAProxy will use layer4 checks or mark servers up by default).                                                                                                                                                                                                                                                                                                                                                 |
| **`haproxy_backend_servers`**         | *Empty list* []                                    | List of backend servers in the pool. **This must be provided by the user**, since by default no servers are configured. Each list item is a mapping with keys: <br>`name`: a unique name for the server (for identification in stats/logs) <br>`address`: the host/IP and port of the server (e.g., "192.168.1.10:80"). For example: <br>`yaml<br>haproxy_backend_servers:<br>  - name: app1<br>    address: 192.168.1.10:80<br>  - name: app2<br>    address: 192.168.1.11:80<br>`                                                                                                                                                                 |
| **`haproxy_global_vars`**             | *(see defaults)*                                     | List of configuration lines to place in the **global** section of haproxy.cfg. By default, this includes:<br>`log 127.0.0.1 local0` (enable logging to local syslog)<br>`log 127.0.0.1 local1 notice` (log facility/level)<br>`chroot /var/lib/haproxy` (chroot directory for HAProxy process)<br>`user haproxy` / `group haproxy` (drop privileges to haproxy user/group)<br>`daemon` (run in background as a daemon). You can override this list to add or change global settings (for instance, to adjust logging or add `maxconn` if needed).                                                                                                     |
| **`haproxy_defaults_vars`**           | *(see defaults)*                                     | List of configuration lines for the **defaults** section in haproxy.cfg. By default, this includes typical HTTP settings: <br>`option httplog` (enable HTTP logging format)<br>`option dontlognull` (don't log health check or empty connections)<br>`timeout connect 5s`<br>`timeout client 50s`<br>`timeout server 50s`. You can override this list to customize default timeouts or options (e.g., to add `retries` or change log verbosity).                                                                                                                                                                                                      |
| **`haproxy_ssl_certificate`**         | *Empty string* ""                                  | Filesystem path where an SSL/TLS certificate (combined certificate and private key) will be stored for HAProxy to use on the frontend. If you want HAProxy to terminate SSL/TLS, set this to a path (e.g., "/etc/haproxy/certs/your_site.pem"). When this is non-empty and you provide `haproxy_ssl_certificate_content`, the role will copy the certificate file to this path. If left empty, no SSL will be configured on the frontend.                                                                                                                                                                                                           |
| **`haproxy_ssl_certificate_content`** | *Empty string* ""                                  | The actual content of the SSL certificate file to deploy, including the private key (usually in PEM format). This should be the **combined certificate chain and private key** that HAProxy will use. Provide this as a multi-line string (for example, via an Ansible Vault variable for security). When set along with `haproxy_ssl_certificate`, the role will write this content to the specified path with appropriate permissions. If you prefer to manage the certificate file manually, you can set `haproxy_ssl_certificate` (path) and leave this empty – the role will then skip deploying the file, but still reference it in the config. |
| **`haproxy_stats_enable`**            | false                                              | Whether to enable the HAProxy statistics web interface. Default is false (stats disabled). Set to true to add a `listen stats` section to the configuration, which provides a web dashboard for HAProxy status.                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **`haproxy_stats_user`**              | "admin"                                            | Username for accessing the HAProxy stats page (if enabled). The default is "admin". **Change this for production** to something less predictable.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **`haproxy_stats_password`**          | "admin"                                            | Password for the HAProxy stats page. Default "admin". **Change this for production**. Anyone with these credentials can view stats and potentially change server states via the UI.                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **`haproxy_stats_port`**              | 9000                                               | Port on which the HAProxy stats interface will listen (if enabled). Default is 9000. You might change this to a different port as needed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **`haproxy_stats_bind_address`**      | "127.0.0.1"                                        | Bind address for the stats interface. Default is 127.0.0.1 (accessible only from the local machine). You can set this to 0.0.0.0 or another IP to allow remote access to stats, but ensure you have proper security (firewalls, credentials) if exposing it.                                                                                                                                                                                                                                                                                                                                                                                      |

</details>

## Tags

This role does **not define any Ansible tags** in its tasks. All tasks will run by default when the role is invoked. (You may still apply tags externally when including the role, if desired.)

## Dependencies

* **Ansible Version:** Requires Ansible **2.10** or higher. This role uses modern syntax and modules (e.g., `ansible.builtin.apt`), which are available in Ansible 2.10+.
* **Collections:** No external Ansible collections are required. All modules used (apt, template, copy, file, service) are part of the built-in Ansible distribution.
* **External Roles/Packages:** No other roles are required. The HAProxy package itself will be installed from the OS repositories. (Ensure the target hosts have access to the appropriate package repository for HAProxy, which is usually the default for Debian/Ubuntu.)

## Example Playbook

Here is an example of how to use the `haproxy` role in a playbook. This play will set up a basic HTTP load balancer listening on port 80 and forwarding traffic to two backend web servers:

```yaml
- hosts: loadbalancers
  become: yes
  vars:
    haproxy_backend_servers:
      - name: web1
        address: "10.0.0.10:80"
      - name: web2
        address: "10.0.0.11:80"
  roles:
    - haproxy
```

In the above play, HAProxy will listen on **port 80** (the default `haproxy_frontend_port`) on all interfaces and balance incoming requests between two backend servers (`web1` and `web2`). We did not specify `haproxy_frontend_mode`, so it defaults to "http", and thus the backend connections will also use HTTP mode. No SSL certificate is provided in this example, so HAProxy will terminate traffic in plain HTTP. The stats interface remains disabled (default).

For an HTTPS load balancer, you would set `haproxy_frontend_port: 443` and provide the `haproxy_ssl_certificate` (path) along with `haproxy_ssl_certificate_content`. This will configure HAProxy to listen with TLS. For example, you might store your certificate and key in an Ansible Vault variable and assign them to these vars. Additionally, if you want to enable the HAProxy stats page, set `haproxy_stats_enable: true` and adjust `haproxy_stats_user`/`haproxy_stats_password` to secure credentials. Ensure that port 9000 (or your chosen stats port) is firewalled or bound to localhost unless you explicitly want it accessible.

Typically, you will assign this role to hosts designated as load balancers (e.g., in an inventory group like **`loadbalancers`**). After running the play, HAProxy will be installed and running with your specified configuration. You can then point clients or DNS to the HAProxy host(s) to distribute traffic to the backend servers.

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to ensure it works correctly in your environment before deploying to production. Below are general steps to run tests for the `haproxy` role:

1. **Install Molecule** (and Docker) on your development machine if you haven’t already. For example: `pip install molecule[docker]` to get Molecule with Docker support. Ensure Docker is installed and the daemon is running.
2. **Prepare a test scenario:** If a Molecule scenario is provided with this role (e.g., under `roles/haproxy/molecule/default/`), you can use that. Otherwise, you can create a new scenario by running `molecule init scenario -r haproxy -d docker`. This will set up a basic Molecule configuration for the HAProxy role.
3. **Run the role in a container:** Execute `molecule converge` to spin up a Docker container (by default, Molecule will likely use a Debian or Ubuntu image) and apply the `haproxy` role to it. Molecule will use the playbook in `molecule/default/converge.yml` (or the scenario’s converge playbook) to run the role inside the container.
4. **Verify the results:** After the converge step, verify that HAProxy was installed and configured correctly. You can check the container’s `/etc/haproxy/haproxy.cfg` to see that it contains the expected frontend/backend configuration and any variables you set. Since the container might not have a full init system, the HAProxy service may or may not be running; however, you can perform a config check by running `haproxy -c -f /etc/haproxy/haproxy.cfg` inside the container to validate the configuration. If you included backend servers in your test, you could also install curl and try hitting HAProxy (e.g., `curl http://localhost:80`) within the container to see if it proxies (if test web servers are accessible or you simulate them).
5. **Cleanup:** When finished testing, run `molecule destroy` to tear down the test container. Alternatively, running `molecule test` will perform the entire sequence (create, converge, verify, destroy) in one go.

Using Molecule helps ensure that the role is **idempotent** (running it repeatedly yields the same result) and that it works on a clean system. During testing, you might adjust variables as needed. For example, if you don’t have real backend servers for the test, you can use dummy IPs and just verify the config file is populated, or spin up simple web server containers to act as backends. Always review the Molecule output for any errors or warnings and adjust the role or variables accordingly before deploying in a live environment.

## Known Issues and Gotchas

* **Debian-based OS only:** This role currently supports **Debian/Ubuntu** systems. It uses the `apt` module to install HAProxy and does not include tasks for YUM/dnf or other package managers. Attempting to run it on Red Hat, CentOS, or other non-Debian systems will result in skipped installation tasks and a failed setup. Use a Debian-based target or modify the role to support other OS families if needed.
* **Ensure backend servers are defined:** You must provide at least one backend server in `haproxy_backend_servers` for HAProxy to be useful. An empty backend server list (the default) means HAProxy will have no real servers to route traffic to. In such a case, HAProxy might still start, but any client requests will fail because the sole backend has no members (and will be considered down). Always set `haproxy_backend_servers` to reflect your actual backend nodes. If you run the role without defining any servers, remember to update the configuration later by adding servers and re-running the role (or editing the haproxy.cfg).
* **HAProxy package availability and apt update:** This role does not force an `apt-get update` before installing. If the apt package index on the target host is outdated, the installation of HAProxy could fail (unable to find the package). It’s good practice to run an update (for example, include the **`base`** role from this repository, which updates the system packages, or manually ensure `apt update` is run) prior to applying this role on a fresh server. This will ensure the HAProxy package can be found and installed successfully.
* **SSL certificate format and usage:** If you enable SSL termination (by setting `haproxy_frontend_port` to 443 and providing certificate details), make sure your certificate and key are in the correct format. HAProxy expects a PEM file that contains the **private key and the full certificate chain** (server cert + intermediates). The role will place whatever you provide in `haproxy_ssl_certificate_content` into the file path `haproxy_ssl_certificate`. If the file is misformatted or the key is incorrect, HAProxy will fail to start or reload. Always double-check that your certificate content is correct. It's often helpful to test the haproxy configuration with `haproxy -c` as mentioned above, which will report any issues with the certificate or config.
* **Default credentials on stats page:** If you turn on the HAProxy stats interface (`haproxy_stats_enable: true`), note that the default login is **admin / admin**. This is set in defaults for convenience, but **do not use the default credentials in production**. Anyone who can access the stats URL can see potentially sensitive info (and even disable backends). Always override `haproxy_stats_user` and `haproxy_stats_password` to strong, unique values. Also consider leaving `haproxy_stats_bind_address` as 127.0.0.1 (so stats are only accessible via SSH tunnel or localhost) or otherwise restrict access to the stats port with firewall rules if binding it to a network interface.
* **Single frontend/backend limitation:** The role’s provided configuration template supports **one frontend and one backend** out-of-the-box. This covers many simple use cases (one service or URL being load balanced). However, if you need multiple frontends or backends (for example, HAProxy handling two different sites or ports), you will need to extend the configuration. That could involve modifying the Jinja2 template to loop over multiple frontends/backends or invoking this role multiple times with different variables (which is not straightforward in a single play). Be aware of this design choice. In scenarios requiring more complex HAProxy config (multiple listener ports, ACLs, content switching, etc.), you may need to customize the role or use a different approach.
* **Reload vs Restart behavior:** The role uses a handler to **reload** HAProxy after deploying a new config (`service: state=reloaded`). A reload (graceful restart) will apply new settings without dropping existing connections. This is generally desirable for config changes. However, note that if HAProxy is not already running (e.g., on first install or if it was stopped), a reload command might not start it. The role ensures to start the service after installation, so this is usually fine. Just remember that on initial deployment, the service is started fresh (there is effectively no difference between start and reload at first run), whereas subsequent changes trigger reloads.
* **Firewall and SELinux considerations:** This role does not manage firewall rules. If your servers have a firewall (such as UFW, firewalld, or security groups in cloud environments), you must ensure that the frontend port (e.g., 80/443) and the stats port (if enabled) are allowed as appropriate. Similarly, on systems with SELinux or AppArmor, make sure that HAProxy is allowed to bind to the needed ports and read the certificate file. On Debian/Ubuntu, AppArmor profiles for HAProxy might restrict it; the role’s default placement of certs in `/etc/haproxy/certs` is aligned with standard expectations, but if you customize paths, ensure policy adjustments as needed.

## Security Implications

* **System User:** When installed, **HAProxy** runs under a dedicated system account (`haproxy` user and group). This role’s configuration (in `haproxy_global_vars`) explicitly sets HAProxy to drop privileges to the `haproxy:haproxy` account after starting. This is a security best practice, limiting the impact should HAProxy be compromised. The `haproxy` user is typically a system user with no login shell. The role also creates the directory for SSL certificates (`/etc/haproxy/certs`) owned by root:haproxy with permissions 0750, and any certificate file is deployed with 0640 permissions (readable by root and the haproxy group, but not by other users). This ensures that private keys are not world-accessible, while still allowing the HAProxy process to read them.
* **Network Ports:** By default HAProxy will listen on **port 80** (HTTP) for incoming traffic. This port is unencrypted and open to anyone who can reach the server. If your HAProxy is on a public-facing network, consider whether you want to serve HTTP at all, or if you should redirect to HTTPS (which you could configure in HAProxy with additional rules, though not provided by this simple role). If you configure HTTPS (port 443 with a certificate), the traffic between clients and HAProxy will be encrypted. However, note that **traffic from HAProxy to your backend servers is, by default, unencrypted HTTP**. If your backends require SSL or you need end-to-end encryption, you might run HAProxy in TCP mode or have HAProxy re-encrypt to HTTPS when forwarding (not natively covered by this role’s defaults). Always ensure that any sensitive data is protected in transit according to your needs. Additionally, the HAProxy stats interface (if enabled) listens on **port 9000** by default, and in this role it binds to **127.0.0.1** (localhost) by default. This means it is not accessible externally unless you change the bind address. If you do expose the stats port to a network, treat it as an administrative interface: secure it with strong credentials (and ideally network restrictions) because it can reveal internal information and allow some control over HAProxy.
* **Configuration and Credentials:** The HAProxy configuration file (`/etc/haproxy/haproxy.cfg`) generated by this role may include sensitive information, such as the stats interface credentials (in plaintext). By default, this file is installed with world-readable permissions (0644) by the package, meaning any local user on the system could read the config (and thus any passwords it contains). In secure environments, you may want to restrict this file to 0640 and group-owner `haproxy` so that only root and the haproxy service account can read it. Be mindful of how you handle this file and any backups of it. Also, if using Ansible Vault for `haproxy_ssl_certificate_content` or `haproxy_stats_password`, those secrets are protected at rest, but once deployed to the server (in the config or cert file) they should be treated as sensitive system files.
* **Logging:** HAProxy by default will log via the local syslog facility (as configured in `haproxy_global_vars`: it logs to `127.0.0.1 local0` and `local1`). Ensure your system’s syslog or rsyslog is configured to handle these logs (usually they go to `/var/log/haproxy.log` or the general syslog). From a security perspective, log files can contain IP addresses, URLs, and possibly credentials (if someone passes sensitive info in query strings or headers). Treat HAProxy logs as sensitive data and secure or clean them according to your policies. You may also forward these logs to a central log management system; just be sure to transmit and store them securely because they detail your network traffic patterns.
* **High Availability (HA) considerations:** If you require high availability for HAProxy (so that if one load balancer fails, another takes over), consider using the **`keepalived`** role to set up VRRP-based failover with a virtual IP. While this is more of an architectural concern than a security issue, it does have security angles: e.g., ensure the VRRP traffic (which is essentially heartbeat packets between HAProxy nodes) is on a trusted network segment, and use authentication (VRRP AH password, which this repository’s keepalived role supports via `keepalived_auth_pass`). The HAProxy role itself does not configure any firewall or IP takeover; it assumes a single instance. Pairing it with keepalived can provide redundancy, but be sure to also duplicate your HAProxy configuration (using this role) on the secondary node and secure both nodes equally.

This README covers the usage and considerations for the HAProxy role. By following the above guidelines and tailoring the variables to your environment, you can deploy a reliable and secure HAProxy load balancer via Ansible.
