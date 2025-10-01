FROM debian:buster-slim

# Add ansible PPA: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-debian
RUN apt update; \
    apt install -y gnupg; \
    echo \"deb http://ppa.launchpad.net/ansible/ansible/ubuntu bionic main\" > /etc/apt/sources.list.d/ansible.list; \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367; \
    apt update; \
    apt install -y ansible python-ldap python-pip

RUN useradd -d /home/ansible -U -m -s /bin/bash ansible; mkdir /ansible; chown ansible.ansible /ansible
USER ansible

RUN ansible-galaxy collection install community.general
RUN ansible-galaxy collection install community.postgresql
RUN ansible-galaxy collection install community.proxmox
RUN ansible-galaxy collection install gluster.gluster

WORKDIR /ansible
