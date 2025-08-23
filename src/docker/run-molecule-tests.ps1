# PowerShell Script for Molecule Proxmox Docker Testing
# This script provides easy commands to run molecule tests in Docker on Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "start", "stop", "shell", "test", "create", "converge", "destroy", "logs", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$Scenario = "proxmox"
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

# Function to check if .env file exists
function Test-EnvFile {
    $EnvFile = Join-Path $ScriptDir ".env"
    $ProxmoxEnvFile = Join-Path $ProjectRoot "src\molecule\proxmox\.env"
    $ProxmoxEnvExample = Join-Path $ProjectRoot "src\molecule\proxmox\.env.example"
    
    # Check for .env in docker directory first
    if (Test-Path $EnvFile) {
        return $EnvFile
    }
    
    # Check for .env in proxmox directory
    if (Test-Path $ProxmoxEnvFile) {
        return $ProxmoxEnvFile
    }
    
    # If neither exists, create from example
    if (Test-Path $ProxmoxEnvExample) {
        Write-Warning "No .env file found. Creating from template..."
        Copy-Item $ProxmoxEnvExample $EnvFile
        Write-Warning "Please edit $EnvFile with your Proxmox credentials"
        return $EnvFile
    } else {
        Write-Error ".env.example file not found!"
        return $null
    }
}

# Function to load environment variables
function Import-EnvFile {
    $EnvFilePath = Test-EnvFile
    if ($EnvFilePath -and (Test-Path $EnvFilePath)) {
        Write-Info "Loading environment variables from .env file..."
        Get-Content $EnvFilePath | ForEach-Object {
            if ($_ -match "^([^#=]+)=(.*)$") {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }
        return $true
    }
    return $false
}

# Function to build the Docker image
function Build-Image {
    Write-Info "Building molecule-proxmox Docker image..."
    Set-Location $ProjectRoot
    docker-compose -f $DockerComposeFile build
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully"
    } else {
        Write-Error "Failed to build Docker image"
        exit 1
    }
}

# Function to start the container
function Start-Container {
    Write-Info "Starting molecule-proxmox container..."
    Set-Location $ProjectRoot
    docker-compose -f $DockerComposeFile up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container started successfully"
    } else {
        Write-Error "Failed to start container"
        exit 1
    }
}

# Function to stop the container
function Stop-Container {
    Write-Info "Stopping molecule-proxmox container..."
    Set-Location $ProjectRoot
    docker-compose -f $DockerComposeFile down
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container stopped successfully"
    } else {
        Write-Error "Failed to stop container"
        exit 1
    }
}

# Function to enter the container shell
function Enter-Shell {
    Write-Info "Entering container shell..."
    docker-compose -f $DockerComposeFile exec molecule-proxmox /bin/bash
}

# Function to run molecule test
function Invoke-Test {
    param([string]$TestScenario)
    Write-Info "Running molecule test for scenario: $TestScenario"
    
    docker-compose -f $DockerComposeFile exec molecule-proxmox bash -c "cd /ansible/src && molecule test -s $TestScenario"
}

# Function to run molecule create only
function Invoke-Create {
    param([string]$TestScenario)
    Write-Info "Running molecule create for scenario: $TestScenario"
    
    docker-compose -f $DockerComposeFile exec molecule-proxmox bash -c "cd /ansible/src && molecule create -s $TestScenario"
}

# Function to run molecule converge only
function Invoke-Converge {
    param([string]$TestScenario)
    Write-Info "Running molecule converge for scenario: $TestScenario"
    
    docker-compose -f $DockerComposeFile exec molecule-proxmox bash -c "cd /ansible/src && molecule converge -s $TestScenario"
}

# Function to run molecule destroy only
function Invoke-Destroy {
    param([string]$TestScenario)
    Write-Info "Running molecule destroy for scenario: $TestScenario"
    
    docker-compose -f $DockerComposeFile exec molecule-proxmox bash -c "cd /ansible/src && molecule destroy -s $TestScenario"
}

# Function to show logs
function Show-Logs {
    docker-compose -f $DockerComposeFile logs -f molecule-proxmox
}

# Function to show usage
function Show-Usage {
    @"
Usage: .\run-molecule-tests.ps1 [COMMAND] [SCENARIO]

Commands:
    build           Build the molecule-proxmox Docker image
    start           Start the molecule-proxmox container
    stop            Stop the molecule-proxmox container  
    shell           Enter the container shell
    test [scenario] Run full molecule test (default: proxmox)
    create [scenario] Run molecule create only
    converge [scenario] Run molecule converge only
    destroy [scenario] Run molecule destroy only
    logs            Show container logs
    help            Show this help message

Examples:
    .\run-molecule-tests.ps1 build
    .\run-molecule-tests.ps1 start
    .\run-molecule-tests.ps1 test
    .\run-molecule-tests.ps1 test proxmox
    .\run-molecule-tests.ps1 create
    .\run-molecule-tests.ps1 shell
    .\run-molecule-tests.ps1 stop

Before running tests, make sure to:
1. Copy .env.example to .env in src\molecule\proxmox\
2. Configure your Proxmox credentials in the .env file
3. Ensure network connectivity to your Proxmox server
4. Have Docker Desktop running on Windows

"@
}

# Main execution logic
try {
    switch ($Command) {
        "build" {
            Import-EnvFile
            Build-Image
        }
        "start" {
            Import-EnvFile
            Start-Container
        }
        "stop" {
            Stop-Container
        }
        "shell" {
            Enter-Shell
        }
        "test" {
            Invoke-Test $Scenario
        }
        "create" {
            Invoke-Create $Scenario
        }
        "converge" {
            Invoke-Converge $Scenario
        }
        "destroy" {
            Invoke-Destroy $Scenario
        }
        "logs" {
            Show-Logs
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
