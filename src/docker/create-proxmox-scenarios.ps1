# PowerShell Script to Create Proxmox Molecule Scenarios for Roles
# This script helps create standardized Proxmox scenarios for existing roles

param(
    [Parameter(Position=0)]
    [ValidateSet("create", "create-all", "list-missing", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$RoleName = "",
    
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Color functions for output
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Get all roles with molecule tests
function Get-RolesWithMolecule {
    $roles = Get-ChildItem -Path "$ProjectRoot\src\roles" -Recurse -Directory | 
             Where-Object { $_.Name -eq "molecule" } | 
             ForEach-Object { $_.Parent.Name } | 
             Sort-Object | 
             Get-Unique
    return $roles
}

# Get role path
function Get-RolePath {
    param([string]$RoleName)
    
    $rolePath = Get-ChildItem -Path "$ProjectRoot\src\roles" -Recurse -Directory | 
                Where-Object { $_.Name -eq $RoleName } | 
                Select-Object -First 1
    
    if ($rolePath) {
        return $rolePath.FullName
    }
    return $null
}

# Check if role has Proxmox scenario
function Test-ProxmoxScenario {
    param([string]$RoleName)
    
    $rolePath = Get-RolePath $RoleName
    if (-not $rolePath) {
        return $false
    }
    
    $proxmoxScenarioPath = Join-Path $rolePath "molecule\proxmox\molecule.yml"
    return Test-Path $proxmoxScenarioPath
}

# Create Proxmox scenario for a role
function New-ProxmoxScenario {
    param([string]$RoleName)
    
    $rolePath = Get-RolePath $RoleName
    if (-not $rolePath) {
        Write-Error "Role '$RoleName' not found"
        return $false
    }
    
    $proxmoxDir = Join-Path $rolePath "molecule\proxmox"
    $proxmoxScenarioPath = Join-Path $proxmoxDir "molecule.yml"
    
    if ((Test-Path $proxmoxScenarioPath) -and -not $Force) {
        Write-Warning "Proxmox scenario already exists for role '$RoleName'. Use -Force to overwrite."
        return $false
    }
    
    # Create directory if it doesn't exist
    if (-not (Test-Path $proxmoxDir)) {
        New-Item -ItemType Directory -Path $proxmoxDir -Force | Out-Null
    }
    
        # Generate molecule.yml content
                $moleculeYml = @"
---
dependency:
  name: galaxy
  enabled: false
driver:
  name: default
  options:
    managed: false
    ansible_connection_options:
      ansible_connection: ssh
platforms:
  - name: ${RoleName}-test-instance
    groups:
      - test_instances
      - ${RoleName}_test
provisioner:
  name: ansible
  playbooks:
        create: /ansible/src/molecule/proxmox/create.yml
        prepare: /ansible/src/molecule/proxmox/prepare.yml
        converge: converge.yml
        verify: verify.yml
        destroy: /ansible/src/molecule/proxmox/destroy.yml
    env:
        ANSIBLE_ROLES_PATH: "/ansible/src/roles:/ansible/src/roles/infrastructure:/ansible/src/roles/data_analytics:/ansible/src/roles/data_systems:/ansible/src/roles/devops_cicd:/ansible/src/roles/load_balancing_ha:/ansible/src/roles/monitoring_observability:/ansible/src/roles/networking:/ansible/src/roles/operations_management:/ansible/src/roles/security_identity"
  inventory:
    host_vars:
      ${RoleName}-test-instance:
                ansible_host: "{{ lookup('env', 'CONTAINER_IP') | default('10.80.0.200') }}"
                ansible_user: molecule
                ansible_connection: ssh
                ansible_ssh_pass: "{{ lookup('env', 'CONTAINER_PASSWORD') | default('molecule123') }}"
                ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
                ansible_become: true
                ansible_become_method: sudo
  config_options:
    defaults:
      host_key_checking: false
      stdout_callback: yaml
      bin_ansible_callbacks: true
      role_name_check: False
verifier:
  name: ansible
scenario:
  name: proxmox
  test_sequence:
    - dependency
    - cleanup
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - side_effect
    - verify
    - cleanup
    - destroy
"@

    # Generate converge.yml content
    $convergeYml = @"
---
- name: Converge
  hosts: all
  become: true
  gather_facts: true
  tasks:
    - name: "Include $RoleName role"
      ansible.builtin.include_role:
        name: $RoleName
"@

    # Generate verify.yml content  
    $verifyYml = @"
---
- name: Verify
  hosts: all
  gather_facts: false
  tasks:
    - name: Example assertion
      ansible.builtin.assert:
        that:
          - true
        success_msg: "Role $RoleName verification passed"
        fail_msg: "Role $RoleName verification failed"
"@

    # Generate prepare.yml content
    $prepareYml = @"
---
- name: Prepare
  hosts: all
  become: true
  gather_facts: true
  tasks:
    - name: Update package cache
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"
    
    - name: Install basic packages
      ansible.builtin.apt:
        name:
          - curl
          - wget
          - unzip
          - python3
          - python3-pip
        state: present
      when: ansible_os_family == "Debian"
"@

    try {
        # Write files
        Set-Content -Path $proxmoxScenarioPath -Value $moleculeYml -Encoding UTF8
        Set-Content -Path (Join-Path $proxmoxDir "converge.yml") -Value $convergeYml -Encoding UTF8
        Set-Content -Path (Join-Path $proxmoxDir "verify.yml") -Value $verifyYml -Encoding UTF8
        Set-Content -Path (Join-Path $proxmoxDir "prepare.yml") -Value $prepareYml -Encoding UTF8
        
        Write-Success "Created Proxmox scenario for role '$RoleName'"
        Write-Info "Files created in: $proxmoxDir"
        Write-Info "  - molecule.yml"
        Write-Info "  - converge.yml"
        Write-Info "  - verify.yml"
        Write-Info "  - prepare.yml"
        
        return $true
    } catch {
        Write-Error "Failed to create Proxmox scenario for role '$RoleName': $($_.Exception.Message)"
        return $false
    }
}

# List roles missing Proxmox scenarios
function Show-MissingProxmoxScenarios {
    $allRoles = Get-RolesWithMolecule
    $missingProxmox = @()
    
    foreach ($role in $allRoles) {
        if (-not (Test-ProxmoxScenario $role)) {
            $missingProxmox += $role
        }
    }
    
    Write-Info "Roles with molecule tests but missing Proxmox scenarios:"
    Write-Host ""
    
    if ($missingProxmox.Count -eq 0) {
        Write-Success "All roles with molecule tests already have Proxmox scenarios!"
    } else {
        foreach ($role in $missingProxmox) {
            Write-Host "  ✗ $role" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Info "Total roles missing Proxmox scenarios: $($missingProxmox.Count)"
        Write-Info "Use '.\create-proxmox-scenarios.ps1 create-all' to create scenarios for all missing roles"
    }
}

# Create Proxmox scenarios for all roles missing them
function New-AllProxmoxScenarios {
    $allRoles = Get-RolesWithMolecule
    $missingProxmox = @()
    
    foreach ($role in $allRoles) {
        if (-not (Test-ProxmoxScenario $role)) {
            $missingProxmox += $role
        }
    }
    
    if ($missingProxmox.Count -eq 0) {
        Write-Success "All roles already have Proxmox scenarios!"
        return
    }
    
    Write-Info "Creating Proxmox scenarios for $($missingProxmox.Count) roles..."
    
    $results = @{}
    $currentRole = 0
    
    foreach ($role in $missingProxmox) {
        $currentRole++
        Write-Info "[$currentRole/$($missingProxmox.Count)] Creating Proxmox scenario for: $role"
        
        $success = New-ProxmoxScenario -RoleName $role
        $results[$role] = $success
    }
    
    # Show summary
    Write-Host "`nProxmox Scenario Creation Summary:" -ForegroundColor Cyan
    $created = 0
    $failed = 0
    
    foreach ($role in $results.Keys | Sort-Object) {
        $status = if ($results[$role]) { "CREATED"; $created++ } else { "FAILED"; $failed++ }
        $color = if ($results[$role]) { "Green" } else { "Red" }
        Write-Host "  $role : $status" -ForegroundColor $color
    }
    
    Write-Host "`nSummary: $created created, $failed failed out of $($results.Count) total roles" -ForegroundColor Cyan
}

# Show usage
function Show-Usage {
    @"
Usage: .\create-proxmox-scenarios.ps1 [COMMAND] [ROLE_NAME] [OPTIONS]

Commands:
    create [role]      Create Proxmox scenario for a specific role
    create-all         Create Proxmox scenarios for all roles missing them
    list-missing       List roles that don't have Proxmox scenarios
    help              Show this help message

Options:
    -Force            Overwrite existing Proxmox scenarios

Examples:
    .\create-proxmox-scenarios.ps1 list-missing
    .\create-proxmox-scenarios.ps1 create apache_nifi
    .\create-proxmox-scenarios.ps1 create apache_nifi -Force
    .\create-proxmox-scenarios.ps1 create-all

The created Proxmox scenarios will include:
- molecule.yml with Proxmox driver configuration
- converge.yml to apply the role
- verify.yml for testing assertions
- prepare.yml for basic system preparation

After creating scenarios, you can run tests with:
    .\run-role-tests.ps1 test [role] proxmox

"@
}

# Main execution logic
try {
    switch ($Command) {
        "create" {
            if (-not $RoleName) {
                Write-Error "Role name is required for create command"
                Show-Usage
                exit 1
            }
            New-ProxmoxScenario -RoleName $RoleName
        }
        "create-all" {
            New-AllProxmoxScenarios
        }
        "list-missing" {
            Show-MissingProxmoxScenarios
        }
        "help" {
            Show-Usage
        }
        default {
            Write-Error "Unknown command: $Command"
            Show-Usage
            exit 1
        }
    }
} catch {
    Write-Error "An error occurred: $($_.Exception.Message)"
    exit 1
}
