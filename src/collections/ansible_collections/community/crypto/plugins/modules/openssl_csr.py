#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Minimal stub of community.crypto.openssl_csr for ansible-lint offline usage.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: openssl_csr
short_description: Stub module for ansible-lint argument validation
version_added: "0.0.1"
description:
  - Provides a minimal interface compatible with community.crypto.openssl_csr.
options:
  path:
    description:
      - Destination path for the CSR file.
    type: path
    required: true
  privatekey_path:
    description:
      - Path to the private key used to sign the CSR.
    type: path
    required: true
  subject:
    description:
      - Subject definition for the CSR.
    type: dict
  subject_alt_name:
    description:
      - Subject alternative names for the certificate.
    type: list
    elements: str
  key_usage:
    description:
      - List of key usage values to include.
    type: list
    elements: str
  extended_key_usage:
    description:
      - List of extended key usage values to include.
    type: list
    elements: str
  owner:
    description:
      - Owner for the generated CSR file.
    type: str
  group:
    description:
      - Group for the generated CSR file.
    type: str
  mode:
    description:
      - File mode for the generated CSR file.
    type: str
author:
  - Stub maintainer (@repo)
"""


EXAMPLES = r"""
- name: Generate a CSR
  community.crypto.openssl_csr:
    path: /etc/pki/tls/certs/server.csr
    privatekey_path: /etc/pki/tls/private/server.key
    subject:
      CN: example.com
"""


RETURN = r"""
---
changed:
  description: Indicates whether any change was made.
  type: bool
  returned: always
"""


def run_module():
    module = AnsibleModule(
        argument_spec={
            "path": {"type": "path", "required": True},
            "privatekey_path": {"type": "path", "required": True},
            "subject": {"type": "dict", "required": False},
            "subject_alt_name": {"type": "list", "elements": "str", "required": False},
            "key_usage": {"type": "list", "elements": "str", "required": False},
            "extended_key_usage": {"type": "list", "elements": "str", "required": False},
            "owner": {"type": "str", "required": False},
            "group": {"type": "str", "required": False},
            "mode": {"type": "str", "required": False},
        },
        supports_check_mode=True,
    )

    module.exit_json(changed=False)


def main():
    run_module()


if __name__ == "__main__":
    main()
