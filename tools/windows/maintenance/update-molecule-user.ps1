# PowerShell script to update molecule user configurations
$dataAnalyticsPath = "g:\Code\Ansible2\src\roles\data_analytics"
$proxmoxMoleculeFiles = Get-ChildItem -Path $dataAnalyticsPath -Recurse -Name "*molecule.yml" | Where-Object { $_ -like "*proxmox*" }

Write-Host "[INFO] Found $($proxmoxMoleculeFiles.Count) data analytics proxmox molecule files to update"

foreach ($file in $proxmoxMoleculeFiles) {
    $fullPath = Join-Path $dataAnalyticsPath $file
    Write-Host "[INFO] Updating $fullPath"
    
    $content = Get-Content $fullPath -Raw
    
    # Update ansible_user from root to molecule
    if ($content -match "ansible_user: root") {
        $content = $content -replace "ansible_user: root", "ansible_user: molecule"
        Write-Host "  - Updated ansible_user to molecule"
    }
    
    # Update password reference
    if ($content -match 'ansible_ssh_pass: "\{\{ lookup\(''env'', ''CONTAINER_PASSWORD''\) \| default\(''molecule12345''\) \}\}"') {
        $content = $content -replace 'ansible_ssh_pass: "\{\{ lookup\(''env'', ''CONTAINER_PASSWORD''\) \| default\(''molecule12345''\) \}\}"', "ansible_ssh_pass: molecule123"
        Write-Host "  - Updated ssh password"
    }
    
    # Add become configuration if not present
    if ($content -notmatch "ansible_become:") {
        $content = $content -replace "(ansible_ssh_common_args:.*)", "`$1`n        ansible_become: yes`n        ansible_become_method: sudo"
        Write-Host "  - Added become configuration"
    }
    
    Set-Content $fullPath $content
}

Write-Host "[SUCCESS] Updated all data analytics proxmox molecule configurations"
