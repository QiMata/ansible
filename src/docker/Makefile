all:
	docker build . -t ansible:latest

# Build molecule-proxmox Docker image
molecule-build:
	docker build -f Dockerfile.molecule-proxmox ../.. -t ansible-molecule-proxmox:latest

# Start molecule testing environment
molecule-start:
	docker-compose -f docker-compose.molecule.yml up -d

# Stop molecule testing environment
molecule-stop:
	docker-compose -f docker-compose.molecule.yml down

# Enter molecule container shell
molecule-shell:
	docker-compose -f docker-compose.molecule.yml exec molecule-proxmox /bin/bash

# Run molecule test
molecule-test:
	docker-compose -f docker-compose.molecule.yml exec molecule-proxmox bash -c "cd /ansible/src && molecule test -s proxmox"

# Clean up molecule containers and images
molecule-clean:
	docker-compose -f docker-compose.molecule.yml down --rmi all --volumes --remove-orphans

# Show molecule logs
molecule-logs:
	docker-compose -f docker-compose.molecule.yml logs -f molecule-proxmox

.PHONY: all molecule-build molecule-start molecule-stop molecule-shell molecule-test molecule-clean molecule-logs