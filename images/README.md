Hardened Image Playbooks

This folder contains Ansible playbooks to bake hardened “golden images” for common node types. Each playbook applies a shared hardening baseline and then installs/configures the target service(s).

How to run locally (packer/CI friendly)
- Use the provided localhost inventory and run one playbook at a time:
  - `ansible-playbook -i images/inventory/localhost.ini images/postgresql-node/playbook.yml`
- To open the service ports via UFW during bake, pass: `-e image_open_service_ports=true`

Baseline applied
- `infrastructure.shared.update_system`
- `infrastructure.shared.remove_unnecessary_packages`
- `infrastructure.shared.sshd`
- `infrastructure.shared.ufw` (service ports optional)
- `infrastructure.shared.base`

Notes
- These playbooks favor install-time configuration but avoid environment-specific secrets. Supply environment-specific values later (cloud-init, first-boot Ansible, or inventory vars).
- Keepalived and HAProxy deploy valid, minimal configs. Tune their variables (VIPs/backends) per environment.

