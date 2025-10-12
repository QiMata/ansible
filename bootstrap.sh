#!/usr/bin/env bash
set -euo pipefail

# Ensure pipx is available (existing pip/pipx setup lines)
python3 -m pip install --user --upgrade pipx

# Ensure pipx is on PATH in this shell
pipx ensurepath

# Install the Ansible dev bundle (ansible-core, ansible-lint, molecule, etc.)
pipx install --include-deps ansible-dev-tools

# Project layout
mkdir -p ./src/collections ./src/roles ./src/inventory

# Install Galaxy deps into ./src so lint/molecule can resolve them
ANSIBLE_GALAXY_DISPLAY_PROGRESS=true \
ansible-galaxy collection install -r ./src/requirements.yml -p ./src/collections
