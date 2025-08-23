# Ansible Molecule Testing with Docker-Powered Proxmox
## Complete Setup and Testing Guide

### 🎯 **What's Ready**

✅ **67 Ansible roles** with molecule tests organized by category  
✅ **Proxmox scenarios** created for all roles  
✅ **Docker container** with molecule + Proxmox support  
✅ **Automated test runners** with multiple strategies  
✅ **Comprehensive tooling** for systematic validation  

---

## 🚀 **Quick Start**

### 1. **Validate Setup** (Recommended First Step)
```powershell
# Test 5 simple roles to ensure everything works
.\src\docker\test-strategy.ps1 quick-test
```

### 2. **Test Individual Roles**
```powershell
# Test specific roles with Proxmox scenarios
.\src\docker\run-role-tests.ps1 test update_system proxmox
.\src\docker\run-role-tests.ps1 test postgresql proxmox
.\src\docker\run-role-tests.ps1 test apache_nifi proxmox
```

### 3. **Test by Category**
```powershell
# Test entire categories
.\src\docker\run-role-tests.ps1 test-category infrastructure proxmox
.\src\docker\run-role-tests.ps1 test-category security_identity proxmox -ContinueOnError
```

### 4. **Systematic Testing**
```powershell
# Test foundational infrastructure first
.\src\docker\test-strategy.ps1 infrastructure-first -ContinueOnError

# Test in dependency order (recommended)
.\src\docker\test-strategy.ps1 dependency-order -ContinueOnError

# Test all categories systematically
.\src\docker\test-strategy.ps1 category-sweep -ContinueOnError
```

---

## 📊 **Available Roles by Category**

### **Infrastructure** (9 roles)
- `base`, `common`, `update_system`, `remove_unnecessary_packages`
- `sshd`, `ufw`, `apt_mirror`, `apt_mirror_client_setup`, `glusterfs_setup`

### **Data Analytics** (8 roles)
- `apache_nifi`, `apache_superset`, `apache_airflow`, `spark_role`
- `amundsen_frontend`, `amundsen_metadata`, `amundsen_search`, `airflow_connector`

### **Data Systems** (12 roles)
- `postgresql`, `postgresql_client`, `postgresql_monitoring`, `postgres_backup`
- `elasticsearch` (+ 5 elasticsearch sub-roles), `minio`, `neo4j`

### **Security & Identity** (17 roles)
- `keycloak`, `keycloak_realm`, `letsencrypt_setup`, `letsencrypt_godaddy`
- `openldap_server`, `openldap_client` (+ 8 openldap sub-roles)
- `step_ca`, `snapca_client`, `vault`

### **Monitoring & Observability** (4 roles)
- `prometheus`, `grafana`, `filebeat`, `configure_filebeat_os`

### **DevOps/CI-CD** (4 roles)
- `jenkins_controller`, `jenkins_agent`, `jenkins_backup`, `python_git_repo_service_install`

### **Load Balancing/HA** (4 roles)
- `haproxy`, `ha_proxy_load_balancer_setup`, `keepalived`, `keepalived_setup`

### **Networking** (3 roles)
- `bind9`, `cloudflare`, `pfsense`

### **Operations Management** (3 roles)
- `netbox`, `backup_netbox`, `itop`

### **MariaDB** (3 roles)
- `mariadb_backups`, `mariadb_galera_loadbalancer_install`, `mariadb_security`

---

## 🛠 **Available Tools**

### **1. Role Test Runner** (`run-role-tests.ps1`)
```powershell
# Basic commands
.\src\docker\run-role-tests.ps1 list                    # Show all roles
.\src\docker\run-role-tests.ps1 test [role] proxmox     # Test specific role
.\src\docker\run-role-tests.ps1 test-category [category] proxmox  # Test category
.\src\docker\run-role-tests.ps1 test-all proxmox -ContinueOnError  # Test everything
```

### **2. Proxmox Scenario Generator** (`create-proxmox-scenarios.ps1`)
```powershell
.\src\docker\create-proxmox-scenarios.ps1 list-missing   # Show missing scenarios
.\src\docker\create-proxmox-scenarios.ps1 create [role]  # Create for specific role
.\src\docker\create-proxmox-scenarios.ps1 create-all     # Create for all roles (DONE)
```

### **3. Strategic Test Runner** (`test-strategy.ps1`)
```powershell
.\src\docker\test-strategy.ps1 quick-test               # Test 5 simple roles
.\src\docker\test-strategy.ps1 infrastructure-first     # Test foundation roles
.\src\docker\test-strategy.ps1 dependency-order         # Test in dependency order
.\src\docker\test-strategy.ps1 category-sweep           # Test all categories
```

### **4. Core Molecule Runner** (`run-molecule-tests.ps1`)
```powershell
.\src\docker\run-molecule-tests.ps1 build              # Build container
.\src\docker\run-molecule-tests.ps1 start              # Start container
.\src\docker\run-molecule-tests.ps1 shell              # Enter container shell
.\src\docker\run-molecule-tests.ps1 test proxmox       # Test main proxmox scenario
```

---

## 🎯 **Recommended Testing Workflows**

### **Option A: Quick Validation** (15-30 minutes)
```powershell
# 1. Validate setup with simple roles
.\src\docker\test-strategy.ps1 quick-test

# 2. Test key infrastructure components
.\src\docker\run-role-tests.ps1 test postgresql proxmox
.\src\docker\run-role-tests.ps1 test apache_nifi proxmox
.\src\docker\run-role-tests.ps1 test keycloak proxmox
```

### **Option B: Foundation-First** (1-2 hours)
```powershell
# 1. Test infrastructure foundation
.\src\docker\test-strategy.ps1 infrastructure-first -ContinueOnError

# 2. Test security components
.\src\docker\run-role-tests.ps1 test-category security_identity proxmox -ContinueOnError

# 3. Test data systems
.\src\docker\run-role-tests.ps1 test-category data_systems proxmox -ContinueOnError
```

### **Option C: Comprehensive Testing** (3-4 hours)
```powershell
# Test everything in dependency order
.\src\docker\test-strategy.ps1 dependency-order -ContinueOnError

# Or test all categories systematically
.\src\docker\test-strategy.ps1 category-sweep -ContinueOnError
```

### **Option D: Continuous Testing** (Background)
```powershell
# Set up automated testing for specific categories
.\src\docker\run-role-tests.ps1 test-category infrastructure proxmox -ContinueOnError > infrastructure-test-results.log
.\src\docker\run-role-tests.ps1 test-category data_analytics proxmox -ContinueOnError > data-analytics-test-results.log
```

---

## 🔧 **Common Options**

- `-ContinueOnError` - Don't stop on first failure
- `-SkipBuild` - Don't rebuild Docker container  
- `-DryRun` - Show what would be tested without running
- `proxmox` - Use Proxmox scenarios (recommended)
- `default` - Use default scenarios (Docker-based, needs fixes)

---

## 📈 **Next Steps**

1. **Start with quick validation**: `.\src\docker\test-strategy.ps1 quick-test`
2. **Test priority roles individually** based on your needs
3. **Progress to category testing** for comprehensive coverage
4. **Use dependency-order strategy** for complete validation
5. **Set up automated testing workflows** for ongoing validation

---

## 🎉 **You're Ready!**

The complete molecule testing infrastructure is now set up and ready to systematically validate all 67 Ansible roles using Docker-powered Proxmox scenarios. Choose your testing approach and start validating your roles!
