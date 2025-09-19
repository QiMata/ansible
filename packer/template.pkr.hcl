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
  image  = var.base_image
  discard = true
}

build {
  sources = [
    "source.docker.ubuntu"
  ]

  provisioner "shell" {
    inline = [
      "apt-get update",
      "DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 python3-pip python3-venv ca-certificates curl git ansible",
      "rm -rf /var/lib/apt/lists/*"
    ]
  }

  // Run the requested playbook using ansible-local inside the container
  provisioner "ansible-local" {
    // Copy full repo ansible tree into the guest and execute
    playbook_dir  = "${path.root}/../src"
    playbook_file = "${path.root}/../src/${var.playbook_file}"

  // Generate a minimal inventory targeting localhost (adds 127.0.0.1 to these groups)
  inventory_groups = ["all"]

    // Optional flags from the caller
    extra_arguments = concat(var.become ? ["--become"] : [], var.ansible_extra_args)
  }
}
