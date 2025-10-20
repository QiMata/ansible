# jenkins_controller Ansible Role

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

The **jenkins_controller** role installs and configures a Jenkins Controller (master) on a target host. Jenkins is a popular Continuous Integration/Continuous Delivery (CI/CD) server, and this role automates the setup of the Jenkins controller service along with initial configuration for immediate usability. Its key tasks include:

* **Package Installation**: Adds the official Jenkins APT repository and GPG key, then installs Jenkins (pinned to a specific version) along with the required Java runtime (OpenJDK 11). This ensures the controller is installed from a trusted source and has all necessary dependencies.
* **Service Configuration**: Configures Jenkins to run on the desired HTTP port (default **8080**) and disables the initial setup wizard for non-interactive deployment. The role updates the Jenkins defaults (e.g. `/etc/default/jenkins`) to include appropriate startup arguments such as `--httpPort={{ jenkins_controller_http_port }}` and any custom Java options.
* **Admin User Bootstrapping**: Automates the creation of an initial **admin** user on first startup. A Groovy init script is deployed to Jenkins’ initialization directory to create the admin account (with credentials provided via variables) and to set the security realm/authorization strategy. This means you will have a known admin login without needing to retrieve the random initial password that Jenkins normally generates.
* **Plugin Management**: Supports offline installation of Jenkins plugins during provisioning. You can specify a list of plugin IDs, and the role will generate a plugins file and run the Jenkins Plugin Manager CLI to download those plugins into the Jenkins instance. This allows the controller to come up pre-loaded with required plugins (and their dependencies) without manual UI steps.
* **Service Startup**: Ensures the Jenkins service is enabled and started on the host, so Jenkins launches on boot and is running after the playbook execution. Any configuration changes that require a restart (such as installing plugins or modifying the port/config) will notify a handler to restart Jenkins, applying changes immediately.

Overall, this role is designed to be **idempotent** – running it multiple times will not duplicate installations or users. It handles setting up a production-ready Jenkins Controller with minimal manual intervention. After applying this role, the Jenkins web UI should be accessible (on the configured port) with the admin credentials configured, and agents can then be connected as needed. The **jenkins_controller** role focuses on the Jenkins master node; for setting up build agents or additional Jenkins maintenance tasks, see the related roles in this repository (refer to **Cross-Referencing** below).

```mermaid
flowchart LR
    subgraph "Jenkins CI/CD Architecture"
      A[Jenkins Controller<br/>(Master Node)] -- Dispatch builds --> B[(Agent Nodes)]
      B -- Run jobs and report back --> A
    end
    C(Developers) -- Commit code / Trigger jobs --> A
    A -- Web UI & API --> C
```

## Supported Operating Systems/Platforms

This role is tested on and supported with Debian-based Linux distributions, specifically:

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal) and 22.04 LTS (Jammy)

Other Debian/Ubuntu-derived systems should work as well, as the role uses the `apt` package manager and assumes a systemd-based service. **Red Hat/CentOS and other non-APT systems are not supported** without modifications, since tasks like apt installations and repository setup are Debian/Ubuntu-specific. Ensure your target hosts match one of the supported OS versions to prevent incompatibilities.

> **Note:** The Jenkins APT repository configured by this role is the official **Debian-stable (LTS)** repository. By default, it will install Jenkins LTS releases. Using the role on unsupported platforms or trying to use a non-Debian package manager will result in task failures.

## Role Variables

Below is a list of important variables for this role, along with default values (defined in **`defaults/main.yml`** or expected from user input) and their descriptions:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable                       | Default Value                                                | Description                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`jenkins_repo_url`**         | `"https://pkg.jenkins.io/debian-stable"`                     | Base URL of the official Jenkins APT package repository (LTS channel) to configure on the target host. Unless you need weekly releases or a custom mirror, this should point to the stable Jenkins repo for your OS.                                                                                                                                                                             |
| **`jenkins_repo_key_url`**     | `"https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key"` | URL to the GPG key for the Jenkins APT repository. This key is downloaded and installed to ensure APT trusts the Jenkins packages. (The default is the 2023 signing key from Jenkins.)                                                                                                                                                                                                           |
| **`jenkins_controller_version`**          | *No default* (e.g. `"2.452.2"` in inventory)                 | Version of Jenkins to install. This should be an LTS version string available in the Jenkins repo. For example, in production it might be set to `"2.452.2"`. The role uses this to pin the package version (ensuring reproducible installs). If not specified, the installation may attempt to get the latest available version (but pinning is recommended for consistency).                   |
| **`jenkins_home`**             | `/var/lib/jenkins`                                           | Jenkins home directory on the controller host. This is where Jenkins stores configuration, plugins, and job data. It’s created by the Jenkins package install and is typically owned by the `jenkins` system user.                                                                                                                                                                               |
| **`jenkins_controller_http_port`**        | `8080`                                                       | TCP port that Jenkins will listen on for its web interface. The default Jenkins HTTP port is 8080. You can change this if you need Jenkins on a different port (e.g., 80 or 8081), but ensure no firewall or other service conflicts. The role will update Jenkins’ startup args to use this port.                                                                                               |
| **`jenkins_controller_java_opts`**        | *No default* (e.g. `"-Xms512m -Xmx2048m"`)                   | Additional Java runtime options for the Jenkins process. By default, Jenkins has its own memory settings; you can override them here. For instance, in one environment it is set to allocate 512MB min and 2048MB max heap. If left undefined, Jenkins will use its package default Java options. This can be used to tune performance (heap size, GC flags, etc.).                              |
| **`jenkins_controller_admin_user`**       | `"admin"`                                                    | Username for the initial Jenkins administrator account. The role will create this user at first startup via a Groovy init script if it doesn’t already exist. The default is “admin,” but you may choose a different name.                                                                                                                                                                       |
| **`jenkins_controller_admin_password`**   | *No default (must provide)*                                  | Password for the initial admin user. **This must be provided by the user**, preferably via an encrypted variable (Ansible Vault) for security. The role does not set a default password (to avoid using a well-known credential). If this variable is not set, the admin user creation script will not have a valid password, and you may be unable to log in securely.                          |
| **`jenkins_controller_plugins`**          | *Empty list* `[]`                                            | List of Jenkins plugin IDs to install on the controller. By default this is an empty list (meaning no additional plugins are installed). If you provide plugin names (e.g., `["git", "matrix-auth", "job-dsl"]`), the role will download those plugins (and their dependencies) using the Jenkins Plugin Manager CLI. Plugins listed here will be added to the controller’s `plugins` directory. |
| **`jenkins_controller_plugins_state`**    | `present`                                                    | Desired state for plugins defined in `jenkins_controller_plugins`. This role only supports installing plugins (`present`). While this variable exists for potential use (e.g., to remove plugins if set to `absent`), the current implementation always ensures listed plugins are present.                                                                                                                 |
| **`jenkins_backup_dir`**       | `/var/backups/jenkins`                                       | Directory where Jenkins backups will be stored. This is used by the complementary **jenkins_backup** role (see **Cross-Referencing**). You can override it if you want backups in a specific location. Ensure the Jenkins user has write permission here if backups run as Jenkins or adjust permissions accordingly.                                                                           |
| **`jenkins_backup_keep_days`** | `7`                                                          | Number of days to keep old Jenkins backup files. The **jenkins_backup** role will delete backups older than this threshold to save space. You can increase or decrease this retention period based on your backup policy.                                                                                                                                                                       |

</details>

<!-- markdownlint-enable MD033 -->

Most of the above defaults can be found in the role’s **defaults/main.yml**, except those marked as “must provide” which should be supplied via inventory or extra vars. In a typical usage, you **must** at least set `jenkins_controller_admin_password` (for security) and likely pin a `jenkins_controller_version`. You’ll also commonly specify some `jenkins_controller_plugins` to install useful plugins. The rest have reasonable defaults (e.g., port 8080, standard paths).

## Tags

This role does not define any custom Ansible tags. All tasks are executed when the role runs (no tasks are tagged for selective runs by default). In other words, you cannot skip or run only subsets of tasks via `--tags` or `--skip-tags` specific to this role, because no tags are assigned in the role tasks.

*(If you need to isolate certain steps, you would have to modify the role to add tags. For example, tagging the plugin installation tasks as `jenkins_controller_plugins` would allow skipping them. However, out-of-the-box, no such tags are provided.)*

## Dependencies

**None.** This role has no strict dependencies on other Ansible roles or Galaxy collections. All required actions (installing packages, configuring files) are handled within the role using Ansible built-in modules. The role assumes an internet connection for downloading Jenkins packages and plugins.

While there are no external role dependencies, note that Jenkins itself depends on Java (which this role installs via the system package manager). The target system should support `apt` (Debian/Ubuntu) and have systemd (or an init system) to manage the Jenkins service. No additional Ansible collections are required, as the role uses core modules (e.g., `ansible.builtin.apt`, `ansible.builtin.service`, etc.).

*(Optionally, you might run the complementary **Base** hardening role before this to ensure the system is up-to-date and secure, but it’s not a prerequisite. Other Jenkins-related roles like **jenkins_agent** and **jenkins_backup** are not dependencies but can be used alongside — see **Cross-Referencing**.)*

## Example Playbook

Here is a concise example of how to use the `jenkins_controller` role in a playbook. This example assumes you want to set up a Jenkins Controller on a host (or group of hosts) with some custom parameters:

```yaml
- hosts: jenkins_controllers
  become: yes  # Run with privilege escalation to install packages and configure services
  vars:
    jenkins_controller_version: "2.452.2"             # Pin a specific Jenkins LTS version
    jenkins_controller_admin_user: "admin"            # Admin username (default is 'admin')
    jenkins_controller_admin_password: "SuperSecretPassword!"  # Admin password (use vault in practice)
    jenkins_controller_plugins:
      - git
      - matrix-auth
      - job-dsl
      - configuration-as-code
    jenkins_controller_http_port: 8080                # (Optional) Port for Jenkins UI (8080 is default)
    jenkins_controller_java_opts: "-Xms1g -Xmx2g"     # (Optional) JVM memory settings
  roles:
    - jenkins_controller
```

In the above playbook:

* We target a host group `jenkins_controllers` (as defined in inventory) and elevate privileges with `become: yes` because installation needs root rights.
* We explicitly set several role variables: Jenkins version, admin credentials, plugin list, etc. (In practice, sensitive values like the password should be provided via Ansible Vault or an external vars file.)
* We then include the `jenkins_controller` role. The role will apply all tasks using the given variables on the target host(s).

This usage is analogous to how the role is used in the repository’s Jenkins playbook. For instance, in the repository, a playbook assigns the role to hosts in the `jenkins_controllers` group, and similarly the **jenkins_agent** role to `jenkins_agents` hosts. You can adapt the example above by adding it to your playbook or including it in a larger site YAML.

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to verify it works as expected before using it in production. Molecule enables you to simulate the role on disposable containers:

1. **Install Molecule** (and Docker). For example, install via pip: `pip install molecule[docker]`. Ensure Docker is installed and the daemon is running on your system.
2. **Initialize a test scenario** (if not already provided): Check if the role has a Molecule scenario under `roles/jenkins_controller/molecule/`. If not, you can create one by running:

   ```bash
   molecule init scenario -r jenkins_controller -d docker
   ```

   This will set up a `molecule/default` directory with a basic scenario for the role.
3. **Configure the scenario**: Edit the `molecule.yml` in the scenario if necessary to choose a suitable Docker image (e.g., an Ubuntu 22.04 image) and to set any required variables. For Jenkins, ensure the container has systemd or use Docker’s capability to run services. You might also want to predefine `jenkins_controller_admin_password` in the scenario’s playbook for testing.
4. **Run the role in a container**: Execute `molecule converge` to create and provision the Docker container with this role. Molecule will bring up a container and apply the `converge.yml` playbook (which includes the `jenkins_controller` role). Watch the output for any errors.
5. **Verify the results**: After converge, you can perform checks: for example, use `docker exec -it <container_id> /bin/bash` to enter the container. Then verify that Jenkins is installed: check that the Jenkins package is present (`dpkg -l jenkins`), that the service is running (`systemctl status jenkins` or check the process), and that files like `/var/lib/jenkins/config.xml` exist. If the container’s port 8080 is exposed, you could even try to reach the Jenkins UI from your host browser. Also confirm that the admin user script (`/var/lib/jenkins/init.groovy.d/init_admin_user.groovy`) was deployed and that the plugins directory contains any specified plugins (e.g., `.jpi` files for each plugin you listed).
6. **Run tests (if any)**: If you have written Molecule verification tests (using Ansible assertions or Testinfra/Inspec), run `molecule verify` to execute them. These tests might check idempotence or that Jenkins is responding on the expected port, etc. In absence of explicit tests, you can run `molecule converge` again to ensure the role is **idempotent** (the second run should result in 0 changes if everything was configured correctly).
7. **Cleanup**: Finally, run `molecule destroy` to tear down the test container. You can also run `molecule test` to perform the full cycle (create, converge, verify, destroy) in one go.

**Notes for container testing:** Running Jenkins inside a Docker container for testing can be tricky because Jenkins is normally launched as a system service. If the Molecule Docker container does not have systemd, the `jenkins` service may not actually start during convergence (the role will install and configure it, but `service: started` might not function without an init system). In such cases, to truly verify Jenkins is up, you might need to start the Jenkins process manually inside the container or use a base image that supports systemd (e.g., the `geerlingguy/docker-ubuntu2204-ansible` Molecule image which has systemd enabled). Even without the service running, you can still verify that the installation and configuration steps completed (files in place, etc., as noted above).

Using Molecule with this role helps ensure that:

* All tasks complete without errors on a fresh system.
* The role is idempotent (multiple runs result in no changes after the first).
* Jenkins comes up configured as expected (correct port, admin user, plugins, etc.).

By testing in a controlled environment, you can catch issues early and adjust variables or role settings before applying to production servers.

## Known Issues and Gotchas

* **Initial Admin Credentials:** The role creates an admin user with a specified password on first launch. Failing to set the `jenkins_controller_admin_password` will result in no valid admin credentials. Ensure you provide a strong admin password (preferably via vault). Also note that because the role disables Jenkins’ setup wizard, you will **not** be prompted for the initial password on the Jenkins UI – you are expected to log in with the credentials given to the role. Keep them secure.
* **Plugin Installation Idempotence:** The offline plugin installation step uses the first plugin as a marker file to avoid re-downloading on subsequent runs. This means if you change the `jenkins_controller_plugins` list (for example, add new plugins later), running the role again might skip the plugin installation step because it sees the first plugin already installed. In such cases, new plugins won’t be installed unless you manually remove the marker (e.g., delete the plugin files) or otherwise force the step. A workaround is to run the plugin manager manually for new plugins or adjust the role to handle incremental plugin installs.
* **Plugin Updates:** Similarly, the role doesn’t automatically update plugins once installed. All plugins are installed at their latest version at the time of role execution. If you need to update plugins later, you must either update the plugin list (with version specifications or by removing the old `.jpi` files to force re-download) or handle it through Jenkins’ UI/CLI outside of this role.
* **Jenkins Startup & Ports:** After the role runs, Jenkins will be configured to listen on the specified `jenkins_controller_http_port`. Make sure nothing else on the server is already using that port. If you change the port from the default 8080, remember to include that in the URL when accessing Jenkins (and update any firewall rules accordingly). The role does not configure firewall settings; if your servers have a firewall (UFW/iptables, etc.), you must allow the Jenkins port separately.
* **Service Startup in Containers:** As noted, if you test this role in a Docker container without systemd, the Jenkins service might not actually be running after convergence (even though the role reports “started”). This is usually a test environment issue and not a problem on real VMs/servers with proper init systems. In production, on a normal VM or bare metal, the service should start as expected. Just be aware when testing in containers that lack an init, you might need a different approach to verify the service.
* **Upgrading Jenkins:** To upgrade Jenkins to a newer version, you can update the `jenkins_controller_version` variable and re-run the role. Because the APT repository is configured, updating the version will cause apt to install the new version. Jenkins will restart to apply the update. Be sure to coordinate downtime, as upgrading Jenkins will interrupt any running builds. Also consider compatibility of plugins with the new version.
* **Backup Strategy:** The role itself doesn’t perform backups (that’s handled by the **jenkins_backup** role), but note that Jenkins home contains all config and job data. It’s good practice to run the backup role or otherwise back up `${jenkins_home}` regularly. The variables `jenkins_backup_dir` and `jenkins_backup_keep_days` should be set appropriately for your environment if you use the backup role. Always verify that backups are happening and stored off-server if the Jenkins data is critical.
* **Jenkins Security**: The role sets Jenkins security to disallow anonymous access by default (the Groovy script applies the “FullControlOnceLoggedInAuthorizationStrategy” with anonymous read disabled). This means **you must log in to Jenkins to see anything** – which is good for security (no broad anonymous access). If you require some level of anonymous read (for example, public job statuses), you would need to modify the security settings after installation. Also, be aware that the provided admin user has full control; create additional regular users or integrate with LDAP/OAuth if needed, and consider rotating the admin credentials periodically.
* **No TLS by Default**: Jenkins is served over HTTP by default on port 8080. This role does not set up HTTPS. If you are deploying in a production environment, it is strongly recommended to put Jenkins behind a reverse proxy or use Jenkins’ own SSL configuration to secure the UI with TLS. At minimum, ensure that port 8080 is firewalled from untrusted networks if running HTTP. The role focuses on Jenkins setup and leaves network security to the operator (or to other roles like a web proxy or firewall).
* **System Resources**: Ensure the target server has sufficient resources for Jenkins. The role itself doesn’t enforce any minimum CPU/RAM, but Jenkins can be memory-intensive. Adjust `jenkins_controller_java_opts` (especially the heap size) based on the instance size. A small VM (1-2 CPU, 2GB RAM) can run Jenkins for testing, but for production with multiple jobs and plugins, you’ll want more memory and CPU. Monitor the service and tune accordingly.

## Security Implications

This role has several security-related effects and considerations that operators should be aware of:

* **Linux User Account**: Installing Jenkins via the OS package will create a system user **`jenkins`** (if not already present) under which the Jenkins service runs. This is a security best practice – Jenkins does not run as root. The role’s use of `apt` ensures this user is created with limited privileges (usually with `/bin/false` or `/usr/sbin/nologin` as shell). All Jenkins files (in `/var/lib/jenkins`, `/var/log/jenkins`, etc.) are owned by this user. Administrators should avoid altering permissions in ways that give broader access to these files.
* **Initial Admin User**: The role sets up a Jenkins admin account with credentials you provide. It’s crucial to use a strong password and keep it secret (store it in Ansible Vault or a secrets manager). The admin user has full control over Jenkins, including configuring security, agents, and executing code on agents. Compromise of this account would mean complete Jenkins compromise. If possible, change this password on first login to something not stored in playbooks, or better yet, integrate Jenkins with an external auth (LDAP/OAuth) and remove the static admin after initial setup.
* **Disabled Anonymous Access**: By default, the role configures Jenkins security to **disallow anonymous reads**. This means until a user logs in, they cannot see or trigger any jobs. This is a secure default, preventing accidental exposure of projects or build information to unauthenticated users. If your use-case requires some openness (like allowing read-only access to build results), you’ll have to manually adjust the authorization strategy in Jenkins after deployment.
* **Jenkins Web Interface**: The Jenkins UI is exposed on port **8080** (HTTP). The role does not configure SSL/TLS, so the web traffic (including logins) is unencrypted if you access it directly. For a production setup, consider one of the following:

  * Use a reverse proxy (like Nginx or Apache) in front of Jenkins to terminate SSL and forward to Jenkins on localhost:8080.
  * Configure Jenkins to use HTTPS directly by adding a certificate and enabling HTTPS in the Jenkins config.
  * At minimum, restrict access to the Jenkins port at the network level (e.g., only allow internal IPs or VPN).
    Failing to secure the Jenkins UI can expose credentials or allow attackers to intercept sessions.
* **Firewall and Access**: This role does not set up a firewall. If your environment has no external firewall, consider using a host-based firewall (like UFW or iptables) to limit access to Jenkins. Ideally, only trusted networks or users should be able to reach the Jenkins port. Also ensure that the SSH credentials or other access to the Jenkins host are secure, as an attacker who gains server access could manipulate Jenkins files or steal credentials.
* **Plugin Security**: The role installs plugins as specified, but you should vet the plugins you include. Jenkins plugins have had security vulnerabilities in the past. Only install plugins from trusted sources and keep them updated. The `configuration-as-code` plugin (if used) can expose configuration; ensure any sensitive configuration (like credentials in CasC) is handled properly (encrypted if possible).
* **Backing up Data**: Jenkins stores critical data (job configurations, build logs, credentials, etc.) in its home directory. The companion **jenkins_backup** role can help automate backups to `${jenkins_backup_dir}`. Use it to regularly back up Jenkins data, and store those backups securely (since they may contain sensitive information like credentials or tokens). Verify that backups are encrypted at rest or stored in a secure location, as they effectively contain the keys to your CI kingdom.
* **System Updates**: Since this role adds a new apt repository to your system (the Jenkins repo), keep in mind that your system will now trust and potentially auto-update Jenkins from that source. Make sure to include Jenkins in your regular patch management strategy. When new Jenkins security releases come out, update the `jenkins_controller_version` (or allow the apt repository to provide the update if you prefer automatic updates) and run the role or `apt upgrade` to apply them. Unpatched Jenkins instances are a common target for attackers.
* **Build Execution**: By design, Jenkins will execute build jobs, which often involve running arbitrary code (build scripts, test suites) on agents or the controller. Ensure that build agents are locked down or isolated if they run untrusted code. The controller itself should ideally not run builds (set up separate agents) to reduce risk on the master node. If the controller does run builds (because you have no separate agents), be cautious about what jobs you run on it. The role itself doesn’t configure this aspect, but as a security consideration, try to segregate responsibilities.

In summary, this role sets secure defaults for Jenkins (account created, anonymous access off), but the security of the Jenkins installation will ultimately depend on how you manage it post-installation. Always follow Jenkins security advisories and best practices. Use this role as a starting point, and layer on additional security (SSL, user access controls, backups, etc.) as appropriate for your environment.

## Cross-Referencing

Within this repository, there are additional roles that complement or integrate with **jenkins_controller**. Depending on your CI/CD setup, you may use these roles alongside the Jenkins Controller role:

* **[jenkins_agent](../jenkins_agent/README.md)** – This role provisions Jenkins agent nodes that connect to the Jenkins Controller. While the controller manages the Jenkins server and UI, the **jenkins_agent** role handles installing the agent software (or configuring the JNLP/SSH connection) on worker nodes. Use it for any servers that should act as build executors. Together, **jenkins_controller** and **jenkins_agent** allow you to scale out Jenkins builds across multiple machines.
* **[jenkins_backup](../jenkins_backup/README.md)** – This role automates backups of the Jenkins Controller’s data. It can be used to periodically create tarball backups of the Jenkins home directory and related data, storing them in `jenkins_backup_dir` and rotating old backups according to `jenkins_backup_keep_days`. In the repository’s Jenkins playbooks, the **jenkins_backup** role is applied to Jenkins controller hosts (for example, via a scheduled playbook or cron job). If you require regular backups of Jenkins configuration and job history, consider using this role in conjunction with **jenkins_controller**.
* **Base/System roles** – Although not specific to Jenkins, you might run roles like **base** (baseline system configuration) or security hardening roles before/alongside Jenkins. For instance, ensuring the server has basic security (updated packages, firewall rules via an external role, etc.) is a good practice. The **jenkins_controller** role assumes the system is already basically configured and focuses only on Jenkins itself.
* **Jenkins Casc (Configuration as Code)** – This repository does not have a dedicated role for Jenkins CasC, but since the **configuration-as-code** plugin can be installed via this role, you might manage CasC YAML through other means (another playbook or template). Keep in mind that if you use CasC, you should deploy the `jenkins_casc.yml` config file to `${jenkins_home}` (usually under a path like `/var/lib/jenkins/jenkins.yaml`) and set the environment variable or Jenkins argument to point to it. You could extend this role or create a small task to copy CasC config as needed.

Each of the above roles has its own documentation in this repository. They are designed to work together: for example, you would run **jenkins_controller** on the master node(s) and **jenkins_agent** on any agent nodes in the same Ansible play or in separate plays (as shown in the `playbooks/jenkins/site.yml` structure). Using the backup role is optional but highly recommended to protect your Jenkins data. By combining these roles, you can deploy a full Jenkins ecosystem: controllers, agents, and backup routines, all managed via code.
