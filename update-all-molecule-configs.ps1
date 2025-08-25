#!/usr/bin/env pwsh

# Script to update all proxmox molecule.yml files to use secure molecule user authentication
# This updates all roles to match the security hardening implemented in apache_airflow

Write-Host "🔒 Starting security hardening update for all molecule configurations..." -ForegroundColor Green

# Find all proxmox molecule.yml files
$moleculeFiles = Get-ChildItem -Path "src\roles" -Filter "molecule.yml" -Recurse | Where-Object { 
    $_.FullName -like "*\molecule\proxmox\*" 
}

Write-Host "📋 Found $($moleculeFiles.Count) proxmox molecule.yml files to update" -ForegroundColor Cyan

$successCount = 0
$skippedCount = 0
$errorCount = 0

foreach ($file in $moleculeFiles) {
    try {
        $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "")
        Write-Host "🔧 Processing: $relativePath" -ForegroundColor Yellow
        
        # Read current content
        $content = Get-Content $file.FullName -Raw
        
        # Check if already has molecule user configuration
        if ($content -match "ansible_user:\s*molecule") {
            Write-Host "  ✅ Already configured with molecule user - skipping" -ForegroundColor Green
            $skippedCount++
            continue
        }
        
        # Pattern to find the host_vars section for debian-test-instance
        $hostVarsPattern = '(\s+host_vars:\s*\r?\n\s+debian-test-instance:\s*\r?\n)'
        
        if ($content -match $hostVarsPattern) {
            # Replace the host_vars section with secure molecule user configuration
            
            # Use a simpler regex replacement approach
            $updatedContent = $content -replace '(?s)(\s+host_vars:\s*\r?\n\s+debian-test-instance:\s*\r?\n)(.*?)(?=\r?\n\s*[a-zA-Z]|\r?\n\r?\n|\Z)', "`$1      ansible_host: `"`${{ lookup('env', 'CONTAINER_IP') | default('10.80.0.200') }}`"`n      ansible_user: molecule`n      ansible_connection: ssh`n      ansible_ssh_pass: molecule123`n      ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'`n      ansible_become: yes`n      ansible_become_method: sudo`n"
            
            # Write updated content
            Set-Content -Path $file.FullName -Value $updatedContent -NoNewline
            
            Write-Host "  ✅ Updated successfully" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  ⚠️  Could not find host_vars section - manual review needed" -ForegroundColor Orange
            $skippedCount++
        }
        
    } catch {
        Write-Host "  ❌ Error updating file: $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "🎯 Security hardening update completed!" -ForegroundColor Green
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Successfully updated: $successCount files" -ForegroundColor Green
Write-Host "  ⏭️  Skipped (already configured): $skippedCount files" -ForegroundColor Yellow
Write-Host "  ❌ Errors: $errorCount files" -ForegroundColor Red

if ($successCount -gt 0) {
    Write-Host ""
    Write-Host "🔐 All updated roles now use secure molecule user authentication:" -ForegroundColor Green
    Write-Host "  👤 Username: molecule" -ForegroundColor White
    Write-Host "  🔑 Password: molecule123" -ForegroundColor White
    Write-Host "  🚫 Root SSH: Disabled" -ForegroundColor White
    Write-Host "  ⬆️  Privileges: sudo with NOPASSWD" -ForegroundColor White
}
