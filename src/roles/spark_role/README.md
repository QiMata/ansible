# Ansible Role: Apache Spark (Standalone Cluster)

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
* [Cross-Referencing Related Roles](#cross-referencing-related-roles)

## Overview

The **Apache Spark** Ansible role installs and configures an Apache Spark **standalone cluster** on target hosts. It sets up Spark in a distributed mode with a **Spark Master** service and one or more **Spark Worker** services (executors). The role handles the following major tasks:

* **Installation**: Downloads the specified Spark release (by default, Apache Spark *3.4.1* built for Hadoop 3) from the official source and unpacks it under the installation directory (by default, **`/opt/spark`**). It also installs the required **OpenJDK 17** package (by default, `openjdk-17-jdk`) to provide a Java runtime for Spark. A dedicated system user and group (default **`spark`**) are created to own the Spark files and run the services.

* **Configuration**: Deploys configuration files for Spark, including the environment file (`spark-env.sh`) and Spark defaults (`spark-defaults.conf`). These templates set up environment variables such as memory and core usage for workers, log directories, and master connection settings. Event logging is enabled by default to a configurable directory (for use with the History Server). If high availability (HA) is enabled, the configuration will include the necessary settings for either **ZooKeeper** or file-based master recovery. The role also expects the inventory to define which hosts are Spark masters vs. workers using group names (see **Known Issues and Gotchas**).

* **Service Setup**: Installs and enables systemd service units for the Spark Master, Spark Worker, and (optionally) the Spark History Server. Each service is configured to run under the `spark` user with the appropriate startup commands (`start-master.sh`, `start-worker.sh`, `start-history-server.sh`). The Spark Master service listens on the default cluster port (7077) and a web UI port (default 8080). Spark Workers will register with the master’s URL and each provide a web UI (default 8081). A handler is included to restart Spark services if configuration changes (e.g., environment file updates).

* **Optional Features**: Supports deploying a **Spark History Server** (when `spark_history_enabled: true`) to aggregate and display job logs. If enabled, the role will set up a `spark-history-server` systemd service on the Spark Master node(s) and configure Spark to log events to a shared directory for history tracking. The role can also be configured for **High Availability (HA)** of the Spark Master. When `spark_ha_enabled: true`, multiple master nodes can be used: either using **ZooKeeper** for leader election (if `spark_zookeeper_hosts` is provided) or using a shared filesystem for master state (`spark_recovery_dir`). In HA mode, Spark masters coordinate so one is active and others are standby.

In summary, this role automates the provisioning of a Spark standalone cluster, handling the installation of binaries, creation of a dedicated user, configuration of cluster settings, and management of Spark as a persistent service. After applying this role, you will have Spark Master and Worker services running (on the designated hosts), ready to accept Spark jobs and manage them across the cluster.

> **Diagram:** The diagram below illustrates a typical Spark standalone cluster deployment with one master and two workers. It also shows optional components (dashed) for high availability (a standby master using ZooKeeper for coordination) and the Spark History Server for viewing past job events.

```mermaid
flowchart LR
    subgraph SparkCluster["Spark Cluster"]
        Master[Spark Master]
        Worker1[Spark Worker]
        Worker2[Spark Worker]
        Master --> Worker1
        Master --> Worker2
    end
    subgraph HAOptional["Optional HA"]
        Standby[Spark Master (Standby)]
        Master & Standby --> ZK[(ZooKeeper Ensemble)]
    end
    Master & Worker1 & Worker2 -. "Event Logs" .-> HistoryServer[Spark History Server]
    classDef dashed stroke-dasharray: 5 5;
    HAOptional:::dashed
    Standby:::dashed
    ZK:::dashed
    HistoryServer:::dashed
```

## Supported Operating Systems/Platforms

This role is designed for **Debian-based Linux distributions** and uses the APT package manager for installations. It has been developed and tested on:

* **Debian** – e.g. Debian 11 (Bullseye), Debian 12 (Bookworm)
* **Ubuntu** – e.g. Ubuntu 20.04, 22.04 LTS (should be compatible, given similar package names and availability of OpenJDK 17)

Other Debian/Ubuntu derivatives that use `apt` should also work with minimal or no modifications.

> **Note:** The role is **not natively supported on RHEL/CentOS or other non-Debian systems**. Tasks use Debian-specific package names and the `apt` module. Additionally, the role assumes a systemd-based OS for managing services. To use this role on Red Hat or CentOS systems, you would need to adapt it (e.g., replace `apt` with `yum`/`dnf` tasks, adjust package names for Java, and ensure systemd or equivalent service management is available). It’s recommended to run this role on Debian/Ubuntu hosts or containers. The minimum required Ansible version is **2.11** (as specified in `meta/main.yml`).

## Role Variables

Below is a list of variables available for this role, along with their default values (from **`defaults/main.yml`**) and descriptions. All variables are optional (the role provides defaults), but you will typically override some for your cluster needs (for example, memory or core settings, or to enable HA). Variables marked as **(conditional)** require special attention: for example, certain variables must be set when enabling specific features like HA or the history server.

<!-- markdownlint-disable MD033 -->

<details><summary>Role Variables (click to expand)</summary>

| Variable                | Default Value                                                                             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ----------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `spark_version`         | "3.4.1"                                                                                 | Version of Apache Spark to install. By default, this role installs Spark **3.4.1**. You can change this to any version available from the Apache Spark download site, ideally matching a version compatible with your applications.                                                                                                                                                                                                                                                                                                                                     |
| `spark_hadoop_version`  | "3"                                                                                     | The major Hadoop version that the Spark distribution is built for. Spark downloads are packaged for different Hadoop versions (e.g., "3" for Hadoop 3.x, "2" for Hadoop 2.x). The default is **3**, meaning the Spark binaries are for Hadoop 3.x. If you need a Spark build for Hadoop 2, set this to "2".                                                                                                                                                                                                                                                       |
| `spark_package_name`    | "spark-{{ spark_version }}-bin-hadoop{{ spark_hadoop_version }}"                        | The filename (base name) of the Spark package. This is constructed from `spark_version` and `spark_hadoop_version`. Typically you would not override this unless using a custom build; it forms the directory name after extraction (e.g., "spark-3.4.1-bin-hadoop3").                                                                                                                                                                                                                                                                                                |
| `spark_download_url`    | "https://dlcdn.apache.org/spark/spark-{{ spark_version }}/{{ spark_package_name }}.tgz" | URL to download the Spark tarball. By default it points to the official Apache download CDN for the specified version. In offline or firewalled environments, you should override this to a local mirror or pre-downloaded file path. **Note:** The role will skip re-downloading if the target file already exists (to avoid unnecessary downloads on repeat runs).                                                                                                                                                                                                    |
| `spark_install_dir`     | "/opt/spark"                                                                            | The base installation directory for Spark on the target host. The role will create this directory if it doesn’t exist and install Spark under this path. The actual Spark version will reside in a subdirectory named after `spark_package_name`.                                                                                                                                                                                                                                                                                                                       |
| `spark_symlink_dir`     | "/opt/spark/current"                                                                    | A symlink path that will point to the current Spark installation. After extracting Spark, the role updates this symlink to point to the `spark_install_dir/spark-{{ spark_version }}-bin-hadoop{{ spark_hadoop_version }}` directory. This provides a consistent path (`/opt/spark/current`) to refer to the Spark installation, which is used by service scripts and configuration.                                                                                                                                                                                    |
| `spark_user`            | "spark"                                                                                 | The system username that will run the Spark services and own Spark files. The role creates this user (if not present) as a system account. By default it will also create a group of the same name. You can change the name if needed (e.g., to integrate with an existing account policy).                                                                                                                                                                                                                                                                             |
| `spark_group`           | "spark"                                                                                 | The system group for Spark. By default, this is the same as `spark_user`. All Spark files and directories will be owned by this user and group. If you override this, ensure the `spark_user` is a member of the specified group.                                                                                                                                                                                                                                                                                                                                       |
| `java_package`          | "openjdk-17-jdk"                                                                        | Name of the Java JDK package to install. Spark requires a Java runtime. The default is OpenJDK 17 (the full JDK) on Debian/Ubuntu. You may override this if you prefer a different JDK or if your OS uses a different package name. For example, on older Ubuntu you might use "openjdk-11-jdk" if 17 is unavailable.                                                                                                                                                                                                                                                 |
| `spark_eventlog_dir`    | "/var/spark-events"                                                                     | Directory for Spark *event logs*. Spark applications, when event logging is enabled, will write logs about job execution to this path. The Spark History Server uses these event logs to display past job information. **Ensure this directory has sufficient space** and, in multi-node clusters, consider using a shared or network file system so that all events are centralized for the history server.                                                                                                                                                            |
| `spark_log_dir`         | "/var/log/spark"                                                                        | Directory for Spark service logs. Spark’s startup scripts will log output (stdout/stderr) and application logs to this directory. This is typically used for the Spark Master, Worker, and History Server logs when running as services. You might want to rotate these logs or centralize them using a logging system (not handled by this role).                                                                                                                                                                                                                      |
| `spark_worker_dir`      | "/var/lib/spark/work"                                                                   | Working directory for Spark Worker processes. Each Spark Worker uses this path to store temporary data, shuffle files, and downloaded application jars. It’s analogous to Spark’s `SPARK_WORKER_DIR`. By default it’s under `/var/lib/spark/work`. Ensure this path has enough space for your Spark jobs (especially if they perform large shuffles or broadcast large files).                                                                                                                                                                                          |
| `spark_recovery_dir`    | ""                                                                                      | Directory for Spark Master state recovery (when using file-based HA). **Default is empty (not set)**. If you are not using ZooKeeper for HA, you can enable Spark’s file-system based recovery by setting this to a shared directory (accessible by all master nodes). Spark masters will write their state here so that on failover another master can pick up the state. This directory must be on a **shared storage** (e.g., NFS or a distributed filesystem) if you have multiple masters. If left empty, file-based recovery is disabled.                         |
| `spark_master_host`     | {{ inventory_hostname }}                                                                | Hostname or IP that Spark Master uses to identify itself and for workers to connect. By default, it uses the Ansible inventory hostname of the current host (meaning each host will assume itself as the master). **Important:** In a multi-node cluster, you should override this on worker nodes to point to the actual master’s host name. Typically, for hosts in the `spark_worker` group, set `spark_master_host` to the hostname or IP of the Spark Master node. On a master node, this can remain default (it will advertise itself).                           |
| `spark_master_url`      | "spark://{{ spark_master_host }}:7077"                                                  | The Spark cluster URL that workers and clients use to connect to the master. By default it is constructed from `spark_master_host` and the standard Spark standalone port 7077. If you change the master port or use a different host, this will need to be adjusted. In most cases, you do not override this manually; instead ensure `spark_master_host` is correct. Workers will use this URL in their startup to register with the master.                                                                                                                          |
| `spark_ha_enabled`      | false                                                                                   | Whether to enable **High Availability** for the Spark Master. Default is `false` (no HA, single-master mode). When set to `true`, you should have multiple hosts in the Spark Master group, and you **must** configure either ZooKeeper or file-based recovery for master coordination (see `spark_zookeeper_hosts` or `spark_recovery_dir`). Enabling HA without configuring one of those will result in multiple masters that don’t coordinate (which is not a valid setup).                                                                                          |
| `spark_zookeeper_hosts` | ""                                                                                      | ZooKeeper connection string for Spark Master HA (if using ZooKeeper). **Conditional:** Used only when `spark_ha_enabled: true`. If you opt to use ZooKeeper for leader election, set this to a comma-separated list of ZooKeeper hosts (with ports), e.g., "zk1.example.com:2181,zk2.example.com:2181,zk3.example.com:2181". If left empty (default), and HA is enabled, the role will still configure Spark for ZK but with an empty URL, which will not work – so this **must be provided** when using ZooKeeper HA. (Not needed if you use file-based HA instead.) |
| `spark_ha_zk_dir`       | "/spark-cluster"                                                                        | The ZNode directory path in ZooKeeper for Spark’s cluster leader election data. Only applies if using ZooKeeper HA (when `spark_ha_enabled: true` and `spark_zookeeper_hosts` is set). The default is `/spark-cluster`. You can usually leave this as default unless you need to run multiple independent Spark clusters on the *same* ZooKeeper ensemble – in that case use different paths for each cluster.                                                                                                                                                          |
| `spark_history_enabled` | false                                                                                   | Flag to enable the **Spark History Server** deployment. Default `false` means no history server is set up. When `true`, the role will install a `spark-history-server` systemd service on the Spark Master node(s). The Spark History Server will serve a web UI on port 18080 by default and read event logs from `spark_eventlog_dir`. Make sure event logging is enabled (this role enables it by default in Spark’s config) and that `spark_eventlog_dir` is accessible to the history server (shared storage if multi-node cluster).                               |
| `spark_worker_memory`   | "1g"                                                                                    | Amount of memory to allocate to each Spark Worker for its executors, as an absolute value or percentage. This sets the `SPARK_WORKER_MEMORY` environment variable. Default is **1g** (1 GB). Adjust this based on the hardware of your worker nodes and how much of each node’s memory you want to dedicate to Spark tasks. For example, on a node with 8 GB free memory, you might set "6g" to leave some memory for the OS.                                                                                                                                         |
| `spark_worker_cores`    | 1                                                                                       | Number of CPU cores to allocate to each Spark Worker for running executors. This sets `SPARK_WORKER_CORES`. Default is **1**, meaning each worker will run tasks on 1 core at a time. You should increase this to the number of CPU cores (or a subset) available on your worker host. For instance, on a 4-core machine, you might set `spark_worker_cores: 4` to let the worker use all cores for Spark jobs.                                                                                                                                                         |

</details>
<!-- markdownlint-enable MD033 -->

**Note:** The above defaults assume a basic cluster. In practice, you will likely adjust at least the memory and core settings for workers, and possibly enable the history server or HA depending on your use case. If you modify `spark_version` (and `spark_hadoop_version`), the `spark_download_url` and `spark_package_name` will automatically change accordingly (unless you override them explicitly). Always ensure that the combination of Spark version and Hadoop version you choose is available for download, or provide a custom `spark_download_url`. Also, if you use custom download URLs or local files, ensure the target hosts have access to those resources (e.g., place the file in an accessible location or use an internal web server).

## Tags

This role does **not define any specific Ansible tags** in its tasks. All tasks will run whenever the role is invoked (there are no task-level tags set by default). You can still apply tags externally when including the role in a play if you want to control execution with `--tags` or `--skip-tags`. For example, in a playbook you could tag the entire role invocation:

```yaml
- hosts: spark_master
  roles:
    - role: spark_role
      tags: ["spark", "spark_master"]
```

This would allow you to run or skip the Spark role via the tag, but by default (with no tags specified) all tasks in this role always execute. In summary, there are no built-in tags like `spark_install` or `spark_config` within the role – any tagging is left to the user’s playbooks if needed.

## Dependencies

* **Ansible Version:** Requires Ansible **2.11+**. This is the minimum version for which the role has been tested and which is indicated in the role metadata. It’s recommended to use the latest Ansible (or at least Ansible Core 2.11 or newer) to ensure compatibility with all modules used (like `ansible.builtin.unarchive`, which became part of core in modern versions).

* **Collections:** No external Ansible collections are required by this role. All modules used (e.g., `apt`, `get_url`, `file`, `template`, `systemd`) are part of the standard Ansible built-in modules (or included in Ansible by default). You do not need to install any Ansible Galaxy collections to use this role. Just make sure your Ansible installation has these modules (which it will if you’re using a typical Ansible distribution for Debian-based targets).

* **Role Dependencies:** None. This role does not depend on any other Ansible roles. The `meta/main.yml` specifies no role dependencies, and all necessary setup (including Java installation) is handled internally. In contrast to some community Spark roles which require a separate Java role (e.g., `geerlingguy.java`), this role installs OpenJDK by itself. You can, however, use it alongside other roles (see **Cross-Referencing Related Roles** below for some suggestions) but there is no hard requirement to include another role before this one.

* **External Packages:** The role will install the following software on the target hosts:

  * **OpenJDK 17** (or an alternate JDK if you override `java_package`).
  * **Apache Spark** (binaries for the specified version). The download is \~200MB+, so ensure your host has internet connectivity or you have provided a local mirror. If downloading from the internet, the host will need outbound HTTP/HTTPS access to `dlcdn.apache.org` (or the mirror you specify).
  * **System packages**: The role uses `apt` to update the cache and install Java. It also expects common utilities (like tar for unarchive) to be available, which on Debian are usually present by default. No other system packages are explicitly installed besides Java.

* **Privileges:** This role performs system-level changes, so it should be run with **privilege escalation** (e.g., `become: yes`). It creates users, installs apt packages, writes to `/opt` and `/etc/systemd`, etc., all of which require root permissions on the target system. Ensure your Ansible play or inventory is configured to allow sudo/become for the role. (In the examples below, `become: true` is set for the plays.)

* **Service Manager:** The role assumes a systemd-based OS (as noted). The tasks deploy systemd unit files and run `systemd` module commands (like daemon-reload, enabling services). On Debian/Ubuntu this is standard. If you run this role on a container environment (like Docker) for testing, you will need a container that supports or emulates systemd, or adjust the testing approach (see **Testing Instructions**). On a normal VM or physical host with Debian, no special action is needed beyond having systemd (which is default on modern Debian/Ubuntu).

* **Firewall Considerations:** This role does not open any firewall ports by itself. If your environment has a firewall (like UFW or firewalld) enabled by default, you must ensure that Spark’s ports are open for the necessary network ranges. By default:

  * Spark Master: TCP 7077 (cluster communication) and 8080 (master web UI)
  * Spark Worker(s): no fixed cluster port (they connect out to master) but each worker has a web UI on 8081 by default
  * Spark History Server: TCP 18080 (history web UI)

  If using the repository’s **`ufw`** role or similar, you might set variables (e.g., a list of ports or a service flag) to allow these. Otherwise, manually adjust firewall rules to permit traffic on 7077 (so workers can register and clients can submit jobs) and on the web UI ports (if you need web access). If the cluster is internal and behind a firewall, you might not need to expose the UIs externally at all.

## Example Playbook

Below is an example of how to use the `spark_role` in an Ansible playbook to set up a Spark cluster. In this example, we define two groups in inventory: `spark_master` (for master node(s)) and `spark_worker` (for worker nodes). We then apply the role to each group with appropriate variables. This ensures that the master node starts the Spark master service (and optionally history server), and the worker nodes connect to the master.

```yaml
# Example inventory groups (for context, not part of playbook):
# [spark_master]
# spark-master.example.com
#
# [spark_worker]
# spark-worker1.example.com
# spark-worker2.example.com

- name: Install and configure Spark Master
  hosts: spark_master
  become: yes
  roles:
    - role: spark_role
      vars:
        spark_history_enabled: true       # Enable the history server on the master node (optional)
        # spark_ha_enabled: true          # (Optional) If you have multiple masters, enable HA
        # spark_zookeeper_hosts: "zk1.example.com:2181,zk2.example.com:2181,zk3.example.com:2181"  # (Needed for HA with ZooKeeper)
        # spark_recovery_dir: "/mnt/spark-ha"  # (Alternative HA) Shared directory for file-based recovery if not using ZooKeeper

- name: Install and configure Spark Workers
  hosts: spark_worker
  become: yes
  roles:
    - role: spark_role
      vars:
        spark_master_host: "{{ groups['spark_master'][0] }}"  # Point workers to the first master host
        spark_master_url: "spark://{{ groups['spark_master'][0] }}:7077"  # Construct master URL (if not using default)
        # Note: If HA with multiple masters, you might list multiple masters in spark_master_host in a comma-separated form for Spark (not typical; usually ZooKeeper handles HA)
```

**Usage notes:** In the above playbook, we run the role on the master group and workers group separately. We set `spark_history_enabled: true` for the master so that it runs a history server (if you don’t want the history server, you can omit that). On the workers, we override `spark_master_host` to the hostname of the master (using the first host in the `spark_master` group). This ensures that each worker’s systemd service knows where to connect. We also explicitly set `spark_master_url` in this example for clarity, but in fact the role would compute it from `spark_master_host` automatically. The `become: yes` is important because installing packages and configuring services require root privileges.

If you wanted to deploy a **High Availability** Spark Master setup, you would have two or more hosts in `spark_master` group. In that case, you *must* set `spark_ha_enabled: true` on those hosts (e.g., via group vars or in the play as shown commented) and configure either `spark_zookeeper_hosts` (for ZooKeeper-based HA) or `spark_recovery_dir` (for file-based HA on shared storage). ZooKeeper is the more common approach for Spark HA. Ensure you have a ZooKeeper ensemble running and provide its hosts in `spark_zookeeper_hosts`. The role will then configure each Spark Master to register with ZooKeeper and perform leader election. For file-based HA, choose a path (e.g., an NFS mount or distributed filesystem location) that all masters can access, and set `spark_recovery_dir` to that path on all master nodes.

After running the playbook, you should have:

* On the master node(s): the Spark master service running (check `systemctl status spark-master`), and if enabled, the history server (`spark-history-server`) running. The master’s web UI will be reachable on port 8080 (e.g., [http://spark-master.example.com:8080](http://spark-master.example.com:8080)).
* On each worker node: the Spark worker service running (`systemctl status spark-worker`), which should be registered with the master. You can verify on the master’s web UI (Workers tab) that the workers have connected. Each worker’s own web UI is on port 8081 (e.g., [http://spark-worker1.example.com:8081](http://spark-worker1.example.com:8081)).
* If the history server is enabled: you can open [http://spark-master.example.com:18080](http://spark-master.example.com:18080) to see the Spark History Server UI, which will list completed applications (assuming jobs have been run and event logs written to the shared directory).

## Testing Instructions

It is highly recommended to test this role using **Molecule** (with Docker or another driver) to verify its behavior before deploying to production. Molecule can run the role in a disposable environment (container or VM) and check for idempotency and correct configuration. Below are steps to test the `spark_role` using Molecule:

1. **Install Molecule (and Docker)** on your development machine if not already installed. For example, using pip:

   ```bash
   pip install molecule[docker]
   ```

   Ensure you have Docker installed and running, as Molecule will create containers for testing. You may need to run Molecule commands as a user that has permission to run Docker (or use `sudo`, but typically adding your user to the docker group is preferable).

2. **Check for an existing Molecule scenario:** This role may come with a predefined Molecule scenario (commonly in `molecule/default/`). If such a directory exists in the role, you can use it directly. If not, you can initialize a new scenario for this role with:

   ```bash
   molecule init scenario -r spark_role -d docker
   ```

   This will create a `molecule/default/` directory with a basic scenario using Docker driver. It includes a `molecule.yml` (for config) and a `converge.yml` playbook that applies the role to a test instance.

3. **Configure the test scenario:** Open the generated `molecule/default/molecule.yml`. By default, Molecule might use a generic Docker base image (such as `docker.io/pycontribs/debian` or similar). For testing Spark, ensure the image is a systemd-enabled Debian/Ubuntu image, because the role relies on systemd for service management. You might choose an image like `geerlingguy/docker-debian10-ansible` (which has systemd) or configure the container to run systemd (see Molecule docs for enabling systemd in Docker containers). In the `platforms` section of `molecule.yml`, you can specify an image that supports systemd and set `privileged: True` with an entrypoint to start systemd if needed. Also, edit `converge.yml` to assign the test instance to appropriate groups and set required vars:

   * For example, in `converge.yml` under the play, you might set `hosts: spark_master` (and define that group in `molecule.yml` inventory) so that the role will treat the test container as a master. Alternatively, use `hosts: all` and then set `spark_master_host: localhost` for a single-node test.
   * If the role has any required variables with no defaults, set them in the `vars:` of `converge.yml`. In our case, all variables have defaults. You may, however, want to set `spark_history_enabled: true` for testing that feature, or adjust memory if the container is small.

   By default, event logging is enabled and will write to `/var/spark-events`. In a container, this is fine, but remember the history server might be looking at that path. If you enable `spark_history_enabled` in a one-container test scenario, the master and history server are on the same container, so it will work (the events directory is local).

4. **Run the convergence test:** Execute Molecule to apply the role in the test environment:

   ```bash
   molecule converge
   ```

   Molecule will pull up the container, run the `converge.yml` playbook (which applies the `spark_role`), and report the results. Watch for any errors or failed tasks. A successful run should indicate that all tasks completed and (on the first run) changed some state. Running `molecule converge` again after the first time should result in *zero changes*, indicating the role is idempotent.

5. **Verify the outcome in the container:** After convergence, you can manually check the container to ensure Spark was installed and configured:

   * Enter the container shell: `docker exec -it <container_name> /bin/bash` (replace `<container_name>` with whatever name Molecule gave the instance, often `instance`).
   * Check that the Spark directory exists: `ls /opt/spark/current`. You should see Spark files (e.g., `bin/`, `sbin/`, `conf/` directories).
   * Verify the spark user was created: run `id spark` to see if the user exists.
   * If systemd is running in the container (you set it up), check service status: `systemctl status spark-master` (if the container was treated as master). It should show the service as **active**. You can also check `systemctl status spark-worker` on the same container if you configured it as both master and worker for testing. In a single-container test, you might simulate both master and worker on one host by adding it to both groups.
   * Even if systemd isn’t actually running (depending on container setup), you can still verify the service unit files were dropped in `/etc/systemd/system/` (e.g., `spark-master.service` exists) and the environment file `/opt/spark/current/conf/spark-env.sh` has your configurations.
   * You can simulate starting Spark without systemd: for example, run `/opt/spark/current/sbin/start-master.sh` manually in the container and then check if the process is running (`jps` command can show Java processes; or `netstat -tlnp` to see if something listening on 7077/8080). This helps verify that the installation is functional.

   Additionally, check the configuration files:

   * `/opt/spark/current/conf/spark-defaults.conf` should have `spark.eventLog.enabled true` and the event log directory set.
   * `/opt/spark/current/conf/spark-env.sh` should reflect the variables (like `SPARK_MASTER_HOST`, which in a container might be set to the container’s hostname or overridden in converge vars).

6. **Run Molecule verify (optional):** If you have written any verify tests (for example using Testinfra or Inspec to automatically check things like “is the service running” or “is port 7077 open”), you can run:

   ```bash
   molecule verify
   ```

   By default, this role may not come with pre-written verify tests, so this step is optional. It’s useful if you add your own tests to the scenario.

7. **Cleanup the test environment:** When you’re done testing, you can destroy the test container to free resources:

   ```bash
   molecule destroy
   ```

   This will stop and remove the Docker container created for the test. You can also run `molecule test` to perform a full cycle (create, converge, verify, destroy) in one command.

Using Molecule for testing ensures the role is **idempotent** (running it again doesn’t change anything if the system is already configured) and that it works on a clean system. It helps catch issues with package installation, path permissions, or service startup in an isolated environment. It’s a good practice to run Molecule tests, especially after making changes to the role, before applying the role to real servers.

## Known Issues and Gotchas

When using the spark_role, be aware of the following caveats, edge cases, and design limitations:

* **Inventory Group Names:** The role uses hard-coded inventory group names `spark_master` and `spark_worker` to determine which tasks to run on which hosts. This means your inventory should have hosts organized into these groups for the role to work as intended. For example, if you have one master node and multiple workers, ensure the master’s hostname is in the `spark_master` group and all worker hostnames are in the `spark_worker` group. Tasks like deploying the master’s systemd unit or starting the worker service are conditional on group membership. If you run the role on a host that is not in either group, those conditional tasks will all skip, and you might end up with just Spark installed but no service running. In practice, you can include a host in both groups if it should run both master and worker (not typical in production, but possible for testing or small setups). Just be mindful that these group names are expected by the role (they are not configurable via a variable in the current implementation).

* **Multiple Masters Require HA Configuration:** If you put more than one host in the `spark_master` group, you **must** enable high availability (`spark_ha_enabled: true`) and configure the HA coordination method. The role does **not** automatically coordinate multiple masters unless HA is turned on. If you have two masters and do not enable HA, both will attempt to start as independent masters. This can lead to an inconsistent cluster state (essentially two separate masters each unaware of the other). At best, your workers might only connect to one of them (whichever `spark_master_host` is pointing to), and at worst, if they’re somehow configured to the same host and port, one master will fail because the port 7077 is already bound by the other. To avoid this, **only use one master** if `spark_ha_enabled` is false. For multiple masters, always enable HA and use either ZooKeeper or file-based recovery:

  * If using **ZooKeeper** for HA, set `spark_ha_enabled: true` and provide a valid `spark_zookeeper_hosts`. Make sure a ZooKeeper ensemble is actually running at those addresses. The role doesn’t install ZooKeeper; you must have it set up (via another role or externally).
  * If using **FileSystem recovery** for HA (not recommended unless ZooKeeper is not available), set `spark_ha_enabled: false` (since Spark doesn’t consider it HA mode, it’s just for crash recovery) and provide a `spark_recovery_dir`. Actually, Spark Standalone can use `spark.deploy.recoveryMode=FILESYSTEM` as an HA mechanism between masters if both masters share the same directory. In the current role templates, the file-based recovery is configured only if `spark_recovery_dir` is set *and* `spark_ha_enabled` is false (meaning you opt for FS recovery instead of ZK). In that case, you can run two masters; they will both point to the same recovery directory. This setup requires that the directory is on a shared storage accessible by both masters (like NFS). If each master has a separate local directory path, they won’t see each other’s state, defeating the purpose.

* **Spark Master Hostname on Workers:** As mentioned in the variables, remember to set `spark_master_host` (or directly `spark_master_url`) for worker nodes to the actual master’s hostname or IP. The default `spark_master_host` is each host’s own name, which is correct only for the master itself. If you forget to override this on workers, they will try to connect to themselves on port 7077 (since they think they are the master). In such a misconfiguration, the Spark Worker service will continuously try to reach a master at `spark://<worker-host>:7077` which will fail, and the worker will not function (it may keep restarting or just idle with errors). This is a common gotcha – ensure your inventory or playbook sets the master’s address for all workers. One way is to use group variables for `spark_worker` group: e.g., in `group_vars/spark_worker.yml`, set `spark_master_host: "spark-master.example.com"`.

* **Local Event Logs vs. Shared Storage:** By default, event log files are written locally on each node under `/var/spark-events`. In a single-node scenario, or if jobs always run on the master node, this is fine. However, in a multi-node cluster, each Spark application’s event logs will be written on the node where the application ran (usually the node where the Spark driver runs). The Spark History Server *only reads local filesystem paths* on the host it runs on (typically the master host). This means if an application’s driver ran on a worker node, its event log would reside on that worker’s `/var/spark-events`, and the master’s history server wouldn’t see it. To solve this, you should use a **shared directory** for `spark_eventlog_dir`. For example, mount an NFS share at `/var/spark-events` on all nodes, or use a distributed filesystem (HDFS, GlusterFS, etc.) and configure Spark to write to that (Spark can write to HDFS if you set the event log dir to an `hdfs://` URI, but that requires Hadoop configuration not covered by this role). This role does not set up shared storage for event logs; it’s up to the user. If using the default local path in a multi-node cluster, know that the history server will only show jobs that ran on the master node (since that’s where it reads logs). In summary, for full functionality of the history server in a cluster, ensure `spark_eventlog_dir` is a single, unified location accessible by all nodes.

* **OpenJDK Version on Older Systems:** The default Java package is OpenJDK 17, which is available in Debian 11+, Ubuntu 20.04+, etc. If you target an older distribution (e.g., Ubuntu 18.04 or Debian 10), OpenJDK 17 might not be in the default repositories. In such cases, you have a few options:

  * Override `java_package` to a version that exists (e.g., `openjdk-11-jdk`).
  * Install Java via some other method (you could do it before running this role, or modify the role tasks).
  * Upgrade the OS to a version with Java 17 support.

  Keep in mind that Spark 3.4.1 itself requires Java 8 or above (Java 11 or 17 recommended). Java 11 would work for Spark 3.4, so using OpenJDK 11 on older systems is acceptable if 17 is not available. This is not so much a bug in the role as a compatibility note. If the `apt` task fails to find `openjdk-17-jdk`, this is likely the reason.

* **Systemd in Containers:** If you are testing this role in a Docker container (e.g., with Molecule or other CI), note that the systemd service tasks might not work unless systemd is properly running in the container. You might see tasks like "Reload systemd" or "Enable and start Spark Master" fail or hang. This is a common issue with Ansible roles that manage services when run in lightweight containers. The workaround is to use a container image with systemd, or to adjust the Molecule scenario to simulate or bypass service startup (for instance, you could set `spark_master_host` such that the master service is not started in a test, or use an alternative command to verify Spark). When deploying on actual VMs or hosts, this is not a problem.

* **Spark UI Security:** By default, the Spark Master and History Server UIs do not require authentication and are served in plain HTTP. This isn’t a “bug” in the role, but an important consideration. If these UIs are accessible on a network, anyone who can reach the Master UI can see information about running jobs, and potentially perform some actions like killing jobs (if they have access to the Spark REST interface or UI controls). The role does not configure any firewall or authentication for these interfaces. It’s recommended to run Spark on an internal or secure network. If exposure is required (for example, you want to make the Spark UI accessible to developers), consider putting it behind a proxy or enabling SSL. Spark can be configured with authentication (via shared secret) and SSL for the UI, but that would require adding configurations not currently templated by this role. In short, treat the Spark web UIs as sensitive and protect them via network policies or manually enable security features as needed.

* **Spark History Server on Multiple Masters:** In an HA setup with two masters, the role will technically install and start the history server on *both* (because the condition for history server tasks is `inventory_hostname in groups['spark_master'] and spark_history_enabled`). This means if you have two masters and enable history, you’ll end up with two history servers running. Usually, you would only run one history server (it doesn’t need HA in the same way, since it’s stateless reading logs; you could run it on just one node or behind a load balancer). As a workaround, you might choose to only enable `spark_history_enabled` on one of the masters (e.g., set it via host vars for a specific host). The role does not have logic to prevent multiple history servers. Running two in parallel isn’t harmful per se (they would both try to read the same event logs and show the same info), but it’s redundant and could double the processing of logs. Just be aware of this if you deploy HA masters with history server enabled.

* **No Support for Spark on YARN or Kubernetes:** This role is specifically for deploying Spark in *standalone mode* (Spark’s built-in cluster manager). It does not configure Spark to run on YARN or Kubernetes. If you are instead looking to integrate Spark with an existing Hadoop YARN cluster, or to deploy Spark on Kubernetes, this role will not suffice (those scenarios require different setups, like just installing Spark binaries as a client, or deploying via Helm on K8s, etc.). All tasks here assume the standalone Spark master/worker architecture.

* **Resource Limits and Scheduling:** By default, the role sets very conservative resources (1 core, 1g memory per worker). In a real deployment, if you have powerful nodes, you should raise these. Not doing so isn’t a “bug” but it’s a potential pitfall: Spark will under-utilize your machine if you forget to adjust the defaults. For example, an 8-core server with 32 GB RAM running a worker with default `spark_worker_cores=1` and `spark_worker_memory=1g` will only ever use 1 core and 1 GB for Spark tasks! Always review and tune these variables for your environment. Likewise, `spark_worker_dir` defaults to `/var/lib/spark/work` – ensure the partition it’s on has enough space for shuffle and spill files, which can be large.

* **Idempotency Note:** The role tries to be idempotent, but one minor caveat: if you change the `spark_version` to a new version and re-run the role, it will download the new version and update the symlink. It will not remove the old version directory. You may accumulate multiple Spark version directories under `/opt/spark`. This is intentional, as one might want to keep older versions around. But if you don’t need the old one, you’ll have to clean it up manually. Also, when switching versions, the master and workers should be restarted (the role will restart them via handlers if the config or service units changed, but if you only changed version and thus the symlink, you might need to trigger a restart). Ensure to run the play with the role to completion so handlers fire, or manually restart services after a version bump.

## Security Implications

Deploying Spark with this role has a few security considerations to keep in mind:

* **System User and Permissions:** The role creates a user `spark` (by default) and group `spark`, and runs all Spark services under this unprivileged account. This is a security best practice (it prevents Spark processes from running as root). The `spark` user’s home is created and shell is set to `/bin/bash` by default. Note that the account is created without a password, meaning it’s not possible to log in via password, but since the shell is normal, if someone had SSH key access or other means, they could log in as `spark`. If you want to harden this, you could change the shell to `/usr/sbin/nologin` after installation to prevent interactive login. All directories created (like `/opt/spark`, `/var/log/spark`, etc.) are owned by `spark:spark` with mode 0755, which means other local users can read the files. If the machine is multi-user and this is a concern (for example, logs might contain sensitive info about jobs), you might tighten permissions to 0750 and add only appropriate users to the `spark` group. By default, however, a typical Spark deployment is on dedicated servers where this isn’t an issue.

* **Open Ports:** After the role is run, the Spark Master will listen on TCP port **7077** for incoming connections from Spark workers and Spark client applications (this is the RPC port for the cluster). It will also have a web UI on **8080** (HTTP). Each Spark Worker will have a web UI on **8081**. If the history server is enabled, it listens on **18080** (HTTP). None of these ports are encrypted or protected by default. That means if these ports are accessible, anyone could potentially connect:

  * On 7077, a malicious user could attempt to submit a Spark application to your cluster. By default, Spark standalone has no authentication for job submission (unless you configure a `spark.authenticate` secret or use Spark’s RPC security features, which are not configured by this role).
  * The web UIs (8080, 8081, 18080) will show cluster information and, in the case of the master UI, allow viewing and stopping running applications. They do not require a login.

  **Mitigation:** Treat the Spark cluster network as privileged. It’s recommended to run Spark on a private network or VPN where only authorized users can access it. If you must expose the UI or submission port, consider enabling Spark’s built-in authentication mechanisms (this involves setting certain Spark properties for shared secret and using SSL for the UI). You could also front the UI with an authenticating proxy (for example, put Nginx with basic auth in front of port 8080/18080). At the very least, use firewall rules to limit access to these ports to trusted IPs. The repository’s `ufw` role can be leveraged to only allow internal ranges.

* **Data Security:** Spark will process data that may be sensitive, but this largely depends on what jobs you run. The role itself doesn’t introduce data security issues beyond what Spark normally has. Note that by default, event logs written to `/var/spark-events` are not encrypted and could contain some information about the jobs (like job names, possibly SQL queries, etc.). If the system is compromised or accessed by other users, those logs could reveal information. If this is a concern, you might mount the event log directory on an encrypted filesystem or regularly purge sensitive logs. Also, Spark’s logs in `/var/log/spark` might contain stack traces or error messages from jobs that include file paths or snippets of data. Treat these logs as you would any application logs in terms of sensitivity.

* **Process Isolation:** All Spark workers run as the same `spark` user. If multiple users submit jobs to the Spark cluster, those jobs will all run under the same Unix user account on the workers. Spark itself does not provide strong isolation between different applications on the same worker beyond scheduling resources (CPU/mem). This means a malicious Spark job could potentially affect another (e.g., by using more memory than allocated, or trying to access files on the node that belong to `spark` user). In environments where untrusted users run Spark jobs, consider using YARN or Kubernetes for stronger isolation, or at least containerize the Spark executors. That’s beyond the scope of this role, but it’s a security consideration for multi-tenant usage.

* **Sudo and Shell Access:** The role does not give the `spark` user any sudo privileges (and it shouldn’t). The `spark` user also doesn’t need a login. If you want to be stricter, after deployment you can lock the `spark` user password and change its shell to nologin (as mentioned). Make sure that any admin who needs to manage the Spark processes can either switch to the `spark` user (`sudo -u spark ...`) or read the logs as root. Typically, you don’t need to log in as `spark` for any routine operation (you manage services via systemd as root or a sudoer).

* **Filesystem and Keytabs:** This role does not set up any Kerberos keytabs or authentication files for Spark. By default, Spark in standalone mode doesn’t do Kerberos (that’s more for Spark on Hadoop/YARN). If your environment requires Kerberos for HDFS or other services Spark might access, you will need to distribute and manage keytabs outside of this role. Ensure that such keytabs (if placed on the Spark nodes) have proper permissions and are only readable by the services that need them.

* **Firewall and Network Segmentation:** If you are in a secure environment, you might isolate the Spark cluster on an internal network segment. Only open the necessary ports to the users who need to submit jobs (for example, maybe only an edge node or a CI/CD system can talk to the Spark Master on 7077, rather than the whole world). The role doesn’t enforce this, but you should plan network security accordingly. Also, be cautious with the History Server UI if it’s showing data you consider sensitive (like names of jobs or possibly fragments of code in stack traces); restrict access to it as appropriate.

By addressing these considerations — using proper network restrictions, keeping the Spark user unprivileged, and monitoring logs and processes — you can run the Spark cluster in a reasonably secure manner. Always stay updated on Spark security best practices from the official documentation (for instance, Spark’s docs on security cover how to enable authentication between components, which is something you might implement on top of this role if needed). This role provides the infrastructure, but it’s up to the operator to ensure the cluster is deployed in a secure context.

## Cross-Referencing Related Roles

This Spark role is one part of a larger ecosystem. In the same repository (and more broadly in a data platform deployment), there are other roles that can complement or be used alongside **Spark**. Depending on your use case, you might consider the following:

* **`zookeeper` role:** If you plan to enable Spark Master HA with ZooKeeper, you will need a running ZooKeeper ensemble. Check if this repository includes a role to set up **Apache ZooKeeper** (often a role might be named `zookeeper` or integrated into other roles). For example, the **Apache NiFi** clustering in this repo uses ZooKeeper, so a ZK setup might exist. If not, you may use a community role or set up ZooKeeper manually. Ensuring ZooKeeper is highly available and secure is important if it’s used for coordinating Spark masters.

* **`apache_airflow` role:** Apache Airflow is another orchestrator in the data ecosystem. There is an **Apache Airflow** role in this repository that deploys Airflow. Airflow can be used to schedule Spark jobs as part of workflows (using Spark submit operators or Kubernetes operators, etc.). While Airflow and Spark are independent, you might deploy both and have Airflow trigger jobs on the Spark cluster. If you are building out a complete data pipeline, consider deploying Airflow (with the `apache_airflow` role) to manage and schedule Spark jobs or other tasks.

* **`apache_nifi` role:** The repository includes an **Apache NiFi** role for data flow management. NiFi can be used to route and transform data and then hand off data to systems like Spark for processing. NiFi itself can run on a cluster (with ZooKeeper coordination). If your project involves ingesting or pre-processing data with NiFi and then using Spark for heavy compute (ETL, analytics, machine learning), these roles can work in tandem. NiFi might deliver data to HDFS, Kafka, or even directly trigger a Spark job (though not directly common), but conceptually they complement each other in a data platform.

* **`glusterfs_setup` role:** If you require a distributed filesystem for sharing data or log files across the Spark cluster (for example, to implement the shared event log directory or to store input/output data accessible to all nodes), consider the **GlusterFS setup** role. This role can help set up a GlusterFS cluster. Using a distributed filesystem can be an alternative to HDFS in environments without Hadoop. In context, you could use GlusterFS to provide a common mount (e.g., for `/var/spark-events` or for data files that Spark jobs will read/write).

* **`apt_mirror` role:** In secure or offline environments, the **apt_mirror** role can set up a local package repository mirror. If your Spark cluster nodes do not have direct internet access, using an apt mirror is helpful to install packages like OpenJDK. You might deploy the apt_mirror on one host (or use an existing mirror) and configure your cluster’s apt sources to use it. While not directly related to Spark, it’s a useful supporting role for package management.

* **Base/System Roles:** There are roles such as **`base`** or **`common`** (and likely a **`security_hardening`** or similar) that ensure baseline configuration on all servers. For example, the `base` role might set up NTP, manage `/etc/hosts`, or perform system updates. Before deploying Spark, you may want to run such a base role to ensure the system is up-to-date and correctly configured. Additionally, the **`ufw`** (Uncomplicated Firewall) role can configure firewall rules. As noted, you should open Spark-related ports with it if you use it. In the group variables for your Spark hosts, you might find parameters like `ufw_allow_spark_master: true` or a list of ports. If present, enabling those and running the `ufw` role will help secure the cluster’s network access.

* **Monitoring and Logging Roles:** Operating a Spark cluster benefits from monitoring and log aggregation. While this role doesn’t set those up, you might integrate with:

  * **Filebeat/ELK roles:** There is a **`filebeat`** role in the repo. You could use it to ship Spark logs (`/var/log/spark/*.out` or `.log` files) to an ELK stack. Similarly, if there’s an **`elk`** or **`graylog`** role, it could be used to set up centralized logging.
  * **Prometheus/Grafana roles:** If the repository contains roles for **Prometheus** or **node_exporter** (common in monitoring setups), you could deploy those to gather metrics from your Spark nodes. Spark itself can expose metrics via JMX; you might run a JMX exporter to feed Prometheus. While this is not configured by default, consider using a **node_exporter** role on all Spark nodes to at least monitor system metrics, and potentially a **Spark metrics integration** if available.

* **Analytical Applications:** After setting up Spark, you might use tools like **Apache Superset** or **Jupyter Notebook** to interact with data. The repository has an **`apache_superset`** role, which is a BI tool that could query data (though usually via SQL engines; it might not connect to Spark directly unless Spark is exposing a Thrift server or via Hive). If you have a Hive Metastore or other SQL interface for Spark (not covered by this role), Superset could be configured to use it. Also, if there’s a **JupyterHub** or **Zeppelin** role (not sure if present), those can provide interactive environments for running Spark code.

Each of these roles has its own documentation and configuration. When building a complete environment, you would typically: set up the base OS configs, deploy Java (in this role it’s included), deploy Spark (using this role) on the cluster nodes, ensure you have ZooKeeper or other needed services (possibly via another role), and then deploy any higher-level services like Airflow or superset that interface with Spark. The example playbooks in the repository (e.g., a site playbook or specific environment playbooks) can provide guidance on how these roles come together. By leveraging multiple roles, you can orchestrate a full data platform: for instance, a play might include running this Spark role on a set of nodes, a Zookeeper role on a few nodes, an Airflow role on a scheduler node, and so on, to build an integrated system. Be sure to read the README of each relevant role for any special setup needed (for example, the Airflow role might require a database, the NiFi role might require certs for TLS, etc.).

In summary, while the Spark role sets up the core compute cluster, these related roles can provide surrounding services (job orchestration, data ingestion, storage, security, etc.) that turn a standalone Spark cluster into a functional component of your infrastructure.
