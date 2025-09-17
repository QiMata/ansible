#!/usr/bin/env pwsh
# ============================================================================
# Data Systems Testing Framework Validation Script
# Applies proven containerized testing pattern across data systems
# ============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("validate", "test-all", "test-mariadb", "test-neo4j", "test-minio", "help")]
    [string]$Action = "help"
)

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

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "$Message" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
}

# Function to validate testing framework structure
function Test-TestingFramework {
    param(
        [string]$RoleName,
        [string]$RolePath
    )
    
    Write-Header "Validating $RoleName Testing Framework"
    
    $issues = @()
    $successes = @()
    
    # Check molecule directory structure
    $moleculePath = Join-Path $RolePath "molecule\proxmox"
    if (Test-Path $moleculePath) {
        $successes += "✓ Molecule proxmox directory exists"
        
        # Check required files
        $requiredFiles = @("molecule.yml", "converge.yml", "verify.yml")
        foreach ($file in $requiredFiles) {
            $filePath = Join-Path $moleculePath $file
            if (Test-Path $filePath) {
                $successes += "✓ $file exists"
                
                # Validate file content
                $content = Get-Content $filePath -Raw
                switch ($file) {
                    "molecule.yml" {
                        if ($content -match "test_sequence.*(\r?\n.*)*create.*(\r?\n.*)*prepare.*(\r?\n.*)*converge.*(\r?\n.*)*verify") {
                            $successes += "✓ molecule.yml has complete test sequence"
                        } else {
                            $issues += "✗ molecule.yml missing complete test sequence"
                        }
                        
                        if ($content -match "health_check_enabled.*true") {
                            $successes += "✓ molecule.yml has health check configuration"
                        } else {
                            $issues += "✗ molecule.yml missing health check configuration"
                        }
                    }
                    
                    "converge.yml" {
                        if ($content -match "pre_tasks" -and $content -match "handlers") {
                            $successes += "✓ converge.yml has pre_tasks and handlers"
                        } else {
                            $issues += "✗ converge.yml missing pre_tasks or handlers"
                        }
                        
                        if ($content -match "container.*aware" -or $content -match "environment.*test") {
                            $successes += "✓ converge.yml has container-aware configuration"
                        } else {
                            $issues += "✗ converge.yml missing container-aware settings"
                        }
                    }
                    
                    "verify.yml" {
                        if ($content -match "PHASE.*SERVICE VALIDATION" -and $content -match "PHASE.*HEALTH SUMMARY") {
                            $successes += "✓ verify.yml has comprehensive phase structure"
                        } else {
                            $issues += "✗ verify.yml missing comprehensive validation phases"
                        }
                        
                        $hasPortChecks = ($content -match "port:" -and $content -match "wait_for")
                        $hasAssertions = ($content -match "assert:")
                        if ($hasPortChecks -and $hasAssertions) {
                            $successes += "✓ verify.yml has port checks and assertions"
                        } else {
                            $issues += "✗ verify.yml missing port checks or assertions"
                        }
                        
                        if ($content -match "health.*check.*retries" -and $content -match "health.*check.*delay") {
                            $successes += "✓ verify.yml has health check retry logic"
                        } else {
                            $issues += "✗ verify.yml missing health check retry configuration"
                        }
                    }
                }
            } else {
                $issues += "✗ $file missing"
            }
        }
    } else {
        $issues += "✗ Molecule proxmox directory missing"
    }
    
    # Display results
    Write-Info "Validation Results for ${RoleName}:"
    foreach ($success in $successes) {
        Write-Success $success
    }
    foreach ($issue in $issues) {
        Write-Error $issue
    }
    
    $score = ($successes.Count / ($successes.Count + $issues.Count)) * 100
    Write-Info "Framework Completeness Score: $($score.ToString('F1'))%"
    
    return @{
        RoleName = $RoleName
        Score = $score
        Issues = $issues.Count
        Successes = $successes.Count
    }
}

# Function to run molecule test
function Invoke-MoleculeTest {
    param(
        [string]$RoleName,
        [string]$RolePath
    )
    
    Write-Header "Running Molecule Test for $RoleName"
    
    # Check if Docker environment is running
    $dockerCheck = docker ps --filter "name=molecule-proxmox" --format "table {{.Names}}\t{{.Status}}"
    if ($dockerCheck -match "molecule-proxmox.*Up") {
        Write-Success "Docker molecule environment is running"
        
        # Run the test
        Write-Info "Executing molecule test for $RoleName..."
        $testCommand = "cd /ansible/src/roles/data_systems/$($RoleName.ToLower()) && molecule test -s proxmox"
        
        try {
            docker-compose -f "src\docker\docker-compose.molecule.yml" exec molecule-proxmox bash -c $testCommand
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$RoleName molecule test completed successfully"
                return $true
            } else {
                Write-Error "$RoleName molecule test failed with exit code $LASTEXITCODE"
                return $false
            }
        } catch {
            Write-Error "Failed to execute molecule test for ${RoleName}: $($_.Exception.Message)"
            return $false
        }
    } else {
        Write-Warning "Docker molecule environment is not running. Start it with: .\src\docker\run-molecule-tests.ps1 start"
        return $false
    }
}

# Main execution logic
switch ($Action) {
    "validate" {
        Write-Header "Validating Proven Containerized Testing Pattern Implementation"
        
        $roles = @(
            @{ Name = "MariaDB"; Path = "src\roles\data_systems\mariadb" },
            @{ Name = "Neo4j"; Path = "src\roles\data_systems\neo4j" },
            @{ Name = "MinIO"; Path = "src\roles\data_systems\minio" }
        )
        
        $results = @()
        foreach ($role in $roles) {
            $result = Test-TestingFramework -RoleName $role.Name -RolePath $role.Path
            $results += $result
        }
        
        Write-Header "Validation Summary"
        foreach ($result in $results) {
            $status = if ($result.Score -ge 80) { "EXCELLENT" } elseif ($result.Score -ge 60) { "GOOD" } elseif ($result.Score -ge 40) { "NEEDS IMPROVEMENT" } else { "POOR" }
            $color = if ($result.Score -ge 80) { "Green" } elseif ($result.Score -ge 60) { "Yellow" } else { "Red" }
            
            Write-Host "$($result.RoleName): $($result.Score.ToString('F1'))% - $status" -ForegroundColor $color
            Write-Host "  ✓ Successes: $($result.Successes) | ✗ Issues: $($result.Issues)" -ForegroundColor Gray
        }
        
        $overallScore = ($results | Measure-Object -Property Score -Average).Average
        Write-Info "Overall Implementation Score: $($overallScore.ToString('F1'))%"
    }
    
    "test-all" {
        Write-Header "Running All Data Systems Tests"
        
        $roles = @("mariadb", "neo4j", "minio")
        $results = @()
        
        foreach ($role in $roles) {
            $rolePath = "src\roles\data_systems\$role"
            $result = Invoke-MoleculeTest -RoleName $role -RolePath $rolePath
            $results += @{ Role = $role; Success = $result }
        }
        
        Write-Header "Test Results Summary"
        foreach ($result in $results) {
            $status = if ($result.Success) { "PASSED" } else { "FAILED" }
            $color = if ($result.Success) { "Green" } else { "Red" }
            Write-Host "$($result.Role): $status" -ForegroundColor $color
        }
    }
    
    "test-mariadb" {
        Invoke-MoleculeTest -RoleName "mariadb" -RolePath "src\roles\data_systems\mariadb"
    }
    
    "test-neo4j" {
        Invoke-MoleculeTest -RoleName "neo4j" -RolePath "src\roles\data_systems\neo4j"
    }
    
    "test-minio" {
        Invoke-MoleculeTest -RoleName "minio" -RolePath "src\roles\data_systems\minio"
    }
    
    "help" {
        Write-Header "Data Systems Testing Framework Validator"
        Write-Host ""
        Write-Host "This script validates and tests the implementation of the proven containerized" -ForegroundColor White
        Write-Host "testing pattern across MariaDB, Neo4j, and MinIO data systems." -ForegroundColor White
        Write-Host ""
        Write-Host "USAGE:" -ForegroundColor Yellow
        Write-Host "  .\validate-data-systems-testing.ps1 <action>" -ForegroundColor White
        Write-Host ""
        Write-Host "ACTIONS:" -ForegroundColor Yellow
        Write-Host "  validate     - Validate testing framework structure and completeness" -ForegroundColor White
        Write-Host "  test-all     - Run molecule tests for all data systems" -ForegroundColor White
        Write-Host "  test-mariadb - Run molecule test for MariaDB only" -ForegroundColor White
        Write-Host "  test-neo4j   - Run molecule test for Neo4j only" -ForegroundColor White
        Write-Host "  test-minio   - Run molecule test for MinIO only" -ForegroundColor White
        Write-Host "  help         - Show this help message" -ForegroundColor White
        Write-Host ""
        Write-Host "EXAMPLES:" -ForegroundColor Yellow
        Write-Host "  .\validate-data-systems-testing.ps1 validate" -ForegroundColor Green
        Write-Host "  .\validate-data-systems-testing.ps1 test-all" -ForegroundColor Green
        Write-Host ""
        Write-Host "PREREQUISITES:" -ForegroundColor Yellow
        Write-Host "  - Docker environment must be running for tests" -ForegroundColor White
        Write-Host "  - Use .\src\docker\run-molecule-tests.ps1 start to start environment" -ForegroundColor White
        Write-Host ""
    }
}
