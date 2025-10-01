param(
  [string]$EnvFile = (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) '.env'),
  [string[]]$Images = @('postgresql-node','mariadb-node','elasticsearch-node','minio-node','neo4j-node','docker-host','k3s-node','jenkins-agent','haproxy','keepalived','bind9','apt-mirror','container-registry'),
  [switch]$Become,
  [switch]$StopOnError
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot  = Split-Path -Parent (Split-Path -Parent $scriptDir)
$srcDir    = Join-Path $repoRoot 'src'

function Invoke-TemplateBuild {
  param([string]$Image)
  $playbook = "images/$Image/playbook.yml"
  $playbookPath = Join-Path $srcDir $playbook
  if (!(Test-Path $playbookPath)) {
    Write-Warning "Playbook not found for image '$Image': $playbookPath"
    return $false
  }
  $args = @('-File', (Join-Path $scriptDir 'create-hardened-debian-template.ps1'), '-EnvFile', $EnvFile, '-Playbook', $playbook)
  if ($Become.IsPresent) { $args += '-Become' }
  Write-Host "[INFO] Building hardened template for '$Image' using $playbook" -ForegroundColor Cyan
  & pwsh @args
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "Build failed for $Image (exit $LASTEXITCODE)"
    return $false
  }
  return $true
}

$allOk = $true
foreach ($img in $Images) {
  if (-not (Invoke-TemplateBuild -Image $img)) {
    $allOk = $false
    if ($StopOnError) { exit 1 }
  }
}

if ($allOk) { exit 0 } else { exit 1 }

