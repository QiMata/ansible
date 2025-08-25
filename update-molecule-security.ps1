#!/usr/bin/env pwsh

# Simple script to update molecule configurations with secure authentication
Write-Host "Starting security hardening update for all molecule configurations..." -ForegroundColor Green

# Find all proxmox molecule.yml files that still use root user
$moleculeFiles = Get-ChildItem -Path "src\roles" -Filter "molecule.yml" -Recurse | Where-Object { 
    $_.FullName -like "*\molecule\proxmox\*" 
}

$updateCount = 0
$skippedCount = 0

foreach ($file in $moleculeFiles) {
    $content = Get-Content $file.FullName -Raw
    
    # Skip if already has molecule user
    if ($content -match "ansible_user:\s*molecule") {
        Write-Host "SKIP: $($file.Name) - already configured" -ForegroundColor Yellow
        $skippedCount++
        continue
    }
    
    # Update root user to molecule user
    if ($content -match "ansible_user:\s*root") {
        Write-Host "UPDATE: $($file.FullName.Replace((Get-Location).Path + '\', ''))" -ForegroundColor Cyan
        
        # Replace authentication settings
        $newContent = $content -replace 'ansible_user:\s*root', 'ansible_user: molecule'
        $newContent = $newContent -replace 'ansible_ssh_pass:\s*"[^"]*"', 'ansible_ssh_pass: molecule123'
        
        # Add become settings if not present
        if ($newContent -notmatch "ansible_become:") {
            $newContent = $newContent -replace '(ansible_ssh_common_args:[^\r\n]*)', "`$1`n        ansible_become: yes`n        ansible_become_method: sudo"
        }
        
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        $updateCount++
    } else {
        Write-Host "SKIP: $($file.Name) - no root user found" -ForegroundColor DarkYellow
        $skippedCount++
    }
}

Write-Host ""
Write-Host "Security hardening completed!" -ForegroundColor Green
Write-Host "Updated: $updateCount files" -ForegroundColor Green
Write-Host "Skipped: $skippedCount files" -ForegroundColor Yellow
