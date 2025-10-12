# Script to fix molecule.yml paths for data analytics roles

$DataAnalyticsRoles = @(
    "airflow\apache_airflow",
    "airflow\airflow_connector", 
    "amundsen\amundsen_metadata",
    "apache_superset",
    "spark_role"
)

$ProjectRoot = "G:\Code\Ansible2"

foreach ($role in $DataAnalyticsRoles) {
    $moleculeYmlPath = Join-Path $ProjectRoot "src\roles\data_analytics\$role\molecule\proxmox\molecule.yml"
    
    if (Test-Path $moleculeYmlPath) {
        Write-Host "Fixing molecule.yml for role: $role" -ForegroundColor Green
        
        # Read the current content
        $content = Get-Content $moleculeYmlPath -Raw
        
        # Calculate the correct relative path from this role to the shared proxmox files
        # From src/roles/data_analytics/[category]/[role]/molecule/proxmox/ to src/molecule/proxmox/
        $pathDepth = ($role -split "\\").Length + 4  # data_analytics + role parts + molecule + proxmox
        $relativePath = ("..\" * $pathDepth) + "molecule\proxmox"
        $relativePath = $relativePath.Replace("\", "/")
        
        Write-Host "  Using path: $relativePath" -ForegroundColor Yellow
        
        # Replace the playbook paths
        $content = $content -replace "create: .*?/create\.yml", "create: $relativePath/create.yml"
        $content = $content -replace "destroy: .*?/destroy\.yml", "destroy: $relativePath/destroy.yml"
        
        # Write back the fixed content
        Set-Content $moleculeYmlPath -Value $content -NoNewline
        
        Write-Host "  Fixed!" -ForegroundColor Green
    } else {
        Write-Host "Molecule file not found for role: $role" -ForegroundColor Red
    }
}

Write-Host "Done fixing molecule paths!" -ForegroundColor Cyan
