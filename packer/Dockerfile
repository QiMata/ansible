# Packer runner container based on official image
# The repository will be bind-mounted at /workspace at runtime

FROM hashicorp/packer:1.11.2

WORKDIR /workspace

# Ensure plugin path is consistent and writable
ENV PACKER_PLUGIN_PATH=/root/.packer.d/plugins

# Install Docker CLI (for docker builder) and Ansible (for ansible provisioner)
RUN set -eux; \
		if [ -f /etc/alpine-release ]; then \
			apk add --no-cache docker-cli ansible openssh-client; \
		elif command -v apt-get >/dev/null 2>&1; then \
			apt-get update; \
			DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl gnupg ansible openssh-client; \
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

# Default command is inherited (packer)
