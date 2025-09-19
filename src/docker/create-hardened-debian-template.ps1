<#
.SYNOPSIS
  Create a hardened Debian Proxmox LXC template using the same Docker + Ansible flow used by the Molecule Proxmox scenario.

.DESCRIPTION
  Reuses credentials and connection settings from src/docker/.env (or src/molecule/proxmox/.env).
  It creates an LXC from the specified ostemplate via the Proxmox API (like molecule/proxmox/create.yml),
  runs the hardening playbook against the container, and then converts the LXC into a Proxmox template.

.EXAMPLE
  src/docker/create-hardened-debian-template.ps1 -Become

.EXAMPLE
  src/docker/create-hardened-debian-template.ps1 -EnvFile src/molecule/proxmox/.env -DebianVersion 12
#>

param(
  [string]$EnvFile = (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) '.env'),
  [string]$Playbook = 'playbooks/hardened_debian.yml',
  [switch]$Become,
  [switch]$SkipCreate,
  [switch]$SkipHarden,
  [bool]$Cleanup = $true,
  [string]$DebianVersion = 'auto'
)

$ErrorActionPreference = 'Stop'

function Get-EnvFromFile {
  param([string]$Path)
  if (!(Test-Path $Path)) { throw "Env file not found: $Path" }
  $h = @{}
  Get-Content $Path | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith('#')) { return }
    $eq = $line.IndexOf('=')
    if ($eq -lt 1) { return }
    $k = $line.Substring(0, $eq).Trim()
    $v = $line.Substring($eq+1).Trim()
    $h[$k] = $v
  }
  return $h
}

# Resolve repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$SrcDir = Join-Path $RepoRoot 'src'
$ComposeFile = Join-Path $ScriptDir 'docker-compose.molecule.yml'

if (!(Test-Path $SrcDir)) { throw "src/ not found at $SrcDir" }
if (!(Test-Path $ComposeFile)) { throw "docker-compose.molecule.yml not found at $ComposeFile" }

# Load Proxmox settings from docker/.env or fallback to molecule/proxmox/.env
if (!(Test-Path $EnvFile)) {
  $fallback = Join-Path (Split-Path -Parent (Split-Path -Parent $ScriptDir)) 'src/molecule/proxmox/.env'
  if (Test-Path $fallback) { $EnvFile = $fallback }
}
$envMap = Get-EnvFromFile -Path $EnvFile

function Get-OrNull([string]$key) { if ($envMap.ContainsKey($key) -and $envMap[$key]) { $envMap[$key] } else { $null } }

$proxmoxUrlInput = Get-OrNull 'PROXMOX_URL'
$proxmoxHost = Get-OrNull 'PROXMOX_HOST'
$proxmoxUser = Get-OrNull 'PROXMOX_USER'
$proxmoxPassword = Get-OrNull 'PROXMOX_PASSWORD'
$proxmoxTokenId = Get-OrNull 'PROXMOX_TOKEN_ID'
$proxmoxTokenSecret = Get-OrNull 'PROXMOX_TOKEN_SECRET'
# Pull needed settings from .env
$proxmoxNode = Get-OrNull 'PROXMOX_NODE'
$template = Get-OrNull 'TEMPLATE'
$containerIp = Get-OrNull 'CONTAINER_IP'

if (-not $proxmoxUrlInput -and -not $proxmoxHost) { throw "Set PROXMOX_URL or PROXMOX_HOST in $EnvFile" }
if (-not $proxmoxNode) { throw "PROXMOX_NODE not set in $EnvFile" }
if (-not $template)    { throw "TEMPLATE (LXC ostemplate filename) not set in $EnvFile" }

# Derive Debian version from template filename if requested (e.g., debian-12-standard_...)
if ($DebianVersion -eq 'auto' -and $template) {
  if ($template -match 'debian-(\d+)') { $DebianVersion = $matches[1] } else { $DebianVersion = '12' }
}

# Desired Proxmox LXC name to create and then mark as template (DNS-safe: use hyphens)
$templateName = "debian-${DebianVersion}-hardened"

Write-Host "[INFO] Using container/template name: $templateName" -ForegroundColor Cyan

# Ensure Docker compose runner is built and running (same flow as run-molecule-tests.ps1)
Push-Location $RepoRoot
try {
  Write-Host "[INFO] Building molecule-proxmox image..." -ForegroundColor Cyan
  docker-compose -f $ComposeFile build | Write-Output

  Write-Host "[INFO] Starting molecule-proxmox container..." -ForegroundColor Cyan
  docker-compose -f $ComposeFile up -d | Write-Output

  # Run the Proxmox LXC create play the same way Molecule does
  if (-not $SkipCreate) {
    $createCmd = "cd /ansible/src && ansible-playbook molecule/proxmox/create.yml -e container_name=$templateName"
    Write-Host "[INFO] Creating LXC on Proxmox via Ansible..." -ForegroundColor Cyan
    docker-compose -f $ComposeFile exec molecule-proxmox bash -lc "$createCmd"
    if ($LASTEXITCODE -ne 0) { throw "Create LXC playbook failed with exit code $LASTEXITCODE" }
  } else {
    Write-Host "[INFO] SkipCreate set; not running create.yml" -ForegroundColor Yellow
  }

  # Harden the container using the requested playbook against the container's IP
  if (-not $SkipHarden) {
    $becomeArg = if ($Become) { '--become' } else { '' }
    $targetIp = if ($containerIp) { $containerIp } else { '$CONTAINER_IP' }
    Write-Host "[INFO] Running hardening playbook ($Playbook) against $targetIp..." -ForegroundColor Cyan
    $hardenCmd = "cd /ansible/src && ansible-playbook -i `"$targetIp,`" -u molecule --extra-vars 'ansible_password=molecule123' $becomeArg $Playbook"
    docker-compose -f $ComposeFile exec molecule-proxmox bash -lc "$hardenCmd"
    if ($LASTEXITCODE -ne 0) { throw "Hardening playbook failed with exit code $LASTEXITCODE" }
  } else {
    Write-Host "[INFO] SkipHarden set; not running $Playbook" -ForegroundColor Yellow
  }

  # Convert the LXC into a Proxmox template (stop + template), include cleanup flag
  $cleanupArg = if ($Cleanup) { 'true' } else { 'false' }
  $templateCmd = "cd /ansible/src && ansible-playbook playbooks/proxmox_lxc_make_template.yml -e container_name=$templateName -e cleanup_container=$cleanupArg"
  Write-Host "[INFO] Converting LXC to Proxmox template..." -ForegroundColor Cyan
  docker-compose -f $ComposeFile exec molecule-proxmox bash -lc "$templateCmd"
  if ($LASTEXITCODE -ne 0) { throw "Template conversion playbook failed with exit code $LASTEXITCODE" }

  Write-Host "[SUCCESS] Proxmox LXC '$templateName' created, hardened, and templated." -ForegroundColor Green
}
finally {
  Pop-Location
}
