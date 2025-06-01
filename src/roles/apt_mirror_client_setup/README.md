# apt_mirror_client_setup Ansible Role

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

The **apt_mirror_client_setup** role reconfigures Debian/Ubuntu client machines to use a specified APT package mirror instead of the default upstream repositories. It replaces the system’s main APT sources list with entries pointing to your internal or custom mirror, then updates the package list cache. By doing so, all subsequent package installations and updates on the client will be pulled from the mirror (typically for faster, more controlled updates in an isolated environment). This role is designed to be minimal and **idempotent** – it will only modify the sources list if needed and run an `apt-get update` to refresh package indexes.

Common use cases for this role include corporate or lab environments where a local APT mirror (for example, one set up using the companion **apt_mirror** server role) is used to conserve bandwidth or ensure availability of packages even without Internet access. After deploying your mirror server, you apply **apt_mirror_client_setup** to each target host to flip its APT configuration to the mirror URL (e.g. pointing to `http://<your-mirror-server>/mirror/…` in place of the standard archive URLs). The role does **not** install any additional software on the client; it simply updates configuration and triggers a cache update.

## Supported Operating Systems/Platforms

This role is tested on and supported with the following Linux distributions (64-bit):

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)

> **Note:** Target hosts must be Debian-based systems using the `apt` package manager. This role will **not** work on RPM-based or non-APT distributions (e.g. CentOS, RHEL, Alpine) since it specifically manages APT configuration.

## Role Variables

Below is a list of the variable that can be configured for this role, along with its default value (defined in **`defaults/main.yml`**) and a description:

<!-- markdownlint-disable MD033 -->

<details>
<summary>Role Variables (defaults)</summary>

| Variable             | Default Value                | Description                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`apt_mirror_url`** | `http://your-apt-mirror-url` | Base URL of the APT mirror server that clients should use for package downloads. This should include the protocol (`http://` or `https://`) and any path prefix required to reach the mirror’s repository root. For example: `http://mirror.example.com/mirror` (if using the default Apache alias from the **apt_mirror** role). All entries in the generated `/etc/apt/sources.list` will use this URL as the base. |

</details>

Typically, you will override `apt_mirror_url` in your inventory or playbook to point to your own mirror. **No other variables are needed** for this role; it automatically detects the client’s OS and release to construct the appropriate APT sources list.

## Tags

This role does **not** define any Ansible task tags internally. All tasks run whenever the role is invoked by default. (You may apply your own tags at the playbook level if you need to include or skip this role under certain conditions, but there are no built-in tags within the role.)

## Dependencies

* **Ansible Version:** Requires Ansible **2.13** or higher (the role uses standard modules and syntax available in modern Ansible releases, and it was developed alongside other roles requiring 2.13+ for consistency).
* **Collections:** None. All modules used (e.g. `ansible.builtin.template`, `ansible.builtin.apt`) are part of Ansible Core, so no additional Galaxy collections are needed.
* **External Packages:** No specific external packages are required on the control node. The target nodes must, of course, have the APT package manager available (which is inherent on Debian/Ubuntu). The role assumes that the system’s default APT keys (for official repositories) are already present; if your mirror includes custom repositories or requires additional GPG keys, ensure those keys are installed on the clients separately (this role does not handle GPG key management).

## Example Playbook

Below is an example of how to use the `apt_mirror_client_setup` role in a playbook. This example reconfigures client hosts to use an internal APT mirror at **`http://apt-mirror.internal/mirror`** (replace this URL with the actual address of your mirror server):

```yaml
- hosts: clients
  become: yes
  vars:
    apt_mirror_url: "http://apt-mirror.internal/mirror"
  roles:
    - apt_mirror_client_setup
```

In the above playbook, the role will template the file `/etc/apt/sources.list` on all hosts in the **`clients`** group to use the specified `apt_mirror_url`, then run an apt update to refresh the package cache. Ensure that **`become: yes`** is set, as modifying system package sources and updating caches requires root privileges.

If your mirror server was set up using the **apt_mirror** role, the URL typically includes the `/mirror` path as shown (unless you configured a custom alias). After running this play, you can immediately test package operations on the client (e.g. `apt-get upgrade` or `apt install <package>`) to confirm they are pulling from your mirror.

## Testing Instructions

It is recommended to test this role using **Molecule** (with the Docker driver) to verify idempotence and correctness before using it in production. A basic testing workflow might look like:

1. **Install Molecule and Docker:** Make sure you have Molecule installed (e.g. via `pip install molecule[docker]`) and a working Docker runtime on your development machine.
2. **Initialize a test scenario:** If a Molecule scenario is provided with this role (e.g. in `molecule/default/`), you can use that. Otherwise, create a new scenario for this role:

   ```bash
   molecule init scenario -r apt_mirror_client_setup -d docker
   ```

   This will set up a default Molecule configuration using Docker containers. You may need to edit the generated `molecule/default/converge.yml` to include any required variables. For example, set `apt_mirror_url` to a reachable mirror for the test (see next step).
3. **Configure a test mirror source:** For testing in isolation, you have a couple of options:

   * **Use a public mirror:** You can point `apt_mirror_url` to an official mirror (like `http://archive.ubuntu.com/ubuntu`) or a country mirror. This essentially replicates the default sources, but it ensures the role still makes changes and that the apt update will succeed online.
   * **Use a local test mirror:** If you have the **apt_mirror** role’s mirror server running in a container or VM accessible to the test container, use its URL. For example, you might run a mirror container and then set `apt_mirror_url` to that container’s IP (and port/path if different).
     Update the Molecule scenario’s playbook to include the chosen `apt_mirror_url` so that the container will use a valid source.
4. **Run the role in a container:** Execute Molecule to apply the role:

   ```bash
   molecule converge -s default
   ```

   Molecule will launch a fresh Docker container (by default using a Debian or Ubuntu base image) and run the `apt_mirror_client_setup` role inside it. The tasks will template the sources list and update the cache.
5. **Verify the results:** After the converge, check that the container’s APT configuration is updated. You can do this by opening a shell in the container (`molecule login -s default`) and inspecting `/etc/apt/sources.list` – it should contain your `apt_mirror_url` in all entries. Also, you can run `apt-get update` (if it wasn’t run) or `apt-cache policy` to ensure no errors and that the repository is recognized. If you have automated tests (e.g., with Testinfra or Inspec), you can run `molecule verify` to execute them. For example, a Testinfra test might assert that the content of `/etc/apt/sources.list` matches the expected mirror URLs.
6. **Cleanup:** Once testing is done, tear down the test container with `molecule destroy -s default`. You can also run the full test cycle (create, converge, verify, destroy) in one go with `molecule test`.

Using Molecule for testing helps ensure the role performs as expected (e.g., idempotently updating the sources file and not producing errors) on a fresh system. During testing, it’s a good idea to run the role at least twice on the same container to confirm idempotence – the second run should report zero changes (if `apt_mirror_url` remains the same and the mirror is reachable).

## Known Issues and Gotchas

* **Mirror Reachability:** The client must be able to reach the specified `apt_mirror_url` over the network. If the URL is wrong, the mirror server is down, or networking is blocked, the APT update will fail. Double-check DNS names or IP addresses and ensure any firewalls allow access to the mirror. A quick way to test reachability is to `curl` or `ping` the mirror URL from the client hosts before applying this role.
* **Repository Availability Match:** Ensure the mirror contains all the repository components that the client expects. The template used by this role will typically include main release, updates, and security repositories for the client’s distribution. If your mirror was configured (via the **apt_mirror** role or otherwise) to skip certain components (for example, you mirrored only “main” and “universe” but not “multiverse”, or you omitted security updates), you should adjust the client configuration accordingly. Missing repositories on the mirror will cause `apt-get update` to complain about “Failed to fetch” errors. In such cases, either include those components in your mirror or remove/alter those entries in the client’s sources list template.
* **Overwriting Default Sources:** This role **replaces** the default `/etc/apt/sources.list` file. Any custom repository entries that were manually added to that file will be lost when the template is applied. However, the role does **not** touch files under `/etc/apt/sources.list.d/`. So if you have additional APT sources defined in separate files (e.g., for third-party PPAs or other software), those will remain active. Keep in mind that those external sources will continue to fetch from their original locations unless you also mirror them or update those files separately.
* **Mirror Outage or Lag:** When all clients rely on a single mirror, a downtime or out-of-date mirror can impact your environment. If the mirror server goes offline or hasn’t synced recently, clients might be unable to install packages or may install older versions. It’s wise to have a contingency plan: for example, maintain a secondary mirror for failover, or a procedure to quickly switch clients back to official repositories (perhaps by reverting this role’s changes or pointing `apt_mirror_url` to a public mirror temporarily) during emergencies.
* **HTTP vs HTTPS Mirrors:** By default, apt-mirror and this role assume an HTTP mirror (the apt-mirror utility typically syncs from and serves via HTTP). Using HTTP internally is usually fine (APT still verifies package signatures), but be aware that traffic is unencrypted. If your environment mandates encryption, consider setting up HTTPS on your mirror server and use an appropriate `apt_mirror_url` (e.g. `https://mirror.example.com/...`) along with deploying the mirror’s SSL certificate to clients (or using a trusted CA). Also note that if you use a self-signed certificate or an internal CA, clients will need the CA certificate installed to avoid TLS errors. This goes beyond the default scope of this role (which doesn’t handle certificate trust), but is important for security in sensitive environments.

## Security Implications

This role makes a system-level change by altering where the system gets its software updates, which has several security considerations:

* **Trust in Mirror Content:** After applying this role, the client trusts that the mirror server provides the correct packages. The good news is that APT will still check package integrity using GPG signatures. As long as the mirror is an exact copy of official repos (or another trusted source) and the client has the appropriate signing keys (e.g., Debian or Ubuntu archive keys), packages installed from the mirror are verified in the same way as if they came from official servers. **However,** if the mirror is compromised or serves tampered content, clients could be at risk. Treat your mirror server as a critical piece of infrastructure: secure it properly and limit access to it.
* **Elevation of Privilege:** The role runs with `become: yes` (root) on the client, since it modifies `/etc/apt/sources.list` and runs package index updates. These are normal administrative actions on a Linux system. The template operation and apt update do not in themselves introduce security holes, but you should review the template (in `templates/sources.list.j2`) if you have modified it, to ensure no unintended repositories or malicious content is introduced.
* **No New Services or Ports:** This role does not install any new daemon or open any network ports on the client. It only affects outbound package fetching behavior. From a firewall perspective, after the role runs, the client will make outbound HTTP/HTTPS requests to the mirror server (instead of to the public mirrors). Ensure your network settings allow clients to reach the mirror on the required port (e.g., 80 or 443).
* **Use of HTTP:** As noted above, using an HTTP mirror means traffic is not encrypted. While package integrity is still verified, an attacker in a position to sniff traffic could see what packages a host is downloading or potentially perform a denial-of-service by interfering with the connection. If this is a concern, move to HTTPS for the mirror distribution.

In summary, switching to an internal mirror centralizes trust and bandwidth to that mirror. Keep the mirror secure and updated, and your clients will remain as secure as they would be with direct official updates.

## Related Roles

* **apt_mirror:** For setting up the server-side APT repository mirror, see the **apt_mirror** role in this repository. That role installs and configures an apt-mirror service (and an Apache HTTP server to host the mirror) on a designated server. The **apt_mirror_client_setup** role (this document) is intended to be used in tandem with it, to point client machines to the mirror. You can find more details in the [apt_mirror role’s README](../apt_mirror/README.md), including how to configure what gets mirrored and various advanced options.
