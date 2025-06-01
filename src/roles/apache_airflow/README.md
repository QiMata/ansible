# apache_airflow Ansible Role

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

This role installs and configures **Apache Airflow** on Debian/Ubuntu systems. It manages the necessary installation steps and service configuration to run Airflow as a systemd-managed service. The role is designed to be **idempotent** and supports both single-node deployments (using Airflow’s SequentialExecutor) and multi-node high-availability setups (using CeleryExecutor with a message broker). Key features include:

* **Flexible Installation**: Installs a specific Airflow version (default **2.6.3**) via pip, using Python 3. You can install Airflow either in a **system Python environment** or an **isolated virtualenv** (controlled by `airflow_venv_path` variable).
* **Service Orchestration**: Creates a dedicated Unix user/group for Airflow and sets up systemd **unit files** for core Airflow components – **webserver**, **scheduler**, and (optionally) **Celery worker** – enabling them to run as background services (auto-start on boot, auto-restart on failure). The webserver listens on port **8080** by default.
* **Configuration Management**: Deploys Airflow’s configuration file (`airflow.cfg`) with appropriate settings for the executor, database (metadata store), broker (if using Celery), and logging. Sensitive config values (e.g. Fernet key, database URL) are written to `airflow.cfg` with secure file permissions (mode 0600). An environment file is placed at `/etc/default/airflow` (mode 0644) to set `AIRFLOW_HOME`, etc., for the systemd services.
* **Single-node or HA**: By default, the role uses **SequentialExecutor** with a local SQLite database for simplicity (suitable for testing or a single-node setup). For a production or multi-node environment, you can switch to **CeleryExecutor** to distribute tasks across worker nodes – in which case an external **database** (e.g. PostgreSQL) and a **message broker** (e.g. Redis) are required (not installed by this role). The role’s templates already account for Celery settings (broker URL, result backend) when CeleryExecutor is enabled.
* **Remote Logging (Optional)**: Supports toggling Airflow’s remote logging to **Elasticsearch**. If `airflow_remote_logging: true`, the role will configure Airflow to send task logs to an Elasticsearch endpoint (you must provide the `airflow_elasticsearch_host`). By default, remote logging is **disabled** (logs are kept on the local filesystem).
* **User Account Isolation**: Runs Airflow processes under a non-root system account (`airflow` by default) with no login shell, for security and least privilege. All Airflow files (configs, DAGs, logs) reside under a dedicated home directory (default `/opt/airflow`) and are owned by this account.
* **High-Level Workflow**: After this role runs, the Airflow services are installed and started. For example, on a single node, the webserver and scheduler processes will be running and the Airflow UI accessible on port 8080. In a multi-node scenario, you might run this role on one host (webserver/scheduler) and separately on other hosts (workers) with adjusted variables (e.g., only enabling the worker service on those).

> **Architecture Note:** The diagram below illustrates a typical multi-node Airflow setup using CeleryExecutor, which this role can help configure:

```mermaid
flowchart TB
    A[Airflow Webserver] -->|Metadata DB| D[(PostgreSQL/MySQL)]
    B[Airflow Scheduler] -->|Metadata DB| D
    C[Airflow Worker(s)] -->|Metadata DB| D
    B -.->|Task Queue| E[(Redis/RabbitMQ Broker)]
    C -.->|Task Queue| E
```

In the above, all Airflow components share a Metadata Database (storing DAGs, task states, etc.), and if using CeleryExecutor, the Scheduler queues tasks in a message broker which Workers consume. The webserver provides the UI and relies on the DB for state. This role sets up the Airflow processes and configuration, but **external services like the database and broker must be provided separately**.

## Supported Operating Systems/Platforms

This role is tested on and supported with the following Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** Target hosts must use a systemd-based OS (Debian/Ubuntu) for the managed services to function. Other distributions or init systems are not explicitly supported or tested. Ensure Python 3 is available on the target OS (Debian/Ubuntu come with Python3 by default, which is required for Airflow).

## Role Variables

Below is a list of important variables for this role, along with their default values (defined in **`defaults/main.yml`**) and descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                            | Default Value                             | Description |
| ----------------------------------- | ----------------------------------------- | ----------- |
| **`airflow_version`**               | `"2.6.3"`                                 | Version of Apache Airflow to install. This exact version will be installed via pip (using Airflow’s constraint files for consistency). Make sure this version is compatible with your Python version on the target host. |
| **`airflow_user`**                  | `"airflow"`                               | Name of the system user that will run Airflow services. The role will create this user if it does not exist. By default it is a system account (no login shell, no password) for security. |
| **`airflow_group`**                 | `"airflow"`                               | Name of the system group for Airflow. The user specified above will belong to this group. The role ensures this group exists. Files in `airflow_home` will be owned by this user and group. |
| **`airflow_home`**                  | `/opt/airflow`                            | Filesystem path for Airflow Home. All Airflow configuration, DAGs, and logs reside here. The role creates this directory (and key subdirectories like `dags/` and `logs/`) with appropriate ownership (`airflow:airflow`) and permissions (0755) if they don’t exist. |
| **`airflow_python`**                | `/usr/bin/python3`                        | Path to the Python 3 interpreter to use for Airflow. By default, this is the system Python. If using a virtualenv, this should still point to a Python3 binary (e.g. the one used to create the venv). |
| **`airflow_venv_path`**             | *Empty string* (no venv)                  | Path to a **Python virtual environment** to use for Airflow. If provided, the role will create a venv at this path and install Airflow into it. If left empty (`""`), Airflow will be installed into the system Python environment. *(Ensure the `python3-venv` package is installed on the host if using a venv.)* |
| **`airflow_executor`**              | `"SequentialExecutor"`                    | Which Airflow executor to use. Default is SequentialExecutor (all tasks run in-process, single machine). Change to `"CeleryExecutor"` for a multi-node setup to distribute tasks (requires a message broker and a database backend). The role’s configuration template will adjust Airflow config based on this value (enabling Celery settings if CeleryExecutor is chosen). |
| **`airflow_systemd_units_enabled`** | `["webserver", "scheduler", "worker"]`    | List of Airflow component services to set up on the host. By default, all three unit files (webserver, scheduler, worker) are installed. You can adjust this list if a host should run only specific components (e.g., workers only). **Note:** If using SequentialExecutor (no Celery), you may omit `"worker"` here to avoid an unused worker service being started. (If left in, the worker service may fail or remain inactive since Celery isn’t configured in that mode.) |
| **`airflow_database_url`**          | `sqlite:///{{ airflow_home }}/airflow.db` | Connection string (SQLAlchemy URL) for Airflow’s metadata database. Defaults to a local SQLite database file in the Airflow home directory. For production, you should use an external database like PostgreSQL or MySQL (e.g., `postgresql+psycopg2://airflow:<pass>@<host>/<db>`). **Important:** The role does not set up the database server; it must be present and accessible. |
| **`airflow_broker_url`**            | `redis://localhost:6379/0`                | URL for the message broker to use when `airflow_executor` is CeleryExecutor. Defaults to a local Redis instance on default port. If you switch to CeleryExecutor, you must ensure a Redis or RabbitMQ service is running at this URL. Not used at all for SequentialExecutor. |
| **`airflow_fernet_key`**            | `"CHANGE_ME"`                             | Fernet key for Airflow to encrypt connection passwords in the database. **This must be changed for any non-test environment** – all Airflow instances in the same cluster must share the same key. You can generate a key with `openssl rand -base64 32`. The default is a placeholder. Consider using Ansible Vault to keep this secure. |
| **`airflow_remote_logging`**        | `false`                                   | Whether to enable remote logging. If `true`, Airflow will send task logs to the remote log handler (Elasticsearch by default) instead of storing locally. Ensure `airflow_elasticsearch_host` is set if enabling. If `false`, Airflow will rely on local disk logs under `{{ airflow_home }}/logs`. |
| **`airflow_elasticsearch_host`**    | `"http://elasticsearch:9200"`             | The Elasticsearch endpoint URL for remote logging. Used only if `airflow_remote_logging` is enabled. Defaults to a placeholder pointing to a host named "elasticsearch" on port 9200. You may need to adjust this (and ensure the appropriate Elasticsearch configuration on the Airflow side, such as providing credentials or using a secure URL, if applicable). |
| **`airflow_logging_json`**          | `true`                                    | Whether to use JSON format for Airflow logs. If set, Airflow’s logging configuration will output logs in JSON (useful for ingesting into ELK stacks). This affects both local and remote logs. Defaults to true, meaning JSON logging is enabled in Airflow config. |
| **`airflow_extra_pip_packages`**    | *Empty list* `[]`                         | A list of additional Python packages to install via pip **alongside Airflow**. Use this to install Airflow provider packages or extras. For example: `airflow_extra_pip_packages: ["apache-airflow[celery,redis]==2.6.3"]` would ensure Celery and Redis dependencies are installed (matching the Airflow version). By default this list is empty. |

</details>

<!-- markdownlint-enable MD033 -->

In addition to the above, all of these defaults can be overridden in your inventory or playbook as needed. Notably, you should **always change** `airflow_fernet_key` from the default and provide a real key (32-byte base64). Similarly, if using **CeleryExecutor**, you must supply a proper `airflow_database_url` (pointing to a supported external database) and `airflow_broker_url` for your message broker. The `airflow_extra_pip_packages` variable is a convenient way to include necessary extras or provider packages; for example, to use Celery you may include the Airflow Celery extra as shown above, or to use a specific database, include the appropriate Airflow provider (e.g. `apache-airflow-providers-postgres`). All Airflow services will use the same configuration file (`airflow.cfg`), so ensure the variables like `airflow_database_url` and `airflow_fernet_key` are consistent across hosts in a multi-node setup.

## Tags

This role does **not define any Ansible tags** in its tasks. All tasks will run by default when the role is invoked. (You may still apply tags externally when including the role, if desired.)

## Dependencies

* **Ansible Version:** Requires Ansible **2.13** or higher, as defined in the role metadata. This is to ensure compatibility with newer modules (e.g. `ansible.builtin.systemd`) and syntax.
* **Collections:** No external Ansible collections are required by this role; it uses only modules included in Ansible Core (e.g. `group`, `user`, `template`, `pip`, `lineinfile`, `systemd` etc.). Just make sure you have installed any collections needed for your *playbook* if you use external roles for DB/broker (see [Cross-Referencing](#cross-referencing)).
* **Python and System Packages:** The target hosts must have **Python 3** available (the role uses `/usr/bin/python3` by default) and a working package manager. If you plan to use a Python virtual environment (`airflow_venv_path`), ensure that the **`python3-venv`** package is installed on the system (for Debian/Ubuntu) so that the `python3 -m venv` command works. Additionally, having **`pip`** available is recommended; the role will attempt to ensure pip is present by upgrading it via the `pip` module, but on a bare system you might need to install `python3-pip` first.
* **External Services:** Apache Airflow itself depends on a database and (for CeleryExecutor) a message broker, but this role **does not install or configure those external services**. You should prepare:

  * A **database server** (e.g. PostgreSQL or MySQL) for Airflow’s Metadata DB if not using the default SQLite. Airflow will need proper connectivity and credentials to this DB (provided via `airflow_database_url`).
  * A **message broker** such as Redis or RabbitMQ if using CeleryExecutor. The default broker URL assumes Redis on localhost. If you use Redis, it can be running on the same Airflow machine or a different host (adjust the URL accordingly). The Airflow worker systemd service as provided will try to ensure a local Redis service is present (it has `Requires=redis-server.service`), so if your broker is remote or not named `redis-server`, you might need to tweak that service file or use an override.
* **OS Packages for Airflow**: Airflow may require certain system libraries (for example, SSL libraries, SASL, etc.) depending on the features you use. This role doesn’t explicitly install system packages aside from Python, but it’s wise to ensure your system has some common dependencies. For instance, if using PostgreSQL, the `libpq` library and the `psycopg2-binary` Python package (or the OS package `python3-psycopg2`) should be present. The Airflow documentation lists recommended system packages for LDAP, kerberos, etc. (e.g., `libsasl2-modules`, `libkrb5-dev`, etc.); install these as needed before running the role, if you plan to enable those features in Airflow.

No other Ansible roles are required by `apache_airflow` itself – it is a self-contained role. However, you may use additional roles to set up the environment (database, cache, etc.) as described below in [Cross-Referencing](#cross-referencing).

## Example Playbook

Here is an example of how to use the `apache_airflow` role in a playbook to set up a single-node Airflow instance (using defaults for a quick start):

```yaml
- hosts: airflow_server
  become: yes  # ensure we have privilege to install packages, create users, etc.
  vars:
    airflow_fernet_key: "pP5NXB2LwN1kEg4S0dL7X2v9WFMm3n8G"  # example secure key (use your own)
    # (Optional) If you want to use CeleryExecutor in a multi-node setup, uncomment and adjust:
    # airflow_executor: "CeleryExecutor"
    # airflow_database_url: "postgresql+psycopg2://airflow:DB_PASSWORD@dbserver/airflow"
    # airflow_broker_url: "redis://redis-server:6379/0"
    # airflow_extra_pip_packages: ["apache-airflow[celery,redis]==2.6.3"]
  roles:
    - apache_airflow
```

In the above play, we run the role on a host (or group of hosts) designated as `airflow_server`. We elevate privileges with `become: yes` because the role needs to install packages and configure system services. We override `airflow_fernet_key` with a secure value (the default `"CHANGE_ME"` should **never** be used in production). All other variables are left at defaults, which means the play will install Airflow 2.6.3 using SequentialExecutor with a local SQLite DB and set up the webserver and scheduler services on the host.

If you wanted to configure a **multi-node Airflow** deployment, you could adjust the variables as indicated (e.g., use CeleryExecutor and point `airflow_database_url` to an external database and `airflow_broker_url` to your Redis/RabbitMQ). You would run the `apache_airflow` role on each node: perhaps one host as the webserver/scheduler (with `airflow_systemd_units_enabled` containing `"webserver"` and `"scheduler"`) and one or more hosts as workers (with `airflow_systemd_units_enabled: ["worker"]`). All nodes should share the same `airflow_database_url` and `airflow_fernet_key` so they operate against the same backend and encryption key. This role will ensure the Airflow config and services are in place on each machine; it’s up to you to provide the external database, broker, and network configuration so that the components can communicate.

After running the playbook, if everything succeeds, you should have:

* Airflow’s pip packages installed (either globally or in the specified venv).
* An `airflow` user and group on the system.
* Directories `/opt/airflow`, `/opt/airflow/dags`, `/opt/airflow/logs` created.
* Configuration file `/opt/airflow/airflow.cfg` populated with the chosen settings.
* Systemd services `airflow-webserver`, `airflow-scheduler` (and `airflow-worker` if enabled) installed and started. You can check their status with `systemctl status airflow-webserver`, etc.
* The Airflow web UI accessible on port 8080 (e.g., `http://<airflow_host>:8080`) on the webserver host.

**Note:** The first time Airflow is installed, you may need to initialize the database before the scheduler can run tasks. This can be done by running the command `airflow db init` (or `airflow db upgrade`) as the Airflow user. The role itself does **not** run this command for you, so consider performing this step manually or via an ad-hoc Ansible task after the role executes, especially if using a fresh metadata database.

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to verify its behavior in a clean environment before applying it to your servers. A Molecule test scenario is provided under `molecule/` for this role. Here’s how you can run it:

1. **Install Molecule** (and Docker) on your development machine, if not already installed. For example: `pip install molecule[docker]` (this installs Molecule and the Docker support). Make sure Docker is running on your machine.
2. **Navigate to the role directory**. From the root of the `ansible` repository, go to `src/roles/apache_airflow`. Molecule will look for its config in `molecule/default/`.
3. **Run the Molecule test sequence**. You can run `molecule test` to perform a full test (which will create containers, apply the role, run verifications, then destroy the containers). During development, you might run steps individually:

   * `molecule create` to spin up the test container(s).
   * `molecule converge` to apply the role to the container(s) (this uses the playbook in `molecule/default/converge.yml`, which applies the role with default settings).
   * `molecule verify` to run any verification tests (if implemented; e.g., with Testinfra or Ansible asserts).
   * `molecule destroy` to clean up the containers.
     Running `molecule test` will do all of the above in order.
4. **Examine the results**. After converge, you can check manually that the role did what you expect. For example, you might connect to the container: `docker exec -it <container_id> /bin/bash`, and then verify:

   * The `airflow` user exists (`id airflow`).
   * Airflow is installed (`airflow version` command works).
   * Configuration file is present at `/opt/airflow/airflow.cfg`.
   * Services are enabled (check `/etc/systemd/system/airflow-*.service` files). If the container supports systemd, you can even try `systemctl status airflow-webserver`.
   * Logs or any other expected files are in place (`/opt/airflow/logs/` has been created, etc.).
5. **Cleanup**. Destroy the test environment with `molecule destroy` if you didn’t already run `molecule test`. This will remove the test container(s) to free resources.

Using Molecule ensures the role is idempotent and works on a fresh system. The provided Molecule scenario uses a Docker image (Debian/Ubuntu) to simulate a target host. Note that when testing Airflow in Docker, the systemd services might not fully start if the container isn’t systemd-enabled. The focus of testing should be on the role’s idempotence and configuration changes. You can adjust variables in `molecule/default/converge.yml` (for example, to test with CeleryExecutor by setting `airflow_executor: "CeleryExecutor"`) and run `molecule converge` again. If you do so, ensure the container has a broker available (you might spin up a Redis container and adjust `airflow_broker_url` accordingly for the test).

## Known Issues and Gotchas

* **Initial Database Initialization:** After installing Airflow, you must initialize the metadata database schema. This role does **not** run `airflow db init` or migrations automatically. On a brand new Airflow installation (especially with a fresh PostgreSQL/MySQL backend), the scheduler and webserver might fail to start properly until the database is set up. To address this, run `airflow db init` (for a new install) or `airflow db upgrade` (when upgrading versions) as the `airflow` user before or just after the first deployment. This step creates the necessary tables in your Airflow database.
* **SQLite vs. Real Database:** The default setup uses SQLite (a local file) for simplicity, but SQLite has limitations. It does not support concurrent access by multiple processes well, so if you run multiple Airflow components (e.g. webserver and scheduler) on the same SQLite DB, you may encounter locks or other issues. SQLite is fine for testing or single-user scenarios. For any production or multi-node use, switch `airflow_database_url` to a proper database (Postgres, etc.) and install the corresponding DB driver (e.g. include `psycopg2-binary` in `airflow_extra_pip_packages` for Postgres).
* **Celery Executor Requirements:** If you enable `CeleryExecutor`, remember that you **must** have a message broker (and preferably a results backend, though Airflow can use the metadata DB as the result backend as configured by default). The default `airflow_broker_url` is pointing to a local Redis, and the provided systemd **worker** service expects a `redis-server` service on the same host. If you intend to use an external Redis or RabbitMQ host, you should adjust the broker URL accordingly *and* be aware that the systemd unit’s dependency on `redis-server` might need removal or override. In addition, you’ll likely want to install Celery and Redis support for Airflow (e.g. via `airflow_extra_pip_packages` as shown in the example) since the base Airflow installation may not include those extras. Failing to do so will cause the worker or scheduler to error out due to missing dependencies.
  Also, when using CeleryExecutor in a multi-node setup, ensure all nodes use the **same Fernet key** and connect to the **same metadata database**. Tasks won’t run if, for example, workers point to a different DB than the scheduler.
* **No Default Admin User:** This role does not create any Airflow user accounts. Out of the box, Airflow’s web UI will have **no user** initially (Airflow >=2 requires you to create an admin account to log in, since there is no default password). After the first deploy, create an admin user by running the appropriate command on the Airflow host, for example: `airflow users create --username admin --password YOUR_PASSWORD --firstname YOUR_NAME --lastname YOUR_NAME --role Admin --email YOUR_EMAIL`. Do this once (e.g., on the webserver host) to be able to log into the Airflow UI. Keep in mind to use a strong password and possibly execute this in a secure manner (you could automate it with an Ansible task if desired, but it’s not included here).
* **Webserver Access & Authentication:** The Airflow webserver is configured to run on port 8080 and, by default, will allow connections from anywhere (no firewall rules are set by this role). Ensure that you don’t expose the Airflow UI to the public internet unintentionally. If this Airflow instance is for internal use, run it in a private network or behind a firewall/security group. If it must be accessible externally, consider putting it behind a reverse proxy with SSL and perhaps enabling authentication (Airflow supports various auth backends like LDAP, OAuth, etc., beyond the scope of this role). At minimum, remember to create the admin user as noted above, so the UI is password-protected.
* **Changing/Removing Components:** By default, all three systemd services (webserver, scheduler, worker) are installed and started. If you are setting up a host that should **not** run one of these (for example, a dedicated worker node that shouldn’t run a webserver), you need to override `airflow_systemd_units_enabled` accordingly. The role will only manage the services listed in that variable. If you leave `worker` in the list but you’re not actually using CeleryExecutor, the `airflow-worker` service may continuously restart/fail since it cannot connect to a broker. It’s safe to remove unused services from the list to tailor each host’s role.
* **DAG Distribution:** This role does not handle how your Airflow **DAG files** are distributed or managed. It creates an empty `dags/` directory in `airflow_home` on each host. In single-node setups, you can simply place your DAG files there (e.g., copy them as part of a deploy play or use a separate role). In multi-node scenarios (multiple workers), you are responsible for ensuring all Airflow machines have the same set of DAGs (via NFS mounts, git-sync, or other deployment strategies). If workers don’t have the DAG definition, they won’t be able to run the tasks. Plan a strategy for DAG distribution outside of this role’s scope.
* **Log Handling:** By default, Airflow writes task logs to files under `{{ airflow_home }}/logs`. The role sets up this directory but does not rotate or ship these logs off the server. If `airflow_remote_logging` is enabled, logs will go to Elasticsearch instead, but you need to have a reachable Elasticsearch service and possibly additional configuration (authentication, index management) in place – the role only populates the basic Airflow config for it. Monitor the size of the local logs directory over time; you may want to periodically clean old logs or enable log rotation. Airflow has a built-in log cleanup utility you can use via an Airflow task or script.
* **Systemd in Containers:** If you are testing this role in a container (e.g., with Molecule or Docker), note that running systemd services inside a Docker container can be tricky. The Molecule test scenario attempts to run the role in a Docker container, but without a full init system, the `Enable and start Airflow services` task might not actually launch the services. In a real VM or physical server, systemd will properly enable and start the services. For container-based tests, focus on checking that the unit files were generated correctly and installation steps completed, rather than expecting the services to be running in the container.

## Security Implications

* **System User & Permissions:** This role creates an `airflow` system user and group to run Airflow, with no login shell (`/usr/sbin/nologin`) and home directory set to the Airflow home path. Running Airflow under a dedicated non-root account is a security best practice – it confines the Airflow processes to limited privileges. All files under `airflow_home` are owned by `airflow:airflow`. The role sets directory permissions to 0755 (owner read/write/execute, world-readable) and the main config file `airflow.cfg` to 0600 (only the airflow user can read it). This means other users on the system cannot read sensitive Airflow configuration like the Fernet key or database password. However, note that the DAGs and logs (in directories with 0755) are readable by others on the system; if your server is multi-user, you might tighten those permissions or use group isolation.
* **Service Ports:** The Airflow webserver listens on **TCP port 8080** by default (configured in the systemd unit). This is a non-privileged port and the service runs as the airflow user, which is good from a privilege standpoint. There is no SSL or authentication configured by this role; security relies on Airflow’s own authentication for the web UI and network-level protections. If 8080 is open in your firewall, anyone who can reach it could attempt to access the UI. Ensure that only trusted networks can reach the Airflow web interface, or put a reverse proxy with HTTPS in front of it if needed. Similarly, if you expose the Airflow REST API (not covered by this role explicitly), consider securing it with authentication and TLS.
* **Data Encryption:** Airflow uses the Fernet key provided to encrypt passwords and other sensitive data in its metadata database. By default, the role sets a dummy Fernet key `"CHANGE_ME"`, which is **not secure**. If you do not change this, all your connection passwords in the Airflow DB would effectively be unencrypted (since the key is public and known). It is crucial to supply a strong, random Fernet key and keep it consistent across Airflow instances. Treat this key like a password – store it securely (for example, in an Ansible Vault or a secrets manager) and limit its exposure. The key is stored in plaintext in `airflow.cfg` on each Airflow host, but as mentioned, that file is permissioned 0600 to restrict access.
* **Database Credentials:** The `airflow_database_url` typically contains the database credentials for Airflow’s metadata DB (username, password, host, etc.). This URL is saved in the Airflow config file. Ensure your database is configured securely: use a strong password for the Airflow DB user, and ideally restrict the database to only accept connections from the Airflow hosts. The config file’s protections (0600 mode) help prevent local users from reading the password, but you should also guard against any backups or logs that might reveal it. If possible, use TLS connections to the database and do not enable remote access to the database from arbitrary hosts.
* **Broker Security:** For CeleryExecutor, the default assumes a local Redis instance without authentication (Redis by default has no password and listens on localhost). If you use a remote Redis or RabbitMQ, configure proper authentication (e.g., Redis password or SSL, RabbitMQ user credentials) and firewalls. The Airflow config can include these in the broker URL (for example: `redis://:password@redis-host:6379/0`). This role does not expose a separate variable for the broker password, so you’d include it directly in `airflow_broker_url`. That means it will be stored in plaintext in `airflow.cfg` as well, so handle accordingly. The systemd **worker service** includes `Requires=redis-server.service`, which implies the broker is local; if you run a broker on a different host, that dependency doesn’t apply and can be overridden or ignored (the worker will still attempt to connect to the remote broker as long as the URL is correct). If running Redis locally, ensure it’s bound to a secure interface (e.g., localhost or internal network) and not exposing ports publicly.
* **Inter-process Communication:** In a multi-node Airflow deployment, the scheduler, webserver, and workers communicate via the database and message broker. There is no direct authentication between these processes beyond what the database and broker enforce. So securing those components (DB access control, broker auth) is essential. Also, all nodes must have synchronized time (consider running NTP) to avoid issues with schedule timing and token expirations (especially if using Kerberos or OAuth for Airflow, if applicable).
* **Elevated Privileges for Tasks:** Airflow tasks themselves will run under the `airflow` user account (since the worker or scheduler launches them). This user has no special sudo privileges by default (this role does not configure any sudoers entry for airflow). If your DAGs require accessing system resources or other privileges, you might be tempted to grant airflow broader rights – avoid doing so unless absolutely necessary, as it could undermine the isolation. It’s better to design DAG tasks that don’t need root access, or to use specific service accounts for particular tasks if needed.
* **Log Data and PII:** Airflow task logs can contain sensitive information (e.g., stack traces with secrets, data samples, etc.). With default local logging, these reside on the server and are readable by the airflow user (and by others if they have read access to the logs directory). With remote logging to Elasticsearch, those logs will be sent over the network to the `airflow_elasticsearch_host`. Ensure that your transport to ES is secure (consider using an HTTPS URL and proper auth for Elasticsearch). Anyone with access to the Elasticsearch index or the local log files could read the log contents, so restrict access accordingly. The role’s default of JSON logging `true` means logs might include structured data; ensure no sensitive data is inadvertently being logged by your DAGs.
* **Airflow Upgrades:** When upgrading Airflow to a new version (by changing `airflow_version` and rerunning the role), be mindful of security changes or new config in Airflow itself. Always read the Airflow release notes. This role will install the new version and update the config file, but it will not automatically run `airflow db upgrade` – which may be required to apply database migrations for the new version. Failing to apply migrations could leave your Airflow in an inconsistent (and possibly insecure) state. Always perform database backups and then run migrations when upgrading Airflow. Airflow may also generate a new Fernet key if one is not provided on upgrade (in our case we always provide one, so it should reuse it).
* **Cleaning Up Sensitive Data:** If you ever need to decommission an Airflow server, remember that the metadata DB contains your connection info (encrypted by Fernet) and potentially XCom data that might hold snippets of data from tasks. The `airflow.cfg` holds secrets as discussed. Treat these files and databases as sensitive data. Wipe or securely delete as appropriate when disposing of hardware or handing off servers.

## Cross-Referencing

This role focuses on installing Airflow itself. You will likely use it in conjunction with other roles/services to build a complete Airflow environment:

* **Database Setup**: For a robust setup, use a role to deploy a database like PostgreSQL or MySQL. For example, the **`postgresql`** role in this repository can set up a PostgreSQL server which Airflow can use as its metadata database.
* **Message Broker**: If you need a Redis broker for Celery, you can use an existing Ansible role such as the popular **`geerlingguy.redis`** role (which this project uses in some playbooks) to install and configure Redis. Ensure the broker is running and reachable at the URL you configure in `airflow_broker_url`.
* **Related Roles**: There may be other roles in this repository that complement Airflow in a data platform context. For instance, roles for schedulers, monitoring, or specific integrations. Check the repository documentation for any references to Airflow. (At this time, there aren’t specific “Airflow client” roles here, but you might find roles for things like reverse proxies or for deploying Airflow on Kubernetes, etc., in other contexts.)

Remember that Airflow is just one component of your data workflow ecosystem. While this role sets up Airflow itself, you should also consider using roles or playbooks to configure:

* **External Storage** for DAG code or plugins (if not keeping them in the local filesystem).
* **Monitoring/Alerting** for Airflow (ensuring logs are aggregated, setting up health checks, etc.).
* **Backups** of your Airflow metadata database.

By combining the `apache_airflow` role with database and cache roles, and following the guidelines above, you can compose a full Airflow deployment playbook tailored to your needs. Each component can be managed by its respective role for clarity and reuse.
