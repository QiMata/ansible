# Rocket.Chat Role

This document describes the `rocket_chat` Ansible role which deploys a
single-instance Rocket.Chat server on Debian hosts. The role installs
Node.js, downloads a specified Rocket.Chat release, and configures the
application as a systemd service. It is suitable for development or small
installations. For production clustering, extend the inventory and MongoDB
configuration accordingly.

## Usage

Add hosts to the `rocketchat` group and apply the role:

```yaml
- hosts: rocketchat
  become: true
  roles:
    - rocket_chat
```

Customize variables such as `rocket_chat_version`, `rocket_chat_mongo_url`,
and `rocket_chat_root_url` via inventory or extra vars.
