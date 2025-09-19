// Packer template to build a Proxmox LXC template by running an Ansible playbook

packer {
  required_version = ">= 1.10.0"

  required_plugins {
    proxmox = {
      // Telmate Proxmox builder supports LXC
      source  = "github.com/hashicorp/proxmox"
      version = ">= 1.1.6"
    }
    ansible = {
      source  = "github.com/hashicorp/ansible"
      version = ">= 1.0.5"
    }
  }
}

// General playbook variables (repo-relative)
variable "playbook_file" {
  type        = string
  description = "Path to the playbook relative to src/ (e.g. playbooks/base.yml)"
}

variable "ansible_extra_args" {
  type        = list(string)
  description = "Additional args to pass to ansible-playbook"
  default     = []
}

variable "become" {
  type        = bool
  description = "Use become for Ansible tasks (maps to --become)"
  default     = false
}

// Proxmox connection
variable "proxmox_url" {
  type        = string
  description = "Proxmox API URL, e.g. https://pve.example.com:8006/api2/json"
}

variable "proxmox_insecure" {
  type        = bool
  description = "Skip TLS verification for Proxmox API"
  default     = true
}

variable "proxmox_node" {
  type        = string
  description = "Proxmox node name to build on (e.g. pve)"
}

// Auth options: Use either username/password OR token_id/token_secret
variable "proxmox_username" {
  type        = string
  description = "Proxmox username (e.g. root@pam) — leave empty if using token auth"
  default     = ""
}

variable "proxmox_password" {
  type        = string
  description = "Proxmox user password — leave empty if using token auth"
  sensitive   = true
  default     = ""
}

variable "proxmox_token_id" {
  type        = string
  description = "Proxmox API token ID (e.g. packer@pve!token) — leave empty if using password auth"
  default     = ""
}

variable "proxmox_token_secret" {
  type        = string
  description = "Proxmox API token secret — leave empty if using password auth"
  sensitive   = true
  default     = ""
}

// LXC settings
variable "lxc_ostemplate" {
  type        = string
  description = "Base LXC OS template, e.g. local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst"
}

variable "lxc_unprivileged" {
  type        = bool
  description = "Create unprivileged container"
  default     = true
}

variable "lxc_memory" {
  type        = number
  description = "Container memory in MB"
  default     = 1024
}

variable "lxc_cores" {
  type        = number
  description = "vCPU cores"
  default     = 2
}

variable "lxc_swap" {
  type        = number
  description = "Swap size in MB"
  default     = 0
}

variable "rootfs_storage" {
  type        = string
  description = "Rootfs storage (e.g. local-lvm)"
  default     = "local-lvm"
}

variable "rootfs_size" {
  type        = number
  description = "Rootfs size in GB"
  default     = 10
}

variable "network_bridge" {
  type        = string
  description = "Bridge to attach (e.g. vmbr0)"
  default     = "vmbr0"
}

variable "network_firewall" {
  type        = bool
  description = "Enable Proxmox firewall on NIC"
  default     = false
}

variable "features_nesting" {
  type        = bool
  description = "Enable nesting feature for LXC"
  default     = true
}

variable "ssh_username" {
  type        = string
  description = "SSH username to connect (e.g. root)"
  default     = "root"
}

variable "ssh_password" {
  type        = string
  description = "SSH password for the user"
  sensitive   = true
}

variable "lxc_password" {
  type        = string
  description = "Initial root password set inside the LXC (used when ssh_username=root)"
  sensitive   = true
  default     = ""
}

variable "template_name" {
  type        = string
  description = "Final Proxmox LXC template name to save (e.g. ubuntu-22.04-ansible-2025-09-18)"
}

source "proxmox" "lxc" {
  // Connection
  url                        = var.proxmox_url
  insecure_skip_tls_verify   = var.proxmox_insecure
  node                       = var.proxmox_node

  // Auth (one of the two methods)
  username                   = var.proxmox_username != "" ? var.proxmox_username : null
  token_id                   = var.proxmox_token_id != "" ? var.proxmox_token_id : null
  token_secret               = var.proxmox_token_secret != "" ? var.proxmox_token_secret : null

  // LXC
  ostemplate                 = var.lxc_ostemplate
  unprivileged               = var.lxc_unprivileged
  memory                     = var.lxc_memory
  cores                      = var.lxc_cores
  swap                       = var.lxc_swap
  ssh_username               = var.ssh_username
  ssh_password               = var.ssh_password
  ssh_timeout                = "20m"
  start                      = true
  onboot                     = true
  template                   = true
  // Set initial root password inside the LXC so Ansible can SSH as root
  password                   = var.lxc_password != "" ? var.lxc_password : null

  features = {
    nesting = var.features_nesting
  }

  // Storage and rootfs sizing
  storage     = var.rootfs_storage
  // Many Proxmox APIs expect sizes with a unit suffix for LXC (e.g., 10G)
  rootfs_size = "${var.rootfs_size}G"

  // Network defaults to DHCP on eth0 via bridge; explicit configuration can be added if needed

  template_name = var.template_name
}

build {
  sources = [
    "source.proxmox.lxc"
  ]

  // Ensure base packages for Ansible targets
  provisioner "shell" {
    inline = [
      "export DEBIAN_FRONTEND=noninteractive",
      "apt-get update || true",
      "apt-get install -y --no-install-recommends python3 ca-certificates sudo || true"
    ]
  }

  // Run the requested playbook from this repo against the LXC over SSH
  provisioner "ansible" {
    playbook_file = "${path.root}/../src/${var.playbook_file}"

    // Set project context so roles/config resolve correctly
    ansible_env_vars = [
      "ANSIBLE_CONFIG=${path.root}/../src/ansible.cfg",
      "ANSIBLE_ROLES_PATH=${path.root}/../src/roles",
      "ANSIBLE_COLLECTIONS_PATHS=${path.root}/../src/collections"
    ]

    extra_arguments = concat(var.become ? ["--become"] : [], var.ansible_extra_args)
  }
}
