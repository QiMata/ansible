#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Minimal stub of community.crypto.x509_certificate for ansible-lint offline usage.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: x509_certificate
short_description: Stub module for ansible-lint argument validation
version_added: "0.0.1"
description:
  - Provides a minimal interface compatible with community.crypto.x509_certificate.
options:
  path:
    description:
      - Destination path for the generated certificate file.
    type: path
    required: true
  privatekey_path:
    description:
      - Path to the private key to sign with when provider is selfsigned.
    type: path
  csr_path:
    description:
      - Path to a certificate signing request to sign.
    type: path
  provider:
    description:
      - Provider used to issue the certificate.
    type: str
  selfsigned_not_after:
    description:
      - Expiration for self-signed certificates.
    type: str
  ownca_path:
    description:
      - Path to the CA certificate when using ownca provider.
    type: path
  ownca_privatekey_path:
    description:
      - Path to the CA private key when using ownca provider.
    type: path
  ownca_not_after:
    description:
      - Expiration for ownca certificates.
    type: str
  subject:
    description:
      - Subject definition for the certificate.
    type: dict
  basic_constraints:
    description:
      - List of basic constraints to include in the certificate.
    type: list
    elements: str
  basic_constraints_critical:
    description:
      - Whether basic constraints extension is critical.
    type: bool
  key_usage:
    description:
      - List of key usage values.
    type: list
    elements: str
  key_usage_critical:
    description:
      - Whether key usage extension is critical.
    type: bool
  owner:
    description:
      - File owner for the generated certificate.
    type: str
  group:
    description:
      - File group for the generated certificate.
    type: str
  mode:
    description:
      - File mode for the generated certificate.
    type: str
author:
  - Stub maintainer (@repo)
"""


EXAMPLES = r"""
- name: Generate a certificate
  community.crypto.x509_certificate:
    path: /etc/pki/tls/certs/server.crt
    csr_path: /etc/pki/tls/certs/server.csr
    provider: ownca
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
            "privatekey_path": {"type": "path", "required": False},
            "csr_path": {"type": "path", "required": False},
            "provider": {"type": "str", "required": False},
            "selfsigned_not_after": {"type": "str", "required": False},
            "ownca_path": {"type": "path", "required": False},
            "ownca_privatekey_path": {"type": "path", "required": False},
            "ownca_not_after": {"type": "str", "required": False},
            "subject": {"type": "dict", "required": False},
            "basic_constraints": {"type": "list", "elements": "str", "required": False},
            "basic_constraints_critical": {"type": "bool", "required": False},
            "key_usage": {"type": "list", "elements": "str", "required": False},
            "key_usage_critical": {"type": "bool", "required": False},
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
