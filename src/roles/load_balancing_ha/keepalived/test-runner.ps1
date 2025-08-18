# Comprehensive test runner for keepalived role (PowerShell version)
# This script runs all molecule scenarios and validates the role functionality

param(
    [Parameter(Position=0)]
    [ValidateSet("", "lint", "syntax", "scenario", "list", "help")]
    [string]$Command = "",
    
    [Parameter(Position=1)]
    [string]$ScenarioName = ""
)

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-Log {
    param([string]$Message, [string]$Color = "Blue")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Colors[$Color]
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check prerequisites
function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check if molecule is installed
    try {
        $null = Get-Command molecule -ErrorAction Stop
    }
    catch {
        Write-Error "Molecule is not installed. Install with: pip install molecule[docker]"
        exit 1
    }
    
    # Check if docker is running
    try {
        $null = docker info 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker check failed"
        }
    }
    catch {
        Write-Error "Docker is not running or not accessible"
        exit 1
    }
    
    # Check if ansible is installed
    try {
        $null = Get-Command ansible -ErrorAction Stop
    }
    catch {
        Write-Error "Ansible is not installed"
        exit 1
    }
    
    Write-Success "All prerequisites met"
}

# Test a specific scenario
function Test-Scenario {
    param([string]$Scenario)
    
    Write-Log "Testing scenario: $Scenario"
    
    if (-not (Test-Path "molecule\$Scenario")) {
        Write-Warning "Scenario $Scenario does not exist, skipping..."
        return $true
    }
    
    # Run the full test cycle
    molecule test -s $Scenario
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Scenario $Scenario passed"
        return $true
    }
    else {
        Write-Error "Scenario $Scenario failed"
        return $false
    }
}

# Lint the role
function Test-Lint {
    Write-Log "Running role linting..."
    
    # Ansible lint
    try {
        $null = Get-Command ansible-lint -ErrorAction Stop
        Write-Log "Running ansible-lint..."
        ansible-lint .
    }
    catch {
        Write-Warning "ansible-lint not found, skipping..."
    }
    
    # YAML lint
    try {
        $null = Get-Command yamllint -ErrorAction Stop
        Write-Log "Running yamllint..."
        yamllint .
    }
    catch {
        Write-Warning "yamllint not found, skipping..."
    }
    
    Write-Success "Linting completed"
}

# Run syntax check
function Test-Syntax {
    Write-Log "Running syntax checks..."
    
    # Check playbook syntax
    $playbooks = Get-ChildItem -Path "examples\*.yml" -ErrorAction SilentlyContinue
    foreach ($playbook in $playbooks) {
        Write-Log "Checking syntax of $($playbook.Name)"
        ansible-playbook --syntax-check $playbook.FullName
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Syntax check failed for $($playbook.Name)"
            return $false
        }
    }
    
    Write-Success "Syntax checks passed"
    return $true
}

# Generate test report
function New-TestReport {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $resultsFile = "test_results_$timestamp.txt"
    
    Write-Log "Generating test report: $resultsFile"
    
    $reportContent = @"
Keepalived Role Test Report
Generated: $(Get-Date)
Role Directory: $ScriptDir

Test Scenarios Run:
"@
    
    $scenarios = Get-ChildItem -Path "molecule" -Directory | ForEach-Object { "- $($_.Name)" }
    $reportContent += "`r`n" + ($scenarios -join "`r`n")
    $reportContent += "`r`n`r`nTest completed successfully"
    
    $reportContent | Out-File -FilePath $resultsFile -Encoding UTF8
    
    Write-Success "Test report generated: $resultsFile"
}

# List available scenarios
function Get-Scenarios {
    Write-Host "Available scenarios:"
    $scenarios = Get-ChildItem -Path "molecule" -Directory -ErrorAction SilentlyContinue
    foreach ($scenario in $scenarios) {
        Write-Host "  - $($scenario.Name)"
    }
}

# Main execution
function Invoke-Main {
    Write-Log "Starting comprehensive tests for keepalived role"
    Write-Log "Role directory: $ScriptDir"
    
    # Track failed scenarios
    $failedScenarios = @()
    
    # Run checks
    Test-Prerequisites
    
    # Lint the role
    try {
        Test-Lint
    }
    catch {
        Write-Warning "Linting issues found, but continuing with tests"
    }
    
    # Syntax check
    if (-not (Test-Syntax)) {
        Write-Error "Syntax checks failed"
        exit 1
    }
    
    # List available scenarios
    Write-Log "Available test scenarios:"
    $scenarios = Get-ChildItem -Path "molecule" -Directory -ErrorAction SilentlyContinue
    foreach ($scenario in $scenarios) {
        Write-Host "  - $($scenario.Name)"
    }
    
    # Test each scenario
    foreach ($scenario in $scenarios) {
        if (-not (Test-Scenario $scenario.Name)) {
            $failedScenarios += $scenario.Name
        }
    }
    
    # Report results
    Write-Host ""
    Write-Log "Test Summary:"
    
    if ($failedScenarios.Count -eq 0) {
        Write-Success "All test scenarios passed!"
        New-TestReport
        exit 0
    }
    else {
        Write-Error "The following scenarios failed:"
        foreach ($scenario in $failedScenarios) {
            Write-Host "  - $scenario"
        }
        exit 1
    }
}

# Handle command line arguments
switch ($Command) {
    "lint" {
        Test-Prerequisites
        Test-Lint
    }
    "syntax" {
        Test-Prerequisites
        Test-Syntax
    }
    "scenario" {
        if ([string]::IsNullOrEmpty($ScenarioName)) {
            Write-Error "Please specify a scenario name"
            exit 1
        }
        Test-Prerequisites
        Test-Scenario $ScenarioName
    }
    "list" {
        Get-Scenarios
    }
    "help" {
        Write-Host @"
Keepalived Role Test Runner (PowerShell)

Usage: .\test-runner.ps1 [command] [options]

Commands:
  (no command)    Run all tests
  lint            Run linting only
  syntax          Run syntax checks only
  scenario NAME   Run specific scenario
  list            List available scenarios
  help            Show this help

Examples:
  .\test-runner.ps1                    # Run all tests
  .\test-runner.ps1 lint              # Run linting only
  .\test-runner.ps1 scenario default  # Run default scenario only
  .\test-runner.ps1 list              # List available scenarios

"@
    }
    default {
        Invoke-Main
    }
}
