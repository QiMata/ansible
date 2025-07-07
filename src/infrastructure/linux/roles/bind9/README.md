# Bind9 Ansible Role

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

This role installs and configures the BIND9 DNS server (named) on target hosts. It handles the full setup of a DNS server, including package installation, core configuration (BIND options and zone definitions), zone file templating, and optional features like DNSSEC and dynamic DNS updates. The role is designed to be **idempotent** and flexible, allowing you to deploy a DNS caching resolver and/or authoritative nameserver with minimal input. Key features include:

* **Automatic installation and service management:** Installs the Bind9 package and ensures the DNS service is available (using the appropriate package and service names for the OS). Post-installation, any configuration changes trigger service reloads or restarts via handlers.
* **Configurable recursion and forwarding:** By default, the role configures Bind9 for recursive DNS service (caching resolver) with customizable *forwarders* (upstream DNS servers for external queries). This allows the DNS server to resolve queries for external domains via specified forwarders (or root servers if none specified).
* **Authoritative DNS zones:** You can define DNS *zones* (domains) to be hosted authoritatively on the server. The role will set up zone definitions in BIND and generate zone files from templates based on the records you provide. Both primary (master) and secondary (slave) zones are supported in variables (see **bind9_zones** structure).
* **DNSSEC support:** For zones where DNSSEC is enabled (via a flag in variables), the role can generate signing keys using `dnssec-keygen` (by default RSA 2048-bit KSK keys). This lays the groundwork for securing zones with DNSSEC (though additional steps are needed to fully sign and maintain zones, see **Known Issues**).
* **Dynamic DNS updates:** The role supports dynamic DNS updates for zones that require it (e.g., if you have DHCP updating DNS records). When enabled for a zone, an update policy is added to allow changes via a TSIG key named "`rndc-key`". This allows secure automated updates to DNS records from authorized clients.
* **Logging and integration:** If enabled, the role can configure Bind9 to use a dedicated log directory (e.g. **/var/log/named**) for query or event logs and installs a logrotate policy to manage log files. This can be useful for debugging or compliance. The role is also designed to integrate with external log shipping solutions (e.g. ELK stack) by preparing local logs that tools like Filebeat can forward (actual log forwarding setup is outside the scope of this role).
* **Extensibility and modular structure:** The role’s tasks are organized into includes (install, configure, DNSSEC, logging) for clarity. It uses Handlers to restart or reload the DNS service only when needed (e.g., after configuration changes), and avoids downtime when possible. Variables allow tuning package names, service names, and paths to adapt to slight differences in environment.

## Supported Operating Systems/Platforms

This role is tested on and supported with the following Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)

> **Note:** The target hosts must be Debian-based systems because the role uses the `apt` package manager and Debian-specific service names. While it may work on Ubuntu (which uses the same package names and service name) or other Debian derivatives, it has not been explicitly tested on those. It will **not** work on RHEL/CentOS or other non-Debian OS without modifications (e.g., to use `dnf`/`yum` and the `named` service name).

## Role Variables

Below is a list of important variables for this role, along with default values (defined in **`defaults/main.yml`**) and their descriptions. Refer to the role’s **`defaults/main.yml`** and **`templates`** for additional context on how these are used.

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                    | Default Value     | Description |
| --------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`bind9_forwarders`**      | *Empty list* `[]` | List of IP addresses of upstream DNS servers to which queries for non-local zones will be forwarded. If set, BIND9 will forward recursive queries to these servers (e.g. corporate DNS or public resolvers). If left empty, no forwarders are used and the server will fall back to using root name servers for recursion. **Note:** An empty forwarder list will result in a configuration of `forwarders { }`, meaning queries go to root servers. Typically you should set at least one forwarder for faster resolution or as required by your network. |
| **`bind9_allow_query`**     | *Empty list* `[]` | List of hosts or networks that are permitted to query the DNS server (ACL for queries). Define entries as CIDR strings (e.g. `"192.168.10.0/24"`) or `"any"` to allow all. This controls who can use this DNS server for recursion and who can query authoritative records. **Note:** If this list is empty or not set, the resulting BIND configuration may be invalid or default to none; you should explicitly set allowed clients. For an internal DNS server, restrict this to your internal subnets. For a public authoritative server, you might set this to `"any"` so that anyone can query your DNS records. |
| **`bind9_zones`**           | *Empty list* `[]` | List of DNS zones to configure on this server. Each list item is a dictionary defining a zone. For example:<br>`yaml<br>- name: example.com<br>  type: master<br>  dnssec: true<br>  dynamic_updates: true<br>  records:<br>    - { name: 'www', type: 'A', value: '192.168.10.50' }<br>    - { name: 'mail', type: 'A', value: '192.168.10.60' }<br>    - { name: '@', type: 'MX', value: '10 mail.example.com.' }<br>`<br>**Keys**:<ul><li>`name`: (string) DNS zone name (domain) to serve.</li><li>`type`: Zone type, `"master"` (primary) or `"slave"` (secondary).</li><li>`dnssec`: (bool) Enable DNSSEC for this zone. If `true`, a DNSSEC key will be generated for the zone (you will still need to configure signing, see notes).</li><li>`dynamic_updates`: (bool) If `true`, allow dynamic DNS updates for this zone. The role will configure an update policy to permit updates using the **rndc-key** TSIG key.</li><li>`records`: List of DNS records (for master zones) to populate in the zone file. Each record is a dict with keys `name` (e.g. `"www"` or `"@"` for the zone apex), `type`(e.g.`"A"`, `"CNAME"`, `"MX"`, etc.), and `value` (the record data). These will be rendered into the zone file template. Ensure you include necessary NS and MX records as needed – the template will provide an SOA and NS by default, but you should list additional records.</li></ul> |
| **`bind9_logging_enabled`** | `false`           | Whether to enable dedicated BIND9 logging to a file. If `true`, the role will create a log directory and set up log rotation for BIND logs. **Note:** The BIND default configuration logs to syslog; enabling this will prepare a separate log file, but you may need to adjust BIND’s logging channels to actually write queries or events to file (by default, query logging is off). |
| **`bind9_log_dir`**         | `/var/log/named`  | Directory on the host where BIND will write logs if file logging is enabled. This role ensures the directory exists (owned by the bind user) and configures logrotate for files in this path. Make sure the BIND AppArmor profile (on Debian) allows writing to this location (Debian’s default AppArmor policy does include `/var/log/named/**`). |
| **`elk_logstash_host`**     | (none)            | Hostname or IP of a Logstash/ELK endpoint to which DNS logs should be shipped. *This role does not install or configure the shipper itself*, but this variable can be used in your environment to configure Filebeat or other log forwarders. For example, you might use the **`filebeat`** role to send BIND logs to Logstash – in which case set this to your ELK server’s host, and ensure logging is enabled so logs are produced. |
| **`bind9_package_name`**    | `"bind9"`         | Name of the BIND9 package to install on the target system. Defaults to the official package name on Debian-based systems. You can change this if you need a specific version or a differently named package (for example, if using an alternate repository). |
| **`bind9_service_name`**    | `"bind9"`         | Name of the BIND9 service. On Debian/Ubuntu the service is called **bind9**. If your distribution uses a different service name (e.g., **named**), you should override this accordingly so handlers and service tasks reference the correct name. |
| **`bind9_dnssec_policy`**   | `"default"`       | DNSSEC policy name to apply to zones (if supported by the BIND version). This variable is reserved for future use – currently, the role does not automatically apply any `dnssec-policy` statements in named.conf. In BIND 9.16+, setting a policy (e.g., `"default"`) in a zone would enable automatic DNSSEC key rotation and signing as per that policy. By default it is set to `"default"` as a placeholder, but the role does *not* yet use it. Users can manually implement DNSSEC policy by editing the zone configs if needed. |

</details>

## Tags

This role does **not define any Ansible tags** in its tasks. All tasks will run whenever the role is invoked. (You may still apply tags externally when including the role, if you want to skip or limit execution to this role’s tasks.)

## Dependencies

* **Ansible Version:** Requires Ansible **2.13** or higher, due to usage of newer syntax and modules.
* **Collections:** No external Ansible collections are required. All modules used (e.g., `apt`, `file`, `template`, `command`, `service`) are part of Ansible Core.
* **Roles:** No dependent roles are required for this role to function. It is self-contained. (Ensure, however, that your environment meets any external requirements such as internet access for APT or proper DNS ports open, as noted below.)
* **System Packages:** The role will install the BIND9 server package. On Debian, the `bind9` package includes the DNS server daemon and related utilities (like `dnssec-keygen` for key generation). The role also drops a config in `/etc/logrotate.d/` – this assumes the **logrotate** utility is present on the target (it typically is on Debian by default). If using DNSSEC features, the `bind9` package is sufficient; no additional packages for DNSSEC are needed on Debian (the tools are included).

## Example Playbook

Here is an example of how to use the `bind9` role in a playbook. This will set up a DNS server that acts as an **internal caching resolver** (forwarding queries to public DNS servers) and an **authoritative server** for one domain (`example.com`), with DNSSEC and dynamic DNS enabled for that zone:

```yaml
- hosts: dns_servers
  become: yes

  vars:
    bind9_forwarders:
      - "8.8.8.8"
      - "1.1.1.1"
    bind9_allow_query:
      - "192.168.10.0/24"
    bind9_zones:
      - name: "example.com"
        type: master
        dnssec: true
        dynamic_updates: true
        records:
          - { name: "www",  type: "A",  value: "192.168.10.50" }
          - { name: "mail", type: "A",  value: "192.168.10.60" }
          - { name: "@",    type: "MX", value: "10 mail.example.com." }
    bind9_logging_enabled: true
    # elk_logstash_host: "logstash.intra.example.com"  # (optional) specify if using log shipping

  roles:
    - bind9
```

In the above play, we define two upstream DNS forwarders (Google DNS at 8.8.8.8 and Cloudflare DNS at 1.1.1.1) and restrict query access to the `192.168.10.0/24` subnet (presumably our internal network). We configure one zone, **example.com**, as a master zone with DNSSEC and dynamic updates enabled. Three DNS records are provided for that zone: two A records (`www` and `mail`) and an MX record pointing to the mail host. Logging is enabled so BIND will log to **/var/log/named** and we could optionally set `elk_logstash_host` if we plan to ship those logs to a logging system.

When this playbook runs against hosts in the `dns_servers` group, the `bind9` role will:

* Install the Bind9 server package and ensure the service (bind9) is running.
* Write the configuration files **`/etc/bind/named.conf.options`** (for global options like recursion, forwarders, allow-query ACL) and **`/etc/bind/named.conf.local`** (for zone definitions). In this case, named.conf.options will allow recursion and include our forwarders and ACL, and named.conf.local will define the *example.com* zone.
* Create the zone file **`/etc/bind/db.example.com`** from a template, containing an SOA record, NS record, and the records we specified (A and MX). It will also create any necessary DNSSEC keys and include their references if `dnssec: true` (the keys are stored under `/etc/bind/keys`).
* Adjust permissions and create **`/var/log/named`** for logging, and install a logrotate rule for BIND logs.
* Trigger a service reload to apply the new zone (or a restart if the main config changed). The DNS server should then be authoritative for *example.com* (answering queries with the provided records) and will forward other queries to 8.8.8.8 and 1.1.1.1. Because we enabled DNSSEC for *example.com*, the keys are generated and ready; BIND can be configured to sign the zone (see **Known Issues** on DNSSEC). Because we enabled dynamic updates, BIND will accept DNS updates for *example.com* that are signed with the `rndc-key` TSIG (allowing, for example, DHCP servers to update records).

For a more **basic caching DNS server** (no authoritative zones), you could leave `bind9_zones` empty or not set, and just set `bind9_forwarders` and `bind9_allow_query` (and perhaps disable DNSSEC and dynamic updates flags). This would configure the server as a pure recursive resolver for your network. Conversely, for a **public authoritative DNS** (no recursion), you might set `bind9_forwarders: []` (no forwarders) and be sure to manually disable recursion in the options (the role doesn’t currently have a toggle for recursion, which is always on by default). In such a case, you’d likely set `bind9_allow_query: ['any']` so the world can query your zones, but ensure you restrict recursion or use it only for authoritative service.

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to ensure everything works as expected before using it in production. You can set up a local test scenario as follows:

1. **Install Molecule** (and Docker) on your development machine, if not already installed. For example, use pip:

   ```bash
   pip install molecule[docker]
   ```

   Ensure that Docker is running and you have permission to run containers.

2. **Prepare a test scenario:** Check if a Molecule scenario is already provided for the `bind9` role (for example, in `molecule/default/`). If not, you can create one with:

   ```bash
   molecule init scenario -r bind9 -d docker
   ```

   This will create a default Molecule configuration for the role using the Docker driver.

3. **Configure the scenario (if needed):** Edit the generated `molecule.yml` and `converge.yml` (under `molecule/default/`) if you want to test specific combinations. For instance, you might set `bind9_forwarders` and `bind9_zones` in the `converge.yml` playbook to mimic a real use-case. By default, the converge play will include the role with its defaults.

4. **Run the Molecule test:**

   * Execute `molecule converge` to create a Docker container (by default it will use a Debian base image) and apply the `bind9` role to it. Molecule will run the playbook (usually `molecule/default/converge.yml`) inside the container.
   * Watch the output for any task failures or error messages. All tasks should complete without errors. The final line should indicate a successful playbook run.

5. **Verify the results:** Once the converge step is done, you can manually verify that the role did its job:

   * **Configuration files:** Use `molecule login` to enter the container (or `docker exec -it <container_id> /bin/bash`). Check that `/etc/bind/named.conf.options` and `/etc/bind/named.conf.local` reflect the expected settings (forwarders, allow-query ACL, zone definitions). Also list the zone file (e.g. `/etc/bind/db.example.com`) to ensure records are present and the SOA serial, etc., look correct.
   * **Service status:** If the Docker container runs a systemd or init process, verify that the `bind9` service is running: e.g. `systemctl status bind9` or `ps aux | grep named`. If using a slim container without systemd, the service might not auto-start. In such cases, you can start BIND manually inside the container (e.g., `named -c /etc/bind/named.conf`) to test. Ensure the process runs without errors (check logs in `/var/log/named/` or `syslog`).
   * **DNS queries:** Still inside the container, you can test DNS resolution. For example, run:

     ```bash
     dig @127.0.0.1 example.com A
     ```

     This should query the local DNS server for the A record of example.com. It should return the IP you configured (e.g., 192.168.10.50 for "www" if you set an A record for the root/apex or `NXDOMAIN` if only subdomains are defined). Also test forwarding by querying an external domain:

     ```bash
     dig @127.0.0.1 google.com A
     ```

     If forwarders are set, you should get a response from the upstream (and the query should be cached on subsequent requests).
   * **DNSSEC keys:** If you enabled `dnssec: true` for a zone, check that keys were generated under `/etc/bind/keys`. You should see files like `Kexample.com.+008+<#####>.key` and `.private`. These are the DNSSEC keys. (BIND won’t be using them to sign unless configured, but presence indicates the role’s key generation ran.)
   * **Log files:** If `bind9_logging_enabled` was true, confirm that the directory (e.g., `/var/log/named`) exists and that a log file (e.g., `queries.log` or similar) is present or being written once you enable query logging. The logrotate configuration `/etc/logrotate.d/bind9` should also exist as installed by the role.

6. **Cleanup:** After testing, run `molecule destroy` to tear down the test container and any associated resources. Alternatively, you can run `molecule test` to perform the full cycle (create, converge, verify, destroy) in one go.

Using Molecule ensures that the role is idempotent (running it multiple times yields the same outcome with no changes if nothing changed in inputs) and that it works on a clean system. During testing, you might adjust variables to simulate different scenarios (e.g., multiple zones, turning DNSSEC on/off). If the container lacks a fully functional init system (thus not auto-starting services), you can still validate configuration files. For a more thorough test of service behavior, consider using a Systemd-enabled base image or the Vagrant driver to test on a VM.

## Known Issues and Gotchas

* **Forwarders Configuration:** The role does not automatically omit the `forwarders` clause when no forwarders are provided. If you leave **bind9_forwarders** empty, the generated `named.conf.options` will contain an empty forwarders block (`forwarders { }`). BIND treats this as having no forwarders (using root servers for recursion), which is usually fine. However, due to a quirk in the template, an empty list could potentially render as `forwarders { ; };` (an empty entry with an extra semicolon) which can cause a syntax error. To avoid issues, provide at least one valid forwarder or explicitly remove/override the forwarders configuration if you intend to rely on root name servers. In most setups, specifying forwarders (e.g., your ISP’s DNS or a public resolver) is recommended for performance.

* **Allow Query / Open Resolver:** Be careful with the **bind9_allow_query** setting. If you set this to `'any'` (or leave it effectively open) on a server that has recursion enabled, you are running an **open resolver**. Open resolvers can be abused for DNS amplification attacks and may attract unwanted traffic. For public-facing authoritative DNS servers, you typically want to allow queries from anyone for your zones **but disable recursion** for external clients. The role by default enables recursion globally and doesn’t distinguish query ACL for recursion vs authoritative queries. If you are using this role for an Internet-facing authoritative server, consider manually setting `recursion no;` in named.conf.options and using `allow-query { any; };` for the zones. If it’s for internal use, restrict **bind9_allow_query** to your internal networks to prevent outside abuse. Always double-check that your DNS server is not inadvertently accessible to the public for recursive queries.

* **Dynamic Updates and Reapplying the Role:** When **dynamic_updates** is enabled for a zone, the DNS server (named) will accept runtime changes to that zone (e.g. via nsupdate or DHCP integrations). These updates are written into a journal file and integrated into the zone. If you re-run the Ansible role, it will re-template the zone file from the static records in **bind9_zones** and then reload BIND. This means any records added via dynamic update **might be overwritten or lost** (since the template does not know about them). To avoid conflict, consider the following:

  * Limit Ansible-applied records to static entries that won’t be updated dynamically. Dynamic entries (like DHCP client hosts) should not be listed in the Ansible variables.
  * If you need to re-run the role on a server with dynamic zones, you may want to temporarily **freeze** the zones (using `rndc freeze <zone>`), or integrate logic to skip zone file tasks when a zone is dynamic and already initialized.
  * The update policy configured by this role for dynamic zones (when `dynamic_updates: true`) is very permissive: it grants the key **rndc-key** permission to update any record in the zone. Ensure that the secret for this TSIG key (found in `/etc/bind/rndc.key`) is kept secure. By default, the key is generated during BIND installation and is only known to the server. Anyone with this key can modify DNS records in the zone.

* **DNSSEC Key Generation and Zone Signing:** When **dnssec** is set to true for a zone, the role will generate a DNSSEC key pair for the zone (a Key Signing Key by default) using `dnssec-keygen`. This is only the first step in enabling DNSSEC. **The role does NOT automatically sign the zone or configure named to serve a signed zone.** By default, the zone will load as unsigned even though keys exist. To fully enable DNSSEC, you have a couple of options:

  * Manually sign the zone using `dnssec-signzone` and include the generated DS/DNSKEY records in the zone file, then adjust the BIND config (e.g., set `auto-dnssec maintain;` and possibly `inline-signing yes;` in the zone options). You would also need to provision the DS record to your parent domain.
  * Use BIND’s built-in DNSSEC policy (if using BIND 9.16+ with `dnssec-policy`) to automate signing. The variable **bind9_dnssec_policy** is intended for this, but the role doesn’t currently apply it. You could manually edit the zone stanza to add `dnssec-policy "default";` which on Debian will cause automatic key generation and signing using the default policy.
  * Always increase the zone’s serial number when introducing DNSSEC or updating keys. The role’s zone template uses a static or initial serial number (often `1` or a timestamp). If you run the role multiple times, ensure the serial in the zone file continues to increment, otherwise BIND may not load the updated zone. (Consider customizing the template to generate a date-based serial if you expect frequent zone changes.)

  In summary, treat the role’s DNSSEC support as *assisted manual configuration*. It helps by creating keys and placing them in the proper directory with correct permissions (owned by `bind` user, not world-readable), but you must take additional steps to activate DNSSEC on the zone and maintain it.

* **Secondary (Slave) Zones:** The role allows defining zones with `type: "slave"`, but it currently does not handle all the necessary configuration for a slave zone. In BIND, slave zones require specifying the master servers (IP addresses of the primary DNS) via a `masters { ...; };` directive. The role’s template for zones does **not** include a masters clause or any logic to differentiate zone content based on type. If you declare a slave zone in **bind9_zones**, the role will still attempt to create a local zone file for it (which is not needed for slaves and may be ignored or overridden by BIND). You will need to manually configure the masters for any slave zone (e.g., by editing named.conf.local after the role runs, or by extending the role). Also, be mindful of zone transfers: by default the role doesn’t set `allow-transfer`, so BIND’s default will apply. Ensure your master is configured to allow transfers to the slave, and consider adding an `allow-transfer` ACL on the master and/or slave as needed for security. In short, the role is primarily geared toward primary zones; use caution and test thoroughly if implementing slave zones with it.

* **Logging Configuration:** When **bind9_logging_enabled** is true, the role creates the log directory and a logrotate entry, but it does **not** add a BIND logging **channel** or category configuration to actually write logs to a file. Out of the box, BIND will continue to send most logs to syslog (and query logs are off by default). To have BIND write query logs or other details to the files in **/var/log/named**, you must configure the logging section in BIND’s config. For example, you might add to your named.conf.local (outside of what the role manages) something like:

  ```
  logging {
      channel query_file {
          file "/var/log/named/queries.log" versions 3 size 5m;
          severity info;
          print-time yes;
      };
      category queries { query_file; };
  };
  ```

  This would direct query logs to the file that will be rotated by the role’s logrotate configuration. You can also enable logging of other categories similarly. Remember to run `rndc querylog on` if you want to toggle query logging at runtime. The key point is that **the role doesn’t configure these logging details for you** – it merely sets up the infrastructure (directory and rotation). If you don’t add a logging config, you might not see any files in `/var/log/named` except perhaps a general log if BIND is configured to log some events there. The default AppArmor profile on Debian allows writing to `/var/log/named`, so no change is needed there when you add logging channels.

* **Firewall and Port Access:** The role does not modify firewall settings. BIND9 listens on port **53** (UDP and TCP) for DNS queries, and on port **953** TCP for the `rndc` control channel (by default, 953 is localhost-only). If your server has an active firewall (ufw, iptables, firewalld, etc.), you need to open port 53 to allow DNS queries from your clients or the public (depending on your use case). For an internal DNS, allow port 53 UDP/TCP from your internal networks. For an authoritative public DNS, allow port 53 from anywhere (and consider allowing 53 TCP as well, since larger queries like zone transfers or DNSSEC responses may use TCP). The `rndc` control port (953) can usually remain firewalled to localhost (the default). Failing to open the firewall will result in a functional DNS service that isn’t reachable by clients. Conversely, if you intentionally deploy an Internet-facing DNS, ensure you **do** secure it as discussed (no open recursion, etc.) before opening it to the world.

## Security Implications

* **Exposure of DNS Service:** By installing BIND9, you are running a network service that listens on UDP/TCP port 53. If this role is applied to hosts accessible on the Internet, you must take precautions to prevent abuse. Use **bind9_allow_query** to restrict which clients can query your DNS (especially for recursion). Public authoritative servers should have recursion disabled to prevent abuse. Always keep BIND9 updated with security patches; DNS servers are high-value targets for attackers and new vulnerabilities do surface.

* **Access Control Lists (ACLs):** The allow-query ACL configured by this role is a primary defense against unauthorized use. If you set it to a specific network (e.g., your LAN), clients outside that network will not receive responses. This is good for an internal resolver. If you set it to "any" on a recursive server, you’ve essentially opened your server to the world – not advisable. Also note, the role does not explicitly set **allow-recursion** or **allow-transfer** options. By default, BIND uses allow-query for both recursion and authoritative responses. If you need finer control (e.g., allow anyone to query authoritative data but only internal hosts to recurse), you should manually set `allow-recursion` in the named.conf.options (not managed by this role). Similarly, consider adding an **allow-transfer** setting if you run secondary DNS servers or want to forbid zone transfers. Without it, BIND’s default allows zone transfers to anyone for public zones, which could expose your DNS data.

* **System User and Permissions:** The BIND9 package on Debian creates a user account (usually **`bind`** or **`named`**) under which the DNS service runs. This role relies on the package defaults, meaning the **bind** user will own the process and certain files. This is a security best practice, as it limits the impact of any compromise of the DNS service (it doesn’t run as root). The role ensures files it creates (zone files, keys, log directory) are owned by this user and with restrictive permissions where appropriate. For example, DNSSEC private keys under `/etc/bind/keys` are set to **750** permissions (owner *bind*, group *bind*), preventing other users from reading them. The log files are created with mode 644 (owner bind) by logrotate so they can be read by admins or shipped out, but be mindful that if your system has untrusted local users, those users could read world-readable DNS logs. Adjust permissions if that is a concern.

* **DNSSEC Key Security:** If you enable DNSSEC for a zone, the generated keys (especially the private `.private` files in `/etc/bind/keys`) are sensitive. Anyone with access to those keys could potentially sign fraudulent DNS records for your domain (undermining DNSSEC). The role protects these files with filesystem permissions, but you should also consider the physical and network security of the server. Regularly back up these keys in a secure manner – if the server is lost or the keys are accidentally deleted, you will need them to restore DNSSEC functionality without a key rollover (which can be time-consuming to coordinate with the parent domain). If you suspect a key compromise, you should initiate a key rollover and update DS records accordingly.

* **Dynamic Update Key (TSIG) Security:** When dynamic DNS updates are enabled, the role relies on the default **rndc-key** for authentication. This key is typically found in `/etc/bind/rndc.key` and is a symmetric secret. Ensure this file is kept secure (it should be chmod 600 or 640 by default, accessible only by root and bind). If an attacker obtains this key, they could maliciously update DNS records on your server (for example, redirecting services to rogue IPs). If you distribute the rndc-key to other systems (e.g., a DHCP server to update DNS), do so securely. You may also consider using a distinct TSIG key for DNS updates (different from the general rndc key) and limit the update policy to specific record types or names if possible, to minimize risk. The role’s default policy is broad (any record in the zone), chosen for simplicity.

* **Zone Transfers and Data Exposure:** As noted, the role does not configure `allow-transfer`. If you are running an authoritative DNS that is publicly queryable, attackers could attempt to AXFR (transfer) your zones to get a full list of domain records (which can be sensitive information about internal hosts if your DNS is serving internal names). By default, modern BIND versions **do not allow zone transfers to arbitrary clients unless they’re listed as secondaries** in the zone stanza, but this can vary. It’s good practice to explicitly restrict zone transfers to your known secondary DNS servers or disable them entirely if not used. You can do this by manually editing named.conf.local or adding a snippet in your playbook outside this role. Monitor your DNS logs for unauthorized transfer attempts if your server is public.

* **Logging and Privacy:** If you enable query logging and/or ship logs to a central system, be aware that DNS query logs can contain sensitive information (such as internal hostnames, VPN query patterns, etc.). Treat these logs as sensitive data. Use secure transport (TLS) if sending to a remote log collector (e.g., use Filebeat with TLS to Logstash, which is beyond the scope of this role). Also consider log retention policies – the provided logrotate keeps 12 weeks of logs by default; adjust this as per your organization’s policy to balance troubleshooting needs with privacy.

* **High Availability Considerations:** This role doesn’t directly configure any high-availability mechanism for BIND (aside from you being able to set up secondary zones). If you need a highly available resolver or authoritative server, you would typically run multiple DNS servers. For caching resolvers, you might deploy two servers and configure clients with both, or use an IP failover tool. For example, you could use the **`keepalived`** role in this repository to manage a Virtual IP that floats between two DNS servers for failover (particularly useful for an internal resolver where clients can’t handle multiple IPs). If you do this, ensure that both servers have identical config (perhaps managed by this role applied to both). For authoritative DNS, you should configure at least two NS records (pointing to two separate servers) rather than relying on IP failover, to achieve redundancy. In either case, plan and test failover scenarios to ensure continuity of DNS service.

* **Integration with ELK/Logging Systems:** If you send DNS logs to a central system, monitor that system for any signs of misuse or sensitive data leakage. Also, if using a log forwarder (like Filebeat), ensure it’s kept up to date and that the connection to ELK is secure. This role prepares logs for shipping but leaves the shipping mechanism to you. The provided **`filebeat`** role (or similar) can be used to ship logs. When enabling such integration, consider filtering out unnecessary data to reduce noise and storage usage (DNS can be very chatty). From a security standpoint, centralizing DNS logs can be a boon (for detecting exfiltration via DNS or malware using DNS); just handle the data responsibly.

---

By understanding and addressing the above points, you can safely deploy the Bind9 role in a production environment. Always tailor the configuration to your specific security requirements – for instance, an internal DNS server in a secure network might allow more leniency (like logging everything to a central system for analysis), whereas an external DNS server would be locked down with minimal open ports and services.
