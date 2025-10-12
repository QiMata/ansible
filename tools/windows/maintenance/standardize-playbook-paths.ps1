#!/usr/bin/env pwsh

# Script to standardize playbook paths in molecule configurations
Write-Host "Standardizing playbook paths in molecule configurations..." -ForegroundColor Green

# Find all proxmox molecule.yml files
$moleculeFiles = Get-ChildItem -Path "src\roles" -Filter "molecule.yml" -Recurse | Where-Object { 
    $_.FullName -like "*\molecule\proxmox\*" 
}

$updateCount = 0

foreach ($file in $moleculeFiles) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    
    # Count the number of directory levels from the molecule file to src/molecule/proxmox
    $relativePath = $file.FullName.Replace((Get-Location).Path + '\', '')
    $pathParts = $relativePath.Split('\')
    
    # Find the depth - molecule files are typically at: src/roles/category/role/molecule/proxmox/molecule.yml
    # We need to go back to src level: ../../../../../../molecule/proxmox/
    $depth = ($pathParts | Where-Object { $_ -ne "src" -and $_ -ne "roles" }).Count - 3  # -3 for molecule/proxmox/molecule.yml
    $backPath = "../" * ($depth + 2)  # +2 to get past roles directory to src
    $centralPath = $backPath + "../molecule/proxmox/"
    
    # Update create and destroy paths to use centralized versions
    $content = $content -replace 'create:\s*[^\r\n]*', "create: ${centralPath}create.yml"
    $content = $content -replace 'destroy:\s*[^\r\n]*', "destroy: ${centralPath}destroy.yml"
    
    # Update prepare path to use centralized version
    $content = $content -replace 'prepare:\s*[^\r\n]*', "prepare: ${centralPath}prepare.yml"
    
    if ($content -ne $originalContent) {
        Write-Host "UPDATE: $relativePath" -ForegroundColor Cyan
        Set-Content -Path $file.FullName -Value $content -NoNewline
        $updateCount++
    }
}

Write-Host ""
Write-Host "Playbook path standardization completed!" -ForegroundColor Green
Write-Host "Updated: $updateCount files" -ForegroundColor Green
