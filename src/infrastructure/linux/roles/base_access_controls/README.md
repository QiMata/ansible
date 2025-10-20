# Base Access Controls

This role provisions baseline administrative accounts and sudo hardening for Linux hosts. It can create standardized admin groups, ensure administrator accounts exist with SSH keys, and install a sudoers drop-in that enforces logging and configurable privilege escalation behavior.

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `base_access_controls_admin_group` | `admin` | Primary Unix group for administrative accounts. |
| `base_access_controls_sudo_group` | `sudo` | Group granted sudo privileges in the drop-in policy. |
| `base_access_controls_accounts` | `[]` | List of dictionaries describing administrative accounts to manage. Each item supports keys like `name`, `state`, `shell`, `primary_group`, `groups`, `ssh_authorized_keys`, and more. |
| `base_access_controls_default_shell` | `/bin/bash` | Default shell assigned to created accounts. |
| `base_access_controls_manage_authorized_keys` | `true` | Whether to manage SSH authorized keys declared for each account. |
| `base_access_controls_sudo_nopasswd` | `false` | When `true`, grants passwordless sudo privileges to the configured group. |
| `base_access_controls_sudo_logfile` | `/var/log/sudo.log` | Log file path recorded via the sudoers drop-in. |
| `base_access_controls_sudo_log_input` | `true` | Enable sudo I/O logging for commands run by the admin group. |
| `base_access_controls_sudo_log_output` | `true` | Enable logging of sudo command output. |
| `base_access_controls_sudo_passwd_timeout` | `5` | Timeout (in minutes) before sudo re-prompts for a password. |
| `base_access_controls_sudo_extra_directives` | `[]` | Additional raw sudoers directives to append to the drop-in. |

## Example

```yaml
base_access_controls_accounts:
  - name: opsadmin
    comment: Platform Operations
    ssh_authorized_keys:
      - "ssh-ed25519 AAAA..."
```
