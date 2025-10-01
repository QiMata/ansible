# Ansible Role: keycloak_realm

## Table of Contents

* [Overview](#overview)
* [Supported Operating Systems & Platforms](#supported-operating-systems--platforms)
* [Role Variables](#role-variables)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues & Gotchas](#known-issues--gotchas)
* [Security Implications](#security-implications)
* [Related Roles](#related-roles)

## Overview

The **keycloak_realm** role automates the creation and management of Keycloak realms and their clients via Keycloak’s Admin REST API. It ensures that specified realms exist (and are enabled or disabled as desired) and that each realm contains the required client registrations. Under the hood, it leverages the Ansible modules `community.general.keycloak_realm` and `community.general.keycloak_client` to perform these tasks. For each realm defined, the role will create or update the realm (with proper display name and enabled state), then iterate through the realm’s clients list to create/update each client with its client ID, public/confidential setting, and redirect URIs. This allows you to declaratively configure SSO realms and applications in your Keycloak or Red Hat Single Sign-On (RH-SSO) server.

## Supported Operating Systems & Platforms

* **Operating Systems:** This role is tested on Debian and Ubuntu Linux distributions (e.g. Debian 11 “Bullseye”, Debian 12 “Bookworm”, Ubuntu 20.04 LTS “Focal”, Ubuntu 22.04 LTS “Jammy”). It should work on any Linux system where Ansible and Keycloak are supported, but the above are the officially supported platforms in this repository.
* **Keycloak Versions:** The role is designed for Keycloak 18+ (modern Quarkus-based distribution) and has been used with Keycloak version 24.0.x. It should equally support Red Hat SSO versions equivalent to these Keycloak releases, as it uses the standard Keycloak REST API. Ensure your Keycloak server is up and reachable on the network before running this role.

## Role Variables

The following variables can be configured for this role (defined in `defaults/main.yml` and expected from inventory):

| Variable                  | Default Value             | Description                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `keycloak_realms`         | `[]` (empty list)         | **Required.** List of realms to ensure present in Keycloak. Each list item is a dictionary describing a realm, with keys such as `name` (realm name), `displayName` (optional display name for the realm), `enabled` (whether the realm is enabled; defaults to true if unspecified), and `clients` (list of client definitions for that realm). See **Example Playbook** below for the structure of this list. |
| `keycloak_admin_user`     | "admin"                 | Admin username for Keycloak’s administration console (the user with privileges to manage realms). By default this is the Keycloak built-in admin account name.                                                                                                                                                                                                                                                  |
| `keycloak_admin_password` | (none – must be provided) | Admin password for the above Keycloak user. **This is required** for the role to authenticate to the Keycloak server (no default is set for security reasons). In practice, you should supply this via inventory or Ansible Vault (e.g. `vault_keycloak_admin_password`).                                                                                                                                       |
| `keycloak_http_port`      | `8080`                    | The HTTP port on which Keycloak is listening for admin requests. This is used to construct the base URL for API calls (e.g. `http://<inventory_hostname>:8080`). Adjust if your Keycloak runs on a non-default port or if using HTTPS (see **Security Implications**).                                                                                                                                          |

**Note:** The role assumes the Keycloak admin realm is `master` and uses the built-in `admin-cli` client for authentication by default (these are defaults of the underlying modules). If your environment uses a different admin realm or client, you may need to override those by customizing the role tasks or using additional module parameters.

## Tags

No specific Ansible tags are applied to tasks in this role. All tasks will run whenever the role is invoked (you cannot selectively skip or run parts of this role via tags, since none are defined).

## Dependencies

**Galaxy Collections:** This role relies on the **Community General** Ansible collection for the Keycloak modules. Make sure the `community.general` collection is installed before running the role. (For example, install with `ansible-galaxy collection install community.general`.)

**Python Libraries:** The Keycloak modules use the Keycloak REST API. Ensure that Python 3 is available on the target host (the Keycloak server) and that the `requests` library (or Ansible’s urllib support) is present to allow HTTPS requests. In most cases, if you have a standard Ansible setup, this will already be satisfied.

**System/Service Requirements:** A running Keycloak or RH-SSO instance **must** be available and configured with an admin user. This role does *not* install Keycloak itself; it only interacts with an existing server. Typically, you would run the **`keycloak`** server installation role (or other installation method) prior to using `keycloak_realm`. Additionally, if Keycloak relies on an external database (e.g., PostgreSQL), that database should be set up and the Keycloak server started before applying this role.

## Example Playbook

Below is an example playbook that demonstrates how to use the `keycloak_realm` role. In this example, we assume Keycloak is already installed (perhaps via a `keycloak` role) on the target hosts, and we want to create a new realm called **“sample-realm”** with a client **“sample-client”**:

```yaml
- name: Configure Keycloak realms and clients
  hosts: keycloak
  become: true
  vars:
    keycloak_admin_user: "admin"                     # Admin username (default is "admin")
    keycloak_admin_password: "MyAdminPassword123"    # Admin password (use Vault in real setups)
    keycloak_http_port: 8080                         # Keycloak HTTP port (if not default)
    keycloak_realms:
      - name: sample-realm
        displayName: "Sample Realm"
        enabled: true
        clients:
          - clientId: sample-client
            publicClient: true
            redirectUris:
              - "https://app.example.com/*"
  roles:
    - role: keycloak_realm
```

In the above playbook:

* We run the role on the hosts in the `keycloak` group (which should point to your Keycloak server(s)).
* We supply the necessary variables: the admin credentials, the Keycloak port, and the desired realms and clients configuration. The `keycloak_realms` list contains one realm named “sample-realm” (enabled and with a display name), and one client “sample-client” configured as a public client with a specified redirect URI.
* When this playbook is executed, the role will log into Keycloak using the provided admin user/password and ensure the **sample-realm** exists (created if absent) and is enabled, then ensure the **sample-client** exists in that realm with the correct settings. The tasks are idempotent, so running the playbook again will not duplicate realms or clients; it will only make changes if something is out of compliance with the specified state.

*(Refer to the repository’s dev playbook for a real-world usage example, where this role is invoked after installing Keycloak and a database client.)*

## Testing Instructions

This role can be tested using **Molecule**, which provides a framework for running ephemeral test instances (e.g., Docker containers or VMs) to verify Ansible roles.

1. **Install Molecule**: If you haven’t already, install Molecule and its Docker driver. For example: `pip install molecule molecule[docker]` (ensure Docker is installed for container-based testing).
2. **Prepare a Test Scenario**: Navigate to the role directory (`roles/keycloak_realm`). If a Molecule scenario is already provided (commonly in a `molecule/` subdirectory), you can use it. If not, you can initialize one with `molecule init scenario -s default -r keycloak_realm -d docker` to create a default scenario (this step creates a `molecule/default/` scenario configuration).
3. **Run the Tests**: Execute `molecule test` from the role directory. This will perform the full test cycle: create instances, apply the role, run verifications, and then destroy the instances. You can also run steps individually:

   * `molecule converge` – create the instance(s) and apply the role.
   * `molecule verify` – run any verification scripts or checks (if configured).
   * `molecule destroy` – tear down the test instance(s).
4. **Inspect & Debug**: If the convergence fails or you want to inspect the instance state, run `molecule login` to drop into a shell on the test container/VM. This is useful for debugging the Keycloak server state after the role has run.

When writing Molecule tests for this role, consider including the **keycloak** installation role or a Docker image with Keycloak pre-installed, since `keycloak_realm` requires a running Keycloak service. For example, your Molecule playbook might first install Keycloak on the container, then apply `keycloak_realm` to configure realms. Ensure that the `community.general` collection is available in the Molecule environment (you can list it in `requirements.yml` for Molecule to install).

## Known Issues & Gotchas

* **Keycloak Service Availability:** The Keycloak server must be running and accessible at the specified host/port when this role is executed. If the service is down or the host/port is firewalled, the tasks will fail to connect. Ensure that `keycloak_http_port` is correct and that the Ansible target host is the Keycloak server or can reach it over the network.
* **Initial Admin User:** This role does not create the initial Keycloak admin account. You must pre-create the admin user (Keycloak’s built-in admin) and set `keycloak_admin_user`/`keycloak_admin_password` accordingly (commonly done during Keycloak installation). Using incorrect credentials will result in authentication failures.
* **Idempotency and Updates:** The role’s tasks are idempotent. If a realm or client already exists, the modules will update them to match the provided parameters instead of creating duplicates. For example, changing a realm’s `displayName` or a client’s `redirectUris` in `keycloak_realms` and re-running the role will update those settings in Keycloak. However, not all realm/client settings are managed by this role – it covers basic attributes as shown. Advanced settings (e.g., client secrets, roles, realm themes) would require extending the role or using additional modules.
* **Multiple Hosts / Clustering:** In a Keycloak cluster (multiple Keycloak server nodes sharing the same database), you typically only need to apply realm changes once, since all nodes share the realm configuration. If this role is run on all cluster nodes, each node will attempt the same changes. This should not cause errors (the second node would find the realms/clients already present), but to avoid any race conditions, it’s recommended to run the role on one node at a time. For example, the production playbook uses `serial: 1` to apply the role sequentially across the cluster. This ensures one node creates the realms/clients and the rest simply verify them.
* **Default Values Behavior:** Some sub-keys in the realm/client definitions default to sane values if not provided. For instance, if `enabled` is not set for a realm in your `keycloak_realms` list, it defaults to `true` (role logic will assume the realm should be enabled). Similarly, if a client’s `publicClient` is not specified, it defaults to `true` (treated as a public client), and `redirectUris` will default to an empty list if omitted. Keep this in mind: not specifying these keys is equivalent to using those default values.
* **HTTP vs HTTPS:** The role examples use `http://` for the Keycloak URL by default. In production, if Keycloak is served over HTTPS (which is recommended), you should adjust the `auth_keycloak_url` accordingly (e.g., include `https://` and possibly a different port). The underlying modules will by default verify SSL certificates; if you are using self-signed certs, you may need to set an environment variable or module parameter to ignore invalid certs (for example, `ANSIBLE_SKIP_CERT_VALIDATION=True` or `validate_certs: false` in module params). Use caution with disabling cert validation – only do this in controlled environments.

## Security Implications

Managing Keycloak realms and clients is a security-sensitive operation, since it controls your authentication domains and application credentials. Here are important security considerations when using this role:

* **Admin Credentials Protection:** The `keycloak_admin_password` variable is highly sensitive. Never store this password in plain text in source control. It is best to keep it encrypted using Ansible Vault or retrieve it from a secure secrets manager. In this repository, for example, the production inventory uses a vaulted password for the admin user. Treat the admin credentials with the same care as root passwords.
* **Use of HTTPS:** When possible, connect to Keycloak over HTTPS to protect the admin credentials in transit. The role will work with `http://` (as commonly used in development or within a secure network), but in any environment where untrusted network access is possible, configure Keycloak with TLS and adjust `keycloak_http_port`/URL to use HTTPS. This helps prevent eavesdropping of the admin token exchange.
* **Role Privilege:** Only run this role against trusted hosts and with appropriate privileges. It uses high-level access to Keycloak’s admin API. Ensure that the Ansible user/account running the play has permission to reach Keycloak. The role itself does not create or modify system accounts or OS-level settings; all changes are confined to the Keycloak application via API.
* **Realm and Client Settings:** Be mindful of the realm and client configurations you apply:

  * Enabling a realm (`enabled: true`) makes it active for logins. If you create realms for testing or staging, consider disabling them when not in use.
  * For clients, setting `publicClient: true` means the client does not require a secret to obtain tokens (suitable for browser-based apps). If you set `publicClient: false` (confidential client), Keycloak will expect to generate or receive a client secret – ensure you handle that securely (the current role tasks do not explicitly set client secrets).
  * The `redirectUris` for clients should be as specific as possible. Avoid overly broad patterns that could pose an open redirect risk (the example uses `https://app.example.com/*` which assumes trust in the subpath). Always verify that the redirect URIs are correct and safe.
* **Audit and Logging:** Changes made by this role (realm created/updated, client created/updated) will be logged in Keycloak’s audit logs. It’s good practice to monitor these logs to detect any unexpected changes. Only authorized personnel should have the ability to run this automation, as it can create new login portals or alter authentication settings for applications.

In summary, the `keycloak_realm` role should be used in a controlled manner, with secrets protected and a clear understanding of the impact of adding realms/clients to your SSO environment.

## Related Roles

* **Keycloak (Server Installation)** – The `keycloak` role in this repository is responsible for installing and configuring the Keycloak server itself (including setting up the service, database connectivity, and initial admin user). It is typically used in tandem with `keycloak_realm`. For example, you would install Keycloak on a host using the **keycloak** role, then apply **keycloak_realm** to populate realms and clients on that server. (See the playbooks in this repo for how both roles are applied in sequence.)
* **postgresql_client (Database Client)** – If your Keycloak uses a PostgreSQL database, you might see the **postgresql_client** role included prior to Keycloak installation. That role ensures PostgreSQL client libraries or utilities are present (used for database setup or health checks). While not a direct dependency of `keycloak_realm`, it is part of the overall stack in deployments (ensuring Keycloak can communicate with its database).

<!-- You can add links to other roles like LDAP setup or others if applicable in the repository context -->

*For more information on the Keycloak ecosystem roles, refer to the repository documentation or the Ansible Galaxy page of each role. The combination of the Keycloak server role and the Keycloak realm configuration role allows for full automation of your SSO setup.*
