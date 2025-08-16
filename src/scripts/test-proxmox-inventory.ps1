#!/usr/bin/env pwsh
# Test Proxmox Dynamic Inventory Script

param(
    [Parameter(Mandatory=$false)]
    [string]$InventoryFile = "inventories\dynamic\proxmox.yml",
    
    [Parameter(Mandatory=$false)]
    [switch]$UseVault,
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowGraph
)

Write-Host "Testing Proxmox Dynamic Inventory..." -ForegroundColor Green

# Change to src directory
Set-Location -Path "src"

if ($UseVault) {
    $InventoryFile = "inventories\dynamic\proxmox-vault.yml"
    Write-Host "Using vault-based configuration: $InventoryFile" -ForegroundColor Yellow
    
    # Test with vault
    Write-Host "Running: ansible-inventory -i $InventoryFile --list --vault-password-file vault_pass.txt" -ForegroundColor Cyan
    ansible-inventory -i $InventoryFile --list --vault-password-file vault_pass.txt
} else {
    Write-Host "Using direct configuration: $InventoryFile" -ForegroundColor Yellow
    
    # Test without vault
    Write-Host "Running: ansible-inventory -i $InventoryFile --list" -ForegroundColor Cyan
    ansible-inventory -i $InventoryFile --list
}

if ($ShowGraph) {
    Write-Host "`nGenerating inventory graph..." -ForegroundColor Green
    if ($UseVault) {
        ansible-inventory -i $InventoryFile --graph --vault-password-file vault_pass.txt
    } else {
        ansible-inventory -i $InventoryFile --graph
    }
}

Write-Host "`nInventory test completed!" -ForegroundColor Green
