#!/bin/bash

# Set variables from environment or use default values
WORK_DIR="${WORK_DIR:-${HOME}/dev/workspace/qimata}"
ANSIBLE_WORK_DIR="${ANSIBLE_WORK_DIR:-${WORK_DIR}/qimata-ansible/ansible}"
SSH_PRIVATE_KEY="${SSH_PRIVATE_KEY:-ansible-dev_id_rsa}"
SSH_KEY_DIR="${SSH_KEY_DIR:-${HOME}/dev/workspace/qimata/ssh/ansible}"
REMOTE_USER="${REMOTE_USER:-ansible}"
ANSIBLE_VAULT_DIR="${ANSIBLE_VAULT_DIR:-${WORK_DIR}/vault}"
ANSIBLE_VAULT_PASSWORD_FILE="${ANSIBLE_VAULT_PASSWORD_FILE:-vault_pass.txt}"
ANSIBLE_HOST_KEY_CHECKING="${ANSIBLE_HOST_KEY_CHECKING:-False}"
ANSIBLE_IMAGE="${ANSIBLE_IMAGE:-ansible:latest}"

# Display configuration (optional)
echo "Configuration:"
echo "  WORK_DIR: ${WORK_DIR}"
echo "  ANSIBLE_WORK_DIR: ${ANSIBLE_WORK_DIR}"
echo "  SSH_PRIVATE_KEY: ${SSH_PRIVATE_KEY}"
echo "  SSH_KEY_DIR: ${SSH_KEY_DIR}"
echo "  REMOTE_USER: ${REMOTE_USER}"
echo "  ANSIBLE_VAULT_DIR: ${ANSIBLE_VAULT_DIR}"
echo "  ANSIBLE_VAULT_PASSWORD_FILE: ${ANSIBLE_VAULT_PASSWORD_FILE}"
echo "  ANSIBLE_HOST_KEY_CHECKING: ${ANSIBLE_HOST_KEY_CHECKING}"
echo "  ANSIBLE_IMAGE: ${ANSIBLE_IMAGE}"
echo

# Execute Docker with parameterized variables
docker run -it \
  -v "${ANSIBLE_WORK_DIR}:/ansible" \
  -v "${ANSIBLE_VAULT_DIR}/${ANSIBLE_VAULT_PASSWORD_FILE}:/vault_pass.txt" \
  -v "${SSH_KEY_DIR}/${SSH_PRIVATE_KEY}:/ansible_id_rsa" \
  -e SSH_PRIVATE_KEY="/ansible_id_rsa" \
  -e REMOTE_USER="${REMOTE_USER}" \
  -e ANSIBLE_HOST_KEY_CHECKING="${ANSIBLE_HOST_KEY_CHECKING}" \
  -e ANSIBLE_VAULT_PASSWORD_FILE="/vault_pass.txt" \
  --rm "${ANSIBLE_IMAGE}" \
  ansible-playbook "$@"
