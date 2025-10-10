# Ansible Role: OpenLDAP Logging

*Ansible role to enable and forward OpenLDAP server logs to a central logging system (e.g. an ELK stack). This role configures system logging and Filebeat on an OpenLDAP server host to capture LDAP logs and ship them to a remote log aggregator for analysis.*

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

The **OpenLDAP Logging** role configures an OpenLDAP server host to produce dedicated log files for LDAP operations and to forward those logs to a centralized logging system (such as an ELK stack). It achieves this by updating the system’s syslog configuration to direct OpenLDAP log messages to a separate file (`/var/log/ldap.log`), and by installing and configuring an Elastic Filebeat agent to monitor that log file and send its contents to an external log collector (by default, a Logstash endpoint). This separation of LDAP logs into their own file, and subsequent forwarding, allows administrators to more easily monitor directory service events (searches, modifications, connections, errors, etc.) in a centralized dashboard without cluttering general system logs.

In practice, you would apply this role to any server where the OpenLDAP service (slapd) is running, typically after the LDAP service is installed and configured. Once applied, the host’s syslog (rsyslog) will create and maintain a dedicated log for LDAP events, and Filebeat will continuously ship new log entries to your logging infrastructure. This provides near real-time visibility into LDAP operations across your infrastructure, which is valuable for troubleshooting authentication issues, monitoring LDAP query load, auditing changes to the directory, and detecting potential misuse or security incidents.

```mermaid
flowchart LR
    subgraph "LDAP Server"
        S[OpenLDAP (slapd) Service] -->|syslog (LOCAL4 facility)| L[/var/log/ldap.log/]
        L --> F[Filebeat Agent]
    end
    F --> E[(Central Logstash/ELK)]
    classDef cluster fill:#f4f4f4,stroke:#333,stroke-width:1px;
    class E cluster;
```

*Diagram: On each LDAP server, OpenLDAP writes logs via syslog to a local file (`ldap.log`), and a Filebeat agent on the host forwards those logs to a central Logstash/ELK stack for aggregation and analysis.*

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian** and **Ubuntu** Linux distributions, using the APT package manager for installation of Filebeat:

* **Debian**: 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu**: 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian-based systems similar to the above releases are likely compatible. The role uses the `apt` module to install Filebeat, so non-APT-based systems (e.g. Red Hat Enterprise Linux, CentOS or other RPM-based OS) are **not supported** out-of-the-box without modifications. Attempting to run this role on an unsupported OS will fail at the package installation step. In such cases, you would need to modify the role to use the appropriate package manager (`yum`, `dnf`, etc.) and repository for Filebeat, or pre-install the Filebeat agent by other means.

Additionally, the target system is assumed to use **systemd** (or a compatible service manager) since the role enables and restarts services like rsyslog and filebeat. Debian 11+/Ubuntu 20.04+ meet this criterion. Ensure you run this role on a supported platform to avoid issues with package availability or service management.

## Role Variables

The main variable used by this role (defined in `defaults/main.yml`) allows you to specify the remote log collector endpoint. Generally, the defaults will work for a basic setup, but you should override this variable to match your environment’s logging server:

| Variable       | Default Value                           | Description |
| -------------- | --------------------------------------- | ----------- |
| **`elk_host`** | "logstash.example.com:5044" (example) | Hostname and port of the Logstash or log collector endpoint where Filebeat should send OpenLDAP logs. Use the `data_systems/logstash` role to provision this endpoint within the repository, or provide the address of an external service. By default, if `elk_host` is not set by the user, the Filebeat configuration will assume a Logstash server at **`logstash.example.com:5044`** as a placeholder. Override this with the actual host:port of your ELK stack’s Logstash (or Beats input) to ensure logs are delivered successfully. |

**Note:** The above default is a placeholder for demonstration. In a real deployment, you must provide a valid `elk_host` value (or set up DNS such that `logstash.example.com` resolves correctly) for log forwarding to function. The new `data_systems/logstash` and `data_systems/kibana` roles can be used to stand up the Elastic ingestion layer referenced here. If your environment uses a different pipeline (for example, sending logs directly to Elasticsearch or using a cloud service), adjust the Filebeat output configuration accordingly (this role, as written, assumes a Logstash endpoint by default).

## Tags

This role does not define any custom Ansible tags. All tasks in **openldap_logging** run whenever the role is invoked (there are no task blocks controlled by special tags). You can apply your own tags at the play level if you need to include or skip this entire role, but within the role every task is untagged and will always execute by default.

## Dependencies

**None.** This role has no strict dependencies on other Ansible roles or Galaxy collections – it uses only built-in Ansible modules (`ansible.builtin.copy`, `apt`, `template`, `service`, etc.) to perform its tasks. In other words, you do not need any external roles to use `openldap_logging`. However, there are a few important prerequisites and assumptions to note:

* *OpenLDAP service:* This role assumes that an OpenLDAP server (slapd) is already installed and running on the target host (for example, via an **openldap_server** role or manual setup). The logging configuration it deploys is specifically for OpenLDAP’s syslog output. If OpenLDAP is not present on the host, the role will still install Filebeat and set up logging, but no logs will actually be produced in `/var/log/ldap.log` until OpenLDAP is installed and running. For a complete LDAP server setup, apply the OpenLDAP server configuration role(s) prior to this logging role.

* *Elastic APT Repository:* The Filebeat package is part of Elastic’s repository and is **not included** in the default Debian/Ubuntu repositories. **Before running this role**, ensure that the Elastic APT repository is configured on the target hosts (and the Elastic GPG signing key is installed) so that `apt` can find and install the `filebeat` package. If this repository is not set up, the installation task will fail because the package won’t be found. (Consult Elastic’s documentation on how to add the Filebeat repository and GPG key, or pre-install the Filebeat .deb package on hosts as needed.)

* *System Logging Service:* The role adds a config file to **rsyslog** (`/etc/rsyslog.d/50-ldap.conf`) to redirect logs to `/var/log/ldap.log`. It then triggers a restart of rsyslog to apply this change. This requires that rsyslog (or a compatible syslog service) is present and enabled on the system (which is the default on Debian/Ubuntu). Ensure you haven’t disabled rsyslog or replaced it with an alternative, or adjust the role accordingly.

Aside from the above, no other roles or system packages are required. It is often wise to run a base setup role (ensuring Python is installed, apt cache updated, etc.) before this role, but that is not a strict requirement if your hosts are already in a default manageable state.

## Example Playbook

Here is a simple example of how to use the `openldap_logging` role in a playbook, including an override of the `elk_host` variable to point to a real Logstash server:

```yaml
- hosts: ldap_servers
  become: yes  # Run as root to allow installation and writing to /etc and /var/log
  vars:
    elk_host: "logcollector.mycompany.com:5044"  # Address of central Logstash/ELK server
  roles:
    - openldap_logging
```

In the above example:

* We target a host group **ldap_servers** (which should contain the hosts running the OpenLDAP server). We use `become: yes` because installing packages and modifying system log configuration requires root privileges.
* We override **`elk_host`** to `"logcollector.mycompany.com:5044"`, which should be replaced with the actual hostname (and port) of your environment’s log collector. This ensures Filebeat will send the LDAP logs to the correct destination instead of the default placeholder.
* We include the **openldap_logging** role. When this play runs, the role will:

  * Install the Filebeat agent (if not already installed) via apt.
  * Drop an rsyslog configuration file (`50-ldap.conf`) that directs OpenLDAP syslog messages (facility LOCAL4) to **/var/log/ldap.log**.
  * Deploy the Filebeat configuration template to **/etc/filebeat/filebeat.yml**, which tells Filebeat to monitor the `/var/log/ldap.log` file and forward logs to the specified `elk_host` (Logstash).
  * Ensure the **rsyslog** and **filebeat** services are running and enabled on startup, and restart them if needed to apply the new configuration.
* After running this play, the OpenLDAP server on each host will be logging to `/var/log/ldap.log` and those log entries will be shipped out to your central log server in near real-time. You should start seeing LDAP log events in your ELK stack (e.g., in Kibana or another log viewer), categorized by the `service: openldap` field (as set in the Filebeat config).

You could also set `elk_host` (and other environment-specific variables) in your inventory or group variables file instead of directly in the playbook. The key is that the role is applied *after* the OpenLDAP service is up, so that any events (like startup messages or client connections) get captured from that point onward.

## Testing Instructions

This role can be tested using **Molecule** (with the Docker driver) and **Testinfra/pytest** for verification. A Molecule test scenario (e.g., `molecule/openldap_logging`) is typically set up to automate the testing of the role in an isolated container environment. To run tests for this role, follow these general steps:

1. **Install Molecule and dependencies:** Ensure you have Molecule installed (`pip install molecule[docker]`) and Docker running on your system. Also install any additional testing frameworks Molecule uses (such as `pytest` and `testinfra`) if not already present. These tools will allow you to spin up containers and assert the role’s behavior inside them.

2. **Prepare the test environment:** The Molecule scenario for this role should provision a Docker container (for example, based on Debian) and apply the `openldap_logging` role inside it. Before running the test, you may need to ensure the container image can successfully install Filebeat. This typically involves:

   * Adding Elastic’s APT repository and GPG key *within the container* (so that `apt-get install filebeat` works). The Molecule playbook or provisioning tasks might handle this (e.g., by using the official Elastic apt repository for Filebeat) – verify that the scenario includes this step. If not, you might need to customize the Molecule setup to add the repository, or use a custom container image that already has Filebeat available.
   * Optionally, installing an OpenLDAP server (slapd) inside the container or otherwise simulating log generation. While not strictly required to test the role (the role can be tested by checking configuration files and service status), having slapd running allows for a more end-to-end test (generating a log entry and verifying it’s caught by Filebeat).

3. **Run the Molecule test suite:** From the repository root (where the `molecule/` directory is), execute Molecule with the scenario for this role. For example:

   ```bash
   molecule test -s openldap_logging
   ```

   This will create the container, apply the role, and then run the verification steps. Molecule will go through its phases:

   * **Dependency & Converge:** It applies the **openldap_logging** role inside the container. This should result in Filebeat being installed, the `/etc/rsyslog.d/50-ldap.conf` file being created, the `/etc/filebeat/filebeat.yml` being templated, and both rsyslog and filebeat services started.
   * **Verify:** Testinfra/pytest will run a series of tests on the container to confirm the role’s effects. Typical checks might include:

     * The file **`/etc/rsyslog.d/50-ldap.conf`** exists and contains the expected content (routing LOCAL4 logs to `/var/log/ldap.log`).
     * The file **`/etc/filebeat/filebeat.yml`** exists and is configured to read `/var/log/ldap.log` and send to the correct `elk_host`.
     * The **rsyslog** service is running, and the **filebeat** service is running and enabled.
     * After forcing a test log entry, the log file is created and contains the entry. (For example, the test might use the `logger` command inside the container: `logger -p local4.info "Test LDAP log message"` to simulate an OpenLDAP log; then verify that `/var/log/ldap.log` now contains "Test LDAP log message".)
     * No errors are present in the Filebeat logs, and Filebeat has successfully connected to the specified `elk_host` (this might be inferred or checked via Filebeat’s registry or log output if accessible).

4. **Cleanup:** Molecule will destroy the test container after the tests pass (as part of the `molecule test` sequence). If you want to troubleshoot or inspect the container manually, you can run `molecule converge -s openldap_logging` to set up the container and keep it running (without tearing it down automatically), then `molecule verify -s openldap_logging` separately. This allows you to `docker exec` into the container for debugging if a test fails.

By following these steps, you can validate that the role works as expected on a fresh system. The Molecule tests help ensure that changes to the role don’t break functionality and that it remains idempotent and effective.

## Known Issues and Gotchas

* **Debian/Ubuntu only:** As noted, this role is currently implemented using the `apt` module for installing Filebeat. Attempting to run it on RedHat/CentOS or other non-APT distributions will fail unless you modify the tasks to use the appropriate package manager and repos. In short, use this role on Debian-based targets, or extend it with conditional tasks for other OS families if needed.

* **Elastic repo required:** The Filebeat package must be available to apt. A common pitfall is forgetting to add the Elastic package repository (and key) on the target hosts before running this role. If you see errors like "package 'filebeat' not found", it means the repository is missing. Ensure the Elastic APT repository is configured (see **Dependencies** above). This role does not add the repo by itself (to keep things focused), so this setup must be done separately (for example, via an earlier play or a role that manages apt repositories).

* **Log file growth:** The role directs OpenLDAP logs to **`/var/log/ldap.log`**, but it does **not** set up any log rotation for this file. Over time, especially if OpenLDAP’s log level is set to a verbose level, this file can grow large. You should consider adding a logrotate rule for `/var/log/ldap.log` (for example, via a logrotate role or manually placing a config in `/etc/logrotate.d/`) to ensure the LDAP log is rotated and does not fill up the disk. Many default systems rotate common logs but a custom log like `ldap.log` may not be covered by the default logrotate configuration.

* **OpenLDAP log level:** By default, OpenLDAP’s logging might be minimal (depending on your slapd configuration). If you find that very little is being recorded in `ldap.log`, you may need to increase the OpenLDAP log level (for instance, to **stats** level or higher) in the OpenLDAP server configuration. This role does not alter the OpenLDAP server’s `loglevel` setting; it assumes logging is already enabled to syslog. You can set the log level via your main OpenLDAP setup (e.g., using `olcLogLevel` in the cn=config or `loglevel` in slapd.conf if using file-based config). Adjusting this is outside the scope of the logging role, but it’s something to be aware of – the role can only forward what OpenLDAP produces. No logs in `ldap.log` could indicate that slapd isn’t logging (check your OpenLDAP config) rather than an issue with this role.

* **Filebeat config overlap:** If you are also using a general Filebeat role or other service-specific Filebeat configurations, be careful about overlapping configurations. The **openldap_logging** role writes a complete Filebeat config to `/etc/filebeat/filebeat.yml`, which will override any existing Filebeat configuration. In a scenario where you have multiple roles targeting Filebeat, you should **coordinate their usage**. For example, if you use the general **configure_filebeat_os** role on most servers but choose to use **openldap_logging** on an LDAP server, note that the latter will replace the Filebeat config put in place by the former (or vice versa, depending on order). It’s recommended *not* to run two Filebeat-configuring roles on the same host. Instead, use one unified Filebeat configuration that includes all necessary inputs:

  * If you want to capture both system logs and OpenLDAP logs on the same node, you might merge the config by hand or run one role and then manually adjust its config. Alternatively, run the **openldap_logging** role *after* **configure_filebeat_os** to overwrite with LDAP-specific settings (but note you’d then lose the general log inputs unless you re-add them).
  * Some roles (e.g., an `apt_mirror` role in this repo) use a flag to append their log paths to an existing Filebeat config instead of overwriting it. The OpenLDAP Logging role doesn’t currently append – it manages its own config file. So plan accordingly to avoid conflicts. Future enhancements might include making this role append an input to an existing config, but by default it assumes it has full control of Filebeat’s config on the host.

* **Service restarts:** The role restarts rsyslog and Filebeat to apply changes. In production, be mindful that restarting rsyslog momentarily could cause a brief interruption in syslog processing. This is usually very quick and not an issue, but if the host is under heavy logging load, some log lines could theoretically be missed during the restart window. Similarly, restarting Filebeat will briefly pause log forwarding. This is generally acceptable, but consider scheduling the playbook run during a maintenance window if continuous logging is critical.

## Security Implications

Running this role has a few security-related considerations:

* **Exposure of logs off-server:** By forwarding OpenLDAP logs to a central server, you are transmitting potentially sensitive information over the network. LDAP logs can include usernames, IP addresses of clients, and details about directory operations (e.g., password change attempts, bind DN names, etc.). Ensure that the transport is secure. In the default configuration, Filebeat is set to send to Logstash on port 5044 without any authentication or encryption. If your network is untrusted or you are sending across network boundaries, consider enabling TLS encryption and/or authentication for Beats traffic (this would involve additional Filebeat and Logstash configuration not covered by this role). At minimum, restrict the network path (e.g., via firewall rules or VPN) so that only authorized hosts can receive the logs.

* **Log data sensitivity:** The log file `/var/log/ldap.log` will reside on the server and contain the LDAP logs. By default, when rsyslog creates this file, it is likely owned by **root** and readable only by members of the **adm** group (on Debian/Ubuntu, most logs under `/var/log` follow this pattern). This is good from a security standpoint – it limits who on the system can read potentially sensitive log entries. Verify the permissions of `ldap.log` after the role runs. If they are too open, you should tighten them (e.g., `600` or `640` with appropriate owner/group). The role itself does not explicitly set file permissions for `ldap.log` (it relies on rsyslog’s defaults for file creation). Always treat your directory service logs as sensitive data and protect them accordingly.

* **Running services and privileges:** This role will install Filebeat, which typically runs as a service with root privileges (or at least with the capability to read log files owned by root). The Filebeat package from Elastic might create a dedicated `filebeat` user; however, in order to read `/var/log/ldap.log` (owned by root/adm), that user would need to be added to the adm group or the file’s permissions adjusted. If you find that Filebeat cannot read the log (e.g., if it runs as `filebeat` user without proper group access), you may need to adjust permissions or run Filebeat as root. Running any service with elevated privileges carries risk – ensure you trust the source of the Filebeat package and keep it up to date with security patches. The role uses the official Elastic package, but you should still be mindful that a compromise of the central logging server or the Beats protocol could potentially be used to inject or tamper with data.

* **No new network ports on LDAP host:** This role does not open any new listening ports on the LDAP server host itself. Filebeat initiates an outgoing connection to the `elk_host` on port 5044 (Logstash Beats input) by default. Ensure your firewall (if any) allows outbound connections to the log collector on that port. Conversely, from a security view, since no new inbound ports are opened, the attack surface on the LDAP host remains the same in terms of network services (slapd on 389/636, etc., are unaffected by this role). Just be aware that the Filebeat service will be running and could potentially be targeted *if* an attacker already has access to the host (e.g., they might try to abuse it to send false logs or use its privileges to read files). This risk is relatively low and mostly mitigated by system access controls.

* **User accounts:** This role does not create any new user accounts. The only potential user-related change is that the `filebeat` package installation might create a system user for running the Filebeat service (commonly `filebeat` user). This is normal and desired. Make sure this account is properly restricted (it should have no login shell and limited permissions, which the package usually handles). There is no interactive login or home directory for this service account in most cases.

In summary, applying **openldap_logging** enhances your security monitoring (by centralizing logs for analysis and alerting) but also requires you to consider the confidentiality and integrity of those logs in transit and at rest. Be sure to secure the pipeline (via network policies or encryption) and handle the log data according to your organization’s privacy and security policies.

## Cross-Referencing

This repository contains other roles related to OpenLDAP and logging that you may want to use in conjunction with **openldap_logging**:

* **OpenLDAP Server Roles:** The logging role assumes you have set up the LDAP server beforehand. For that purpose, see roles like **`openldap_server`** (which installs and configures the slapd service) and **`openldap_content`** (which loads initial LDAP schemas/entries). There is also **`openldap_replication`** (for setting up multi-master or master-slave replication, if you need a highly available LDAP environment) and **`openldap_backup`** (which handles periodic backups of the LDAP database). These roles complement each other:

  * *openldap_server* sets up the core server and basic configuration.
  * *openldap_content* populates the directory with base DN, organizational units, and any initial data.
  * *openldap_replication* (optional) configures replication between multiple LDAP servers (ensure logging is enabled on all masters for a full audit trail).
  * *openldap_backup* automates backups (which is important for disaster recovery, and also for auditing changes over time).

  Typically, you would run those roles first to get a functional LDAP server, then run *openldap_logging* to enable log forwarding, and finally perhaps *openldap_backup* to schedule backups. All these roles together provide a complete solution for managing OpenLDAP servers.

* **System Log Forwarding:** For general system logs (auth logs, syslog, kernel logs, etc.), this repository includes a role **`configure_filebeat_os`** which installs Filebeat and configures it to send all system logs to Elasticsearch (or Logstash). If you want **all** logs from a server centralized (not just LDAP logs), you might use that role. **However, do not use** *configure_filebeat_os* and *openldap_logging* on the same host without careful consideration – both manage the Filebeat configuration and could conflict. The *configure_filebeat_os* role is tailored to OS logs and by default sends directly to Elasticsearch, whereas *openldap_logging* is tailored to LDAP logs and sends to Logstash. If you decide to combine them, ensure that their configurations are merged. One approach is to run *configure_filebeat_os* on all servers for baseline logs, and then run *openldap_logging* only on LDAP servers, *after* the OS log role, to overwrite the Filebeat config with one that includes LDAP logs (knowing that it will replace the generic config). Another approach is to integrate the LDAP log path into the general Filebeat config via a variable (or modify the Filebeat OS role’s template to include `/var/log/ldap.log`). The key is avoiding two separate Filebeat configs. Refer to the Filebeat OS role’s documentation for guidance on integration – it specifically notes to avoid clobbering configs when using multiple logging roles.

* **Direct Filebeat Role:** In some cases, you might have a more general **`filebeat`** role (separate from the OS-specific one). This repo’s documentation mentions a *filebeat* role that handles basic installation and service setup. If you are using that, it might already ensure Filebeat is present. The *openldap_logging* role overlaps in that it also ensures Filebeat is installed (and running) on the host. Duplicate installation isn’t usually harmful (apt will just report it’s already installed), but you should be aware of the overlap. If you prefer to let the general *filebeat* role handle installation, you could modify *openldap_logging* to skip the installation step. The main difference is configuration: *openldap_logging* provides a specific config for LDAP logging. You can choose to use one role or the other, or use *openldap_logging* purely for the config portion. Generally, stick to one consistent method to manage Filebeat to reduce complexity.

* **ELK Stack Setup:** While not provided in this repository, remember that having Filebeat send logs is only one part of the equation. You need a functioning ELK (Elasticsearch/Logstash/Kibana) or other log management solution to receive and utilize these logs. Ensure that your central log server (whether it’s Logstash or another endpoint specified in `elk_host`) is configured to accept Beats input on the given port and parse the OpenLDAP logs appropriately. If you maintain roles or playbooks for your ELK stack, make sure to point `elk_host` to the correct address/port and update any log parsing rules for LDAP logs if needed. (For example, OpenLDAP log lines could be parsed by Logstash grok patterns or Filebeat modules, but that setup is outside this role’s scope.)

Each of the above points helps place **openldap_logging** in context within a broader IT infrastructure. By combining this role with the core OpenLDAP roles and your logging/monitoring stack, you gain full visibility into your directory services. For more details on related roles, see their respective README files. Integrating this role properly will ensure that your LDAP servers are not just functioning, but also actively monitored through centralized logs – a crucial aspect for both operational troubleshooting and security auditing.
