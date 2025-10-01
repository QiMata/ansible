# Ansible Role: Jenkins Agent

*Ansible role to set up a Jenkins build agent (worker node) on a Linux host.*

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

The **Jenkins Agent** role prepares a target server to act as a Jenkins build agent (also known as a Jenkins node). It ensures that a dedicated system user account for Jenkins is present, that Java (OpenJDK 11) is installed on the host, and that the Jenkins Controller’s SSH public key is deployed to the agent for authentication. After running this role, the target host will be ready to be connected to a Jenkins Controller (master) as an agent for running build jobs.

This role is primarily intended for **SSH-based Jenkins agents**, where the Jenkins Controller initiates an SSH connection to the agent to start the Jenkins agent process. (Jenkins’s built-in SSH launch method is used.) The role does *not* automatically register the node in the Jenkins Controller’s configuration – it only prepares the OS environment. You will need to add the agent node in Jenkins (via the GUI or API) and configure it to use the SSH credentials set up by this role. For users who prefer **JNLP (inbound) agents** (where the agent connects out to the controller), note that this role does not handle installing the Jenkins agent JAR or running it as a service; additional steps would be required in that case.

## Supported Operating Systems/Platforms

This role is tested on and supported with the following 64-bit Linux distributions:

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** The target host must be a Debian-based system with the `apt` package manager. The role uses the `ansible.builtin.apt` module to install packages, so Red Hat, CentOS, or other non-APT-based systems are **not supported** without modifications. Ensure you are using a supported OS version to avoid failures. (OpenJDK 11 packages are available by default on the supported Debian/Ubuntu versions listed above.)

## Role Variables

Below is a list of variables configurable for this role, along with their default values (defined in **`defaults/main.yml`**) and descriptions:

<details><summary>Click to see default role variables.</summary>

| Variable                           | Default Value                      | Description                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`jenkins_agent_user`**           | `"jenkins"`                        | Username of the Jenkins agent account to create on the target host. The role will create this user (if it does not exist) with a home directory and login shell. All Jenkins build processes on the agent will run under this user.                                                                                                                                                                                                  |
| **`jenkins_agent_home`**           | `"/home/{{ jenkins_agent_user }}"` | Filesystem path for the Jenkins agent user’s home directory. By default it is under `/home` (e.g. `/home/jenkins`). This is where Jenkins agent runtime files, build workspaces, and logs will reside. Ensure the partition has sufficient space for build artifacts if needed.                                                                                                                                                      |
| **`jenkins_agent_executors`**      | `2`                                | Number of executors (parallel jobs) that this agent is intended to run. This value is used when configuring the agent on the Jenkins Controller side (it tells Jenkins how many concurrent builds the node can handle).                                                                                                                                                                                                              |
| **`jenkins_agent_labels`**         | `"linux"`                          | Labels to assign to this Jenkins agent. This is typically a comma-separated or space-separated string of tags (in this default case, just “linux”). Labels can be used in Jenkins to select this node for certain jobs. (**Note:** This role does not directly use this value in any tasks; it is provided for your reference when adding the node to Jenkins.)                                                                      |
| **`jenkins_agent_ssh_public_key`** | *No default* (required)            | **Required.** The SSH **public** key that will be added to the agent’s authorized keys for the Jenkins Controller. This should correspond to the private key that Jenkins (controller) will use for connecting to the agent. The role places this key in `~jenkins/.ssh/authorized_keys` for the `jenkins` user. If not provided, the role will not complete successfully (this variable must be set in your inventory or playbook). |

</details>

## Tags
The **Jenkins Agent** role prepares a target server to act as a Jenkins build agent (also known as a Jenkins node). It ensures that a dedicated system user account for Jenkins is present, that Java is installed via the distribution’s default JDK package, and that the Jenkins Controller’s SSH public key is deployed to the agent for authentication. After running this role, the target host will be ready to be connected to a Jenkins Controller (master) as an agent for running build jobs.
This role does not define any intrinsic Ansible task tags. All tasks will run whenever the role is invoked. There are no "required" tags that must be set for the role to function.

You can apply your own tags to this role when including it in a play if desired. For example, you might tag the role as `jenkins_agent` in your playbook to allow running or skipping it with `--tags`/`--skip-tags`. But by default, there are no internal tags within the role.

## Dependencies

* **Ansible Version:** This role requires Ansible **2.13** or higher. It relies on standard modules available in ansible-core 2.13+ (e.g. `ansible.builtin.user`, `ansible.builtin.apt`, `ansible.builtin.authorized_key`). Make sure your Ansible installation meets this version requirement.

* **Collections:** No additional Ansible collections are required. All modules used are part of the built-in ansible-core. (For example, the apt module used for package installation is included in ansible.builtin.)

* **Root/Privilege Requirements:** The tasks in this role must run with **root** privileges, since they create a system user and install packages. Ensure your play or inventory uses `become: yes` for the hosts that apply this role.
* **Ansible Version:** This role requires Ansible **2.14** or higher. It relies on standard modules available in ansible-core 2.14+ (e.g. `ansible.builtin.user`, `ansible.builtin.apt`, `ansible.builtin.authorized_key`). Make sure your Ansible installation meets this version requirement.
* **External Packages:** The role will install **OpenJDK 11** on the target system via the OS package manager. An active internet connection or access to an internal package mirror is needed for the package installation (unless the package is already present). If your environment restricts external access, ensure that the appropriate package repository (or offline package) for OpenJDK 11 is available to the target host.

* **External Packages:** The role will install Java using the distribution’s default JDK meta-package (e.g., `default-jdk`). An active internet connection or access to an internal package mirror is needed for the package installation (unless the package is already present). If your environment restricts external access, ensure that the appropriate package repository is available to the target host.

Here is an example of how to use the `jenkins_agent` role in a playbook, preparing a group of hosts as Jenkins agents. This example assumes you have the Jenkins controller’s public SSH key ready to deploy:

```yaml

This repository includes a Dockerized Molecule harness and a Proxmox-backed scenario that provisions a real Debian LXC for validation. Prefer this path for reliable, CI-friendly tests across platforms (including Windows hosts).

1) Configure Proxmox scenario environment
- Copy `src/molecule/proxmox/.env.example` to `src/molecule/proxmox/.env` and fill in your Proxmox API details (host, token/credentials, node, storage, template, container ID/IP, etc.). See `src/molecule/proxmox/README.md` for field descriptions.

2) Run tests via the provided scripts
- Windows PowerShell:

```powershell
# Validate local prerequisites
src\docker\test-setup.ps1

# Build the Molecule tools image (one time or after updates)
src\docker\run-molecule-tests.ps1 build

# Start the tools container
a src\docker\run-molecule-tests.ps1 start

# Run this role's Proxmox scenario end-to-end
src\docker\run-role-tests.ps1 test jenkins_agent proxmox
```

- Linux/macOS:

```bash
# Validate local prerequisites
src/docker/test-setup.sh

# Build the Molecule tools image
src/docker/run-molecule-tests.sh build

# Start the tools container
src/docker/run-molecule-tests.sh start

# Run this role's Proxmox scenario end-to-end
src/docker/run-role-tests.sh test jenkins_agent proxmox
```

3) Notes
- The scenario’s `converge.yml` sets a dummy public key; replace as needed or supply via inventory/vars. The role requires `jenkins_agent_ssh_public_key`.
- Idempotence and verify are part of `molecule test`; logs are available via the orchestrator scripts.
- A local Docker driver scenario may exist, but on Windows hosts the Docker daemon is exposed via a named pipe, not a Unix socket; running the Docker driver inside the tools container can fail without additional setup. Prefer the Proxmox scenario on Windows.
  become: yes
  vars:
* **No SSH Daemon Restart:** Adding an authorized key does not restart `sshd` in this role. The key is effective immediately without a service restart, avoiding disruption of existing SSH sessions.
    # Optional overrides (if defaults need to be changed):
    # jenkins_agent_user: jenkins   # default "jenkins"
* **Java Package Selection:** The role installs Java via the distro’s default JDK meta-package (e.g., `default-jdk`). There is no built-in variable to select a specific JDK version. If you must pin to a specific Java (e.g., OpenJDK 17), adapt the task or introduce your own variable/override to change the package name. Ensure your Jenkins controller and plugins support the chosen Java version.
    # jenkins_agent_labels: "linux" # default "linux"
  roles:
    - jenkins_agent
```

In the above play, we target hosts in the **jenkins_agents** group and elevate privileges with `become`. We provide the required `jenkins_agent_ssh_public_key` (shown here as an example string – use your actual Jenkins controller’s public key). The role will then create the `jenkins` user, install OpenJDK 11, and add the given SSH key to `jenkins`’s authorized keys on each host. After running this playbook on your agent servers, you would proceed to add these nodes to your Jenkins Controller (using the same SSH key for authentication).

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to verify its behavior before using it in a production environment. You can follow these basic steps to run the role in a disposable container:

1. **Install Molecule** and the Docker Python library on your development machine (for example, via pip: `pip install molecule[docker]`). Also ensure Docker is installed and running.

2. **Prepare a test scenario:** If a Molecule scenario is already provided for this role (e.g. in `molecule/` directory), you can use that. Otherwise, you can create one with Molecule:

   ```bash
   molecule init scenario -r jenkins_agent -d docker
   ```

   This will create a `molecule/default/` directory with a basic scenario for the `jenkins_agent` role. After initialization, edit the generated **`molecule/default/converge.yml`** to specify the necessary role variables (at minimum, set `jenkins_agent_ssh_public_key` to a test value, since it’s required). You can use a dummy SSH key for testing purposes.

3. **Run the role in a container:** Execute Molecule to run the role in a container:

   ```bash
   molecule converge -s default
   ```

   Molecule will build a Docker container (by default, using a base image like Ubuntu) and apply the `jenkins_agent` role inside it using the playbook in the scenario (which includes this role). Watch the output to ensure all tasks complete successfully. The tasks should create the user, install Java, and add the SSH key without errors.

4. **Verify the results:** After the converge, you can manually check the container to verify that the role’s changes took effect:

   * Ensure the **jenkins** user exists: `docker exec -it <container_id> id jenkins` should show a valid user and group.
   * Check that Java is installed: `docker exec -it <container_id> java -version` should run and display OpenJDK 11 (confirming the package was installed).
   * Verify the authorized key: `docker exec -it <container_id> cat /home/jenkins/.ssh/authorized_keys` should show the public key you provided.
   * *(Optional)* Run `molecule verify` if you have written any automated tests (e.g. with Testinfra) for additional validation.

5. **Cleanup:** Once testing is done, tear down the test container with:

   ```bash
   molecule destroy -s default
   ```

   Or simply run `molecule test` to perform the full cycle (create, converge, verify, destroy) in one command.

Using Molecule for testing ensures that the role is idempotent (running it again yields no changes) and works on a fresh system as expected. It allows you to experiment with different variable values safely. When testing this role, you might use an ephemeral SSH key for `jenkins_agent_ssh_public_key` (since the key is just for test). Also note that the Docker container will have an SSH service for the `jenkins` user to simulate real conditions – ensure you started the container with SSH or use Molecule’s default container image which includes SSH service.

## Known Issues and Gotchas

* **SSH Key is Required:** Remember to provide the Jenkins controller’s public key via `jenkins_agent_ssh_public_key` when running this role. If this variable is not set, the **authorized_key** task will fail (and the role cannot configure SSH access). There is no default key for security reasons, so you must supply one in your inventory or playbook. Ensure the corresponding private key is configured on the Jenkins controller side (usually as a credential in Jenkins) so that it can authenticate to the agent.

* **Agent Not Automatically Registered:** This role **does not** register the agent with your Jenkins Controller. After the role runs on an agent host, you will still need to go into Jenkins and add a new node (or use an automation script/role on the controller side). Use the same `jenkins` username, and set up the SSH private key credential in Jenkins that matches the public key deployed by this role. Jenkins will then be able to connect to the agent via SSH and launch the agent process. (If using the `jenkins_controller` role from this repo, refer to its documentation on how to handle node registration or credentials.)

* **SSH Service Restart:** Adding the new authorized key triggers a restart of the SSH daemon on the agent host. The role includes a handler to restart `sshd` so that any configuration changes or new keys are recognized immediately. This means that the SSH service on the agent will momentarily restart during the play. In practice, adding keys to `authorized_keys` doesn’t strictly require a restart, but the role calls it to ensure the new user and key are fully applied. Be aware that this could disrupt ongoing SSH sessions to the host (if any). Plan maintenance accordingly, especially if running on an existing server.

* **Operating System Constraints:** As noted, the role uses APT for installation. Attempting to run it on a system that doesn’t have `apt` (e.g. CentOS or Windows) will result in failures. Windows Jenkins agents are not handled by this role. For RedHat-based Linux distributions, you would need to adapt the tasks (e.g. use `dnf`/`yum` to install Java and create the user appropriately). Currently, support is limited to Debian/Ubuntu environments.

* **Java Version Fixed to 11:** The role installs specifically OpenJDK 11 (`openjdk-11-jdk`) by name. This ensures a known Java version is present (Jenkins requires Java 11+ in recent releases). If you require a different Java version (for example, OpenJDK 17 for newer Jenkins or specific build tools), you will need to modify the role or override the package name. There is no built-in variable to toggle the JDK version in this role. Keep in mind that Jenkins 2.357 and above support Java 17, but Java 11 remains a common choice for compatibility. Always verify that your Jenkins controller and plugins are compatible with the Java version installed on the agent.

* **Jenkins User Account:** The `jenkins` user created on the agent has no password set (login is key-based only) and is not given sudo privileges by this role. This is a security feature, ensuring that builds running as `jenkins` cannot elevate to root unless you explicitly configure it outside this role. If your build jobs need root access for certain tasks, consider using sudo with careful restrictions (e.g., editing sudoers for specific commands) or run those steps as part of a different role. By default, the Jenkins agent runs in a constrained user context for safety.

* **Multiple Jenkins Masters:** This role is designed around a single Jenkins Controller’s access. It deploys one public key to the agent. If you have multiple Jenkins controllers that need to use the same agent host (an uncommon scenario), you would need to add additional authorized keys (e.g., by extending the role or running the authorized_key task for each additional key). Also, ensure coordination of executors and job scheduling across controllers to avoid conflicts. In most cases, an agent is dedicated to one Jenkins controller.

* **Firewall and Network:** The role does not open any firewall ports on the agent. If you are using an internal firewall (UFW, firewalld, etc.), you must ensure that the Jenkins controller can reach the agent’s SSH port (TCP 22). Configure your firewall accordingly (for instance, allow inbound SSH from the Jenkins master’s IP). Conversely, if using JNLP mode, ensure the agent can reach the controller on the required port (default TCP 50000 for Jenkins inbound agents). In secure environments, it’s good practice to restrict SSH access on agents to only trusted sources (e.g., the controller).

## Security Implications

* **Least Privilege User:** The role creates a dedicated `jenkins` system account on the agent with limited privileges. All Jenkins jobs on that node run under this account, isolating them from other system services. The user is not given sudo access by this role, which helps enforce least privilege. Administrators should resist adding broad sudo rights to the Jenkins user; if specific elevated actions are needed for builds, grant only those via tightly scoped sudo rules (and consider security implications carefully).

* **SSH Key-Based Access:** By installing the Jenkins controller’s *public* key on the agent, the role enables key-based authentication for Jenkins. No password authentication is used for the `jenkins` user, reducing the risk of brute-force attacks. However, this means the security of the SSH connection is entirely reliant on the private key held by the Jenkins controller. Protect that private key – for example, store it in Jenkins Credentials securely and do not reuse it for other purposes. If the key is compromised, an attacker could gain access to all agents that trust it. It’s advisable to use a unique key pair per controller and rotate keys if needed.

* **Agent Connectivity:** Out of the box, the agent does not run any persistent network service except SSH. In the SSH-based setup, the Jenkins controller will open an SSH session to launch the agent process when needed, then disconnect when jobs are done. This means the attack surface on the agent is minimal (SSH on port 22, which you should secure as you would on any server). If you configure the agent for JNLP (so it continuously runs and connects to the controller), the agent initiates an outbound connection to the controller – ensure your network allows this, and note that the agent will then constantly run the `java` process for the agent. In either case, keep the system’s packages (especially OpenSSH and Java) up to date to patch any security vulnerabilities.

* **File and Directory Permissions:** The role creates the home directory for the Jenkins user (typically `/home/jenkins`) with default permissions. Jenkins job workspaces and any artifacts will be stored under this directory. By default, on most Linux systems, a user’s home is world-readable (0755). Consider tightening this if necessary (e.g., to 0750) to prevent other local users from browsing Jenkins build files. The `.ssh` directory and `authorized_keys` file are created with appropriate permissions by the Ansible module. Always avoid placing sensitive credentials in the agent’s filesystem; use Jenkins Credentials for secrets so that they are not stored in plain text on the agent.

* **Auditing and Monitoring:** Since Jenkins agents can execute arbitrary build steps, treat them as semi-trusted. Monitor the agent’s activity and logs. The `jenkins` user’s actions (via build processes) may be logged in system logs or audit logs. Ensure that your security monitoring includes these hosts. For example, you might want to install intrusion detection or at least ensure the Fail2Ban (set up by the Base role) monitors SSH login attempts on agents. Though the agent’s SSH is key-only, attempts could still occur and should be blocked/alerted if suspicious.

## Cross-Referencing

Other roles and playbooks in this repository that relate to Jenkins or complement the Jenkins Agent role:

* **[jenkins_controller](../jenkins_controller/README.md)** – This role sets up the Jenkins Controller (master) server. It installs Jenkins, configures it as a service, and manages initial setup like plugins or admin user. Use the Jenkins Controller role on your Jenkins master node(s) in tandem with the Jenkins Agent role on your worker nodes. After deploying a controller with that role, you will need to create agent node entries (either manually in the Jenkins UI or via automation) for each host configured with **jenkins_agent**. The two roles together allow you to orchestrate a complete Jenkins environment with Ansible.

* **Base system hardening roles** – It is often a good idea to apply a baseline security role before provisioning a Jenkins agent. In this repository, the **[Base](../base/README.md)** role (and its sub-roles like `update_system`, `fail2ban`, etc.) can be applied to ensure the system is up-to-date and secured. While not a direct dependency, running the Base role on your agents (and controllers) prior to Jenkins setup is recommended for a stable and secure system.

* **Firewall configuration** – If you need to lock down network access on your Jenkins agents, consider using a role such as **UFW** (Uncomplicated Firewall) if available, or another host firewall role. (This repository includes a note about UFW in the Base role documentation.) Proper firewall rules can ensure that only the Jenkins controller or other authorized sources can reach the agent’s SSH port.

Each of the above related roles has its own documentation. Consult those README files for detailed usage. By using the Jenkins Agent role alongside the Jenkins Controller role and appropriate security roles, you can automate a full Jenkins deployment that adheres to best practices in both functionality and security.
