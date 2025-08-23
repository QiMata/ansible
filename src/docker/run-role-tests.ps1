# PowerShell Script for Running Molecule Tests for Multiple Ansible Roles
# This script helps run molecule tests systematically across multiple roles

param(
    [Parameter(Position=0)]
    [ValidateSet("list", "test", "test-all", "test-category", "create", "converge", "destroy", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$RoleName = "",
    
    [Parameter(Position=2)]
    [string]$Scenario = "default",
    
    [switch]$SkipBuild,
    [switch]$ContinueOnError,
    [switch]$Parallel,
    [switch]$SkipCleanup
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$DockerComposeFile = Join-Path $ScriptDir "docker-compose.molecule.yml"

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

# Role categories and their paths
$RoleCategories = @{
    "data_analytics" = @(
        "airflow_connector", "amundsen_frontend", "amundsen_metadata", "amundsen_search",
        "apache_airflow", "apache_nifi", "apache_superset", "spark_role"
    )
    "data_systems" = @(
        "elasticsearch", "elasticsearch_cluster", "elasticsearch_config", "elasticsearch_install",
        "elasticsearch_security", "elasticsearch_snapshot", "minio", "neo4j", "postgresql",
        "postgresql_client", "postgresql_monitoring", "postgres_backup"
    )
    "devops_cicd" = @(
        "jenkins_agent", "jenkins_backup", "jenkins_controller", "python_git_repo_service_install"
    )
    "infrastructure" = @(
        "apt_mirror", "apt_mirror_client_setup", "base", "common", "glusterfs_setup",
        "remove_unnecessary_packages", "sshd", "ufw", "update_system"
    )
    "load_balancing_ha" = @(
        "ha_proxy_load_balancer_setup", "haproxy", "keepalived", "keepalived_setup"
    )
    "monitoring_observability" = @(
        "configure_filebeat_os", "filebeat", "grafana", "prometheus"
    )
    "networking" = @(
        "bind9", "cloudflare", "pfsense"
    )
    "operations_management" = @(
        "backup_netbox", "itop", "netbox"
    )
    "security_identity" = @(
        "keycloak", "keycloak_realm", "letsencrypt_godaddy", "letsencrypt_setup",
        "open_ldap_setup", "openldap_backup", "openldap_client", "openldap_content",
        "openldap_haproxy", "openldap_logging", "openldap_mfa", "openldap_password_policies",
        "openldap_replication", "openldap_server", "snapca_client", "step_ca"
    )
    "mariadb" = @(
        "mariadb_backups", "mariadb_galera_loadbalancer_install", "mariadb_security"
    )
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

# Get available scenarios for a role
function Get-RoleScenarios {
    param([string]$RoleName)
    
    $rolePath = Get-RolePath $RoleName
    if (-not $rolePath) {
        return @()
    }
    
    $moleculePath = Join-Path $rolePath "molecule"
    if (Test-Path $moleculePath) {
        return Get-ChildItem -Path $moleculePath -Directory | ForEach-Object { $_.Name }
    }
    return @()
}

# Ensure container is running
function Start-ContainerIfNeeded {
    if (-not $SkipBuild) {
        Write-Info "Ensuring Docker container is ready..."
        & "$ScriptDir\run-molecule-tests.ps1" "build"
        & "$ScriptDir\run-molecule-tests.ps1" "start"
    }
}

# Run molecule test for a specific role
# Destroy LXC container to ensure clean environment
function Reset-TestEnvironment {
    param([string]$TestScenario = "proxmox")
    
    Write-Info "Destroying LXC container to ensure clean test environment..."
    try {
        $destroyCommand = "cd /ansible/src && molecule destroy -s $TestScenario"
        docker-compose -f $DockerComposeFile exec molecule-proxmox bash -c $destroyCommand
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Test environment cleaned successfully"
            return $true
        } else {
            Write-Warning "Container destroy completed (may have been already destroyed)"
            return $true
        }
    } catch {
        Write-Warning "Error during environment cleanup: $($_.Exception.Message)"
        return $true # Continue even if destroy fails
    }
}

function Invoke-RoleTest {
    param(
        [string]$RoleName,
        [string]$TestScenario = "default",
        [string]$Action = "test",
        [switch]$SkipCleanup
    )
    
    $rolePath = Get-RolePath $RoleName
    if (-not $rolePath) {
        Write-Error "Role '$RoleName' not found"
        return $false
    }
    
    $scenarios = Get-RoleScenarios $RoleName
    if ($TestScenario -notin $scenarios) {
        Write-Warning "Scenario '$TestScenario' not found for role '$RoleName'. Available scenarios: $($scenarios -join ', ')"
        if ("default" -in $scenarios) {
            $TestScenario = "default"
            Write-Info "Using 'default' scenario instead"
        } else {
            $TestScenario = $scenarios[0]
            Write-Info "Using '$TestScenario' scenario instead"
        }
    }
    
    # Clean environment before running test (unless explicitly skipped)
    if (-not $SkipCleanup -and $Action -eq "test") {
        Reset-TestEnvironment -TestScenario $TestScenario
    }
    
    $relativeRolePath = $rolePath.Replace("$ProjectRoot\", "").Replace("\", "/")
    Write-Info "Running molecule $Action for role '$RoleName' with scenario '$TestScenario'"
    Write-Info "Role path: $relativeRolePath"
    
    try {
        $command = "cd /ansible/$relativeRolePath && molecule $Action -s $TestScenario"
        docker-compose -f $DockerComposeFile exec molecule-proxmox bash -c $command
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Molecule $Action completed successfully for role '$RoleName'"
            
            # Clean environment after successful test (unless explicitly skipped)
            if (-not $SkipCleanup -and $Action -eq "test") {
                Write-Info "Cleaning up after successful test..."
                Reset-TestEnvironment -TestScenario $TestScenario
            }
            
            return $true
        } else {
            Write-Error "Molecule $Action failed for role '$RoleName'"
            
            # Clean environment after failed test to prevent interference
            if (-not $SkipCleanup -and $Action -eq "test") {
                Write-Info "Cleaning up after failed test..."
                Reset-TestEnvironment -TestScenario $TestScenario
            }
            
            return $false
        }
    } catch {
        Write-Error "Error running molecule $Action for role '$RoleName': $($_.Exception.Message)"
        
        # Clean environment after error
        if (-not $SkipCleanup -and $Action -eq "test") {
            Write-Info "Cleaning up after error..."
            Reset-TestEnvironment -TestScenario $TestScenario
        }
        
        return $false
    }
}

# List all roles with molecule tests
function Show-RolesList {
    Write-Info "Roles with molecule tests:"
    Write-Host ""
    
    foreach ($category in $RoleCategories.Keys | Sort-Object) {
        Write-Host "[$category]" -ForegroundColor Cyan
        $rolesInCategory = $RoleCategories[$category]
        $availableRoles = Get-RolesWithMolecule
        
        foreach ($role in $rolesInCategory) {
            if ($role -in $availableRoles) {
                $scenarios = Get-RoleScenarios $role
                Write-Host "  ✓ $role" -ForegroundColor Green -NoNewline
                Write-Host " (scenarios: $($scenarios -join ', '))" -ForegroundColor Gray
            }
        }
        Write-Host ""
    }
    
    # Show uncategorized roles
    $allCategorizedRoles = $RoleCategories.Values | ForEach-Object { $_ }
    $uncategorizedRoles = Get-RolesWithMolecule | Where-Object { $_ -notin $allCategorizedRoles }
    
    if ($uncategorizedRoles) {
        Write-Host "[uncategorized]" -ForegroundColor Cyan
        foreach ($role in $uncategorizedRoles) {
            $scenarios = Get-RoleScenarios $role
            Write-Host "  ✓ $role" -ForegroundColor Yellow -NoNewline
            Write-Host " (scenarios: $($scenarios -join ', '))" -ForegroundColor Gray
        }
    }
}

# Test all roles in a category
function Invoke-CategoryTest {
    param([string]$Category)
    
    if (-not $RoleCategories.ContainsKey($Category)) {
        Write-Error "Category '$Category' not found. Available categories: $($RoleCategories.Keys -join ', ')"
        return
    }
    
    Start-ContainerIfNeeded
    
    $roles = $RoleCategories[$Category]
    $availableRoles = Get-RolesWithMolecule
    $testRoles = $roles | Where-Object { $_ -in $availableRoles }
    
    Write-Info "Testing all roles in category '$Category'"
    Write-Info "Roles to test: $($testRoles -join ', ')"
    
    $results = @{}
    $totalRoles = $testRoles.Count
    $currentRole = 0
    
    foreach ($role in $testRoles) {
        $currentRole++
        Write-Info "[$currentRole/$totalRoles] Testing role: $role"
        
        $success = Invoke-RoleTest -RoleName $role -TestScenario $Scenario -Action "test" -SkipCleanup:$SkipCleanup
        $results[$role] = $success
        
        if (-not $success -and -not $ContinueOnError) {
            Write-Error "Testing stopped due to failure in role '$role'. Use -ContinueOnError to continue with remaining roles."
            break
        }
    }
    
    # Show summary
    Write-Host "`nTest Results Summary for category '$Category':" -ForegroundColor Cyan
    foreach ($role in $results.Keys) {
        $status = if ($results[$role]) { "PASS" } else { "FAIL" }
        $color = if ($results[$role]) { "Green" } else { "Red" }
        Write-Host "  $role : $status" -ForegroundColor $color
    }
}

# Test all roles
function Invoke-AllTests {
    Start-ContainerIfNeeded
    
    $allRoles = Get-RolesWithMolecule
    Write-Info "Testing all $($allRoles.Count) roles with molecule tests"
    
    $results = @{}
    $totalRoles = $allRoles.Count
    $currentRole = 0
    
    foreach ($role in $allRoles) {
        $currentRole++
        Write-Info "[$currentRole/$totalRoles] Testing role: $role"
        
        $success = Invoke-RoleTest -RoleName $role -TestScenario $Scenario -Action "test" -SkipCleanup:$SkipCleanup
        $results[$role] = $success
        
        if (-not $success -and -not $ContinueOnError) {
            Write-Error "Testing stopped due to failure in role '$role'. Use -ContinueOnError to continue with remaining roles."
            break
        }
    }
    
    # Show summary
    Write-Host "`nTest Results Summary:" -ForegroundColor Cyan
    $passed = 0
    $failed = 0
    
    foreach ($role in $results.Keys | Sort-Object) {
        $status = if ($results[$role]) { "PASS"; $passed++ } else { "FAIL"; $failed++ }
        $color = if ($results[$role]) { "Green" } else { "Red" }
        Write-Host "  $role : $status" -ForegroundColor $color
    }
    
    Write-Host "`nSummary: $passed passed, $failed failed out of $($results.Count) total roles" -ForegroundColor Cyan
}

# Show usage
function Show-Usage {
    @"
Usage: .\run-role-tests.ps1 [COMMAND] [ROLE_NAME] [SCENARIO] [OPTIONS]

Commands:
    list                    List all roles with molecule tests
    test [role] [scenario]  Run molecule test for a specific role
    test-all [scenario]     Run molecule tests for all roles
    test-category [category] [scenario] Run tests for all roles in a category
    create [role] [scenario] Run molecule create for a specific role
    converge [role] [scenario] Run molecule converge for a specific role
    destroy [role] [scenario] Run molecule destroy for a specific role
    help                    Show this help message

Categories:
    data_analytics, data_systems, devops_cicd, infrastructure, 
    load_balancing_ha, monitoring_observability, networking, 
    operations_management, security_identity, mariadb

Options:
    -SkipBuild             Skip building/starting the Docker container
    -ContinueOnError       Continue testing even if a role fails
    -Parallel              Run tests in parallel (experimental)
    -SkipCleanup           Skip destroying LXC containers between tests (faster but less clean)

Examples:
    .\run-role-tests.ps1 list
    .\run-role-tests.ps1 test apache_nifi
    .\run-role-tests.ps1 test apache_nifi default
    .\run-role-tests.ps1 test-category security_identity
    .\run-role-tests.ps1 test-all -ContinueOnError
    .\run-role-tests.ps1 create postgresql
    .\run-role-tests.ps1 destroy postgresql

Before running tests, make sure to:
1. Have Docker Desktop running
2. Configure Proxmox credentials in .env file
3. Ensure network connectivity to Proxmox server

"@
}

# Main execution logic
try {
    switch ($Command) {
        "list" {
            Show-RolesList
        }
        "test" {
            if (-not $RoleName) {
                Write-Error "Role name is required for test command"
                Show-Usage
                exit 1
            }
            Start-ContainerIfNeeded
            Invoke-RoleTest -RoleName $RoleName -TestScenario $Scenario -Action "test" -SkipCleanup:$SkipCleanup
        }
        "test-all" {
            if ($RoleName) {
                $Scenario = $RoleName  # If role name provided, treat it as scenario
            }
            Invoke-AllTests
        }
        "test-category" {
            if (-not $RoleName) {
                Write-Error "Category name is required for test-category command"
                Show-Usage
                exit 1
            }
            Invoke-CategoryTest -Category $RoleName
        }
        "create" {
            if (-not $RoleName) {
                Write-Error "Role name is required for create command"
                Show-Usage
                exit 1
            }
            Start-ContainerIfNeeded
            Invoke-RoleTest -RoleName $RoleName -TestScenario $Scenario -Action "create" -SkipCleanup:$SkipCleanup
        }
        "converge" {
            if (-not $RoleName) {
                Write-Error "Role name is required for converge command"
                Show-Usage
                exit 1
            }
            Start-ContainerIfNeeded
            Invoke-RoleTest -RoleName $RoleName -TestScenario $Scenario -Action "converge" -SkipCleanup:$SkipCleanup
        }
        "destroy" {
            if (-not $RoleName) {
                Write-Error "Role name is required for destroy command"
                Show-Usage
                exit 1
            }
            Start-ContainerIfNeeded
            Invoke-RoleTest -RoleName $RoleName -TestScenario $Scenario -Action "destroy" -SkipCleanup:$SkipCleanup
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
