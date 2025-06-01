# Ansible Role: Amundsen Frontend

## Overview

**Amundsen Frontend** is the web application (UI) component of the Amundsen data discovery platform. This Ansible role installs and configures the Amundsen Frontend service on a target host. It handles setting up a Python virtual environment, installing the Amundsen Frontend package (via pip), applying the necessary configuration (such as connecting to Amundsen metadata and search services), and running the frontend as a persistent service under **Gunicorn** and **systemd**. By using this role, you can deploy the Amundsen UI on a host and integrate it with the rest of the Amundsen platform in an automated, idempotent way.

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
* [Diagrams](#diagrams)

## Supported Operating Systems/Platforms

This role is tested on **Ubuntu 20.04 LTS** and **Ubuntu 22.04 LTS** (64-bit). It should also work on other Debian-based Linux distributions and on Red Hat Enterprise Linux/CentOS 8+ (as well as their derivatives) provided that the system meets the role requirements (Python 3, systemd, etc.). The target host **must** use a systemd-based init system because the role installs a systemd unit file for the Amundsen Frontend service. Non-systemd environments (e.g., containers without an init system, or Windows) are not supported out-of-the-box.

> **Note:** Ensure that Python 3 is available on the managed host. On Ubuntu, the package `python3-venv` is required to create Python virtual environments. On RHEL/CentOS, ensure the `python3` interpreter and venv module are installed. The role does not install Python itself.

## Role Variables

The following variables can be adjusted to configure the Amundsen Frontend installation. Each variable, along with its default value (defined in the role’s `defaults/main.yml`), is listed below:

| Variable                    | Default                                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `amundsen_frontend_version` | `"4.0.0"`                                | The version of the **Amundsen Frontend** Python package to install (via pip). By default, version 4.0.0 is used. You can change this to install a different release of Amundsen Frontend (ensure compatibility with the metadata and search services).                                                                                                                                                                                                       |
| `frontend_bind_host`        | `"0.0.0.0"`                              | The network interface address on which the frontend web service will listen. By default this is all interfaces (`0.0.0.0`), meaning the UI will be accessible from any network interface on the host. You can set this to `127.0.0.1` to restrict it to localhost or to a specific IP.                                                                                                                                                                       |
| `frontend_port`             | `5000`                                   | The TCP port that the frontend service listens on for incoming HTTP requests. The default is **5000**, which is Amundsen’s standard frontend port. If you change this, clients must adjust their URLs accordingly.                                                                                                                                                                                                                                           |
| `frontend_gunicorn_workers` | `4`                                      | Number of Gunicorn worker processes to run for the frontend application. By default 4 workers are spawned to handle requests concurrently. Increase this value for higher traffic or more CPU cores, if needed (each worker is a separate process). This value is used in the systemd startup command for Gunicorn.                                                                                                                                          |
| `frontend_virtualenv`       | `/opt/amundsen/frontend/venv`            | Filesystem path for the Python virtual environment where the Amundsen Frontend package will be installed. The role will create this venv and install the package inside it. You can change this to relocate the installation (useful if you have a different directory structure or storage location).                                                                                                                                                       |
| `metadata_api_base`         | `http://localhost:5002`                  | Base URL of the **Amundsen Metadata service** API that the frontend will communicate with. By default, it points to localhost on port 5002 (the default metadata service port). If your metadata service is on a different host or port, you **must** override this to the correct URL. For example, `http://meta1.internal:5002` if the metadata service runs on host `meta1.internal`.                                                                     |
| `search_api_base`           | `http://localhost:5001`                  | Base URL of the **Amundsen Search service** API that the frontend will use for search queries. Default is localhost on port 5001. Change this if the search service is on a different host/port. For example, set `http://search1.internal:5001` if the search service runs on a separate host.                                                                                                                                                              |
| `frontend_config_class`     | `amundsen_application.config.ProdConfig` | The Python class (with module path) that the frontend service will use for its configuration. By default, this is set to Amundsen’s `ProdConfig` class. This role deploys a config file that defines `ProdConfig` to extend the default settings. In most cases you should leave this as default. Advanced users can supply a different config class or extend the configuration if custom settings (like authentication options or UI branding) are needed. |

**Variable usage:** Most deployments will at minimum need to adjust `metadata_api_base` and `search_api_base` if the metadata/search services are not running on the same host as the frontend. All other variables have sane defaults but can be overridden as required (e.g., to upgrade `amundsen_frontend_version`, change port, etc.). The variables can be overridden in your playbook or inventory. For reference, the role’s default values are defined in [`roles/amundsen_frontend/defaults/main.yml`](../amundsen_frontend/defaults/main.yml).

## Tags

This role does **not** define any task-level tags by default. All tasks will run whenever the role is invoked. If you need to control execution more granularly, you can apply your own tags at the play level or when including the role. For example, in a playbook you could tag the role as `amundsen_frontend` and then use `--tags amundsen_frontend` or `--skip-tags amundsen_frontend` on the command line. By default, however, there are no internal tags, so the role’s tasks are either all applied or all skipped together.

## Dependencies

**Ansible Collections:** This role uses only modules from Ansible’s built-in collection (e.g., `ansible.builtin`). No specific Ansible Galaxy collections are required for the role itself. (Modules like `user`, `file`, `command`, `pip`, `template`, and `systemd` are part of Ansible core or the default `ansible.builtin` collection.) However, note that the wider project’s requirements include **community.general** (>= 8.4.0) and **community.postgresql** (>= 3.4.0). Ensure those collections are installed if you are running this role as part of the larger playbook that requires them.

**System Packages:** The target host needs Python 3 and the ability to create Python virtual environments. On Ubuntu/Debian, install `python3` and `python3-venv` (if not already present) to satisfy this requirement. The role assumes that the host can access the Python Package Index (PyPI) or an internal mirror to download the `amundsen-frontend` Python package. If the host has no internet access, you should pre-download the package or provide an offline wheel/cache. Additionally, the host should have **systemd** (the role installs a systemd service unit to manage the frontend process).

**Other Dependencies:** This role focuses on the frontend component and does not install backend components of Amundsen. For a fully functional Amundsen deployment, you will also need:

* **Amundsen Metadata service** – provides the metadata API (commonly deployed via the `amundsen_metadata` role).
* **Amundsen Search service** – provides the search API (commonly deployed via the `amundsen_search` role).
* **Metadata database** – Amundsen’s metadata service typically uses Neo4j as a backend (you may deploy Neo4j via the `neo4j` role or have it pre-provisioned).
* **Search index** – The search service uses Elasticsearch as the search index. You may deploy an Elasticsearch cluster (for example via the unified `elasticsearch` role) or use an existing one.

While not formal Ansible role dependencies (this role can run on its own), the above components are required for Amundsen to function. Ensure that the `metadata_api_base` and `search_api_base` URLs are configured to point to the running metadata and search services. This role will not install Neo4j or Elasticsearch; those should be set up separately (the Amundsen metadata/search roles or other means should handle their installation and configuration).

## Example Playbook

Below is an example of how to use the `amundsen_frontend` role in an Ansible playbook. This example assumes you have separate hosts (or groups) for the frontend, metadata service, and search service. We override the `metadata_api_base` and `search_api_base` variables to point to the appropriate hostnames for those services:

```yaml
- hosts: amundsen_frontend
  become: yes  # The role performs system-level tasks, so escalation is needed.
  vars:
    metadata_api_base: "http://meta1.internal:5002"      # URL of metadata service
    search_api_base: "http://search1.internal:5001"      # URL of search service
  roles:
    - amundsen_frontend
```

**Explanation:** This play will run on the hosts in the inventory group **`amundsen_frontend`**. It elevates to root (`become: yes`) because tasks like installing packages and writing to `/etc/systemd` require privileges. The variables `metadata_api_base` and `search_api_base` are set so that the frontend knows how to reach the metadata and search services (in this case, hostnames `meta1.internal` and `search1.internal`). Finally, the role `amundsen_frontend` is applied to install and start the frontend service. In a full deployment, you would also run the `amundsen_metadata` role on the metadata host and `amundsen_search` on the search host, etc., possibly orchestrated in one playbook or across multiple plays.

## Testing Instructions

This role includes Molecule scenarios for automated testing. Molecule is used to create test environments (for example, Docker containers) and verify that the role works as expected. To run the tests for `amundsen_frontend`, follow these steps:

1. **Install Molecule and dependencies:** Ensure you have Python 3 on your control machine, then install Molecule and its Docker driver. For example:

   ```bash
   pip install molecule[docker] pytest testinfra
   ```

   You will also need Docker installed and running on your system, since the Molecule default scenario uses Docker containers as test instances.

2. **Navigate to the role directory:**

   ```bash
   cd roles/amundsen_frontend
   ```

   (Run this from the root of the Ansible repository. The molecule configuration for this role is located in its directory.)

3. **Run the test suite:** Execute:

   ```bash
   molecule test
   ```

   This will run Molecule’s default test sequence: it will create a container, apply the role, run verifications (if any), and then destroy the container. The output will show each step. If all goes well, you should see a "converged" message and the container will be torn down at the end.

4. *(Optional)* **Iterative testing:** During development or debugging, you can run steps individually. For example:

   * `molecule create` to just create the instance,
   * `molecule converge` to apply the role,
   * `molecule verify` to run verification tests (e.g., using Testinfra),
   * `molecule destroy` to clean up.
     This allows you to inspect the container in between steps (useful for debugging if something fails). Typically, however, `molecule test` is sufficient for a full run.

**Note:** The Molecule configuration by default uses a recent Ubuntu image (e.g., Ubuntu 22.04) as the test platform. You can inspect or modify `molecule/default/molecule.yml` to change the image or to adjust test settings. Ensure you have internet connectivity within the test environment (the role will attempt to `pip install` the Amundsen frontend package, which requires access to PyPI or a mirror).

## Known Issues and Gotchas

* **Missing or Incorrect Backend URLs:** One of the most common misconfigurations is not updating `metadata_api_base` or `search_api_base` when the metadata/search services are on separate hosts. If the Amundsen UI comes up but shows no data or cannot fetch information, double-check that these variables point to the correct location of your metadata and search services. The default is `localhost`, which is correct only if all services run on the same host. In multi-host deployments, override these to the proper hostnames or IPs.

* **Service Fails to Start:** If the `amundsen-frontend` service does not start or immediately stops, you can debug it by examining the logs. Use `journalctl -u amundsen-frontend -f` to tail the service logs. Common causes for startup failure include inability to reach the metadata or search APIs (which could cause the frontend to error out on startup), or missing Python dependencies. Ensure that the metadata and search services are running and accessible. Also verify that the Python virtualenv was successfully created and populated with the `amundsen-frontend` package (Molecule tests cover this, but in a custom environment you might want to check `/opt/amundsen/frontend/venv` for the installed package).

* **Version Mismatch:** Amundsen components (frontend, metadata service, search service) are developed in tandem. Running mismatched versions (e.g., frontend 4.0.0 with metadata service 3.x) may lead to API incompatibilities or UI errors. It’s recommended to use the same version for all Amundsen components. If you change `amundsen_frontend_version`, you should likely also update `amundsen_metadata_version` and `amundsen_search_version` in the respective roles to match, unless release notes indicate cross-version compatibility.

* **Authentication and Authorization:** By default, Amundsen Frontend does not enforce authentication – it’s typically open to anyone who can access the UI. The provided configuration (ProdConfig) does not enable any auth mechanism out of the box. If you require login or integration with an authentication provider (LDAP, OIDC, etc.), you will need to customize the frontend configuration. This may involve editing the `frontend_config.py.j2` template or overriding `frontend_config_class` to point to a custom config that enables your chosen auth. This role does not configure auth for you, so it’s a known gap for deployments that need it. Make sure to also secure the UI via network controls (firewalls or load balancer rules) if it’s in a sensitive environment and you are not enabling authentication.

* **SSL/TLS and Proxy Considerations:** The frontend service as installed by this role listens on HTTP (no TLS) by default on port 5000. If you need HTTPS, a common approach is to place a reverse proxy (like Nginx or Apache httpd, or a load balancer) in front of Amundsen Frontend to terminate SSL. The role itself does not set up HTTPS. When using a proxy, you might run the frontend bound to localhost (`frontend_bind_host: 127.0.0.1`) and let the proxy handle external requests. Ensure that any proxy or load balancer is configured to allow the needed URL paths. Also, if you restrict `frontend_bind_host` to localhost, remember to adjust monitoring or health-check systems accordingly (they may need to check via the proxy or on localhost).

* **Firewall and Connectivity:** In a multi-node setup, the frontend needs network access to the metadata service (default port 5002) and search service (default port 5001). If you have firewall rules (iptables, cloud security groups, etc.), ensure that the frontend host can reach those ports on the respective hosts. Similarly, end-users will connect to the frontend’s port (5000 by default), so that port should be accessible to your end-users (or open between the load balancer and the frontend). Conversely, you might want to **close off** direct access to the metadata and search service ports from end-users, since only the frontend needs to talk to those.

* **Updating Configuration:** If you change any configuration variable after the role has run (for example, altering `metadata_api_base` to point to a new metadata service endpoint), you will need to re-run the role or manually update the config file and restart the service. The config file is located at `{{ frontend_virtualenv }}/config.py` (by default `/opt/amundsen/frontend/venv/config.py`). The systemd service will pick up changes on restart. The role will handle restarting the service whenever it updates the config (it uses handlers to restart on config changes), but if you manually change something, be sure to restart the service (`systemctl restart amundsen-frontend`).

## Security Implications

Deploying the Amundsen Frontend via this role has a few security considerations to keep in mind:

* **System User:** The role creates a dedicated system user **`amundsen`** to run the frontend service. This user has no login shell (`/usr/sbin/nologin`) and is not meant for interactive use. Running the service as a non-root user is a security best practice – it limits the impact of any compromise of the application. The files and directories for the frontend (e.g., the virtualenv directory and config) are owned by this user. You should avoid giving this account extra privileges on the system beyond what’s needed to run the service.

* **Open Port:** By default, the frontend listens on TCP port **5000** on all network interfaces. This means that unless otherwise firewalled, the Amundsen UI will be accessible to anyone who can reach the host on that port. If this is not desired (for example, if the host has a public interface but you only want the UI available internally), consider one or more of the following: (a) set `frontend_bind_host` to a more restrictive address (such as `127.0.0.1` to bind only to localhost), (b) use firewall rules to restrict access to port 5000, or (c) deploy behind a VPN or reverse proxy. Only expose the UI to trusted networks or users, especially since by default it doesn’t require login.

* **No Encryption by Default:** The service as configured runs over plain HTTP. If you are deploying in a production environment, it is recommended to secure the traffic using TLS. The role does not configure TLS itself; typically you would handle this by putting the service behind an HTTPS reverse proxy or load balancer. Ensure that any sensitive metadata being viewed is protected in transit by implementing HTTPS at the network edge.

* **Authentication:** As noted in *Known Issues*, the default configuration does not enforce authentication. Anyone with network access to the frontend can use the Amundsen UI (which allows viewing of data metadata). If your data catalog contains sensitive information about data assets, you should enable an authentication mechanism. Amundsen supports integrations with OAuth/OIDC, LDAP, etc., but those require additional configuration not covered by this role. From a role perspective, enabling auth might involve providing a different config class or additional environment variables for the frontend. Treat the frontend as a sensitive application endpoint; control access to it if needed (via network or app-level auth).

* **Service Permissions:** The systemd unit file that this role installs runs the service as the `amundsen` user and group. It does not run as root, and it does not require any special privileges. The service is confined to its install directory and whatever network calls it needs to make. There are no elevated file system permissions given beyond that directory. The role sets file ownership and modes such that configuration files are readable by the `amundsen` user (and by root) but not writable by others. This helps ensure that unauthorized users on the system cannot tamper with the service or its configuration.

* **Ports and External Services:** The frontend will initiate connections to the metadata service (port 5002 by default) and search service (5001). Make sure those connections are secured appropriately (if running over a network, consider using TLS for those APIs if supported, or at least ensure the network path is internal). Also, because the frontend connects to these services, a malicious actor who gains control of the frontend could potentially send unexpected queries to metadata/search backends. Ensure your metadata and search services are not overly privileged in what they allow the frontend to do, and monitor their access as needed.

* **Automatic Restarts:** The systemd service is configured to always restart on failure (Restart=always with a 5 second delay). This is generally good for availability, but be aware that if the service is crashing due to a persistent issue (like misconfiguration), it will keep trying to restart. This could potentially fill logs or create a load on the system or backend services. If you notice the service in a crash loop (`systemctl status amundsen-frontend` will show if it's repeatedly restarting), investigate the cause in the logs (`journalctl -u amundsen-frontend`). The automatic restart policy can be tuned or disabled in the unit file if necessary for your environment.

In summary, after using this role, **review the exposure of the Amundsen Frontend** (open ports, accessible networks) and apply standard security hardening as appropriate: limit network access, enable authentication (if needed), and keep the system and Python packages updated (to pull in security fixes for Flask, Gunicorn, etc., which the frontend depends on).

## Diagrams

Below are diagrams to illustrate the deployment and architecture of Amundsen Frontend in the context of this Ansible role and the Amundsen ecosystem.

**High-Level Deployment Flow:** The flowchart below shows the main steps this role performs on the target host to deploy the Amundsen Frontend service:

```mermaid
flowchart TD
    A[Ensure 'amundsen' user exists] --> B[Create frontend directory<br/>(e.g. /opt/amundsen/frontend)]
    B --> C[Create Python virtualenv<br/>in /opt/amundsen/frontend/venv]
    C --> D[Install Amundsen Frontend<br/>Python package (pip)]
    D --> E[Generate config.py from template<br/>(with API endpoints)]
    E --> F[Deploy systemd unit file<br/>(amundsen-frontend.service)]
    F --> G[Enable & start service via systemd]
    G --> H[Amundsen Frontend running<br/>on port 5000]
```

**Network Communication Structure:** The following diagram shows how the Amundsen Frontend interacts with other components in a typical deployment (ports in parentheses are the default values):

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

In the network diagram above: end-users interact with the **Frontend** through their web browser (typically via HTTP or HTTPS on port 5000). The Frontend server, in turn, calls the **Metadata Service** and **Search Service** over internal APIs (HTTP calls to port 5002 and 5001, respectively) to fetch data and search results. The Metadata service uses a Neo4j graph database (Bolt protocol on port 7687) to store catalog data, and the Search service communicates with an Elasticsearch cluster (usually over HTTP port 9200) to index and query search data. The Frontend itself does not directly talk to the databases; it relies on those service APIs. Each component can be on a different host or all on one, depending on deployment size. The role **amundsen_frontend** configures the Frontend piece (highlighted in the diagram as "Amundsen Frontend"), and it assumes the other components are available and configured separately.
