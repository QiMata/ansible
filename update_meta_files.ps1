#!/usr/bin/env pwsh

# Enhanced script to add role_name and namespace to all Ansible roles

# Define namespace mappings based on role categories
$namespaceMap = @{
    "data_analytics" = "data_analytics"
    "data_systems" = "data_systems" 
    "devops_cicd" = "devops_cicd"
    "infrastructure" = "infrastructure"
    "load_balancing_ha" = "load_balancing_ha"
    "monitoring_observability" = "monitoring_observability"
    "networking" = "networking"
    "operations_management" = "operations_management"
    "security_identity" = "security_identity"
}

# Function to get namespace for a role path
function Get-Namespace {
    param($rolePath)
    
    foreach ($category in $namespaceMap.Keys) {
        if ($rolePath -like "*\$category\*") {
            return $namespaceMap[$category]
        }
    }
    return "example_inc"  # Default namespace
}

# Function to get role name from path
function Get-RoleName {
    param($metaFile)
    
    # Extract role name from path - get the parent directory of meta folder
    $roleDir = Split-Path (Split-Path $metaFile -Parent) -Parent
    $roleName = Split-Path $roleDir -Leaf
    return $roleName
}

# Function to add namespace and role_name to a meta file
function Update-MetaFile {
    param($metaFile, $namespace, $roleName)
    
    if (Test-Path $metaFile) {
        $content = Get-Content $metaFile -Raw
        
        # Check if both namespace and role_name already exist
        $hasNamespace = $content -match "namespace:\s*\w+"
        $hasRoleName = $content -match "role_name:\s*\w+"
        
        if ($hasNamespace -and $hasRoleName) {
            Write-Host "Both namespace and role_name already exist in $metaFile" -ForegroundColor Yellow
            return
        }
        
        # Add role_name and namespace after galaxy_info:
        if ($content -match "galaxy_info:\s*\n") {
            $newLines = ""
            
            if (-not $hasRoleName) {
                $newLines += "  role_name: $roleName`n"
            }
            
            if (-not $hasNamespace) {
                $newLines += "  namespace: $namespace`n"
            }
            
            if ($newLines) {
                $newContent = $content -replace "(galaxy_info:\s*\n)", "`$1$newLines"
                Set-Content $metaFile -Value $newContent -NoNewline
                Write-Host "Updated $metaFile with role_name '$roleName' and namespace '$namespace'" -ForegroundColor Green
            }
        } else {
            Write-Host "Could not find galaxy_info section in $metaFile" -ForegroundColor Red
        }
    }
}

# Find all meta/main.yml files
$metaFiles = Get-ChildItem -Path "src\roles" -Recurse -Filter "main.yml" | Where-Object {
    $_.Directory.Name -eq "meta"
} | ForEach-Object {
    $_.FullName
}

Write-Host "Found $($metaFiles.Count) meta files to process" -ForegroundColor Cyan

foreach ($metaFile in $metaFiles) {
    $namespace = Get-Namespace $metaFile
    $roleName = Get-RoleName $metaFile
    Write-Host "Processing $metaFile with role_name '$roleName' and namespace '$namespace'"
    Update-MetaFile $metaFile $namespace $roleName
}

Write-Host "Completed updating all meta files!" -ForegroundColor Green
