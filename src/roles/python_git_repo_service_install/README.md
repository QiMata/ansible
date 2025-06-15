# Ansible Role: Python Git Repo Service Install

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
* [Related Roles](#related-roles)

## Overview

The **Python Git Repo Service Install** role automates the deployment of a Python application from a Git repository and sets it up as a persistent systemd service on a host. It is a generic role intended for simple Python applications that need to be cloned from source control, installed with Python dependencies, and run continuously as a service. Key tasks performed by this role include:

* **Git-based Deployment:** Clones the application code from the specified Git repository (`python_git_repo_service_install_app_repo`) into the `/opt/{{ python_git_repo_service_install_app_name }}` directory on the target system. You can specify a branch, tag, or commit via `app_version` if needed (defaults to the latest commit on the default branch). This ensures the latest application code is present on the host.
* **Dependency Installation:** Installs required Python packages by running `pip` on the repository's **requirements.txt** file. All Python dependencies listed in that file will be installed into the system environment (no virtual environment is created by default).
* **Service Setup:** Deploys a systemd service unit file for the application using a provided Jinja2 template. The unit file is placed at `/etc/systemd/system/{{ python_git_repo_service_install_app_name }}.service` and defines how to start the app (by default, invoking a Python script like `app.py` in the repo directory).
* **Service Enablement:** Registers the application service with systemd, then starts the service and enables it to auto-start on boot. This means the application will be launched immediately and will also come up automatically after reboots.

```mermaid
flowchart TD
    subgraph "Python App Deployment Role"
    A[Clone Git repository] --> B[Install requirements (pip)]
    B --> C[Template systemd service unit]
    C --> D[Start and enable service]
    end
```

*(Diagram: **Role execution flow** – the role clones the app code, installs its Python dependencies, sets up a systemd unit, and starts/enables the service.)*

In practice, this role provides a quick way to turn a Python project (hosted in a git repository) into a running service on a server. You would provide the repository URL and application name (and optionally version), and the role takes care of fetching the code, installing dependencies, and configuring the service. It's assumed that the application's repository contains an executable script (e.g. `app.py` or similar) and a `requirements.txt` file for its dependencies. After running this role, the application will be running as a background service under systemd, ready to accept requests or perform its tasks continuously. No application-specific configuration beyond what's in the repo is performed by this role – it focuses solely on installation and service setup.

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian-based Linux distributions**, specifically **Debian 11 (Bullseye)**, **Debian 12 (Bookworm)**, **Ubuntu 20.04 LTS (Focal)**, and **Ubuntu 22.04 LTS (Jammy)**. The tasks are written with the assumption of a systemd-based Debian/Ubuntu environment.

Other Linux platforms are **not officially supported** without modification. While the role doesn't use any Debian-specific package managers (it relies only on git, pip, and systemd, which can exist on other distros), running it on Red Hat, CentOS, or other non-Debian systems may require additional preparation. For example, you would need to ensure Python3/pip and Git are installed via the appropriate package manager (`yum`, `dnf`, etc.) and that systemd is present. The role may work on such systems if these conditions are met, but there is no guarantee or testing for those platforms. Using the role on its intended Debian/Ubuntu targets is recommended to avoid compatibility issues.

## Role Variables

<details><summary>**Default Variables (from `defaults/main.yml`)**</summary>

| Variable          | Default Value       | Description |
| ----------------- | ------------------- | ----------- |
| **`python_git_repo_service_install_app_repo`**    | `""` (empty string) | **Git repository URL** of the application to deploy. This should be the full clone URL (HTTPS or SSH) pointing to the Git repo containing your Python application's code. *No default is set* in the role (this is a required variable—you must provide the repo URL). |
| **`python_git_repo_service_install_app_name`**    | `""` (empty string) | **Application name** to use for deployment. This name determines the directory under `/opt` and the systemd service name. For example, if `python_git_repo_service_install_app_name` is `"myapp"`, the code will be cloned into `/opt/myapp` and the service will be named `myapp.service`. *No default is set* (you must specify this name). |
| **`app_version`** | `"HEAD"`            | **Git revision to deploy**. Can be a branch name, tag, or commit SHA. By default it uses `"HEAD"`, meaning the tip of the default branch of the repository. You can pin this to a specific tag or commit (e.g. `"v1.0.0"`) if you want a deterministic deployment version. |

</details>

**Notes on variables:** Both `python_git_repo_service_install_app_repo` and `python_git_repo_service_install_app_name` **must** be provided by the user, as they have no effective default. If these are not set, the role cannot clone the repository or configure the service properly. The `app_version` is optional; if not set, it defaults to the repository's HEAD (latest code). If you want to lock deployments to a particular release, set `app_version` accordingly. Ensure that the `python_git_repo_service_install_app_name` you choose is a valid directory name and service name (stick to alphanumeric and underscores/dashes, without spaces). Also, make sure the `python_git_repo_service_install_app_repo` URL is accessible from the Ansible control machine or target host (for example, if it's a private repo over SSH, set up the necessary SSH keys or credentials).

## Tags

This role does **not define any custom Ansible tags** in its tasks. All tasks will run whenever the role is invoked (there are no task-specific tags to selectively skip or run parts of this role). You can, however, apply your own tags at the play level if you want to include or exclude the entire role during certain runs. For instance, you might tag the role as `deploy_app` in your playbook and then run `--tags deploy_app` to execute it selectively. By default, though, every task in **Python Git Repo Service Install** executes as part of the role without requiring any tag.

## Dependencies

* **Ansible Version:** This role requires Ansible **2.13+** (it has been tested with Ansible 2.13 and above). The tasks use the `ansible.builtin` module namespace and assume features available in modern Ansible releases. Using a recent Ansible ensures compatibility with the `git`, `pip`, and `systemd` modules used by the role.
* **Collections:** No external Ansible Galaxy collections are required by this role. All modules invoked (`git`, `pip`, `template`, `systemd`) are part of Ansible's built-in module set. Just ensure you have run `ansible-galaxy collection install -r requirements.yml` for the repository in general, to install any collections needed by other roles or by Ansible (for example, **community.general** for some modules). The **Python Git Repo Service Install** role itself does not depend on any non-core modules.
* **Software on Target Hosts:** The target host should have **Git** and **Python 3 (with pip)** installed prior to running this role. The role does *not* currently install Git or Python/pip by itself. It expects those to be present (for example, by running the **`common`** role beforehand, which installs pip and other base utilities, and by having Git included in your base system or installed via a separate step). If Git is missing, the repository clone step will fail; if pip is missing, the dependency installation step will fail. Make sure these prerequisites are in place (Debian/Ubuntu users can install them via apt, e.g., `apt-get install git python3-pip` if not using the **common** role).
* **Systemd:** The host must be running **systemd** as its init system. The role will place a unit file and use the `ansible.builtin.systemd` module to manage the service. On Debian/Ubuntu, this is the standard. On containerized systems or minimal installs without systemd, this role cannot enable or manage the service.
* **Network Access:** The target host needs internet access to clone the git repository (unless you use a local/path URL) and to download Python packages from PyPI. Ensure the server can reach the Git server (e.g., github.com or your internal git) and has connectivity to PyPI or your Python package index. If the environment is locked down, you might need to configure proxy settings or mirror repositories.
* **Privilege Escalation:** This role's tasks should be run with **administrator privileges**. In your playbook, set `become: true` (and possibly `become_user: root`) for the play or for this role. Installing files to `/opt` and `/etc/systemd`, as well as installing packages, requires root access on the target system. The role itself does not call `become: true` on each task, assuming you will run the role under an account with the necessary privileges.

## Example Playbook

Below is an example of how to use the `python_git_repo_service_install` role in an Ansible playbook. In this example, we assume a single host (or group) that we want to deploy our application to. We provide the required variables (`python_git_repo_service_install_app_repo` and `python_git_repo_service_install_app_name`) and optionally specify `app_version`. We also ensure we run with `become: yes` to have the necessary privileges for installation tasks:

```yaml
- hosts: my_application_server
  become: yes  # Elevate to root for installation
  vars:
    python_git_repo_service_install_app_name: "myapp"  # Name for the application and service
    python_git_repo_service_install_app_repo: "https://github.com/example/myapp.git"  # Git repository URL
    app_version: "main"  # Branch or tag to deploy (e.g., "main" branch)
  roles:
    - python_git_repo_service_install
```

In the above playbook, replace `my_application_server` with your actual inventory host or group name. The `vars` provide the basic configuration for the role:

* We set `python_git_repo_service_install_app_name` to "myapp" – this means the code will clone into `/opt/myapp` and the systemd service will be named **myapp.service**.
* We specify `python_git_repo_service_install_app_repo` as the HTTPS URL of the git repository. In this case it points to a GitHub repo `example/myapp`. You could use an SSH URL (like `git@github.com:...`) if you have keys set up, or an internal Git server URL as needed.
* We set `app_version: "main"` to deploy the `main` branch of the repository. This could be omitted if you are fine with the default (`HEAD` of default branch), but it's included here for clarity. You might change this to a specific tag like "v1.0.0" for reproducible deployments.

When this play is run, the **Python Git Repo Service Install** role will perform all the steps to get the application running on the host. After the playbook finishes, you should find your application's code in `/opt/myapp`, installed Python packages (system-wide) as listed in the repo's requirements, and a running systemd service `myapp` (enabled to start on boot). You can then visit or interact with the application according to how it's supposed to run (for example, if it's a web service listening on a port, connect to that port; if it's a background worker, check its logs or status via `systemctl status myapp`).

## Testing Instructions

It is highly recommended to test this role using **Molecule** (with Docker) to ensure it works as expected in a clean environment before applying it to production systems. A Molecule test scenario can automatically run the role inside a container and verify outcomes using Testinfra. To run the tests for the **Python Git Repo Service Install** role, follow these steps:

1. **Install Molecule and prerequisites:** On your control machine (where you run Ansible), install Molecule and its Docker driver. You can do this with pip, for example:

   ```bash
   pip install molecule[docker] pytest testinfra
   ```

   Ensure you also have Docker installed and running, as Molecule will use Docker containers for testing. The above command also installs **pytest** and **testinfra**, which Molecule uses for writing and running tests.
2. **Prepare environment:** This role doesn't require any external Ansible roles, but it's good practice to have all required collections installed for the repository. Run `ansible-galaxy collection install -r requirements.yml` in the repository root to make sure collections like **community.general** are present (this covers any module dependencies across all roles). For this specific role, all needed modules are built-in, so no additional role dependencies need to be pulled. If the Molecule scenario for this role uses any supporting roles (for example, it might include the **common** role to ensure pip is installed in the test container), make sure those roles are accessible to Molecule (since all roles are in this repo, Molecule will find them automatically as long as you run it from the repo root).
3. **Run Molecule tests:** Execute the Molecule test for this role by running:

   ```bash
   molecule test -s python_git_repo_service_install
   ```

   This will launch the Molecule scenario named "python_git_repo_service_install". Molecule will build a fresh Docker container (using a Debian-based image, such as Debian 12) and then apply a test playbook to it. The test playbook will include the **python_git_repo_service_install** role (with some test variables for `python_git_repo_service_install_app_name` and `python_git_repo_service_install_app_repo`). During the **converge** step, the role's tasks run inside the container just as they would on a real server. After convergence, Molecule will execute **Testinfra** tests to verify that the role did what it's supposed to. For example, the tests may check that:

   * The application directory exists under `/opt` (e.g. `/opt/myapp` if a dummy python_git_repo_service_install_app_name "myapp" was used).
   * The Git repository content was cloned (e.g. checking for the presence of the expected files from the repo).
   * Python packages were installed (perhaps by importing a known package in the test, or checking pip list).
   * The systemd service unit file is present at `/etc/systemd/system/myapp.service`.
   * The service is enabled and (if systemd is running in the container) maybe that the service would start successfully. (In a Docker container, a full systemd may not be running, so the test might simply ensure the unit file is in place and perhaps simulate starting it.)
     Molecule will then destroy the container. All these steps happen automatically with the `molecule test` command.
4. **Review results:** Check the output of the Molecule run. A successful test will end with an "OK" or similar message after running the verify step, and no failed tasks or tests. If something fails:

   * Use `molecule converge -s python_git_repo_service_install` to rerun the role in the container without tearing it down, so you can inspect the container state. For example, you can then `molecule login -s python_git_repo_service_install` to get a shell inside the container and look around (check files, service status, logs, etc.).
   * Use `molecule verify -s python_git_repo_service_install` to rerun the tests on an existing container if you made changes or want to see test output again.
   * Make adjustments to the role or the test scenario as needed, then run `molecule test` again until it passes. For instance, if the role failed because pip wasn't present, the scenario might need to include the **common** role or you might add a task to install pip in the container for testing.

By running Molecule tests, you gain confidence that the role will perform as expected on a fresh system. It helps catch issues like missing dependencies or syntax errors in a controlled environment. Contributors who modify this role should run the Molecule test scenario to verify they haven't broken functionality. The Molecule configuration for this role (in the `molecule/` directory) can also serve as living documentation of how the role is supposed to be used (with example vars and test assertions about the outcomes).

## Known Issues and Gotchas

* **Service template requires customization:** The provided systemd service template (`templates/app.service.j2`) contains placeholder values that **must be edited for your application**. Notably, the `[Service]` section in the template hard-codes `User=your_username` and `ExecStart=/usr/bin/python3 app.py` as dummy values. You **must** change these to an appropriate system user and execution command for your app. For example, if your app should run under a user `webapp` and is started via a script `server.py` with arguments, you should modify the unit file accordingly (or adjust the template via role variables if you make it more dynamic). As-is, if you do not change it, the service will either run as `your_username` (which likely doesn't exist, causing failure) or as root (if you remove the User line), and it will try to execute `app.py` which may not be the correct entry-point for your application. In short: **review and update the service file** before deploying to production.
* **No automatic user creation:** This role does **not** create a dedicated user to run the application service. It assumes that if you specify a `User=` in the service unit, that account already exists on the system. If you plan to run the app under a non-root account (recommended for security), you need to ensure that user is present. You can handle this by pre-creating the user (for example, using Ansible's `user` module in a prior task or another role, or via the **base** role if it's something that could be included there). If no user is specified in the service file, systemd will run the service as **root**, which is not ideal for application security (see **Security Implications** below).
* **`requirements.txt` is expected:** The role's pip installation task assumes a `requirements.txt` file exists in the root of the repository (cloned to `/opt/{{ python_git_repo_service_install_app_name }}/requirements.txt`). If your application repository does not have this file, the pip task will fail. In case your app has no dependencies or uses a different mechanism, you may need to skip or override this task. A workaround is to include an empty `requirements.txt` in the repo if there truly are no dependencies, just to satisfy the role. Alternatively, you could modify the role to conditionally skip the pip task if the file is absent.
* **Global Python environment usage:** This role installs dependencies into the system's global Python environment (the default `python3` environment on the host). It does **not** set up a virtual environment for the application. This means all packages from `requirements.txt` are installed system-wide. Be cautious if the host has other Python applications – there could be version conflicts or unintended interactions through shared libraries. If isolation is needed, you would have to modify the role (for example, create a venv in `/opt/{{ python_git_repo_service_install_app_name }}/venv` and install there, and adjust the service ExecStart to use that venv's Python). As provided, the role keeps things simple by installing globally, but that may not suit all use cases.
* **Idempotence and updates:** The role is designed to be idempotent (running it twice in a row without changes should result in no changes the second time, except where inherently non-idempotent actions occur like git pull). Notably, if you run the role again after the repository has new commits, the **Git task will pull the updates** (so you'll see a change detected on that task) and the **pip task may install new or updated packages** if the requirements changed. The systemd service task will rewrite the unit file each run, but since it's usually unchanged, it won't trigger a reload unless you actually changed the template or variables. **Gotcha:** The role does **not automatically restart the application service when the code is updated**. If the service is already running and you pull new code, the process may still be running the old code in memory. The role only ensures the service is started (it doesn't issue a `systemctl restart` on code change). To apply updates, you might need to manually restart the service (e.g., via a handler or by running `systemctl restart yourapp` after the role). In future, a handler could be added to restart the service whenever the git repo had changes – but currently that isn't implemented.
* **Private repository access:** If `python_git_repo_service_install_app_repo` points to a private git repository, the role will attempt to clone it using the Ansible `git` module. For this to work non-interactively, you need to have authentication set up. For example, if using an SSH Git URL (`git@...`), ensure the target host (or the user Ansible connects as) has the necessary SSH key and known hosts configured. If using an HTTPS URL that requires credentials, you might need to include those credentials in the URL or configure a `.netrc` on the host. The role itself does not handle authentication prompts. Failure to authenticate will cause the clone task to error. Always test that the Ansible host can clone the repo (e.g., manually or with an ad-hoc task) before running the role in an unattended playbook.
* **Firewall and ports:** The role doesn't open or adjust any firewall settings. If your application listens on a network port (for example, a web app might listen on port 8000 or similar), you may need to ensure that port is allowed through the firewall. If you use UFW or other firewall management (the repository includes a **ufw** role), configure it accordingly *after* this role sets up the service. For instance, if your `myapp` listens on port 8000, you'd want to allow 8000/tcp in UFW so that external clients can reach it. Conversely, if the application is meant to be accessed only locally or on a private network, still be mindful that the port is open on the system (bind address and firewall rules should be set to appropriate scope).

## Security Implications

Deploying an application as a system service involves several security considerations. This role makes changes that could affect the security posture of the system, and it's important to understand and mitigate any risks:

* **Trust of Source Code:** This role pulls code from a Git repository and runs it on your server. **Only use this role with repositories you trust.** If the repository is compromised or the code is malicious, it will have whatever effect the code is designed to have on your server (which could be catastrophic if run as root). It's a good practice to pin `app_version` to a specific known-good commit or release, and to review changes before updating the deployed version. Treat the combination of `python_git_repo_service_install_app_repo` and `app_version` as you would any software source – with the same scrutiny as installing a package from a third-party source.
* **Privilege of the Service Process:** By default (unless you modify the service file), the application might run as **root**, which is dangerous. Running application code with full root privileges means any exploit in the app or dependency can give an attacker control over the entire system. It is strongly recommended to run the service as an unprivileged user. Create a system user (with no shell login) dedicated to the app (e.g., `myapp` user) and update the `User=` in the service unit. Also adjust file permissions (the role doesn't automatically chown the app directory to that user, but you should do so) so that the app can write to where it needs (if it writes files). Ensuring the app runs with least privilege greatly limits the impact if the app is compromised. For example, if running as a user `myapp` with limited rights, an exploit in the app might only allow writing to `/opt/myapp` and not to system directories.
* **Systemd Service Configuration:** The role's systemd unit uses a very basic template. Consider hardening the service unit by adding relevant security settings in the `[Service]` section once you customize it. For instance, you could add `ProtectSystem=full`, `PrivateTmp=yes`, `NoNewPrivileges=yes`, etc., to limit what the service can do. Systemd has many options to restrict the environment of services (chroot directories, capability bounding sets, read-only paths, etc.). These aren't configured by default in the provided template, but you might want to incorporate some if your application will run on sensitive systems. At minimum, ensure the working directory and user/group are set correctly.
* **Network Exposure:** If the application opens a network port (for example, a web API or daemon listening on a socket), be mindful of who can reach that port. The role itself does not configure any firewall, so by default the service's port will be accessible according to the host's existing firewall rules (or lack thereof). Consider using the **ufw** role or other firewall tooling to restrict access. For example, if the app should only be reached by an internal network or load balancer, block the port from public interfaces. Also, ensure the app has its own authentication or encryption as appropriate (the role doesn't manage SSL certificates or credentials).
* **Python Package Integrity:** The pip installation step pulls packages from PyPI (or whatever index is configured on the target host). This means you are downloading code from the internet. To mitigate risks:

  * Use hashed requirements files if possible (pip can verify package hashes).
  * Pin exact versions of your dependencies to avoid unexpected upgrades to potentially vulnerable versions.
  * Optionally, host an internal PyPI mirror or repository and configure pip to use it, to have more control over what packages are installed.
  * Keep the system's pip and setuptools versions up to date (the **common** role installs `python3-pip`, which should be kept updated via system packages).
* **System Changes and Persistence:** This role writes to `/opt` (which is typically a world-readable directory) and to `/etc/systemd/system`. The application files in `/opt/{{ python_git_repo_service_install_app_name }}` will have whatever permissions came from git. You might want to tighten those (for instance, if they include sensitive configs, ensure proper file permissions). The systemd unit file is world-readable by default in `/etc/systemd/system`. If it contains any sensitive information (which it typically should not, and in our case it doesn't), be cautious. Also note that enabling the service means it will persist across reboots – if you remove or change the application, remember to disable or update the service accordingly.
* **Logging and Monitoring:** The role itself doesn't configure any logging for the app beyond what the app does. Systemd will capture the app's stdout/stderr, which you can view with `journalctl -u myapp`. You should consider how to monitor the application's health and logs. If the app fails to start, systemd will try to restart it (since `Restart=always` in the template). Repeated crashes could indicate an issue – ensure you have some monitoring in place to catch if the service is continually restarting or not performing its function. From a security standpoint, monitor the logs for unusual activity (if the app logs incoming requests or errors, those could show attempted exploits, for example).

In summary, this role gives you a convenient deployment mechanism, but it's up to you to **operate the application securely**. Follow best practices: run with least privilege, update regularly, restrict network access, and keep an eye on the application once it's running. All changes made by the role (code and service) should be reviewed in the context of your system's security policies.

## Related Roles

* **common:** Before deploying a custom application, it's often useful to run the **common** role on the host. The common role updates package lists and installs basic tools including Python pip and venv, which are prerequisites for many other roles. Running **common** ensures that when **Python Git Repo Service Install** runs, the system has an up-to-date APT cache and pip is available to install Python packages. In short, **common** prepares the base environment (installing packages like `python3-pip`, `python3-venv`, etc.) so this role can focus on the app itself.
* **base:** For a new server, the **base** role is typically applied early to enforce baseline configuration and security policies. The base role performs tasks like upgrading all packages, removing insecure defaults, and setting up core security services (automatic updates, Fail2Ban, ClamAV, etc.). While not a direct dependency, using **base** (and its constituent hardening roles) in your playbook before deploying applications ensures the system is in a good state (fully patched and secured). After **base** and **common** have run, the system should have necessary components (like Git, if you include it in your base setup) and be hardened, making the app deployment via this role smoother and more secure.
* **ufw:** If you need to manage firewall rules for your application, the **ufw** role can be used. This role configures Ubuntu's Uncomplicated Firewall (UFW) to allow or deny traffic. After deploying the app, you might apply **ufw** to open the specific port your app listens on (e.g., allow inbound TCP on port 8000 for the app, while keeping other ports closed) or to restrict access to that port to certain IP ranges. This is especially important if your application is network-facing; you'll want to ensure only legitimate users can reach it. See the **ufw** role's documentation for how to specify allowed ports and sources.
* **haproxy (load balancer):** Although not directly related to a single app deployment, if you plan to run multiple instances of your application for high availability or scaling, you might consider using the **haproxy** role as a front-end. The haproxy role can set up a load balancer that distributes traffic across multiple application servers running the same app. This goes beyond a single node deployment, but it's worth noting as a pattern: combine **python_git_repo_service_install** (to set up the app on several nodes) with **haproxy** (to distribute traffic among those nodes) for a production cluster. Additionally, the **keepalived_setup** role could be used with haproxy to manage a virtual IP for failover between load balancers (as seen in other parts of this repository).
* **letsencrypt_setup / cert management:** If your application is a web service that needs HTTPS, you may want to use roles like **letsencrypt_setup** to obtain and install TLS certificates, and perhaps configure a proxy (like **nginx** or use haproxy's SSL capabilities) in front of your app. This role doesn't handle TLS at all – it deploys whatever the app is (which might itself handle TLS or not). Refer to the repository's Let's Encrypt roles or web server roles for implementing TLS termination in your stack.

Each of the above roles can complement **Python Git Repo Service Install** in a larger playbook. For example, a typical play might run **base** -> **common** -> **python_git_repo_service_install** (to set up the app) -> **ufw** (to adjust firewall) -> **monitoring roles**, etc. The **Related Roles** mentioned can be found in this same repository; see their READMEs for detailed usage instructions and how they integrate into the overall infrastructure. Using these roles together helps ensure that your custom application is deployed in a robust, secure, and maintainable manner.

