# Packer runner container based on official image
# The repository will be bind-mounted at /workspace at runtime

# Use Packer 1.8.x which supports legacy builder binaries (packer-builder-*)
FROM hashicorp/packer:1.8.7

WORKDIR /workspace

# Ensure plugin path is consistent and writable
ENV PACKER_PLUGIN_PATH=/root/.packer.d/plugins

# Install Docker CLI (for docker builder) and Ansible (for ansible provisioner)
RUN set -eux; \
		if [ -f /etc/alpine-release ]; then \
			apk add --no-cache docker-cli ansible openssh-client git go; \
		elif command -v apt-get >/dev/null 2>&1; then \
			apt-get update; \
			DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl gnupg ansible openssh-client git golang unzip; \
			if apt-get install -y --no-install-recommends docker.io 2>/dev/null; then \
				true; \
			else \
				apt-get install -y --no-install-recommends docker-cli || true; \
			fi; \
			rm -rf /var/lib/apt/lists/*; \
		else \
			echo "Unsupported base image for installing docker cli" >&2; \
			exit 1; \
		fi

# Attempt to install Telmate Proxmox LXC packer plugin (build from source)
RUN set -eux; \
  mkdir -p /root/.packer.d/plugins/github.com/Telmate/proxmox; \
  if command -v go >/dev/null 2>&1; then \
    export GOPATH=/root/go; \
    mkdir -p "$GOPATH"; \
    git clone --depth 1 https://github.com/Telmate/packer-proxmox /tmp/packer-proxmox || true; \
    if [ -d /tmp/packer-proxmox ]; then \
      cd /tmp/packer-proxmox; \
      go mod download || true; \
      # Build legacy builder binary discoverable as 'proxmox' (packer-builder-proxmox)
      go build -o /usr/local/bin/packer-builder-proxmox . || true; \
      chmod +x /usr/local/bin/packer-builder-proxmox || true; \
    fi; \
  fi; \
  true

# Default command is inherited (packer)
