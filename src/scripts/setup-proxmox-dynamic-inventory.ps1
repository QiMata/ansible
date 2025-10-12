#!/usr/bin/env pwsh
# Setup Proxmox Dynamic Inventory - Manual Installation Script

param(
    [Parameter(Mandatory=$false)]
    [string]$ProxmoxUrl = "https://your-proxmox-server:8006",

    [Parameter(Mandatory=$false)]
    [string]$ProxmoxUser = "ansible@pve",

    [Parameter(Mandatory=$false)]
    [string]$ProxmoxPassword = "",

    [Parameter(Mandatory=$false)]
    [switch]$CreateVaultFile
)

Write-Host "=== Proxmox Dynamic Inventory Setup ===" -ForegroundColor Green

# Step 1: Check Python and pip
Write-Host "`n1. Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Step 2: Install required Python packages
Write-Host "`n2. Installing required Python packages..." -ForegroundColor Yellow
$packages = @("ansible", "proxmoxer", "requests")

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    try {
        pip install $package --quiet
        Write-Host "✓ $package installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to install $package" -ForegroundColor Red
    }
}

# Step 3: Create collections directory and download manually
Write-Host "`n3. Setting up Ansible collections..." -ForegroundColor Yellow

$collectionsPath = "collections\ansible_collections"
if (-not (Test-Path $collectionsPath)) {
    New-Item -Path $collectionsPath -ItemType Directory -Force | Out-Null
    Write-Host "✓ Created collections directory" -ForegroundColor Green
}

# Manual collection setup instructions
Write-Host "`n4. Manual Collection Setup Required:" -ForegroundColor Yellow
Write-Host "Due to Windows compatibility issues with ansible-galaxy, please manually download the collections:" -ForegroundColor White
Write-Host ""
Write-Host "For community.general collection:" -ForegroundColor Cyan
Write-Host "1. Visit: https://galaxy.ansible.com/community/general" -ForegroundColor White
Write-Host "2. Download the latest version" -ForegroundColor White
Write-Host "3. Extract to: $collectionsPath\community\general" -ForegroundColor White
Write-Host ""
Write-Host "For community.proxmox collection:" -ForegroundColor Cyan
Write-Host "1. Visit: https://galaxy.ansible.com/community/proxmox" -ForegroundColor White
Write-Host "2. Download the latest version" -ForegroundColor White
Write-Host "3. Extract to: $collectionsPath\community\proxmox" -ForegroundColor White
Write-Host ""

# Step 5: Configure dynamic inventory
Write-Host "`n5. Configuring Proxmox dynamic inventory..." -ForegroundColor Yellow

# Update the proxmox.yml with provided values
if ($ProxmoxUrl -ne "https://your-proxmox-server:8006" -or $ProxmoxUser -ne "ansible@pve" -or $ProxmoxPassword -ne "") {
    $configPath = "inventories\dynamic\proxmox.yml"
    if (Test-Path $configPath) {
        $config = Get-Content $configPath -Raw
        $config = $config -replace "url: https://your-proxmox-server:8006", "url: $ProxmoxUrl"
        $config = $config -replace "user: ansible@pve", "user: $ProxmoxUser"
        if ($ProxmoxPassword -ne "") {
            $config = $config -replace "password: your-password", "password: $ProxmoxPassword"
        }
        Set-Content -Path $configPath -Value $config
        Write-Host "✓ Updated $configPath with your settings" -ForegroundColor Green
    }
}

# Step 6: Create vault file if requested
if ($CreateVaultFile -and $ProxmoxPassword -ne "") {
    Write-Host "`n6. Creating vault file..." -ForegroundColor Yellow
    $vaultPath = "inventories\dynamic\vault_proxmox.yml"
    
    $vaultContent = @"
---
# Proxmox connection details
vault_proxmox_url: "$ProxmoxUrl"
vault_proxmox_user: "$ProxmoxUser"
vault_proxmox_password: "$ProxmoxPassword"
"@
    
    Set-Content -Path $vaultPath -Value $vaultContent
    Write-Host "✓ Created vault file at $vaultPath" -ForegroundColor Green
    Write-Host "⚠  Remember to encrypt this file with: ansible-vault encrypt $vaultPath" -ForegroundColor Yellow
}

# Step 7: Test configuration
Write-Host "`n7. Testing dynamic inventory..." -ForegroundColor Yellow
Write-Host "To test your configuration, run:" -ForegroundColor White
Write-Host "python -c `"import yaml; print('YAML parser OK')`"" -ForegroundColor Cyan
Write-Host ""

# Step 8: Usage instructions
Write-Host "`n=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Download and install the community.general and community.proxmox collections manually (see above)" -ForegroundColor White
Write-Host "2. Configure your Proxmox credentials in src\inventories\dynamic\proxmox.yml" -ForegroundColor White
Write-Host "3. Test the connection:" -ForegroundColor White
Write-Host "   python -c `"from proxmoxer import ProxmoxAPI; print('Proxmoxer OK')`"" -ForegroundColor Cyan
Write-Host "4. Test inventory listing:" -ForegroundColor White
Write-Host "   python -c `"import yaml; print(yaml.safe_load(open('src/inventories/dynamic/proxmox.yml')))`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Use with ansible-playbook:" -ForegroundColor White
Write-Host "   ansible-playbook -i src/inventories/dynamic/proxmox.yml src/playbooks/site.yml" -ForegroundColor Cyan
Write-Host ""

Write-Host "Setup completed! Please follow the manual steps above." -ForegroundColor Green
