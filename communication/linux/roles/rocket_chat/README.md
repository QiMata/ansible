# rocket_chat Ansible Role

## Overview

This role installs the Rocket.Chat messaging server on Debian-based systems.
It downloads a specific Rocket.Chat release, installs required Node.js
packages, and sets up a systemd service to manage the application.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `rocket_chat_version` | `"6.13.0"` | Rocket.Chat version to install |
| `rocket_chat_install_dir` | `/opt/Rocket.Chat` | Installation directory |
| `rocket_chat_user` | `rocketchat` | System user running the service |
| `rocket_chat_port` | `3000` | Service listening port |
| `rocket_chat_mongo_url` | `mongodb://localhost:27017/rocketchat` | MongoDB connection string |
| `rocket_chat_root_url` | `http://localhost:3000` | Public URL of the service |

## Example Playbook

```yaml
- hosts: rocketchat
  become: true
  roles:
    - rocket_chat
```
