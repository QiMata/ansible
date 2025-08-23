# PowerShell test script to verify the Molecule Proxmox Docker setup

param(
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

if ($Verbose) {
    $VerbosePreference = "Continue"
}

# Colors for output
function Write-TestResult {
    param(
        [string]$Test,
        [bool]$Success,
        [string]$Message = ""
    )
    
    $status = if ($Success) { "✓" } else { "✗" }
    $color = if ($Success) { "Green" } else { "Red" }
    
    Write-Host "$Test " -NoNewline
    Write-Host $status -ForegroundColor $color
    
    if ($Message) {
        Write-Host "  $Message" -ForegroundColor Gray
    }
}

Write-Host "=== Molecule Proxmox Docker Setup Test ===" -ForegroundColor Yellow

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

$allTestsPassed = $true

# Test 1: Check if Docker is available
try {
    $null = Get-Command docker -ErrorAction Stop
    Write-TestResult "Checking Docker availability..." $true
} catch {
    Write-TestResult "Checking Docker availability..." $false "Docker is not installed or not in PATH"
    $allTestsPassed = $false
}

# Test 2: Check if Docker Compose is available
try {
    $null = Get-Command docker-compose -ErrorAction Stop
    Write-TestResult "Checking Docker Compose availability..." $true
} catch {
    Write-TestResult "Checking Docker Compose availability..." $false "Docker Compose is not installed or not in PATH"
    $allTestsPassed = $false
}

# Test 3: Check if Docker daemon is running
try {
    $null = docker info 2>$null
    Write-TestResult "Checking Docker daemon..." $true
} catch {
    Write-TestResult "Checking Docker daemon..." $false "Docker daemon is not running"
    $allTestsPassed = $false
}

# Test 4: Check if required files exist
$dockerfilePath = Join-Path $ScriptDir "Dockerfile.molecule-proxmox"
if (Test-Path $dockerfilePath) {
    Write-TestResult "Checking Dockerfile..." $true
} else {
    Write-TestResult "Checking Dockerfile..." $false "Dockerfile.molecule-proxmox not found"
    $allTestsPassed = $false
}

$composePath = Join-Path $ScriptDir "docker-compose.molecule.yml"
if (Test-Path $composePath) {
    Write-TestResult "Checking Docker Compose file..." $true
} else {
    Write-TestResult "Checking Docker Compose file..." $false "docker-compose.molecule.yml not found"
    $allTestsPassed = $false
}

$moleculePath = Join-Path $ProjectRoot "src\molecule\proxmox\molecule.yml"
if (Test-Path $moleculePath) {
    Write-TestResult "Checking molecule configuration..." $true
} else {
    Write-TestResult "Checking molecule configuration..." $false "molecule.yml not found in src\molecule\proxmox\"
    $allTestsPassed = $false
}

# Test 5: Check environment file
$envPath = Join-Path $ProjectRoot "src\molecule\proxmox\.env"
$envExamplePath = Join-Path $ProjectRoot "src\molecule\proxmox\.env.example"

if (Test-Path $envPath) {
    Write-TestResult "Checking environment configuration..." $true "Environment file found at src\molecule\proxmox\.env"
} elseif (Test-Path $envExamplePath) {
    Write-Host "Checking environment configuration... " -NoNewline
    Write-Host "!" -ForegroundColor Yellow
    Write-Host "  Environment example found. Copy .env.example to .env and configure it." -ForegroundColor Gray
} else {
    Write-TestResult "Checking environment configuration..." $false "No environment configuration found"
    $allTestsPassed = $false
}

# Test 6: Try building the Docker image (optional, can be slow)
if ($Verbose) {
    Write-Host "Testing Docker image build... " -NoNewline
    try {
        Set-Location $ProjectRoot
        $buildOutput = docker build -f src\docker\Dockerfile.molecule-proxmox -t ansible-molecule-proxmox:test . 2>&1
        Write-Host "✓" -ForegroundColor Green
        Write-Host "  Docker image built successfully" -ForegroundColor Gray
        
        # Clean up test image
        try {
            docker rmi ansible-molecule-proxmox:test | Out-Null
        } catch {
            # Ignore cleanup errors
        }
    } catch {
        Write-Host "✗" -ForegroundColor Red
        Write-Host "  Failed to build Docker image" -ForegroundColor Gray
        Write-Verbose "Build output: $buildOutput"
        $allTestsPassed = $false
    }
}

Write-Host ""

if ($allTestsPassed) {
    Write-Host "=== All tests passed! ===" -ForegroundColor Green
    Write-Host "Your Molecule Proxmox Docker setup is ready."
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Configure your Proxmox credentials in src\molecule\proxmox\.env"
    Write-Host "2. Run: .\run-molecule-tests.ps1 build"
    Write-Host "3. Run: .\run-molecule-tests.ps1 start"
    Write-Host "4. Run: .\run-molecule-tests.ps1 test"
} else {
    Write-Host "=== Some tests failed ===" -ForegroundColor Red
    Write-Host "Please fix the issues above before proceeding."
    exit 1
}
