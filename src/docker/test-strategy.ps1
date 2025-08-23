# Comprehensive Testing Strategy for Ansible Roles with Proxmox
# This script provides various testing strategies for systematic validation

param(
    [Parameter(Position=0)]
    [ValidateSet("quick-test", "infrastructure-first", "category-sweep", "dependency-order", "parallel-test", "help")]
    [string]$Strategy = "help",
    
    [switch]$ContinueOnError,
    [switch]$DryRun,
    [switch]$SkipBuild
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

# Testing strategies with recommended order
$TestingStrategies = @{
    "quick-test" = @{
        "description" = "Test a few simple roles to validate the setup"
        "roles" = @("update_system", "remove_unnecessary_packages", "common", "sshd", "ufw")
        "parallel" = $false
    }
    "infrastructure-first" = @{
        "description" = "Test infrastructure roles first (foundational)"
        "categories" = @("infrastructure", "networking", "load_balancing_ha")
        "parallel" = $false
    }
    "category-sweep" = @{
        "description" = "Test all categories systematically"
        "categories" = @("infrastructure", "networking", "security_identity", "data_systems", "monitoring_observability", "devops_cicd", "data_analytics", "operations_management", "mariadb")
        "parallel" = $false
    }
    "dependency-order" = @{
        "description" = "Test in dependency order (basic → complex)"
        "order" = @(
            @{category = "infrastructure"; roles = @("update_system", "remove_unnecessary_packages", "common", "sshd", "ufw")},
            @{category = "infrastructure"; roles = @("base", "apt_mirror", "apt_mirror_client_setup", "glusterfs_setup")},
            @{category = "networking"; roles = @("bind9", "cloudflare", "pfsense")},
            @{category = "security_identity"; roles = @("letsencrypt_setup", "letsencrypt_godaddy", "step_ca", "snapca_client")},
            @{category = "load_balancing_ha"; roles = @("keepalived", "keepalived_setup", "haproxy", "ha_proxy_load_balancer_setup")},
            @{category = "data_systems"; roles = @("postgresql", "postgresql_client", "postgresql_monitoring", "postgres_backup")},
            @{category = "data_systems"; roles = @("minio", "neo4j", "elasticsearch", "elasticsearch_install", "elasticsearch_config")},
            @{category = "monitoring_observability"; roles = @("prometheus", "grafana", "filebeat", "configure_filebeat_os")},
            @{category = "security_identity"; roles = @("openldap_server", "openldap_client", "openldap_content", "openldap_backup")},
            @{category = "devops_cicd"; roles = @("jenkins_controller", "jenkins_agent", "jenkins_backup", "python_git_repo_service_install")},
            @{category = "data_analytics"; roles = @("apache_nifi", "apache_superset", "spark_role", "apache_airflow")},
            @{category = "operations_management"; roles = @("netbox", "backup_netbox", "itop")}
        )
        "parallel" = $false
    }
}

# Execute a test strategy
function Invoke-TestStrategy {
    param(
        [string]$StrategyName,
        [hashtable]$StrategyConfig
    )
    
    Write-Info "Executing testing strategy: $StrategyName"
    Write-Info "Description: $($StrategyConfig.description)"
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No tests will be executed"
    }
    
    $totalTests = 0
    $results = @{}
    
    # Handle different strategy types
    if ($StrategyConfig.roles) {
        # Direct role list
        $totalTests = $StrategyConfig.roles.Count
        Write-Info "Testing $totalTests specific roles..."
        
        foreach ($role in $StrategyConfig.roles) {
            if ($DryRun) {
                Write-Info "Would test role: $role"
                $results[$role] = $true
            } else {
                Write-Info "Testing role: $role"
                $success = Invoke-RoleTest -RoleName $role
                $results[$role] = $success
                
                if (-not $success -and -not $ContinueOnError) {
                    Write-Error "Testing stopped due to failure in role '$role'"
                    break
                }
            }
        }
    }
    elseif ($StrategyConfig.categories) {
        # Category-based testing
        foreach ($category in $StrategyConfig.categories) {
            Write-Info "Testing category: $category"
            
            if ($DryRun) {
                Write-Info "Would test category: $category"
            } else {
                $success = Invoke-CategoryTest -Category $category
                $results[$category] = $success
                
                if (-not $success -and -not $ContinueOnError) {
                    Write-Error "Testing stopped due to failure in category '$category'"
                    break
                }
            }
        }
    }
    elseif ($StrategyConfig.order) {
        # Dependency-ordered testing
        $phaseNum = 1
        foreach ($phase in $StrategyConfig.order) {
            Write-Info "Phase $phaseNum - $($phase.category): Testing $($phase.roles.Count) roles"
            
            foreach ($role in $phase.roles) {
                if ($DryRun) {
                    Write-Info "Would test role: $role"
                    $results[$role] = $true
                } else {
                    Write-Info "Testing role: $role"
                    $success = Invoke-RoleTest -RoleName $role
                    $results[$role] = $success
                    
                    if (-not $success -and -not $ContinueOnError) {
                        Write-Error "Testing stopped due to failure in role '$role'"
                        return $results
                    }
                }
            }
            $phaseNum++
        }
    }
    
    return $results
}

# Test a single role
function Invoke-RoleTest {
    param([string]$RoleName)
    
    try {
        if (-not $SkipBuild) {
            $buildArgs = @()
        } else {
            $buildArgs = @("-SkipBuild")
        }
        
        $command = ".\src\docker\run-role-tests.ps1"
        $arguments = @("test", $RoleName, "proxmox") + $buildArgs
        
        & $command @arguments
        
        return $LASTEXITCODE -eq 0
    } catch {
        Write-Error "Error testing role '$RoleName': $($_.Exception.Message)"
        return $false
    }
}

# Test a category
function Invoke-CategoryTest {
    param([string]$Category)
    
    try {
        if (-not $SkipBuild) {
            $buildArgs = @()
        } else {
            $buildArgs = @("-SkipBuild")
        }
        
        $continueArgs = if ($ContinueOnError) { @("-ContinueOnError") } else { @() }
        
        $command = ".\src\docker\run-role-tests.ps1"
        $arguments = @("test-category", $Category, "proxmox") + $buildArgs + $continueArgs
        
        & $command @arguments
        
        return $LASTEXITCODE -eq 0
    } catch {
        Write-Error "Error testing category '$Category': $($_.Exception.Message)"
        return $false
    }
}

# Show test results summary
function Show-TestResults {
    param([hashtable]$Results, [string]$StrategyName)
    
    Write-Host "`n" + "="*60 -ForegroundColor Cyan
    Write-Host "TEST RESULTS SUMMARY - $StrategyName" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Cyan
    
    $passed = 0
    $failed = 0
    
    foreach ($item in $Results.Keys | Sort-Object) {
        $status = if ($Results[$item]) { "PASS"; $passed++ } else { "FAIL"; $failed++ }
        $color = if ($Results[$item]) { "Green" } else { "Red" }
        Write-Host "  $item : $status" -ForegroundColor $color
    }
    
    Write-Host "`nSummary: $passed passed, $failed failed out of $($Results.Count) total items" -ForegroundColor Cyan
    
    if ($failed -eq 0) {
        Write-Success "All tests passed! 🎉"
    } else {
        Write-Warning "Some tests failed. Review the output above for details."
    }
}

# Show available strategies
function Show-TestingStrategies {
    Write-Host "Available Testing Strategies:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($strategy in $TestingStrategies.Keys | Sort-Object) {
        $config = $TestingStrategies[$strategy]
        Write-Host "[$strategy]" -ForegroundColor Yellow
        Write-Host "  Description: $($config.description)" -ForegroundColor Gray
        
        if ($config.roles) {
            Write-Host "  Roles: $($config.roles.Count) specific roles" -ForegroundColor Gray
        } elseif ($config.categories) {
            Write-Host "  Categories: $($config.categories -join ', ')" -ForegroundColor Gray
        } elseif ($config.order) {
            Write-Host "  Phases: $($config.order.Count) dependency-ordered phases" -ForegroundColor Gray
        }
        Write-Host ""
    }
}

# Show usage
function Show-Usage {
    @"
Usage: .\test-strategy.ps1 [STRATEGY] [OPTIONS]

Testing Strategies:
    quick-test         Test 5 simple roles to validate setup
    infrastructure-first  Test foundational infrastructure roles first
    category-sweep     Test all categories systematically
    dependency-order   Test in dependency order (basic → complex)
    parallel-test      Test multiple roles in parallel (experimental)
    help              Show this help message

Options:
    -ContinueOnError   Continue testing even if a role/category fails
    -DryRun           Show what would be tested without running tests
    -SkipBuild        Skip building/starting the Docker container

Examples:
    .\test-strategy.ps1 quick-test
    .\test-strategy.ps1 infrastructure-first -ContinueOnError
    .\test-strategy.ps1 dependency-order -DryRun
    .\test-strategy.ps1 category-sweep -ContinueOnError -SkipBuild

Recommended Testing Sequence:
1. Start with 'quick-test' to validate your setup
2. Use 'infrastructure-first' to test foundational components
3. Progress to 'dependency-order' for comprehensive testing
4. Use 'category-sweep' for complete validation

Prerequisites:
- Docker Desktop running
- Proxmox environment configured (.env file)
- Network connectivity to Proxmox server

"@
}

# Main execution logic
try {
    if ($Strategy -eq "help") {
        Show-Usage
        Show-TestingStrategies
        exit 0
    }
    
    if (-not $TestingStrategies.ContainsKey($Strategy)) {
        Write-Error "Unknown strategy: $Strategy"
        Show-Usage
        exit 1
    }
    
    $strategyConfig = $TestingStrategies[$Strategy]
    
    Write-Info "Starting testing strategy: $Strategy"
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No actual tests will be executed"
    }
    if ($ContinueOnError) {
        Write-Info "Continue-on-error mode enabled"
    }
    if ($SkipBuild) {
        Write-Info "Skipping Docker build/start"
    }
    
    $results = Invoke-TestStrategy -StrategyName $Strategy -StrategyConfig $strategyConfig
    
    if (-not $DryRun) {
        Show-TestResults -Results $results -StrategyName $Strategy
    } else {
        Write-Info "Dry run completed. Use without -DryRun to execute tests."
    }
    
} catch {
    Write-Error "An error occurred: $($_.Exception.Message)"
    exit 1
}
