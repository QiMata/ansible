// Packer template to run an Ansible playbook from this repo using the Docker builder

packer {
  required_version = ">= 1.10.0"

  required_plugins {
    docker = {
      source  = "github.com/hashicorp/docker"
      version = ">= 1.0.9"
    }
    ansible = {
      source  = "github.com/hashicorp/ansible"
      version = ">= 1.0.5"
    }
  }
}

variable "base_image" {
  type        = string
  description = "Base Docker image to provision"
  default     = "ubuntu:22.04"
}

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

source "docker" "ubuntu" {
  image   = var.base_image
  discard = true
}

build {
  sources = [
    "source.docker.ubuntu"
  ]

  provisioner "shell" {
    inline = [
      "apt-get update",
      "DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 python3-pip python3-venv ca-certificates curl gnupg git ansible",
      "rm -rf /var/lib/apt/lists/*"
    ]
  }

  // Prepare workspace directory for uploaded content
  provisioner "shell" {
    inline = [
      "mkdir -p /opt/workspace"
    ]
  }

  // Upload the repo context used by Ansible
  provisioner "file" {
    source      = "${path.root}/../src"
    destination = "/opt/workspace/src"
  }

  // Install Galaxy deps (roles + collections) if requirements.yml exists
  provisioner "shell" {
    inline = [
      "if [ -f /opt/workspace/src/requirements.yml ]; then ANSIBLE_CONFIG=/opt/workspace/src/ansible.cfg ansible-galaxy role install -r /opt/workspace/src/requirements.yml -p /opt/workspace/src/roles || true; ANSIBLE_CONFIG=/opt/workspace/src/ansible.cfg ansible-galaxy collection install -r /opt/workspace/src/requirements.yml -p /opt/workspace/src/collections || true; fi"
    ]
  }

  // Execute the requested playbook inside the container with Ansible
  provisioner "shell" {
    inline = [
      "ANSIBLE_CONFIG=/opt/workspace/src/ansible.cfg ANSIBLE_ROLES_PATH=/opt/workspace/src/roles ANSIBLE_COLLECTIONS_PATHS=/opt/workspace/src/collections ansible-playbook /opt/workspace/src/${var.playbook_file} -i 'localhost,' -c local --become"
    ]
  }
}
