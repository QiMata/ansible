# Ansible Role:## Overview

The **Letsencrypt Setup** role installs and configures the Certbot client (for Let's Encrypt) on a host, obtains an SSL/TLS certificate for a given domain, and sets up automated renewals. It supports two challenge methods for certificate issuance: **HTTP-01 (webroot)** and **DNS-01 (using GoDaddy's DNS API)**. This role will **install necessary packages**, **request a certificate from Let's Encrypt**, and **create a cron job** for renewing certificates. It does *not* configure your web server or application to use the certificate (that should be done in your web server's role or playbook), but it leaves the certificate files in place for you to reference. Key capabilities include:

> **Note:** Variables for this role now follow the `security_identity_letsencrypt_setup_` prefix to satisfy ansible-lint checks. Existing playbooks that use the legacy variable names (`letsencrypt_setup_domain_name`, `letsencrypt_setup_email_address`, etc.) continue to work because the role maps them to the new names internally.

## When to Use This Role vs. Alternative

This repository contains two Let's Encrypt roles for different use cases. Choose the appropriate one based on your requirements:

| Feature | letsencrypt_setup (This Role) | letsencrypt_godaddy |
|---------|-------------------------------|-------------------|
| **ACME Client** | Certbot (official) | acme.sh (lightweight) |
| **Domain Support** | Single domain | Multiple domains/SAN certificates |
| **Challenge Methods** | HTTP-01 (webroot), DNS-01 (GoDaddy) | DNS-01 only (GoDaddy) |
| **DNS Providers** | GoDaddy (extensible to others) | GoDaddy only |
| **Dependencies** | Ubuntu PPA packages | Git clone only |
| **Complexity** | Simple configuration | Advanced features |
| **Wildcard Certificates** | Yes (DNS-01 only) | Yes |
| **Installation Method** | APT packages via PPA | Direct script installation |
| **Best For** | Simple single-domain setups, users preferring official tools | Multi-domain certificates, minimal dependencies |

**Use this role when:**
- You need a single domain certificate
- You prefer the official Certbot client
- You want HTTP-01 challenge support (port 80 accessible)
- You plan to extend to other DNS providers later

**Use letsencrypt_godaddy when:**
- You need multiple domains on one certificate
- You require wildcard certificates
- You prefer lightweight installations without PPAs
- HTTP challenge is not possible (firewall restrictions)tsencrypt Setup

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

The **Letsencrypt Setup** role installs and configures the Certbot client (for Let’s Encrypt) on a host, obtains an SSL/TLS certificate for a given domain, and sets up automated renewals. It supports two challenge methods for certificate issuance: **HTTP-01 (webroot)** and **DNS-01 (using GoDaddy’s DNS API)**. This role will **install necessary packages**, **request a certificate from Let’s Encrypt**, and **create a cron job** for renewing certificates. It does *not* configure your web server or application to use the certificate (that should be done in your web server’s role or playbook), but it leaves the certificate files in place for you to reference. Key capabilities include:

- HTTP challenge is not possible (firewall restrictions)

## Key Features

* **Certbot installation:** Adds the official Certbot PPA repository and installs Certbot along with the GoDaddy DNS plugin (if needed) via apt. This ensures the latest Certbot version and required dependencies are present on Debian-based systems.
* **Flexible challenge modes:** Obtains a Let’s Encrypt certificate either by using an HTTP webroot challenge or a DNS challenge. For GoDaddy-managed domains (`use_godaddy: true`), it uses the **certbot-dns-godaddy** plugin to create and clean up DNS TXT records automatically. If `use_godaddy` is false, it uses the **webroot** method, placing a challenge file in the specified `webroot_path` for Let’s Encrypt to verify.
* **Idempotent operation:** The role is safe to re-run. It will not re-request a certificate if one already exists for the domain (the certificate request command uses a `creates` flag pointing to the certificate’s private key path). Package installation and repository setup tasks also only run as needed. Re-running the role will simply verify the certificate is in place or skip tasks if already done.
* **Automatic renewal scheduling:** Installs a cron job (running as root) to renew certificates daily at 2:30 AM, ensuring continued validity. The renewal job runs `certbot renew --quiet` to silently renew any certificates nearing expiration. This helps maintain HTTPS availability without manual intervention.
* **Minimal external requirements:** The role requires either a working web server (for webroot validation) or access to GoDaddy’s DNS API (for DNS validation). It does not install a web server itself, but it will place challenge files into your existing document root if using webroot. No changes are made to DNS records except transient TXT records during DNS validation (when using GoDaddy API).

By using this role, you can quickly automate obtaining Let’s Encrypt certificates for your servers. Combine it with your web server role (to deploy the certificate to, say, Nginx or Apache) for a fully automated HTTPS setup. The diagram below illustrates the high-level flow of this role’s operations, from installing dependencies to certificate issuance and renewal setup:

```mermaid
flowchart TD
    subgraph "Let's Encrypt Setup Role"
    A[Install Certbot<br/>and dependencies] --> B{Challenge Method?}
    B -- DNS (GoDaddy) --> C[Copy API credentials<br/>to godaddy.ini]
    C --> D[Run certbot DNS challenge<br/>(--dns-godaddy)]
    B -- HTTP (Webroot) --> E[Ensure webroot path<br/>exists (if needed)]
    E --> F[Run certbot webroot challenge<br/>(--webroot)]
    D --> G[Certificate obtained<br/>(/etc/letsencrypt)]
    F --> G[Certificate obtained<br/>(/etc/letsencrypt)]
    G --> H[Install cron job for<br/>auto-renewal]
    end
    style H fill:#cff,stroke:#333,stroke-width:1px,color:#000
```

## Supported Operating Systems/Platforms

This role is designed for **Debian-based Linux distributions**, since it uses the APT package manager and PPA repositories. Specifically, it supports:

* **Ubuntu** – tested on Ubuntu 20.04 LTS (Focal) and Ubuntu 22.04 LTS (Jammy). It should work on other Ubuntu/Debian versions that support Certbot’s PPA.
* **Debian** – Debian 10 (Buster) and 11 (Bullseye) are supported in principle, though you may need to adjust repository steps (the role adds the Ubuntu Certbot PPA which is primarily intended for Ubuntu systems). On Debian, Certbot may also be available via backports or Snap.
* **Raspbian/Other Debian derivatives** – Should work if the system uses `apt` and is compatible with Ubuntu’s certbot repository. Extra care might be needed for architecture-specific packages.

**Not supported:** RHEL/CentOS, Amazon Linux, or other non-Debian OS families are not supported out-of-the-box. The tasks use apt and assume a Debian/Ubuntu environment. Attempting to run on YUM/dnf based systems will fail. (You could adapt the role by replacing package installation steps for other distros, but that is outside the scope of this role.)

## Role Variables

The main variables configurable for this role are defined in its **defaults/main.yml**. Users should override these in their playbook inventory or `-e` extra vars as needed. The table below lists each variable, its default value, and a description of its purpose:

| Variable                 | Default Value               | Description                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------ | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`domain_name`**        | `"your_domain"`             | **Domain name** for which to obtain the certificate. This should be the fully qualified domain (e.g. `"example.com"`). If you need a wildcard certificate (e.g. `*.example.com`), you must use the DNS challenge (set `use_godaddy: true`) because Let’s Encrypt requires DNS-01 for wildcards.                                                                                                           |
| **`email_address`**      | `"your_email"`              | Email address for Let’s Encrypt registration and urgent renewal notices. Let’s Encrypt will send expiration reminders here. Use a valid email that you monitor.                                                                                                                                                                                                                                           |
| **`godaddy_api_key`**    | `"your_godaddy_api_key"`    | GoDaddy API key for DNS challenge. **Required if** `use_godaddy: true`. This is the “API Key” part of a GoDaddy production API key pair. You can obtain it from GoDaddy’s developer console. It should be kept secret (consider using Ansible Vault for this value).                                                                                                                                      |
| **`godaddy_api_secret`** | `"your_godaddy_api_secret"` | GoDaddy API secret corresponding to the above key. **Required if** using the GoDaddy DNS challenge. Together with the API key, this allows the role (via Certbot) to create and remove DNS records in your GoDaddy DNS zone for domain validation. Keep this secret safe.                                                                                                                                 |
| **`use_godaddy`**        | `true`                      | Boolean toggle to choose the challenge method. **`true` = use DNS-01 via GoDaddy**, **`false` = use HTTP-01 webroot**. By default it’s `true` (assuming GoDaddy DNS). Set this to `false` if you want to use the webroot file-based challenge. When `false`, the `godaddy_api_key/secret` are not used, and the role will expect an HTTP server to be serving the `webroot_path`.                         |
| **`webroot_path`**       | `"/var/www/html"`           | Filesystem path that will be used for the webroot challenge (if `use_godaddy` is `false`). Certbot will create a temporary file under `WEBROOT_PATH/.well-known/acme-challenge/` for Let’s Encrypt to verify the domain over HTTP. This should correspond to the document root of your website for the domain. For example, if using Nginx or Apache, ensure this path is correct for the domain’s vhost. |

**Notes:** If using the DNS challenge (`use_godaddy: true`), ensure the `godaddy_api_key` and `godaddy_api_secret` are set to your GoDaddy production API credentials. The role copies these into a protected credentials file at `~/.secrets/certbot/godaddy.ini` (owner-readable only) for Certbot to use. If using the webroot method (`use_godaddy: false`), make sure that the `webroot_path` exists on the target host and is served by a running web server (the role does **not** start a web server). You can override `webroot_path` if your site’s root is different.

## Tags

This role does not define any fine-grained task tags internally – all tasks will run by default when the role is executed. However, you can use the role name as a tag when running playbooks to specifically include or exclude this role. For example, running `--tags letsencrypt_setup` (if the role is tagged in the play) will run all tasks in this role, and conversely `--skip-tags letsencrypt_setup` will skip it.

* **`letsencrypt_setup`** – Tag applied to the role inclusion (if you specify it in your playbook). Use this tag to run *only* this role or to skip it during larger playbook runs. (By default, if you include the role without any tag filtering, all its tasks execute.)

There are no “required” tags that must be provided for this role to function – tagging is purely optional and for organizational purposes.

## Dependencies

**Ansible Collections:** This role has no external Galaxy role dependencies and relies only on Ansible built-in modules. All modules used (e.g. `ansible.builtin.apt`, `apt_repository`, `copy`, `command`, `cron`) are part of Ansible Core 2.14+. You do not need to install any additional collections for this role. (Ensure you run Ansible on a Debian-based host so that the apt modules are available and applicable.)

**System Packages:** The role will automatically install the necessary system packages on the target host using apt. These include:

* `software-properties-common` – ensures the `add-apt-repository` command is available (required to add the Certbot PPA).
* **Certbot and plugin:** `certbot` (the Let’s Encrypt client) and `python3-certbot-dns-godaddy` (the Certbot DNS plugin for GoDaddy). These are installed from the Ubuntu PPA to obtain the latest versions. If `use_godaddy` is false, the DNS plugin isn’t strictly needed, but it’s installed by default; it’s harmless if unused (it just won’t be invoked).
* The role also uses the system’s **cron** service to schedule renewals (the `cron` Ansible module is used, but it assumes the cron daemon is present, which is true on virtually all Ubuntu/Debian systems).

**External requirements:**

* For **webroot challenge**: a running web server (e.g., Nginx or Apache) serving the `webroot_path` over HTTP. The role doesn’t install or configure any web server. You must ensure that HTTP (port 80) is open and directed to the host, and that the specified webroot directory corresponds to the served site content. Let’s Encrypt will connect to `http://<domain>/.well-known/acme-challenge/...` to verify the challenge.
* For **DNS challenge**: a GoDaddy API key/secret with permission to modify DNS for your domain. No additional software is required beyond the `python3-certbot-dns-godaddy` plugin (installed by the role). Ensure the API credentials are correct and **for production** (GoDaddy’s OTE/test credentials will not work against Let’s Encrypt’s production endpoint).

In summary, there are no Ansible role dependencies or custom plugins required. Just ensure your target system is Debian/Ubuntu with internet access (to download packages from the PPA and to reach Let’s Encrypt’s servers or GoDaddy’s API).

## Example Playbook

Here is a minimal example of how to use the `letsencrypt_setup` role in an Ansible playbook. This example shows the role configuring a certificate via the webroot method (HTTP challenge):

```yaml
- name: Obtain Let's Encrypt certificate for my site
  hosts: webservers
  become: true  # ensure we have root privileges for package install and cert tasks
  vars:
    domain_name: "example.com"              # Replace with your domain
    email_address: "admin@example.com"      # Your email for Let's Encrypt notices
    use_godaddy: false                     # Use webroot challenge
    webroot_path: "/var/www/html"          # The webroot path served by your webserver for this domain
  roles:
    - role: letsencrypt_setup
```

In the above playbook, the role will install Certbot, use the webroot at `/var/www/html` to place a challenge file, and obtain a certificate for **example.com**. Make sure that your web server is serving the `example.com` site from `/var/www/html` and that port 80 is accessible.

**Using the GoDaddy DNS challenge:** If your domain’s DNS is hosted on GoDaddy and you want to use the DNS-01 challenge (for example, to obtain a wildcard certificate or because the host may not serve HTTP), set `use_godaddy: true` and provide your GoDaddy API credentials. For example:

```yaml
- hosts: webservers
  become: true
  vars:
    domain_name: "example.com"
    email_address: "admin@example.com"
    use_godaddy: true
    godaddy_api_key: "YOUR_GODADDY_API_KEY"
    godaddy_api_secret: "YOUR_GODADDY_API_SECRET"
  roles:
    - role: letsencrypt_setup
```

It’s recommended to **store your API key and secret securely** (for instance, in an Ansible Vault or as encrypted variables) rather than plain text. When using the DNS method, the role will add the necessary TXT record in GoDaddy for validation and remove it afterward automatically. You do not need a web server in this case, and Let’s Encrypt will validate via DNS. Ensure the API key/secret are valid *production* credentials and that your GoDaddy account has API access enabled.

## Testing Instructions

This role includes a Molecule test scenario (typically under `molecule/default`). You can test the role locally using Molecule with Docker to verify that it installs packages and configures the certificate tasks correctly. Below are some basic instructions to run the tests:

1. **Install Molecule** (and Docker): Ensure you have Molecule and its Docker driver installed in your Python environment. For example, use `pip install molecule[docker]` to get started, and have Docker running on your machine.
2. **Navigate to the role directory**: Go into the `roles/letsencrypt_setup` directory of this repository (where the Molecule config is located).
3. **Run Molecule converge**: Execute `molecule converge -s default`. This will instantiate a Docker container (based on a supported OS, e.g., Ubuntu 20.04) and apply the role to that container. Molecule will use the variables defined in `molecule/default/converge.yml` (if present) or the role defaults for the test run.
4. **Verify results**: After converge, you can check the container to ensure the certificate was obtained or at least that Certbot was installed and attempted to run. You might shell into the container (`molecule login -s default`) to inspect `/etc/letsencrypt` or the presence of cron jobs, etc. (In automated tests, you might not actually hit Let’s Encrypt’s servers – often a staging environment or dummy domain is used to avoid real DNS/HTTP challenges.)
5. **Run the full test (optional)**: You can run `molecule test -s default` to perform the entire test cycle: create -> converge -> verify -> destroy. If you have written verification tests (e.g., in `molecule/default/verify.yml` or using Testinfra), this will run them. By default, this role’s Molecule might just ensure the playbook runs without errors. Always use Let’s Encrypt’s staging environment or dummy data in tests to avoid hitting rate limits or needing real DNS entries during CI.

**Sample commands:**

* `molecule create -s default` – creates the Docker instance.
* `molecule converge -s default` – applies the role to the instance (you can rerun this to test idempotence).
* `molecule verify -s default` – runs any verification steps (if defined).
* `molecule destroy -s default` – cleans up the container.
* **Or** simply `molecule test -s default` to run all the above in sequence (and destroy at the end).

Ensure you have internet connectivity in the test container; the role will need to apt-get packages and contact Let’s Encrypt (unless you’ve modified it to use a stub or dry-run mode for testing). In a CI environment, you might set `use_godaddy: false` and use a dummy domain that resolves to the test container, or use Let’s Encrypt’s staging servers (though this role does not currently expose a staging flag). Always monitor the output for any failed tasks.

## Known Issues and Gotchas

* **GoDaddy API limitations:** If using the DNS challenge with GoDaddy, be aware that as of 2024 GoDaddy has imposed restrictions on their production API for certain accounts. Users with personal accounts (fewer than 50 domains) might encounter HTTP 403 Forbidden errors when Certbot tries to use the API. This is due to GoDaddy requiring higher-tier service for API usage. If you see errors during the DNS challenge, consider:

  * Using Let’s Encrypt’s **staging environment** for testing (unfortunately, this role does not have a built-in staging toggle for Certbot; you would have to manually modify the Certbot command to add `--staging` for test runs to avoid rate limits and API issues).
  * Upgrading your GoDaddy plan or contacting GoDaddy to enable API access.
  * As a workaround for certain cases, you could manually create the required `_acme-challenge` DNS record if the automated method fails, but that defeats the automation benefit.
* **Webroot challenge requirements:** When using `use_godaddy: false`, ensure that the `domain_name` DNS actually points to the server where you run this role. Let’s Encrypt’s CA will connect to the host via HTTP on port 80. If you have a firewall or security group, **port 80 must be open** to the internet for the challenge. If you’re using the **Base** role or UFW firewall, make sure to allow HTTP traffic (and HTTPS for your site) – otherwise the challenge will time out. Also, the specified `webroot_path` **must exist** and be served by your web server. The role does not create the webroot directory; if it’s missing, Certbot may fail to create the challenge file. You can create the directory (e.g., `/var/www/html`) in advance or via another role/task if needed.
* **No service reload or integration:** This role obtains the certificate and key, but **does not restart or reload your web server or other services** to pick up the new certificate. You need to integrate that step separately. For example, after obtaining the cert, your Nginx or Apache role should be configured to use `/etc/letsencrypt/live/your_domain/fullchain.pem` and `privkey.pem`. After the first run of this role, you may need to reload the webserver to start serving the new certificate. Similarly, on renewal, you’ll need a hook or another mechanism to reload services (Let’s Encrypt’s `--deploy-hook` option or a separate Ansible task) if you want zero downtime certificate updates.
* **Single-domain focus:** The `letsencrypt_setup` role as currently designed issues a certificate for **one domain at a time** (the `domain_name` value). It doesn’t natively support multiple SANs or a list of domains in one certificate. If you require a certificate covering multiple domains or subdomains, you have a couple of options: (a) run this role multiple times with different `domain_name` for each domain, or (b) use the **letsencrypt_godaddy** role (see Related Roles below) which can handle a list of domains in one go. Wildcard certificates (`*.example.com`) are supported only via DNS challenge, and you should include the base domain as well if needed (e.g., many setups need both `example.com` and `*.example.com` on the same cert – this role doesn’t handle multiple `-d` flags, so consider using an alternate approach for that scenario).
* **Let’s Encrypt rate limits:** When obtaining certificates from the production Let’s Encrypt servers, remember there are rate limits (e.g., 5 certificates per domain per week, etc.). This role will not request a new certificate if one is already present (to avoid unnecessary renewals on every run). However, if you are testing repeatedly, you could hit rate limits if you keep changing the domain or forcing issuance. Use the staging environment for tests whenever possible. Unfortunately, to use staging with this role, you’d have to modify the Certbot command in the tasks (adding `--staging`), as there is no variable toggle. Keep this in mind if you plan to run integration tests or multiple trial runs.
* **Idempotence and manual renewals:** Because the certificate request command in this role skips if the cert files already exist, re-running the playbook won’t renew an already-obtained certificate. This is by design (so that plays can be re-run any time without triggering needless re-issuance). Certbot’s own renewal via cron is the intended mechanism for renewal. If for some reason you need to force renewal or reissue (e.g., you lost the private key or need to switch from staging to production), you’ll have to either delete the existing certificate from `/etc/letsencrypt` or run Certbot manually with the `--force-renewal` flag. Simply re-running the role won’t do it, due to the `creates` safeguard.
* **GoDaddy plugin execution environment:** The role copies your API credentials to `~/.secrets/certbot/godaddy.ini` with secure permissions and then runs Certbot with `--dns-godaddy` as root. Certbot will use the credentials file for the DNS challenge. If the playbook remote user is not root, that `~/.secrets` path might refer to a different user’s home. In most cases, this role is run with `become: true` for the Certbot command, so effectively it runs as root and uses root’s home directory. Ensure that the home directory (`~`) for the *privileged user running certbot* contains the `.secrets/certbot/godaddy.ini` file. If you run into an error like “No credentials file found,” it could be due to the file being placed in a non-root home. Running the whole role with `become: true` (as shown in the example) will avoid this issue.
* **Time synchronization:** Let’s Encrypt validations can fail if your server’s time is grossly incorrect (rare, but worth noting). This role doesn’t install NTP or chrony – it assumes the system clock is reasonably accurate. It’s generally a good practice to have time synchronization (e.g., chrony or systemd-timesyncd) enabled on servers for many reasons, including SSL/TLS validity checks.

## Security Implications

This role makes several changes to the system that have security implications which users should be aware of:

* **Installation of external packages and repositories:** The role adds the Certbot PPA (Personal Package Archive) to your system. This is an external software source (maintained by Certbot’s developers) and the role does this to ensure the latest Certbot is available. The PPA is generally trustworthy for obtaining Certbot on Ubuntu, but adding any external repository means you are trusting that source. The role then installs packages `certbot` and `python3-certbot-dns-godaddy` from that PPA. If you prefer not to trust this external repository, you would need to obtain Certbot by other means. Also note that package installation is done as root, which is expected and necessary but means a compromise of that repository could affect your system.
* **Root privilege usage:** Many tasks in this role run with elevated privileges. Installing packages, writing to `/etc/letsencrypt`, and adding cron jobs all require root access. The example playbook uses `become: true` for the role, and certain tasks explicitly elevate (the certificate generation commands and cron task use `become: true` in the role). This is normal for system-level changes, but ensure you limit the role to trusted hosts and understand that it will have full root access while running.
* **API credentials handling:** If using the DNS challenge, your GoDaddy API credentials are sensitive secrets. The role places them in `~/.secrets/certbot/godaddy.ini` and restricts the file mode to `0600` (only readable by the owner). This is a good security practice. However, those credentials will reside on the server. An attacker who gains root access to the server could read the API key and potentially tamper with your DNS records. Treat the API key with the same care as you would a password. Remove the credentials file if you ever decommission the server. The role marks the certbot task with `no_log: true` when using acme.sh in the other role (to avoid printing secrets), and while this role’s Certbot command doesn’t echo secrets (since they are in the file), be cautious about debug output. The API key and secret themselves should not appear in logs, but be mindful if you add verbosity or modify tasks.
* **Certificate and key storage:** The obtained certificates and private keys are stored under `/etc/letsencrypt/live/<domain>/` (with the actual keys in `/etc/letsencrypt/archive/`). By default, Let’s Encrypt sets permissions such that only root (and possibly a specific group like `ssl-cert` on Debian) can access the private keys. This means your webserver (running as root or via a privileged helper) can read them, but normal users cannot. This is a security feature. Ensure you do not loosen the permissions on these files. Anyone with read access to the private key could impersonate your site. The cron renewal job runs as root and will also respect these permissions.
* **Cron job**: The role adds a cron job that runs daily as root to execute `certbot renew`. This is generally safe and recommended practice from a security standpoint (automated renewals prevent expired certificates which could cause service disruption). The job runs with `--quiet` to avoid email spam. One implication is that if renewal fails (e.g., if port 80 is closed at renewal time or DNS changes), you might not immediately notice. It’s good to periodically check `certbot renew --dry-run` or monitor `/var/log/letsencrypt/renewal.log` to ensure renewals happen. Security-wise, running certbot as root is standard since it needs to bind to port 80 (for HTTP challenge) or edit DNS (for DNS challenge) and access the key files.
* **Firewall and access**: Obtaining a certificate via webroot requires that your server be reachable on port 80 by Let’s Encrypt’s validation servers. This means you need to allow inbound HTTP to your server (at least during the initial challenge, and ideally always if you want to redirect to HTTPS). If you have a strict firewall (UFW, iptables, etc.), this is an opening that needs to be managed. If you use the **Base** security role (which configures UFW and Fail2Ban), be sure to allow port 80/443 through that firewall for Let’s Encrypt and general web traffic. It’s possible to only allow the validation servers or proxy (like Cloudflare IPs) if you know them, but generally Let’s Encrypt uses a wide range of IPs. Failing to allow port 80 will result in failed challenges. From a security perspective, serving HTTP (even if you redirect to HTTPS) is a minor increase in surface area, but the benefits of automated cert renewal typically outweigh this. If absolutely necessary, you could use DNS validation to avoid opening port 80.
* **No persistent processes**: This role itself does not run any long-lived service (Certbot is invoked on-demand and via cron). It doesn’t introduce a constantly listening daemon aside from the cron schedule. Certbot will spawn the `certbot` process during renewal which contacts Let’s Encrypt and then exits. Ensure your system has the resources to handle that periodic task (it’s lightweight).
* **System modifications summary**: To recap, this role will modify your system by: adding an apt repo and GPG key, installing packages, writing files to `/etc/letsencrypt` and `~/.secrets/certbot/`, and writing a line to root’s crontab. All these are typical for enabling Let’s Encrypt on a server. As with any infrastructure-as-code, review the changes if needed and run in a test environment first if you have strict security compliance requirements.

Overall, when properly used, this role should **increase** security by enabling HTTPS with automatically renewed certificates. Just be mindful of how secrets are stored and the necessity of allowing validation traffic.

## Cross-Referencing

This repository contains other roles that are related to or can complement the **letsencrypt_setup** role in various scenarios:

* **[letsencrypt_godaddy](../letsencrypt_godaddy/README.md)** – *Alternative Let’s Encrypt via GoDaddy (acme.sh)*. This role is a close cousin to `letsencrypt_setup`. It automates obtaining and renewing Let’s Encrypt certificates using the GoDaddy DNS API, but does so via the **acme.sh** client instead of Certbot. It supports multiple domains (a list of `cert_domains`) including wildcard certificates, and can be useful if you need more flexibility or want to avoid the Certbot PPA. Essentially, `letsencrypt_godaddy` is tailored for GoDaddy DNS challenges as well, but using a different ACME tool under the hood. If your use case involves many subdomains or you prefer acme.sh’s lightweight approach, you might consider that role. Keep in mind, however, that it may not integrate the same way (it might store certs in a different path or require different handling of renewals). For most simple single-domain cases on Ubuntu, `letsencrypt_setup` (Certbot) is perfectly fine.
* **[cloudflare](../cloudflare/README.md)** – *Cloudflare DNS and settings management.* If your DNS is hosted on Cloudflare instead of GoDaddy, the Cloudflare role can automate managing your DNS records and security settings via Cloudflare’s API. While we don’t have a dedicated “letsencrypt_cloudflare” role, you can achieve a similar DNS-01 automation by installing the Certbot Cloudflare DNS plugin (`python3-certbot-dns-cloudflare`) and using Certbot in a manner similar to what this role does for GoDaddy. In fact, the Cloudflare role’s documentation notes that the `letsencrypt_setup` role could be extended to use Cloudflare’s DNS challenge by using the appropriate plugin. In practice, that means you would set `use_godaddy: true` (to trigger DNS flow) but substitute the plugin and credentials for Cloudflare – which is a customization not built-in here. Alternatively, you could manually obtain a cert using Cloudflare’s DNS challenge. The bottom line: if you are using Cloudflare for DNS, you’ll use this **letsencrypt_setup** role with `use_godaddy: false` (webroot) or adapt it for Cloudflare’s DNS. The **Cloudflare** role itself is complementary in that it can ensure your DNS records are correctly in place (A/AAAA records for your domain pointing to your server) before or after you obtain the cert. Also, if you enforce **“Strict HTTPS”** in Cloudflare, you’ll definitely need a valid cert on your origin – which is exactly what this role provides. So using Cloudflare’s role and this Let’s Encrypt role together can automate both DNS setup and certificate provisioning for a secure deployment.
* **[base](../base/README.md)** – *Baseline Server Hardening*. The Base role is a security-focused role that configures firewall rules (UFW), Fail2Ban, and other hardening measures on your servers. While not directly related to obtaining certificates, it plays a crucial part in overall security. For example, Base can set up a firewall – you will need to allow ports 80 and 443 through that firewall for Let’s Encrypt and general web traffic. Base also handles SSH hardening, user setup, etc. In context with this role, ensure that if Base is applied, you configure its variables to allow HTTP/HTTPS as needed. The Base role doesn’t conflict with letsencrypt_setup; rather, it complements it by locking down everything else. Running Base across your servers and then using letsencrypt_setup for certificates is a common pattern for a secure configuration. (In Cloudflare’s docs, they note how Base sets up UFW and you might restrict traffic to Cloudflare’s IPs for web traffic for extra security. If you go that route, just remember Let’s Encrypt validation might also need access, unless you’re only allowing Cloudflare which does proxy the validation in certain configurations).
* **Application or Web Server roles** – After obtaining a certificate, you typically will use it in a web service. Roles in this repository such as **nginx**, **apache**, or specific web application roles (for example, if you have roles like `apache_airflow`, `keycloak`, etc.) will need to know about or be configured to use the certificates from `/etc/letsencrypt`. There isn’t a single dedicated “web server configuration” role here to point to, but keep in mind the integration step: your web server’s config (managed by its role or playbook) should point to the Let’s Encrypt certificate paths. For instance, an Nginx role might have a template for the server block where you’d set `ssl_certificate` to `/etc/letsencrypt/live/{{ domain_name }}/fullchain.pem` and `ssl_certificate_key` to the `privkey.pem`. Ensure you reload or restart the web server after the certificate is obtained (the letsencrypt_setup role does not do that for you). If you have multiple application roles that need certificates, you can either run this role for each one or use the more advanced `letsencrypt_godaddy` role for a SAN certificate, depending on your needs.

Each of the roles mentioned has its own documentation. Combining them effectively is up to your infrastructure needs. For example, you might run **Base** on all servers for security, use **letsencrypt_setup** (or `letsencrypt_godaddy`) to issue certificates for each web-facing server, use **Cloudflare** to update DNS records pointing to those servers, and then deploy your application roles (which consume the certificates and serve your apps). This way, you achieve a secure-by-default setup: hardened servers (Base), valid certificates (LetsEncrypt roles), and proper DNS and CDN/WAF configuration (Cloudflare).

## Variable Naming Considerations

For consistency across both Let's Encrypt roles in this repository, consider these variable naming conventions when using both roles:

**Current variables:**
- This role: `domain_name` (single), `email_address`
- letsencrypt_godaddy: `cert_domains` (list), `letsencrypt_account_email`

**Standardized approach:**
```yaml
# For single domain (this role)
letsencrypt_domains: ["example.com"]  # Could replace domain_name
letsencrypt_email: "admin@example.com"  # Could replace email_address

# For multiple domains (letsencrypt_godaddy)
letsencrypt_domains: ["example.com", "www.example.com"]  # Already cert_domains
letsencrypt_email: "admin@example.com"  # Could replace letsencrypt_account_email
```

This would make switching between roles easier and provide a more consistent user experience.
