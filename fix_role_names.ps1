#!/usr/bin/env pwsh

# Script to fix incorrect role names in meta files

# Function to get correct role name from path
function Get-CorrectRoleName {
    param($metaFile)
    
    # Extract role name from path - get the parent directory of meta folder
    $roleDir = Split-Path (Split-Path $metaFile -Parent) -Parent
    $roleName = Split-Path $roleDir -Leaf
    return $roleName
}

# Function to fix role name in meta file
function Update-RoleName {
    param($metaFile)
    
    if (Test-Path $metaFile) {
        $correctRoleName = Get-CorrectRoleName $metaFile
        $content = Get-Content $metaFile -Raw
        
        # Replace incorrect role_name with correct one
        if ($content -match "role_name:\s*meta") {
            $newContent = $content -replace "role_name:\s*meta", "role_name: $correctRoleName"
            Set-Content $metaFile -Value $newContent -NoNewline
            Write-Host "Fixed role_name in $metaFile to '$correctRoleName'" -ForegroundColor Green
        } elseif ($content -match "role_name:\s*(\w+)") {
            $currentRoleName = $matches[1]
            if ($currentRoleName -ne $correctRoleName) {
                $newContent = $content -replace "role_name:\s*$currentRoleName", "role_name: $correctRoleName"
                Set-Content $metaFile -Value $newContent -NoNewline
                Write-Host "Updated role_name in $metaFile from '$currentRoleName' to '$correctRoleName'" -ForegroundColor Yellow
            } else {
                Write-Host "Role name is already correct in $metaFile" -ForegroundColor Gray
            }
        } else {
            Write-Host "No role_name found in $metaFile" -ForegroundColor Red
        }
    }
}

# Find all meta/main.yml files
$metaFiles = Get-ChildItem -Path "src\roles" -Recurse -Filter "main.yml" | Where-Object {
    $_.Directory.Name -eq "meta"
} | ForEach-Object {
    $_.FullName
}

Write-Host "Found $($metaFiles.Count) meta files to fix" -ForegroundColor Cyan

foreach ($metaFile in $metaFiles) {
    $correctRoleName = Get-CorrectRoleName $metaFile
    Write-Host "Processing $metaFile (should be '$correctRoleName')"
    Update-RoleName $metaFile
}

Write-Host "Completed fixing role names!" -ForegroundColor Green
