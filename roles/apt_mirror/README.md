# apt_mirror Ansible Role

Modular, idempotent role for hosting a Debian/Ubuntu `apt-mirror`
served over Apache HTTP. Supports:

* Multiple distributions / components / architectures  
* Scheduled sync via cron  
* Automatic pruning (`clean` lines)  
* Optional ELK shipping, DR backups, HA stubs  
* Simple vs. Complex deployment via `deployment_profile`  

## Quick Start

```bash
ansible-playbook playbooks/deploy_apt_mirror_simple.yml  # dev/test
ansible-playbook playbooks/deploy_apt_mirror_complex.yml # prod
```

## Variables

See `defaults/main.yml` and `group_vars/mirror.yml` for full list.

---
