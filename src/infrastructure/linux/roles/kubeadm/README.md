# Ansible Role: kubeadm

This role installs Kubernetes components (`kubeadm`, `kubelet`, `kubectl`) and can initialize
or join a cluster using **kubeadm** on Debian-based systems.
It aims to provide a simple starting point for automation as described in the
[kubeadm design guide](../../docs/kubeadm-guide.md).

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `kubeadm_version` | `"1.29.0-00"` | Package version for kubeadm, kubelet and kubectl. |
| `kubeadm_role` | `"control-plane"` | Set to `control-plane` to run `kubeadm init` or `worker` to run `kubeadm join`. |
| `kubeadm_pod_network_cidr` | `"10.244.0.0/16"` | Pod network CIDR used during `kubeadm init`. |
| `kubeadm_init_extra_opts` | `""` | Extra options appended to `kubeadm init`. |
| `kubeadm_join_command` | `""` | Full join command for worker nodes (e.g. output of `kubeadm token create --print-join-command`). |
| `kubeadm_disable_swap` | `true` | Whether to disable swap as required by Kubernetes. |

## Example Playbook

```yaml
- hosts: k8s
  become: true
  roles:
    - role: kubeadm
      vars:
        kubeadm_role: control-plane
```

Set `kubeadm_role` to `worker` and provide `kubeadm_join_command` to add a worker node.
