#!/usr/bin/env pwsh

# Script to add namespaces to all Ansible roles based on their category

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

# Function to add namespace to a meta file
function Add-Namespace {
    param($metaFile, $namespace)
    
    if (Test-Path $metaFile) {
        $content = Get-Content $metaFile -Raw
        
        # Check if namespace already exists
        if ($content -match "namespace:\s*\w+") {
            Write-Host "Namespace already exists in $metaFile" -ForegroundColor Yellow
            return
        }
        
        # Add namespace after role_name
        if ($content -match "role_name:\s*(\w+)") {
            $newContent = $content -replace "(role_name:\s*\w+)", "`$1`n  namespace: $namespace"
            Set-Content $metaFile -Value $newContent -NoNewline
            Write-Host "Added namespace '$namespace' to $metaFile" -ForegroundColor Green
        } else {
            Write-Host "Could not find role_name in $metaFile" -ForegroundColor Red
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
    Write-Host "Processing $metaFile with namespace '$namespace'"
    Add-Namespace $metaFile $namespace
}

Write-Host "Completed adding namespaces to all roles!" -ForegroundColor Green
