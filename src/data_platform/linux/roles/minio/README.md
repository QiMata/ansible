# Ansible Role: Minio

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

The **MinIO** role installs and configures [MinIO](https://min.io) – a high-performance, self-hostable object storage server – on a target Linux host. It sets up MinIO as a systemd service running under a dedicated system user, manages the necessary directories and configuration, and optionally configures TLS for secure access. Key tasks performed by this role include:

* **System Preparation:** Ensures required system packages like `curl` (for download) and `openssl` (for TLS key/cert generation) are present. It creates a dedicated `minio` group and user account (system user with no login shell) to run the service, enhancing security by not running MinIO as root.
* **Binary Installation:** Downloads the MinIO server binary from the official source (default is the Linux AMD64 release) and installs it to **`/usr/local/bin/minio`**, setting proper permissions. You can adjust the version or source via role variables (see **Role Variables**).
* **Directory Setup:** Creates the required directory structure, including a base directory (default **`/opt/minio`**) for MinIO data and configuration. Within this, a data directory (by default **`/opt/minio/data`**) is created to store object data, and a **`certs`** directory for TLS certificates is set up if TLS is enabled. Ownership and permissions on these are set so the `minio` user can access them.
* **Configuration:** Generates an environment file (`/etc/default/minio`) from a Jinja2 template with the necessary environment variables (like **MINIO_ROOT_USER**, **MINIO_ROOT_PASSWORD**, **MINIO_VOLUMES**, **MINIO_OPTS**). This includes your specified admin credentials and the storage volume path(s). The role also constructs extra command-line options for MinIO: by default it sets the console address to the chosen port (e.g. `--console-address :9001` for the web UI).
* **TLS Support:** If **TLS** is enabled (`minio_enable_tls: true`), the role will look for provided certificate and key files or generate a self-signed certificate. You can supply an existing cert/key pair (via `minio_cert_public` and `minio_cert_private`), which will be copied into the certs directory, or have the role auto-generate a self-signed certificate (by setting `minio_self_signed: true`). In self-signed mode, it uses the domain name from `minio_domain` (default is the host’s inventory name) and any additional SANs from `minio_extra_sans` to create a certificate. This ensures MinIO will run with HTTPS enabled on the specified ports, improving security for data in transit.
* **Service Deployment:** Deploys a systemd service unit (`/etc/systemd/system/minio.service`) from a template, configured to run the MinIO server as the `minio` user. The service unit uses the environment file and includes safety settings (such as restarting on failure and no kill signal on stop). The role then **enables and starts** the MinIO service, so it will automatically start on boot and be running after the play completes.
* **Idempotence and Configuration Management:** The role is designed to be idempotent. Configuration changes (like toggling TLS, changing ports, or updating credentials) will trigger handlers to restart MinIO so changes take effect. The role does **not** manage MinIO beyond installation and basic setup – for example, it doesn’t create buckets or manage MinIO user accounts beyond the root credentials. This separation means you should handle bucket creation or user provisioning using MinIO’s client tools or API if needed (not covered by this role).

In summary, applying this role yields a functional MinIO server running as a systemd service, reachable on the configured ports with the specified credentials. You get a single-node MinIO deployment by default. *(MinIO can also be scaled out to a distributed cluster across multiple nodes – see diagram below – but this role does **not** automatically configure multi-node clusters. Each host would run its own MinIO instance; cluster coordination requires additional setup as discussed later.)*

```mermaid
flowchart LR
    subgraph Standalone Deployment
      S[Single MinIO Server<br/>(minio.service)] --> D1[(Local Disk<br/>/opt/minio/data)]
      S -->|Listens on port 9000| C1[Clients]
    end
    subgraph Distributed Cluster (4 Nodes Example)
      direction LR
      N1[MinIO Node 1] --> V1[(Disk1)]
      N2[MinIO Node 2] --> V2[(Disk2)]
      N3[MinIO Node 3] --> V3[(Disk3)]
      N4[MinIO Node 4] --> V4[(Disk4)]
      N1 -- sync --> N2
      N1 -- sync --> N3
      N1 -- sync --> N4
      N2 -- sync --> N3
      N2 -- sync --> N4
      N3 -- sync --> N4
    end
```

*Diagram: **MinIO Standalone vs. Distributed.** In a single-node deployment (left), one MinIO server uses a single disk/directory and serves all requests on its own. In a distributed deployment (right), multiple MinIO servers (e.g. 4 nodes) each contribute a disk; the servers synchronize storage and present a unified object store. (Production MinIO clusters require at least 4 nodes for erasure-coded data resiliency.)*

## Supported Operating Systems/Platforms

This role is currently designed for **Debian-based Linux distributions**. It uses the APT package manager and Debian conventions in tasks, so it has been tested and verified on:

* **Debian 11 (Bullseye)** and **Debian 12 (Bookworm)** – (primary supported platforms as listed in role metadata).
* **Ubuntu LTS releases** (20.04 Focal, 22.04 Jammy, etc.) – *likely supported*. While not explicitly listed in the metadata, Ubuntu shares the Debian package names and systemd, and thus the role should work on recent Ubuntu versions. (Ensure the default `apt` repositories provide `curl` and `openssl`, which they do.)
* **Other Debian derivatives** (e.g. Raspbian, Kali) – might work if they use APT and systemd, but not tested. The default MinIO binary is for 64-bit x86_64; on ARM-based Debian (like Raspberry Pi OS), you would need to override the download URL to an ARM binary.

**Not supported out-of-the-box:** RHEL, CentOS, AlmaLinux, Amazon Linux, or other non-Debian systems. The role does not include YUM/DNF tasks or RedHat-specific settings, and it expects a systemd environment. Adapting it to RHEL-based systems would require adding those (e.g., installing `curl`/`openssl` with `dnf` and adjusting paths). Unless modified, attempting to run this role on an unsupported OS will either fail to find the appropriate packages or not function correctly. Use Debian/Ubuntu hosts for this role to avoid compatibility issues.

## Role Variables

Below is a list of the role’s variables, along with their default values (defined in **`roles/minio/defaults/main.yml`**) and descriptions. These variables can be overridden in your playbook or inventory to customize the MinIO deployment.

<!-- markdownlint-disable MD033 -->

<details><summary>Role Variables (defaults/main.yml)</summary>

| Variable                  | Default Value                                              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`minio_version`**       | "RELEASE.2025-05-05T00-00-00Z"                             | **MinIO server version tag to install.** This should correspond to an official MinIO release (in date-tag format). By default, it’s set to a specific release (May 5, 2025). *Note:* This role uses a static download URL for the binary (see `minio_download_url`); it does **not** automatically derive the URL from `minio_version`. If you change `minio_version`, ensure you also update the download URL accordingly to fetch the intended version. This variable primarily serves as documentation of the expected version and for your reference when overriding.                                                                                                        |
| **`minio_download_url`**  | `https://dl.min.io/server/minio/release/linux-amd64/minio` | **URL to download the MinIO server binary.** Defaults to the official MinIO download link for the latest Linux 64-bit (AMD64) server binary. Change this if you need to install a specific version or if you want to point to an internal mirror/file. For example, you might use a versioned link or an alternate architecture’s binary. In offline environments, set this to a local file path or hosted URL accessible to the target. The role will download this URL and place the file at `minio_binary_path`.                                                                                                                                                              |
| **`minio_binary_path`**   | `/usr/local/bin/minio`                                     | **Filesystem path where the MinIO binary will be installed.** The role downloads MinIO to this location and sets it executable. By default this is `/usr/local/bin/minio` (accessible in `$PATH`). You can change it to another directory if needed. If a file already exists at this path, it will be overwritten by the downloaded binary.                                                                                                                                                                                                                                                                                                                                     |
| **`minio_user`**          | "minio"                                                    | **System username to run the MinIO service.** The role will create this user (if it doesn’t exist) as a system account with no login shell (for security). MinIO will run under this account, which owns the data and config directories. You can change the name if necessary (e.g., to comply with naming policies), but it should be a dedicated user for MinIO.                                                                                                                                                                                                                                                                                                              |
| **`minio_group`**         | "minio"                                                    | **System group name for the MinIO service.** The role ensures this group exists (and usually it matches the username). Files and directories for MinIO will be owned by this group. Normally you’d use the same name for user and group.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **`minio_base_dir`**      | "/opt/minio"                                               | **Base directory for MinIO files.** This is the root installation directory under which MinIO stores data and configuration. By default, `/opt/minio` is used. The role will use this as the working directory for the MinIO service and as a parent for sub-directories. You can change this to another path or mount point (for instance, if you want data on a larger disk).                                                                                                                                                                                                                                                                                                  |
| **`minio_data_dir`**      | `{{ minio_base_dir }}/data` (e.g. `/opt/minio/data`)       | **Data directory for MinIO object storage.** This is where MinIO will store object data (bucket contents). By default it’s a folder named “data” under the base dir (e.g. `/opt/minio/data`). If you have a separate storage mount or specific path for data, override this variable to that path. The role ensures this directory exists and is owned by the MinIO user.                                                                                                                                                                                                                                                                                                        |
| **`minio_root_user`**     | "minioadmin"                                               | **MinIO administrator username** (also called Access Key). This user is the login name for the MinIO web console and the API (s3 access key). The default is “minioadmin” (which is the well-known default for MinIO). **For security, it is highly recommended to change this** to a custom name in production so it’s not easily guessable. This value is stored in the environment file and will become the `MINIO_ROOT_USER` for the service.                                                                                                                                                                                                                                |
| **`minio_root_password`** | "minioadmin"                                               | **MinIO administrator password** (also called Secret Key). This is the password for the above `minio_root_user` to log into MinIO. Defaults to “minioadmin” (the MinIO default password). **You must change this for any non-test deployment.** Use a strong password. (It’s wise to supply this via Ansible Vault or an environment variable rather than plain text.) The role will set this in the environment file as `MINIO_ROOT_PASSWORD`.                                                                                                                                                                                                                                  |
| **`minio_server_port`**   | `9000`                                                     | **MinIO server port for the S3 API.** This is the TCP port on which MinIO listens for API and SDK requests (S3-compatible endpoint). By default, MinIO uses **9000**. *Note:* In the current role implementation, this variable is defined for potential use but not directly used in the service configuration (MinIO will simply use its default). To change the API port, you can either override `minio_opts_extra` with an `--address` flag or modify the systemd service template. (Future versions of the role may incorporate this variable into the startup command.)                                                                                                   |
| **`minio_console_port`**  | `9001`                                                     | **MinIO Console port (web UI).** The console is MinIO’s web-based management UI. Default is **9001**. The role uses this value to set the `--console-address` option so that the console listens on this port on all network interfaces. If you need to change the console’s port, adjust this variable. (Ensure the port is free and open in any firewall.)                                                                                                                                                                                                                                                                                                                     |
| **`minio_enable_tls`**    | `true`                                                     | **Whether to enable TLS for MinIO.** Defaults to true, meaning the role will configure MinIO to use HTTPS if certificates are available. When TLS is enabled, MinIO will expect a certificate and key in the `minio_certs_dir` (and the service will include `--certs-dir` in its options). If you prefer to run MinIO without TLS (not recommended for production), you can set this to false to have MinIO listen on HTTP. (If true but no cert is provided, see `minio_self_signed` or provide your own cert files to avoid startup errors.)                                                                                                                                  |
| **`minio_self_signed`**   | `false`                                                    | **Whether to generate a self-signed certificate for MinIO.** If set to true, and `minio_enable_tls` is true, the role will automatically create a self-signed TLS certificate/key pair for MinIO, **but only if** you have not provided a cert and key via the variables below. It uses OpenSSL via the **community.crypto** modules to generate a new private key and a certificate signing request, then a self-signed certificate. The cert will be issued for the `minio_domain` and any `minio_extra_sans`. Default is false (no self-signed cert generation).                                                                                                              |
| **`minio_domain`**        | `{{ inventory_hostname }}`                                 | **Domain name to use for TLS certificate.** When generating a self-signed cert, this value is used as the Common Name (CN) for the certificate, and also as a DNS Subject Alternative Name. By default, it uses the Ansible `inventory_hostname` (the name of the host in your inventory). In many cases, you should set this to the actual DNS name or IP address by which clients will reach the MinIO server (especially if the inventory name isn’t a valid FQDN). This is not used if you provide your own cert.                                                                                                                                                            |
| **`minio_extra_sans`**    | `[]` (empty list)                                          | **Additional Subject Alternative Names** for the TLS certificate. This should be a list of DNS names that should be included in the certificate (typically any other hostnames that clients might use to access MinIO). It’s only relevant when `minio_self_signed: true`. By default it’s an empty list. If you set entries here (e.g. `["minio.internal.local", "storage.example.com"]`), the self-signed certificate will include those as DNS SANs (in addition to the main `minio_domain`). Ignored if not generating a cert.                                                                                                                                               |
| **`minio_cert_public`**   | `""` (empty string)                                        | **Path to an existing public SSL certificate to install** (PEM or CRT file). Use this if you have your own certificate for MinIO. For example, a file path on your Ansible control machine (will be copied) or already on the target. When both `minio_cert_public` and `minio_cert_private` are provided (non-empty), the role will copy these files into `minio_certs_dir` (as `public.crt` and `private.key`) and use them for MinIO TLS. Default is empty (no external cert).                                                                                                                                                                                                |
| **`minio_cert_private`**  | `""` (empty string)                                        | **Path to an existing private key file to install** (PEM key for the above cert). This should be the private key corresponding to the `minio_cert_public`. If provided along with the public cert, the role will copy it to the certs directory (as `private.key`). Leave empty if no external cert is used. Both public and private must be provided together for the copy to occur. By default, this is empty. Make sure to protect the key (use Vault if storing path with sensitive info).                                                                                                                                                                                   |
| **`minio_certs_dir`**     | `{{ minio_base_dir }}/certs` (e.g. `/opt/minio/certs`)     | **Directory where TLS certificates will be stored on the target.** The role will create this directory (owned by `minio_user`) and use it to store `public.crt` and `private.key` for MinIO’s TLS, if enabled. By default it’s a **certs** subdirectory of the base dir (e.g. `/opt/minio/certs`). MinIO will look here for certs when starting with `--certs-dir`. If you change this, it must match the path used in the service ExecStart (you would also override `minio_opts_extra` to specify the new certs directory).                                                                                                                                                    |
| **`minio_volumes`**       | `{{ minio_data_dir }}` (defaults to a single path)         | **Storage volume(s) that MinIO will serve.** This variable defines the **MINIO_VOLUMES** environment variable, which MinIO uses to know where your data resides. By default it’s set to the main data directory path (a single volume). You can specify multiple paths if you want MinIO to use multiple disks or if you are configuring distributed mode. For example, you could set `minio_volumes: "/data1 /data2 /data3 /data4"` (all on the same server for multiple drives) or in a cluster, a list of URLs for each node’s drive. In a distributed setup, each MinIO instance should have the same `MINIO_VOLUMES` list (with all nodes’ addresses) to form the cluster. |
| **`minio_opts_extra`**    | "--console-address :{{ minio_console_port }}"            | **Extra command-line options for the MinIO server.** By default, this is set to specify the console’s address/port (using the `minio_console_port`). These options are appended to the `minio server` command in the systemd unit. You can override this string to include additional flags. For example, to bind the main API to a specific address or port, you could set `minio_opts_extra: "--address :9100 --console-address :9101"`. Ensure the syntax is correct for the `minio` command. (If left default, it only sets the console port as determined above.)                                                                                                           |

</details>

## Tags

This role does not define any special Ansible tags for its tasks. All tasks will run by default when the role is applied. In other words, you cannot selectively skip or run subsets of the MinIO role’s tasks via tags – the role is meant to be executed in full to install/configure MinIO. (You can, however, disable certain functionality by toggling role variables, such as turning off TLS, rather than by skipping tasks.)

## Dependencies

**Role Dependencies:** None. This role does not depend on any other Ansible roles, and the `dependencies` list in its metadata is empty. You can include it in your playbooks without pulling in any other roles automatically.

**Collection/Module Dependencies:** This role requires modules from the **community.crypto** Ansible collection for TLS certificate generation tasks. In particular, it uses `community.crypto.openssl_privatekey`, `community.crypto.openssl_csr`, and `community.crypto.x509_certificate` to create a self-signed cert when needed. These modules are **not** part of the default ansible-base installation. Ensure that the `community.crypto` collection is installed (for example, by adding it to your `collections/requirements.yml` or installing via `ansible-galaxy collection install community.crypto`) before running this role with TLS enabled. All other modules used are part of Ansible’s built-in set (e.g., `ansible.builtin.get_url`, `user`, `template`, `service`, etc.), so no other special collections are needed.

**External Software/Services:** MinIO is delivered as a single binary. By default, the role downloads this binary from the official MinIO website. Thus:

* **Internet access:** The target host (or the Ansible control host, if using delegated download) needs internet access to `dl.min.io` (or wherever `minio_download_url` points) to fetch the binary. If your environment is offline, you should manually download the MinIO binary and host it internally, then override `minio_download_url` to that location.
* **System packages:** The role ensures that `curl` and `openssl` packages are installed on Debian-based systems. These are needed for downloading files and for generating TLS keys/certs. On other OSes, similar packages would be required. (On Debian/Ubuntu, no action is needed as the role installs them. On non-supported OSes, you must ensure equivalent tools are present if you adapt the role.)
* **Systemd:** The role uses systemd to manage the MinIO service. The target nodes should use systemd (which is true for Debian/Ubuntu). Non-systemd init systems would require creating a different service script or manual start mechanism (not provided by this role).

## Example Playbook

Below is a simple example of how to use the `minio` role in an Ansible playbook. This playbook will deploy MinIO on one or more hosts in the **minio** inventory group, using custom credentials and enabling a self-signed TLS certificate for testing.

```yaml
- hosts: minio
  become: true  # ensure we have privilege to install packages, create users, etc.
  vars:
    minio_root_user: "minioadmin"            # custom MinIO admin username (override default)
    minio_root_password: "{{ vault_minio_root_password }}"  # MinIO admin password (pulled from Ansible Vault or secure var)
    minio_self_signed: true                  # enable self-signed certificate generation
    minio_domain: "minio.example.com"        # domain name for the self-signed cert (Common Name & SAN)
    # minio_console_port: 9443               # example of changing console port (optional)
    # minio_enable_tls: false                # (not recommended) example to disable TLS if needed
  roles:
    - role: minio
```

**Notes:**

* It’s strongly recommended to **store sensitive variables like `vault_minio_root_password` in an Ansible Vault** (or another secrets management system). In the example above, `vault_minio_root_password` would be a Vault-encrypted variable containing the desired MinIO admin password. Avoid hardcoding passwords in plaintext playbooks.
* The above example sets `minio_self_signed: true` to quickly enable TLS with a self-signed cert. In a real deployment, for better security, you might instead provide your own TLS certificate (`minio_cert_public`/`minio_cert_private`) issued by a trusted CA, or terminate TLS at a proxy. If you don’t want TLS at all (e.g., internal network or testing behind a firewall), you can set `minio_enable_tls: false` to have MinIO listen on HTTP – but be aware this leaves traffic unencrypted.
* By default, this playbook will use port 9000 for the S3 API and 9001 for the console. If those ports are already in use or you prefer different ones, adjust `minio_server_port` and `minio_console_port` (note: changing `minio_server_port` also requires adjusting the startup options as mentioned in **Role Variables**).
* After running this play, MinIO will be running and accessible. You can verify by browsing to **[https://minio.example.com:9001](https://minio.example.com:9001)** (if DNS is configured for that domain, or use the server’s IP/hostname) and logging in with the credentials you set. Or use the `mc` (MinIO Client) or an S3 client library with the server’s URL (https on port 9000 by default when TLS is enabled).

## Testing Instructions

This role includes (or can be tested with) a **Molecule** scenario for automated testing. Molecule enables you to verify that the role works on a fresh system (often using Docker containers). You can use Molecule to test the MinIO role as follows:

1. **Install Molecule and Docker** on your development machine (if not already installed). You’ll need Python, pip, and a running Docker service. Install Molecule and its Docker driver by running for example:

   ```bash
   pip install molecule molecule[docker] docker-py testinfra
   ```

   This installs Molecule and Testinfra (for assertions). Ensure Docker is installed and you have permission to run containers (e.g., be in the `docker` group).

2. **Prepare a test scenario:** If the role already contains a Molecule scenario (e.g., a `molecule/default` directory under `roles/minio`), you can use it. Otherwise, create a new scenario for this role:

   ```bash
   molecule init scenario -r minio -d docker
   ```

   This will create a `molecule/default` scenario directory with a basic `molecule.yml` (Docker configuration) and a sample converge playbook. Check the files in `roles/minio/molecule/default/` – you might need to edit `converge.yml` to include the `minio` role (and any required vars). By default, it might already simply import this role.

3. **Run the Molecule test** to perform a full test cycle (create instances, apply role, and destroy instances):

   ```bash
   cd roles/minio  # navigate into the role's directory (where molecule config is)
   molecule test
   ```

   Molecule will launch a Docker container (by default using a Debian base image) and apply the `minio` role inside it. It will run the equivalent of a playbook that includes this role with default settings (unless you modified the converge playbook to set vars). If you have Testinfra tests defined (e.g., in `verify.yml` or separate files), Molecule will run those after convergence. Finally, it will destroy the container.

4. **Verify the outcome:** Ensure the Molecule run finishes without errors. You should see the role’s tasks execute and the play recap with OK/changed statuses. If Testinfra tests are included, check their results for any failures (by default, this role may not have explicit tests, so you can do manual verification). Optionally, you can log into the container to inspect:

   ```bash
   molecule login -h instance  # use the appropriate instance name from molecule.yml
   ```

   Once inside the container, you might check that MinIO is installed and running. For example:

   * Verify the **minio binary** exists: `which minio` (should be in `/usr/local/bin/minio`). Run `minio --version` to see if it reports the expected version.
   * Verify the **minio user** exists: `id minio` (should show a system UID and a group).
   * Check that the service is running: since it’s a container, it may not have systemd fully running. If the container uses systemd (some Molecule Docker images do), try `systemctl status minio`. Otherwise, see if the process is running: `ps aux | grep minio`. You can also look for open ports: `ss -tunlp` should show minio listening on 9000/9001.
   * If TLS was enabled in the test, ensure the cert files exist in `/opt/minio/certs` inside the container.

5. **Iterate if needed:** If the role didn’t converge or you found issues, you can adjust the role or scenario and re-run specific steps. For example, run `molecule converge` (without destroying) to apply changes to an existing container, or run `molecule verify` separately to just rerun tests. Use `molecule destroy` to clean up containers when done.

By using Molecule, you can confidently test changes to the role (or new environments) in an isolated manner before deploying to actual servers. The default scenario uses Debian 12; you can test other OS versions by adjusting the Molecule configuration (e.g., use an Ubuntu image) to ensure compatibility.

## Known Issues and Gotchas

When using the `minio` role, be aware of the following common issues, limitations, or quirks:

* **TLS Enabled by Default – Requires Certs:** The role’s default is `minio_enable_tls: true` but with no default cert provided (`minio_cert_public`/`private` are empty) and self-signed generation turned off. This means *if you run the role with defaults, MinIO will be configured to use TLS but no certificate will be present*, causing the MinIO server to fail on startup. To avoid this, you should either:

  * Set `minio_self_signed: true` so the role generates a certificate automatically (for test or internal use), **or**
  * Provide your own `minio_cert_public` and `minio_cert_private` files (for production, using a real certificate), **or**
  * As a last resort, disable TLS by setting `minio_enable_tls: false` (not recommended unless in an isolated environment).

  If you see MinIO’s service not starting, double-check that certificate files exist in the certs directory. This is a common gotcha when one forgets to supply certs with TLS on.

* **Changing the API Port Requires Extra Steps:** The role defines `minio_server_port` (default 9000) as a variable, but currently it does **not automatically apply it** to the MinIO startup command or configuration. MinIO defaults to port 9000 for the API if not told otherwise. If you need MinIO to listen on a different port, simply changing `minio_server_port` will **not** suffice. You must also adjust `minio_opts_extra` to include the `--address :<newport>` flag. For example:

  ```yaml
  minio_server_port: 9100
  minio_opts_extra: "--address :9100 --console-address :{{ minio_console_port }}"
  ```

  This is a known limitation of the current role version. Future updates may integrate `minio_server_port` into the service template. As a workaround, ensure both the server and console ports are set consistently in the options (and update any firewall rules accordingly).

* **Single-Node by Default – No Auto Clustering:** This role installs MinIO on a host as a standalone server. It **does not** automatically cluster multiple hosts together. If you run this role on multiple hosts, you’ll get multiple independent MinIO servers (which can be useful for separate environments or sharding, but not a unified cluster). MinIO *can* operate in a distributed mode (multiple servers forming one object storage cluster), but to achieve that, you must coordinate configuration manually:

  * All MinIO instances in a cluster need to be started with the same `MINIO_VOLUMES` list, containing references to each node’s storage. For example, on each of 4 servers, you might set `minio_volumes: "http://node1:9000/opt/minio/data http://node2:9000/opt/minio/data http://node3:9000/opt/minio/data http://node4:9000/opt/minio/data"`. This is complex to template and not handled by the role out-of-the-box.
  * There is no orchestration in this role to ensure the order or consistency of cluster startup. You have to ensure all nodes are deployed and use a consistent configuration.

  In short, **the role does not magically create a MinIO cluster**; it prepares nodes, and you must configure them appropriately for distributed mode. Consult the [MinIO documentation](https://docs.min.io) for distributed deployment guidelines. For most users, if you need a multi-node MinIO, consider using a load balancer (see **Cross-Referencing**) or MinIO Operator/Kubernetes for orchestration. This role is focused on single-server installs or manual clustering.

* **Not Tested on RedHat/CentOS:** As noted earlier, this role expects a Debian/Ubuntu environment. If you try to use it on a Red Hat-based system without modification, it will likely fail (for example, it will attempt to use apt and the `Debian.yml` vars). Common issues would include package installation failures and service misconfiguration. Porting the role to CentOS would require adding appropriate `vars/RedHat.yml` (with yum package names for curl/openssl) and adjusting tasks for any differences (like maybe using a different default no-login shell path). Use Debian-based OS or container for reliable results.

* **Default Credentials Are Insecure:** The default admin access credentials (minioadmin:minioadmin) are well-known. If you apply the role without changing them, your MinIO server is **vulnerable** – anyone who can reach it can log in with those credentials. Always override at least `minio_root_password`, if not also the username. The role makes it easy to set these; ensure you do so, and ideally use vault/encrypted vars. After deployment, you can further create additional users or keys in MinIO as needed, but the admin credential should be treated like a root secret.

* **Firewall and Port Conflicts:** MinIO by default uses ports 9000 (API) and 9001 (console). If those ports are blocked by a firewall or already in use by another service, you will encounter connectivity issues. Be mindful to:

  * Open the necessary ports on your firewall/UFW. For example, on Ubuntu with UFW: `ufw allow 9000,9001/tcp` (or the ports you chose).
  * Ensure no other process is using port 9000 or 9001. If a conflict exists, either change MinIO’s ports (as described above) or relocate the other service.
  * If using SELinux (not typical on Debian, but on RedHat systems), opening ports or allowing the binary might require additional steps (SELinux contexts for a custom binary).

  Also note that if `minio_console_port` is set to 0 or left blank (not recommended), MinIO might choose a random console port on each start, which can be confusing. The role sets it explicitly to avoid that scenario.

* **Running MinIO on ARM (Raspberry Pi, etc.):** The default download URL is for the 64-bit AMD64 binary. If you run the role on an ARM-based device (like Raspberry Pi OS 64-bit), the binary won’t execute. You will need to override `minio_download_url` to point to MinIO’s ARM64 binary (or ARM32 if applicable) from the MinIO releases. MinIO provides binaries for multiple architectures on their download page. Set the URL appropriately for your architecture before running the role.

* **Data and Configuration Persistence:** The role puts data in `/opt/minio/data` (by default) and config (like certs) in `/opt/minio` as well. If you reinstall or remove MinIO, these directories remain by design (to avoid deleting data). Clean-up is manual. Also, upgrading MinIO (to a new version) simply means changing the download URL/version and re-running the role – it will overwrite the binary. Your data and config will carry over since they’re on disk. Always backup your data directory before upgrades, just in case.

* **Service Startup Issues:** The systemd service unit includes a pre-start check that `$MINIO_VOLUMES` is set (to avoid accidental empty data target). If the service fails immediately with “ERROR: MINIO_VOLUMES is not set”, it means the environment file might be missing or not loaded. This could happen if the environment file wasn’t templated correctly or systemd couldn’t read it. Ensure `/etc/default/minio` exists and has the expected content (this role should create it). Also run `sudo systemctl daemon-reload` if you manually adjusted the unit. The role’s handler should do this on changes. This is just a troubleshooting tip if you manually tweak things.

## Security Implications

Deploying MinIO with this role has a few security considerations to keep in mind:

* **User Privileges:** The role creates a system user **`minio`** with no login shell (`/usr/sbin/nologin`) and no home directory, and runs the MinIO process under this account. This is a security best practice, limiting the impact of a compromise – the MinIO process runs with minimal OS permissions. You should not use the `minio` account for interactive login or any other service. The binary and data files are owned by `minio:minio`. By default, directories are created with mode 0755, which allows read/execution by others; if you require stricter access (for example, to prevent non-root local users from listing files), you might consider tightening permissions to 0750 on the data dir. However, note that the MinIO process itself needs full access to its data and certs.

* **Open Ports:** MinIO listens on network ports for its services (9000 for S3 API, 9001 for web console by default). These ports are opened on **all network interfaces** by default (since `minio_server_address` is not set, it binds to 0.0.0.0). This means MinIO is accessible from any network that can reach the host. You should place MinIO in a protected network segment if possible and/or use firewall rules to restrict access:

  * Use the **ufw role or other firewall** to allow access to 9000/9001 only from known IP ranges (for instance, your application servers or administrators’ IPs). Block unwanted sources.
  * If MinIO is for internal use, consider binding it to an internal interface or private IP. (The role doesn’t directly expose a `minio_server_address` variable use, but you could override `minio_opts_extra` with `--address <IP>:9000` to bind to a specific interface.)
  * Regularly review open ports on the host (`ss -tulpn` or `netstat -plnt`) to ensure only intended services are listening and accessible.

* **TLS and Encryption:** With `minio_enable_tls: true`, the role sets up MinIO to use HTTPS for both API and Console endpoints. This is crucial for protecting data in transit and credentials. If using self-signed certs (via `minio_self_signed`), be aware that clients (browsers, SDKs) will not trust the certificate by default. You’ll need to import the self-signed CA or certificate into their trust store, or use the MinIO client with `--insecure` flag for testing. For production, it’s better to use a certificate signed by a trusted CA:

  * You could use the **Step CA** role (see **Cross-Referencing**) to act as an internal CA and issue a cert for MinIO. Or use Let’s Encrypt (if your MinIO is accessible publicly and has a domain) via an ACME client or a provided role.
  * Ensure private keys are kept secure. The `minio_cert_private` should be protected – if you keep it in Ansible files, use Vault. On the server, it is stored at `minio_certs_dir` with owner `minio` and mode 0640 by default (readable by root and minio group only).
  * MinIO also encrypts object data at rest optionally (server-side encryption). This role does not configure that, but if you require it, you would need to set up a KMS (Key Management Service) or use MinIO’s encryption features manually after installation.

* **Credentials Management:** The MinIO admin credentials (root user/password) are essentially the keys to your kingdom for that server. Anyone with those can create users, buckets, or read all data. Manage these secrets carefully:

  * Rotate the `minio_root_password` after initial setup if it might be exposed, or at regular intervals. You can update the password by rerunning the role with a new value (MinIO will update the admin credentials on restart).
  * Do not share the admin credentials unnecessarily. For applications that need access to MinIO, create separate MinIO users or use access keys with limited privileges (MinIO supports creating users/groups and policies via its console/CLI). The admin account should be reserved for administrators.
  * If using Ansible Vault or other secret storage, restrict access to those who truly need to deploy or manage the server.

* **Data Security and Backups:** MinIO stores all data on the host’s filesystem (in the `minio_data_dir`). Ensure that the host’s storage is reliable and consider using RAID or other redundancy at the storage layer if this is a single node deployment. Also consider **backing up your MinIO data** or setting up a mirror/replication if the data is critical. This role doesn’t set up any backup – it’s up to you to implement backup strategies (e.g., use the **backup** roles in this repository to periodically archive data, or use MinIO’s built-in snapshot/replication features to another MinIO server).

* **Auditing and Logging:** MinIO logs to the console (and hence journal since it’s run by systemd). You may want to aggregate these logs. The role doesn’t configure external logging, but you could use tools (like the **EFK stack** or other roles in the repo) to ship logs to a central location. MinIO logs accesses and errors, which are useful for auditing usage or troubleshooting issues. Regularly review the logs for any suspicious access or errors.

* **Resource Usage & Limits:** The systemd unit that this role installs sets `LimitNOFILE=65536` and `TasksMax=infinity`, which are generally good for high-performance I/O. Ensure your system can handle that (most can). If you are running many services, monitor resource usage. MinIO can consume significant CPU and memory under load (especially for large IO or if running in distributed mode with erasure coding). Plan capacity accordingly. If needed, you can adjust systemd limits via override files if your environment requires different limits.

In conclusion, this role attempts to follow best practices: a dedicated system user, TLS by default, and not exposing unnecessary surface area. It’s important for you as the operator to finish the job by controlling network access, using strong unique credentials, and monitoring the MinIO server’s security (updates, logs, backups) over time.

## Cross-Referencing

Within this repository, several other roles and tools can complement the **MinIO** role or are commonly used alongside it:

* **HAProxy (Load Balancer) Role** – If you are deploying MinIO in a **distributed cluster or HA scenario**, you might consider using the **haproxy** role to front the MinIO servers. HAProxy can provide a single endpoint (virtual IP or DNS name) and balance requests to multiple MinIO nodes. It can also handle SSL termination. For example, you could have HAProxy listen on port 443 with a valid certificate and forward traffic to MinIO instances on port 9000 (over HTTP internally). This approach offloads TLS from MinIO and allows you to scale out horizontally. (See the HAProxy role documentation for configuring backends; you’d list your MinIO servers as backend targets.) Using HAProxy in combination with **keepalived** (via the **keepalived_setup** role) can even provide active-passive failover for the load balancer itself, ensuring high availability at the IP level.

* **Step CA Role** – The **step_ca** role sets up a private certificate authority using Smallstep’s CA tool. This can be extremely useful for MinIO deployments in secure environments. For instance, you can use Step CA to issue an internal TLS certificate for your MinIO server (so you don’t have to rely on self-signed certs). Deploy the Step CA on your network, use it to generate a certificate for the MinIO domain (it will be trusted by your internal systems once you distribute the CA root), and supply that cert/key to the MinIO role via `minio_cert_public` and `minio_cert_private`. This gives you the benefits of TLS with a verifiable chain, without exposing MinIO to Let’s Encrypt or purchasing a cert. (Alternatively, the **letsencrypt_setup** role in the repository could automate obtaining a Let’s Encrypt certificate if your MinIO is accessible on the internet and you want a free publicly trusted cert.)

* **UFW (Firewall) Role** – The **ufw** role can be used to manage firewall rules on Ubuntu/Debian hosts. It’s wise to use it (or the more general **base** hardening role which might include firewall setup) to restrict access to MinIO’s ports. For example, after deploying MinIO, you could apply the UFW role to allow port 9000/9001 from only certain IP ranges (or to close everything except required ports). Integrating the firewall role ensures that even if MinIO is running, it isn’t freely reachable except by intended clients. This is especially important if your server has a public interface – you don’t want MinIO’s console exposed to the whole internet. Use UFW to permit access from your application servers, VPN, or admin workstation IPs only.

* **Backup Roles (NetBox Backup, Jenkins Backup, etc.)** – The repository contains roles for backing up applications (e.g., **backup_netbox**, **jenkins_backup**, **openldap_backup** and others). These roles typically dump data to local files on the host. MinIO can serve as an excellent target for offsite or cloud-like storage for those backups. While there isn’t an out-of-the-box integration in the backup roles to upload to MinIO, you can achieve it by scheduling an additional step: for example, after running the NetBox backup role, use the MinIO client (`mc`) or an S3 module to upload the backup files to a bucket on your MinIO server. This combination yields a robust backup solution: local backups for quick restore and copies stored in MinIO for durability. Consider writing a small play or script to do the upload, or use the **restic** backup tool (if present in the repo or externally) with MinIO as an S3 backend for an integrated approach.

* **Application Roles Using S3/MinIO** – If you have applications that can use S3-compatible storage, you can integrate them with MinIO. For instance, if there’s a role for **Apache Superset** or others that need to store large files or uploads, you could configure those applications to point to MinIO as if it were S3. (Superset doesn’t natively require S3, but as a hypothetical, other apps like GitLab, Nextcloud, or data pipelines might support S3 storage for certain features like artifacts, attachments, or logs. In this repository, an example might be if any role supports external storage for something, you’d supply MinIO’s URL and credentials.) While no specific role in this repo is built solely for MinIO integration, the principle is that any app expecting AWS S3 can be given the MinIO endpoint (e.g., `http://minio.example.com:9000` or `https://` if TLS, along with the access key/secret from `minio_root_user` or a created user) and it should work the same. This enables a fully self-hosted “S3” ecosystem. Always ensure proper policies in MinIO when doing this (create separate MinIO credentials per application with limited permissions).

* **General Base Role and Hardening** – The **base** role (if present) likely handles common setup like apt updates, time sync, users, etc. Running such a role on your servers prior to MinIO is a good idea. It may also configure things like fail2ban or logging that can enhance security for MinIO indirectly. Additionally, the **common** role (if one exists) might set up NTP, system tweaks, etc., which are beneficial for any server including those running MinIO (for example, correct time is important if you use MinIO’s features that rely on time sync for TLS or log timestamps).

Each of these roles has its own README and defaults documentation – refer to them for detailed usage. By combining the MinIO role with others, you can build a more complete and secure infrastructure. For instance, a full stack might involve deploying MinIO with this role, securing it behind HAProxy (with SSL from Step CA), locking down the host with UFW, and scheduling backups of important data into MinIO. This way, the roles within this repository complement each other to cover different aspects (storage, networking, security, data protection) of your deployment.
