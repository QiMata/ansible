# Ansible Role: Amundsen Search

## Overview

**Amundsen Search** is the search service component of the Amundsen data discovery platform. It provides a RESTful API that handles search queries for data catalog metadata, leveraging an Elasticsearch backend for indexing and querying. This Ansible role automates the installation and configuration of the Amundsen Search service on a target host. It sets up a Python virtual environment, installs the Amundsen Search package (via pip), applies the necessary configuration (such as the connection to the Elasticsearch cluster), and runs the service under **Gunicorn** behind a **systemd** unit. By using this role, you can deploy the search API service in an automated, idempotent way, integrating it with the rest of the Amundsen platform (Frontend UI and Metadata service).

## Table of Contents

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
* [Diagrams](#diagrams)

## Supported Operating Systems/Platforms

This role is tested on **Ubuntu 20.04 LTS** and **Ubuntu 22.04 LTS** (64-bit) hosts. It should also work on other Debian-based Linux distributions and on Red Hat Enterprise Linux/CentOS 8+ (and their derivatives), as long as the system meets the role requirements (Python 3, systemd, etc.). The target host **must** use a systemd-based init system because the role installs a systemd unit file for the Amundsen Search service. Non-systemd environments (e.g. minimal containers without an init system, or Windows hosts) are not supported out-of-the-box.

> **Note:** Ensure that Python 3 is available on the managed host. On Ubuntu, the package `python3-venv` is required to create Python virtual environments. On RHEL/CentOS, make sure the `python3` interpreter and venv module are installed. The role does *not* install Python itself. It assumes you have a functioning Python 3 on the host. If these prerequisites are missing, the role’s tasks for creating the virtual environment will fail.

## Role Variables

The following variables can be adjusted to configure the Amundsen Search installation. Each variable (defined in the role’s `defaults/main.yml`) is listed below with its default value and description:

| Variable                  | Default                              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `amundsen_search_version` | `"4.0.0"`                            | The version of the **Amundsen Search** Python package to install (via pip). By default, version 4.0.0 is installed. You can change this to deploy a different release of Amundsen Search – just ensure that the version you choose is compatible with the versions of your Amundsen Frontend and Metadata services (it's recommended to keep all Amundsen components on the same version).                                                                                                                                             |
| `search_bind_host`        | `"0.0.0.0"`                          | The network interface address on which the search service will listen. By default this is all interfaces (`0.0.0.0`), meaning the search API will be accessible on any network interface of the host. You can set this to `127.0.0.1` to restrict it to localhost (only local applications or an on-host Frontend could access it), or to a specific interface IP to limit exposure. This setting affects the bind address in the Gunicorn server.                                                                                     |
| `search_port`             | `5001`                               | The TCP port that the Amundsen Search service listens on for incoming HTTP requests. The default is **5001**, which is Amundsen’s standard port for the search service API. If you change this, be sure to update any clients (e.g. the Amundsen Frontend configuration) to use the new port for search requests.                                                                                                                                                                                                                      |
| `search_gunicorn_workers` | `4`                                  | Number of Gunicorn worker processes to run for the search service application. By default 4 worker processes are spawned to handle requests concurrently. Increase this value if you expect higher query load or have more CPU cores available (each Gunicorn worker is a separate process). This value will be reflected in the systemd service (it sets the `--workers` flag for Gunicorn).                                                                                                                                          |
| `search_virtualenv`       | `"/opt/amundsen/search/venv"`        | Filesystem path for the Python virtual environment where the Amundsen Search package will be installed. The role will create this directory and set up a virtualenv there, then install the `amundsen-search` package into it. You can change this path if you need to use a different directory structure or storage location. By default, it installs under `/opt/amundsen/search/venv`. All service files (like the config file) will reside in this directory.                                                                     |
| `es_host`                 | `"localhost"`                        | Host address of the **Elasticsearch** service (or cluster endpoint) that the Amundsen Search service will connect to for indexing and searching. By default, it assumes Elasticsearch is running on the *same host* (localhost). If your Elasticsearch cluster is on another server or uses a separate endpoint (e.g., an Elasticsearch cluster VIP or DNS name), you **must** override this to point to that host/IP so that the search service can reach it.                                                                         |
| `es_port`                 | `9200`                               | Port number on which Elasticsearch is listening for its HTTP API. The default `9200` is standard for Elasticsearch. If your Elasticsearch runs on a different port (for example, if using a proxy or a managed service with a custom port), set this variable accordingly.                                                                                                                                                                                                                                                             |
| `search_config_class`     | `"search_service.config.ProdConfig"` | The Python class (including module path) that the search service will use for its configuration. By default, this points to the `ProdConfig` class in Amundsen’s search service module. This role deploys a configuration file that defines `ProdConfig` with the appropriate settings (notably the Elasticsearch endpoint and log level). In most cases you should leave this at the default. Advanced users could override it to point to a custom config class if they have a modified configuration, but that is rarely necessary. |

**Variable usage:** In most deployments, you will only need to override a few of these defaults. For example, if your Elasticsearch is running on a different host than the search service, set `es_host` (and possibly `es_port`) to point to the correct location. All other variables have sensible defaults. You might adjust `amundsen_search_version` to match a specific release version across your Amundsen services, or tweak `search_port` if 5001 conflicts with another service, but typically the defaults work for a standard installation. For reference, the role’s default values are defined in [`roles/amundsen_search/defaults/main.yml`](../amundsen_search/defaults/main.yml).

## Tags

This role does **not** define any task-level tags by default. All tasks will run whenever the role is invoked. If you need to control execution more granularly, you can apply your own tags at the play or role inclusion level. For example:

```yaml
- hosts: amundsen_search
  roles:
    - { role: amundsen_search, tags: ["amundsen_search"] }
```

Then you could run `ansible-playbook playbook.yml --tags amundsen_search` (or `--skip-tags amundsen_search`) to specifically target (or skip) this role’s tasks. By default, however, there are no internal tags within the role, so the tasks are either all applied or all skipped together based on whether the role runs.

## Dependencies

**Ansible Collections:** This role uses only modules from Ansible’s built-in collection (i.e. `ansible.builtin`). You do not need any specific Ansible Galaxy collections for the role’s tasks. Modules like `user`, `file`, `command`, `pip`, `template`, and `systemd` are all part of Ansible core (or the default included modules). However, note that the wider repository (playbooks and other roles) may rely on certain collections. In particular, the project’s overall requirements include **community.general** (>= 8.6.0) and **community.postgresql** (>= 3.4.0). Ensure those collections are installed if you are running this role as part of the larger playbook that includes roles (e.g., for PostgreSQL or other components) which require them.

**System Packages:** The target host needs a working Python 3 environment and the ability to create Python virtual environments. On Debian/Ubuntu systems, make sure `python3` and `python3-venv` are installed (the latter is required for the `python3 -m venv` command). On RHEL/CentOS, ensure the `python3` interpreter and venv module are present (e.g., via the `python3` or `python36` packages). The role assumes the host can connect to the Python Package Index (PyPI) or an internal mirror to download the **`amundsen-search`** Python package and its dependencies. If the host has restricted internet access, you should provide the Python package via an offline wheel or local mirror. Additionally, the host must have **systemd** available, since the role installs a systemd service unit to manage the search process.

**Other Dependencies:** This role focuses on the Amundsen *Search* service itself and does *not* install the other components of the Amundsen platform. For a fully functional Amundsen deployment, you will also need the following components set up (via other roles or processes):

* **Amundsen Metadata service** – Provides the metadata API and serves as the source of truth for data catalog information. Typically deployed via the `amundsen_metadata` role. The metadata service uses Neo4j as its backend database.
* **Amundsen Frontend service** – The web UI that end-users interact with. It calls the search service’s API to display search results. Deployed via the `amundsen_frontend` role.
* **Metadata database (Neo4j)** – The Neo4j graph database that the metadata service uses to store catalog data. You may deploy Neo4j using the `neo4j` role in this repository (which replaced the older `neo4j_server` role), or ensure it’s provisioned separately.
* **Search index (Elasticsearch)** – An Elasticsearch cluster or service that stores the search index for Amundsen. The search service uses this as its backend for search queries. You can deploy one via the `elasticsearch` role (which merges the earlier Elasticsearch roles in this repository), or use an existing Elasticsearch service.

While not formal Ansible role dependencies (this role can run on its own), the above components are required for Amundsen to function as a whole. Notably, the Amundsen Search service requires a reachable Elasticsearch backend; this role **does not install Elasticsearch** itself. Ensure that an Elasticsearch instance is available and that `es_host`/`es_port` are set accordingly. Likewise, the search service assumes that the Amundsen Metadata service is populating the Elasticsearch indices with data (via an ingestion job such as Amundsen Databuilder) – without that, the search service will have no data to return. It’s recommended to use the corresponding roles (metadata, frontend, database, Elasticsearch) or other provisioning methods to set up those pieces alongside this role. Make sure to configure the Amundsen Frontend (via its variables `search_api_base` etc.) so it knows how to reach the search service, especially if they are on different hosts.

## Example Playbook

Below is an example of how to use the `amundsen_search` role in an Ansible playbook. This example assumes you have a host (or group of hosts) dedicated to the search service, and that your Elasticsearch cluster is running on a separate host (or cluster) accessible at `es1.internal` on port 9200:

```yaml
- hosts: amundsen_search
  become: yes  # escalate privileges to install packages, create users, etc.
  vars:
    es_host: "es1.internal"         # Elasticsearch host for the search index
    # es_port: 9200                # (Optional) Elasticsearch port, if not the default 9200
  roles:
    - amundsen_search
```

**Explanation:** This play targets the inventory group **`amundsen_search`** (which should contain the host(s) where you want to deploy the search service). We use `become: yes` because the role performs system-level changes (installation, user creation, service setup) that require root privileges. We override the `es_host` variable to point to the Elasticsearch endpoint (`es1.internal` in this example) since the search service is not running on the same machine as Elasticsearch. (If Elasticsearch were local, the default `localhost` would suffice.) Finally, we include the `amundsen_search` role to perform the installation and configuration on those hosts.

In a real-world scenario, you would also run the complementary roles for the other Amundsen components. For example, your playbook might also include `amundsen_metadata` (against a host or group for the metadata service), `neo4j` (if setting up the Neo4j DB for metadata), and `elasticsearch` (for the search backend), as well as the `amundsen_frontend` role for the UI. These could be orchestrated in one playbook (possibly as separate plays for each host group) or invoked via separate playbooks for each layer. The key is to ensure all components are deployed and configured to know each other’s endpoints (e.g., the Frontend needs the search service URL, and the search service needs the Elasticsearch URL as shown above).

## Testing Instructions

This role can be tested using **Molecule**, which is a framework for automating Ansible role tests (often using Docker containers as targets). A Molecule configuration for this role would typically set up a container, apply the role, and verify that the service comes up as expected. To run the tests, ensure you have Molecule installed (along with the Docker driver and any dependencies):

1. **Install testing requirements:** On your development machine, install Molecule and other tools. For example:

   ```bash
   pip install molecule molecule[docker] ansible-core ansible-lint yamllint
   ansible-galaxy collection install -r requirements.yml
   ```

   The above installs Molecule and the Docker driver, Ansible Core, and linting tools, and installs any required Ansible collections (based on the repository’s `requirements.yml`).

2. **Run Molecule tests:** Navigate to the role’s directory and run Molecule. For example:

   ```bash
   cd roles/amundsen_search
   molecule test
   ```

   This will execute the default Molecule test sequence: it will create a Docker container, apply the `amundsen_search` role to it (performing a “converge”), then run any verifications (if configured, such as checking the service status or HTTP health check), and finally destroy the test container. You should see output indicating that the role’s tasks ran and whether the assertions (if any) passed.

   If you want to iterate or debug, you can run steps separately: for instance, `molecule create` (to start the container), `molecule converge` (to apply the role), and then use `molecule login` to enter the container for manual inspection. You can also run `molecule verify` to execute any test scripts, or `molecule destroy` to clean up the environment. Adjust the Molecule commands as needed if there are multiple scenarios (e.g., `molecule test -s <scenario>`), though typically this role would have a default scenario.

3. **Verify functionality:** After Molecule converges the role, you can verify that the Amundsen Search service is running inside the container. For example, you might check that the systemd service `amundsen-search` is active (`systemctl status amundsen-search` inside the container) and that port 5001 is listening. If the Molecule scenario includes a verification step, it may try something like an HTTP health check (e.g., `curl http://localhost:5001/healthcheck`) to ensure the search service is responding. All these steps can be automated in Molecule’s verify phase or done manually when logged into the instance.

By following these steps, you can validate that changes to the role do not break its functionality. Molecule provides an isolated environment to test the role tasks without affecting real servers.

## Known Issues and Gotchas

* **Elasticsearch Host Misconfiguration:** One common pitfall is not setting the `es_host` (and `es_port` if needed) correctly when Elasticsearch is running on a different host. If the Amundsen Search service starts up but cannot connect to Elasticsearch, search queries will fail or return no results. Double-check that `es_host` points to the correct hostname/IP where your Elasticsearch cluster is reachable **from the search host**. The default is `localhost`, which is only correct if Elasticsearch is on the same machine. In multi-host deployments, override this to the proper address of your Elasticsearch node or load balancer.

* **Service Fails to Start:** If the `amundsen-search` service does not start, or starts and then immediately stops, you should inspect the service logs to diagnose the issue. Use `journalctl -u amundsen-search -f` to follow the logs in real time after attempting to start the service. Common causes for startup failure include an inability to reach the Elasticsearch backend (for example, connection refused if `es_host`/`es_port` are wrong or the ES service is down), or missing Python dependencies if the pip installation failed. Ensure that Elasticsearch is running and accessible from the search host (network connectivity, no firewall blocking port 9200, etc.). Also verify that the Python virtual environment was created and the `amundsen-search` package (version specified by `amundsen_search_version`) was installed successfully. If the virtualenv creation step failed (often due to Python’s venv module not being available), install the system’s `python3-venv` package and re-run the role. The role is idempotent, so running it again after fixing prerequisites should configure the service correctly.

* **Version Mismatch Between Components:** Amundsen’s services are designed to work together on matching versions. If you deploy the search service with a version that doesn’t match your frontend or metadata service, you may encounter API incompatibilities or runtime errors. For example, Amundsen Search 4.0.0 expects to work with Amundsen Metadata 4.0.0 and Frontend 4.0.0. Running it against a Metadata service of version 3.x could lead to missing fields or errors in search results. It’s recommended to use the **same version across Amundsen Frontend, Metadata, and Search**. If you change `amundsen_search_version` to try a newer (or older) version, consider updating the other roles’ versions as well to keep the stack in sync, unless the Amundsen release notes explicitly guarantee backward/forward compatibility.

* **Initial Indexing (Empty Search Results):** After deploying the search service, you might find that it returns no results for any query initially. This is expected if the Elasticsearch indices have not been populated yet. This role **does not** handle data ingestion into Elasticsearch. You must run an Amundsen data builder or ingestion job separately to index your metadata into the search service’s indices. For example, using the Amundsen Databuilder to extract metadata from your data sources and publish it to Elasticsearch. Until such an ingestion is done, the search service will have an empty index (or just the index mappings with no documents) and thus will return empty results. If you’re seeing no data in search, ensure that: (a) the Metadata service is up and collecting data, and (b) an ingestion pipeline has run to push data into Elasticsearch. Once the indices (like `table_search_index`, `user_search_index`, etc.) are populated, the search API will start returning results.

* **Security and Access Control:** By default, the search service does not enforce any authentication or authorization on its API. It is assumed to be deployed in a trusted environment (e.g., accessible only by the Amundsen Frontend or internal users). If the search service’s port (5001) is left open on an untrusted network, anyone who can reach it could query your data catalog via the API. This could be a security concern if the metadata is sensitive. Make sure to restrict access to the search service to only the necessary hosts/users. For instance, if Frontend is the only consumer, the search API port might be firewalled to only allow the Frontend host. If you set `search_bind_host` to `127.0.0.1`, that effectively restricts access to processes on the same host (which is secure if Frontend runs on the same machine). In distributed setups, consider using firewall rules or security groups to limit who can reach port 5001. *(See the **Security Implications** section below for more on this.)*

* **TLS/HTTPS and Encryption:** The Amundsen Search service, as deployed by this role, listens over plain HTTP (no TLS) on port 5001. In many cases, the search API is kept internal (not exposed to end-users directly), so this may be acceptable. However, if your Frontend service will communicate with the search service over an untrusted network, or if you have compliance requirements for encryption in transit, you should secure this channel. The role itself does not configure TLS for the search service. A common approach is to place the search service behind a reverse proxy or load balancer that terminates HTTPS. For example, you might run Nginx or Apache on the host (or use a cloud load balancer) that listens on an HTTPS endpoint and forwards requests to `localhost:5001`. Alternatively, if your environment supports it, you could enable TLS within Elasticsearch and use HTTPS between search and ES (though that still doesn’t secure the 5001 port). The key point is that additional steps are needed to enable encryption; out-of-the-box the service is HTTP-only. Be sure to also configure Frontend to use the appropriate protocol (http vs https) and address for the search API if you implement TLS.

* **Firewall and Connectivity:** In a multi-host deployment, verify that all necessary network connections are open:

  * The **Amundsen Frontend** host(s) must be able to reach the search service on port **5001** (HTTP). If there are firewalls or security groups, allow traffic from Frontend to Search on this port.
  * The **Search service** host must be able to reach the **Elasticsearch** cluster on the configured `es_port` (default **9200**). Ensure no firewall is blocking outbound/inbound connections on 9200 between the search host and the ES nodes.
  * End-users typically do *not* need direct access to port 5001 (search) or 5002 (metadata service) – those ports are consumed by the Frontend. It’s wise to prevent public or untrusted access to these backend service ports. Only the Frontend (or your internal admin users for testing) should query the search API. Lock down any unnecessary exposure at the network level.

  If the search service appears unresponsive or the Frontend shows errors connecting to it, a network misconfiguration is a likely culprit. Adjust `hosts.ini` (inventory) variables if needed to ensure the Frontend is pointed at the correct address, and confirm network routes and firewall rules.

* **Updating Configuration Changes:** Whenever you modify the role’s configuration (for instance, changing `es_host` to point to a different Elasticsearch instance, or altering the `search_port`), you will need to re-apply the role or manually update the deployed configuration for those changes to take effect. The search service’s config file is located at `{{ search_virtualenv }}/config.py` (by default, `/opt/amundsen/search/venv/config.py`). The systemd service uses environment variables (such as `ELASTICSEARCH_HOST` and `ELASTICSEARCH_PORT`) and that config file when starting the service. The role is designed to handle changes: it will update the config and restart the service if you run it again with new variable values (thanks to handlers on the template). If you choose to edit the configuration manually, make sure to **restart the service** (`systemctl restart amundsen-search`) after making your changes so that the new settings are applied. Keep in mind that if you manually edit the config.py or service file, those changes may be overwritten by a future run of Ansible, so it’s better to use Ansible variables to manage configuration whenever possible.

## Security Implications

Deploying the Amundsen Search service with this role introduces a few security considerations to keep in mind:

* **System User:** The role creates (if not already present) a dedicated system user **`amundsen`** to run the search service process. This user has no login shell (`/usr/sbin/nologin`) and is not intended for interactive use. Running the search service under a non-root service account is a security best practice – it limits the potential impact of a compromise. All files installed by the role (the virtualenv, config file, logs, etc.) are owned by this `amundsen` user (or accessible to it) and not by root, wherever possible. You should avoid granting this account any additional privileges on the system beyond what’s needed to run the service. For example, do not add `amundsen` to sudoers or to privileged groups. The principle of least privilege ensures that even if the search service is exploited, the attacker’s access to the system is limited.

* **Open Port (Service Accessibility):** By default, the search service listens on TCP port **5001** on all network interfaces (`0.0.0.0`). This means that unless network policies are in place, the Amundsen Search API will be reachable by any client that can contact the host on port 5001. In an environment where the search service host has a public or untrusted network interface, this could expose your metadata search API to the internet or broader network. **This role does not configure any firewall** – it assumes you will manage access control externally. If exposing the search service is not desired, consider the following:

  * Set `search_bind_host: "127.0.0.1"` to bind the service only to the loopback interface. This way, only applications on the same host (such as a co-located Frontend service or SSH port-forwarding) can access it. This is a quick fix if Frontend runs on the same machine.
  * Use firewall rules or cloud security groups to restrict access to port 5001. For instance, allow only the IP address of your Frontend server (or your internal network range) to connect to port 5001 on the search host. Block all other sources.
  * Deploy the search service behind a VPN or reverse proxy that can enforce access controls. For example, you might only allow connection to the search API from within a VPN, or require an SSH tunnel for access in debugging scenarios.

  In summary, treat the search API endpoint as sensitive. In most cases, end-users should never directly talk to it (they go through the Frontend), so it’s good to keep it shielded. Only expose it to the Frontend and perhaps admin machines for troubleshooting. If left open, an attacker could potentially query your data catalog via the search API without going through any UI or authentication.

* **No Encryption (HTTPS) by Default:** The Amundsen Search service, when deployed by this role, does not use TLS encryption on its own. It serves HTTP on port 5001. If your deployment is entirely within a secure network enclave, this might be acceptable. However, if any part of the communication between the Frontend and the Search service goes over an untrusted network (for example, different data centers, or cloud networks where you don’t trust the substrate), you should encrypt the traffic. As mentioned earlier, the role doesn’t configure TLS, but you have options:

  * Terminate TLS at a reverse proxy or load balancer. You could run Nginx/Apache on the search host (or use an external proxy) listening on HTTPS (port 443, for instance) and forward requests to the local search service on 5001. This way, the external traffic is HTTPS, and only the local proxy-to-service is HTTP.
  * Use a VPN or SSH tunnel for connections between Frontend and Search if they must traverse an insecure network.
  * If Elasticsearch itself is configured with TLS, that secures the Search-to-ES traffic, but note you’d still have search service traffic in the clear if not otherwise protected.

  Ensure that any sensitive metadata returned by the search service is not traveling in plaintext over networks where it could be sniffed. In production, it is a good practice to have at least the user-facing portions of the traffic encrypted (Front->Search, Front->Metadata). Often, the Search API is kept internal, but consider your threat model and compliance requirements. **The role leaves HTTPS configuration up to you.**

* **Authentication and Authorization:** The Amundsen Search API does not have built-in authentication in its default configuration – it trusts that only authorized systems (like the Frontend) will call it. That means anyone who can send HTTP requests to it can query the catalog. If your Amundsen instance contains metadata that shouldn’t be open to all employees or all network users, you need to enforce access control at a higher level. This could mean:

  * Securing network access as described above (so only certain hosts/users can even reach the API).
  * Enabling authentication in the Amundsen platform: Typically, authentication is handled at the Frontend level (the UI). The Search service doesn’t usually do auth on its own. If you enable authentication for Frontend (using OAuth/OIDC, LDAP, etc.), and you ensure that Search is not accessible except via the Frontend, that provides a gate.
  * If you have a use case where clients might query the Search API directly, you’d have to implement a custom authentication layer (for example, behind an authenticated gateway or by customizing the search service code to enforce authZ). This is advanced and not covered by the role.

  In short, **do not consider the search service to be safe to expose without restrictions**, since it doesn’t authenticate requests by default. Always integrate it into a larger security context (trusted networks, front-end auth, etc.) to avoid data leakage.

* **Service Permissions & File Security:** The systemd unit that this role installs runs the search service process as the `amundsen:amundsen` user and group (not as root). The installation process places files in `/opt/amundsen/search/venv` (and the config file there) with appropriate ownership. For example, the configuration file `config.py` is owned by `amundsen:amundsen` and set with mode 0644 (readable by owner and others, writable only by owner). The systemd service file (`/etc/systemd/system/amundsen-search.service`) is owned by root and world-readable (which is normal for unit files). By using a dedicated user and restricting file permissions, the role helps ensure that other unprivileged users on the system cannot modify the Amundsen Search service or its configuration. Only the `amundsen` user (and root) should be able to write the important files. This containment reduces risk: even if someone has a normal user account on the server, they shouldn’t be able to alter the search service behavior or read sensitive config (though in this case, the config doesn’t contain secrets, just endpoints). Always review file permissions if you add any credentials or secrets to the config (none are there by default). It’s good practice to keep the virtualenv and config directory owned by the service user and not accessible to others except for read access as needed.

* **Interactions with External Systems:** The Search service will initiate outgoing connections to two places during normal operation: the Elasticsearch cluster (on port 9200, by default) and (indirectly) possibly to a metadata ingestion pipeline (though ingestion usually runs as a separate process, not via the running service). From a security perspective, ensure that the Elasticsearch cluster is secured appropriately. If your ES requires authentication (e.g., basic auth or API keys) or uses TLS, you would need to adjust the search service configuration template (`search_config.py.j2`) to include those details (the default assumes no auth and HTTP). The role currently doesn’t support setting an ES username/password or CA cert via variables, so any such customization would be manual. Also, consider that if the search service were compromised, an attacker could send arbitrary queries to Elasticsearch. Therefore, you might want to configure Elasticsearch security roles to limit what the search service can do (for instance, it likely only needs read/search and index creation privileges on specific indices, not full cluster admin rights). In most deployments, the search service and Elasticsearch reside in the same trusted network, but it’s worth noting for defense-in-depth.

* **Automatic Restart Behavior:** The systemd unit is configured to always restart the search service on failure (with a 5-second delay between attempts). This helps keep the service running if it crashes or encounters a transient error. However, be mindful that if there is a persistent configuration issue (for example, wrong Elasticsearch host causing immediate failure on startup), the service will enter a crash loop, continually restarting. This can fill your logs quickly or put load on Elasticsearch with repeated connection attempts. If you observe the service continuously restarting (`systemctl status amundsen-search` will show a changing PID and "failed" states, and `journalctl` will show repetitive logs), you should intervene: check logs to find the cause, and fix the configuration or environment. You can temporarily stop the service (which will override the restart for that session) using `systemctl stop amundsen-search` while troubleshooting. In extreme cases, you could disable the automatic restart by editing the unit file to `Restart=no`, but usually it’s better to fix the root cause. The restart policy is generally beneficial for resilience. Just be aware it’s happening in the background.

In summary, after deploying with this role, **review the exposure and security posture of the Amundsen Search service**. Key points include ensuring the search API port is not broadly accessible, adding encryption (TLS) if needed for network traffic, and aligning with your organization’s authentication policies (likely by gating access via the Frontend). The role follows best practices by using a least-privilege service account and not running as root. It’s advisable to keep the system and Python packages updated as well, to pull in security fixes for any libraries (Flask, Gunicorn, etc.) that the search service depends on. By combining network security, proper configuration, and regular maintenance, you can run the Amundsen Search service in a secure and reliable manner.

## Cross-Referencing

This repository contains other roles that complement or relate to the **Amundsen Search** role. You will typically use these in conjunction to deploy the full Amundsen platform or its dependencies:

* **[amundsen_metadata](../amundsen_metadata/README.md)** – *Amundsen Metadata Service role*. Installs and configures the Amundsen Metadata service (the API server for metadata, usually running on port 5002). The Metadata service works with a Neo4j database to store catalog information and is responsible for providing metadata to the Frontend, as well as feeding data into the Search index.
* **[amundsen_frontend](../amundsen_frontend/README.md)** – *Amundsen Frontend (UI) role*. Deploys the Amundsen Frontend web application (running on port 5000). The Frontend is the user interface of Amundsen and depends on both the Metadata service and the Search service for its data. In configuration, the Frontend is pointed to the URLs of the Metadata and Search APIs.
* **[neo4j](../neo4j/README.md)** – *Neo4j Database role*. Sets up a Neo4j graph database server. Amundsen Metadata service uses Neo4j as its backend database to store the metadata graph (tables, users, relationships, etc.). Deploying Neo4j (via this role or otherwise) is necessary for the metadata service to function. In the context of Amundsen, Neo4j often runs on a separate host or the same host as metadata service, and it should be secured (it listens on a bolt port, default 7687, and possibly an HTTP port for browser).
* **[elasticsearch](../elasticsearch/README.md)** – *Elasticsearch role*. Provisions an Elasticsearch service or cluster, used by Amundsen Search as the search index backend. This unified role installs Elasticsearch, configures it (including security if desired), and ensures the service is running.

*Additional context:* Aside from the Amundsen-specific roles, you might also consider applying a base or common role to your hosts (e.g., the [Base role](../base/README.md) in this repository) prior to installing Amundsen components. The Base role ensures the OS is up-to-date and has fundamental configuration (like security hardening, Python, etc.) which can be beneficial as a preparation step. While not strictly required, having that baseline can prevent common issues (for example, the base role might install Python or other dependencies that Amundsen roles need). After the search service is up, you will likely run ingestion jobs (not covered by an Ansible role here) to populate data. Those might be orchestrated via Apache Airflow or simple cron jobs running the Databuilder – if an Airflow role or similar exists in the repo, it could be relevant for scheduling Amundsen data updates.

Each of the above roles has its own documentation. Refer to those READMEs for details on their variables and usage. By combining the **amundsen_search** role with the **amundsen_metadata**, **amundsen_frontend**, and the necessary database and search backend roles, you can deploy a complete Amundsen data catalog system. The roles are designed to work together as seen in the example playbook (where each runs on appropriate host groups). Ensure you read the docs of each to understand any interdependencies (for instance, the metadata role will have a variable for Neo4j connection, the frontend role requires the URLs for metadata and search services, etc.).

## Diagrams

Below are diagrams to illustrate the deployment and architecture of the Amundsen Search service in the context of this role and the broader Amundsen ecosystem.

**Deployment Flow (Role Tasks):** The flowchart below shows the main steps this role performs on the target host to install and configure the Amundsen Search service:

```mermaid
flowchart TD
    A[Ensure 'amundsen' user exists] --> B[Create search directory<br/>(e.g. /opt/amundsen/search)]
    B --> C[Create Python virtualenv<br/>in /opt/amundsen/search/venv]
    C --> D[Install Amundsen Search<br/>Python package (pip)]
    D --> E[Generate config.py from template<br/>(with Elasticsearch endpoint)]
    E --> F[Deploy systemd unit file<br/>(amundsen-search.service)]
    F --> G[Enable & start service via systemd]
    G --> H[Amundsen Search service running<br/>on port 5001]
```

In the above flowchart, each step corresponds to a task or set of tasks in the role:

* **A:** The role ensures a system user **`amundsen`** exists to run the service.
* **B:** It creates the necessary directory structure for the service (here the parent directory for the virtualenv, `/opt/amundsen/search`).
* **C:** It creates a new Python virtual environment in that directory (`venv` subdirectory) for isolating the search service’s Python packages.
* **D:** It installs the Amundsen Search Python package inside the virtualenv using pip (pinned to the specified `amundsen_search_version`).
* **E:** It generates a configuration file (`config.py`) from a Jinja template, injecting the Elasticsearch host/port and other settings. This config is placed in the virtualenv directory.
* **F:** It deploys a systemd service unit (`amundsen-search.service`) that defines how to run the search service (Gunicorn command, environment variables for config, etc.).
* **G:** It runs `systemctl daemon-reload` (via a handler) to pick up the new unit file, then enables the service to start on boot and starts it immediately.
* **H:** Once started, the search service is running and listening on the configured port (5001 by default), ready to serve search API requests.

**Network Communication Structure:** The following diagram shows how the Amundsen Search service interacts with other components in a typical Amundsen deployment (default ports in parentheses):

```mermaid
flowchart LR
    U[User Browser]
    F[Amundsen Frontend<br/>(Gunicorn,<br/>port 5000)]
    M[Amundsen Metadata Service<br/>(API, port 5002)]
    S[Amundsen Search Service<br/>(API, port 5001)]
    N[Neo4j Database<br/>(Bolt port 7687)]
    E[Elasticsearch Cluster<br/>(port 9200)]
    U -- HTTP 5000 --> F
    F -- REST API calls 5002 --> M
    F -- REST API calls 5001 --> S
    M -- Bolt 7687 --> N
    S -- HTTP 9200 --> E
```

In the network diagram above:

* End-users interact with the **Amundsen Frontend** through their web browser (typically via HTTP or HTTPS on port 5000). The Frontend is the UI that users see.
* The Frontend server, in turn, makes internal REST API calls to the **Metadata Service** and **Search Service**. By default, the Frontend calls the Metadata API on port 5002 and the Search API on port 5001 (assuming those services run on the same host or reachable addresses). These calls fetch table metadata, user information, search results, etc., which the Frontend then displays.
* The **Metadata Service** uses a **Neo4j** graph database (Bolt protocol on port 7687) to store and retrieve metadata. The Frontend itself does not talk to Neo4j directly; it goes through the Metadata service API.
* The **Search Service** communicates with an **Elasticsearch** cluster (usually over HTTP on port 9200) to index and query search data. When you perform a search in Amundsen, the Frontend sends the query to the Search service, which in turn executes a search query against Elasticsearch and returns the results.
* The Search service does *not* directly interact with the Neo4j database or the Metadata service during normal search queries. Its data comes from Elasticsearch, which is populated by separate ingestion processes (not shown in the diagram). Typically, an ingestion job will extract data from the Metadata service (or directly from data sources) and load it into Elasticsearch via the Search service’s API or directly into ES indices.

All components (Frontend, Metadata service, Search service, Neo4j, Elasticsearch) can be installed on a single server for a small test deployment, or they can be split across multiple servers for scalability and isolation. In production, you might have:

* One host for Frontend,
* One host for Metadata service (and maybe the Neo4j DB on the same or separate host),
* One host for Search service,
* A cluster of hosts for Elasticsearch.

Communication between them should be secured according to your environment (e.g., use internal networks or TLS as needed). The **amundsen_search** role specifically sets up the Search service (highlighted as "Amundsen Search Service" in the diagram). It assumes that the **Elasticsearch** backend is available (as shown on the right side of the diagram) and that the **Frontend** will be configured to know where the Search service is (as shown on the left side). The other roles (for Metadata, Frontend, Neo4j, Elasticsearch) handle their respective pieces. When all are deployed and configured correctly, the Amundsen platform works as follows: a user searches for a data asset in the UI, the Frontend calls the Search service, the Search service fetches results from Elasticsearch (which was loaded with metadata), and the Frontend displays the results, possibly fetching additional details from the Metadata service as needed. This role ensures the Search service part of that pipeline is up and running, ready to serve those search queries.
