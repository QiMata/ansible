Jenkins Agent Registration (role)

Registers a Jenkins agent (node) on a Jenkins Controller via the HTTP API. Use this after provisioning the agent host (for example with the sibling jenkins_agent role) so the controller can connect to it over SSH.

- Creates a “Dumb” SSH-based node on the controller
- Optionally deletes and recreates an existing node of the same name
- Supports environment variables, tool locations, and launcher tuning

Requirements
- A reachable Jenkins Controller
- Controller credentials available to Ansible
- The agent host already exists and is reachable by the controller via SSH with a configured credentialsId

Key variables (see defaults/main.yml for full list)
- jenkins_agent_registration_controller_host: Controller host (default: groups['jenkins_controllers'][0] or localhost)
- jenkins_agent_registration_controller_port: Controller HTTP port (default: 8080)
- jenkins_admin_user: Admin user (default: admin)
- jenkins_admin_password: Admin password (required)
- jenkins_agent_registration_enabled: Gate to enable the role (default: true)
- jenkins_agent_replace_existing: If true and node exists, delete then recreate (set where needed)
- jenkins_agent_registration_agent_name: Node name (default: inventory_hostname)
- jenkins_agent_registration_agent_description: Default: "Auto-provisioned Jenkins agent"
- jenkins_agent_registration_agent_executors: Default: 2 (inherits if already defined)
- jenkins_agent_registration_agent_remote_fs: Default: jenkins_agent_home or /home/jenkins
- jenkins_agent_registration_agent_labels: Default: "linux auto-provisioned" (inherits if already defined)
- jenkins_agent_registration_agent_usage_mode: NORMAL or EXCLUSIVE (default: NORMAL)
- jenkins_agent_registration_ssh_host: Default: ansible_default_ipv4.address
- jenkins_agent_registration_ssh_port: Default: 22
- jenkins_agent_registration_ssh_credential_id: Default: jenkins-ssh-key (or jenkins_credentials_ssh_key_id if provided)
- jenkins_agent_registration_ssh_java_path, jenkins_agent_registration_ssh_jvm_options, jenkins_agent_registration_ssh_prefix_start_slave_cmd, jenkins_agent_registration_ssh_suffix_start_slave_cmd
- jenkins_agent_registration_retry_wait_time, jenkins_agent_registration_max_num_retries, jenkins_agent_registration_keep_alive_strategy
- jenkins_agent_registration_env_vars: Dict of env vars to attach (default: {})
- jenkins_agent_registration_tool_locations: List of tool locations (default: [])

Idempotency
- Checks if the node exists
- Creates it when missing
- If present and jenkins_agent_replace_existing is true, deletes then recreates
- If present and replace is false, leaves it unchanged

Example
- hosts: jenkins_agents
  become: true
  vars:
    jenkins_admin_user: admin
    jenkins_admin_password: "{{ vault_jenkins_admin_password }}"
    jenkins_agent_registration_agent_name: agent01
    jenkins_agent_registration_agent_executors: 2
    jenkins_agent_registration_agent_labels: "linux amd64"
    jenkins_agent_registration_agent_remote_fs: "/home/jenkins"
    jenkins_agent_registration_ssh_host: "{{ ansible_default_ipv4.address }}"
    jenkins_agent_registration_ssh_port: 22
    jenkins_agent_registration_ssh_credential_id: jenkins-ssh-key
    jenkins_agent_replace_existing: false
  roles:
    - role: devops_cicd/jenkins/jenkins_agent_registration

Notes
- The role fetches a CSRF crumb before write operations
- Ensure the referenced credentialsId exists on the controller
- Adjust host/port for HTTPS or proxies
- For full E2E flows, pair with jenkins_controller and jenkins_agent roles

Testing
This role requires a live controller; prefer end‑to‑end validation with the Proxmox Molecule scenario and Jenkins playbooks in this repository. See src/molecule/proxmox/ and MOLECULE_TESTING_GUIDE.md.