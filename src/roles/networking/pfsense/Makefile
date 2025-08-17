# Makefile for pfSense Ansible Role Testing

.PHONY: help test test-all test-basic test-enterprise test-vpn lint syntax clean install-deps

# Default target
help:
	@echo "pfSense Ansible Role - Testing Commands"
	@echo "======================================"
	@echo ""
	@echo "Available targets:"
	@echo "  install-deps    Install testing dependencies"
	@echo "  lint           Run linting and syntax checks"
	@echo "  syntax         Check Ansible syntax only"
	@echo "  test           Run default test scenario"
	@echo "  test-all       Run all test scenarios"
	@echo "  test-basic     Run basic configuration test"
	@echo "  test-enterprise Run enterprise configuration test"
	@echo "  test-vpn       Run VPN configuration test"
	@echo "  clean          Clean up test artifacts"
	@echo "  validate       Validate test configuration"
	@echo ""
	@echo "Environment variables:"
	@echo "  MOLECULE_SCENARIO  Specify which scenario to run"
	@echo "  NO_DESTROY        Set to 1 to keep test instances"

# Install testing dependencies
install-deps:
	@echo "Installing testing dependencies..."
	pip install molecule[docker] ansible-lint yamllint
	ansible-galaxy install -r molecule/requirements.yml --force

# Run linting and syntax checks
lint:
	@echo "Running linting and syntax checks..."
	python molecule/test_runner.py --lint-only

# Check syntax only
syntax:
	@echo "Checking Ansible syntax..."
	ansible-playbook --syntax-check molecule/default/converge.yml
	ansible-playbook --syntax-check molecule/basic_config/converge.yml
	ansible-playbook --syntax-check molecule/enterprise/converge.yml
	ansible-playbook --syntax-check molecule/vpn_config/converge.yml

# Validate test configuration
validate:
	@echo "Validating test configuration..."
	python molecule/test_runner.py --validate-only

# Run default test scenario
test:
	@echo "Running default test scenario..."
	molecule test -s default

# Run all test scenarios
test-all:
	@echo "Running all test scenarios..."
	python molecule/test_runner.py

# Run basic configuration test
test-basic:
	@echo "Running basic configuration test..."
	molecule test -s basic_config

# Run enterprise configuration test  
test-enterprise:
	@echo "Running enterprise configuration test..."
	molecule test -s enterprise

# Run VPN configuration test
test-vpn:
	@echo "Running VPN configuration test..."
	molecule test -s vpn_config

# Quick test without destroying instances
test-quick:
	@echo "Running quick test (no destroy)..."
	molecule converge -s default
	molecule verify -s default

# Run specific scenario based on environment variable
test-scenario:
	@if [ -z "$(MOLECULE_SCENARIO)" ]; then \
		echo "Error: MOLECULE_SCENARIO not set"; \
		exit 1; \
	fi
	@echo "Running scenario: $(MOLECULE_SCENARIO)"
	molecule test -s $(MOLECULE_SCENARIO)

# Clean up test artifacts
clean:
	@echo "Cleaning up test artifacts..."
	molecule destroy -s default || true
	molecule destroy -s basic_config || true
	molecule destroy -s enterprise || true
	molecule destroy -s vpn_config || true
	docker system prune -f || true
	rm -rf .molecule/ .cache/ || true

# Run comprehensive testing pipeline
ci: install-deps validate lint test-all
	@echo "🎉 All CI tests completed!"

# Development testing (faster)
dev-test: validate syntax test-basic
	@echo "🚀 Development testing completed!"

# Security testing (focus on VPN and firewall)
security-test: test-vpn
	@echo "🔒 Security testing completed!"

# Performance testing setup
perf-test:
	@echo "Setting up performance testing..."
	@echo "Note: Performance testing requires additional setup"
	@echo "Consider using tools like Apache Bench for HTTP testing"

# Documentation generation
docs:
	@echo "Generating documentation..."
	@echo "Role documentation is in README.md"
	@echo "Test documentation is in molecule/ directory"

# Show molecule status
status:
	@echo "Molecule instance status:"
	molecule list || echo "No active instances"

# Interactive debugging
debug:
	@echo "Starting interactive debugging session..."
	molecule converge -s default
	molecule login -s default

# Run tests with coverage (if available)
test-coverage:
	@echo "Running tests with coverage..."
	@echo "Note: Coverage requires additional setup for Ansible"

# Parallel testing (experimental)
test-parallel:
	@echo "Running tests in parallel..."
	@echo "Warning: This may consume significant resources"
	make test-basic & \
	make test-enterprise & \
	make test-vpn & \
	wait
	@echo "Parallel testing completed!"
