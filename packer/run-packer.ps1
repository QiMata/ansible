param(
  [Parameter(HelpMessage="Playbook path relative to src/ (e.g. playbooks/base.yml)")]
  [string]$Playbook,
  [string[]]$AnsibleExtraArgs,
  [switch]$Become,
  [string]$Limit,
  [string]$BaseImage = "ubuntu:22.04",
  [ValidateSet('docker','proxmox-lxc')]
  [string]$Template = 'docker',
  [string]$VarsFile
)

$ErrorActionPreference = 'Stop'

# Resolve repo root (this script is in packer/)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$PackerDir = Join-Path $RepoRoot 'packer'
$SrcDir = Join-Path $RepoRoot 'src'

if (!(Test-Path $SrcDir)) {
  throw "src/ directory not found at $SrcDir"
}

# For docker template we require a playbook; for proxmox-lxc it can also be provided via VarsFile
if ($Template -eq 'docker') {
  if (-not $Playbook) { throw "-Playbook is required for Template=docker" }
  $PlaybookPath = Join-Path $SrcDir $Playbook
  if (!(Test-Path $PlaybookPath)) {
    throw "Playbook not found: $PlaybookPath"
  }
}

# Build or rebuild the packer runner image to ensure latest Dockerfile changes are applied
$ImageTag = 'ansible-packer:local'
Write-Host "Building $ImageTag from $PackerDir/Dockerfile..."
docker build -t $ImageTag -f (Join-Path $PackerDir 'Dockerfile') $PackerDir | Write-Output

# Compose Packer args
$null = $Become # keep analyzer happy if not used

# Select template file
switch ($Template) {
  'docker'      { $TemplateFile = 'template.pkr.hcl' }
  'proxmox-lxc' { $TemplateFile = 'template.proxmox-lxc.pkr.hcl' }
}

# Base packer args
$PackerArgs = @('build')

if ($Template -eq 'docker') {
  $PackerArgs += @('-var', "playbook_file=$Playbook", '-var', "base_image=$BaseImage")
}

if ($Template -eq 'proxmox-lxc' -and $Playbook) {
  $PackerArgs += @('-var', "playbook_file=$Playbook")
}

if ($Become.IsPresent) {
  $PackerArgs += @('-var', 'become=true')
}

if ($AnsibleExtraArgs -and $AnsibleExtraArgs.Count -gt 0) {
  # Convert to JSON array string, e.g. ["-e","env=dev"]
  $extraArgsJson = ($AnsibleExtraArgs | ConvertTo-Json -Compress)
  $PackerArgs += @('-var', "ansible_extra_args=$extraArgsJson")
}

# Append --limit if provided
if ($Limit) {
  # Retrieve existing ansible_extra_args if any; otherwise start a new array
  $existing = @()
  if ($AnsibleExtraArgs) { $existing = $AnsibleExtraArgs }
  $existing += @("--limit", $Limit)
  $extraArgsJson = ($existing | ConvertTo-Json -Compress)
  # Remove any previously set ansible_extra_args to avoid duplicates
  $PackerArgs = @($PackerArgs | Where-Object { $_ -notmatch '^ansible_extra_args=' })
  $PackerArgs += @('-var', "ansible_extra_args=$extraArgsJson")
}

# Optional -var-file
if ($VarsFile) {
  if (!(Test-Path $VarsFile)) { throw "Vars file not found: $VarsFile" }
  $resolvedVars = (Resolve-Path $VarsFile).Path
  # Map the host path into the container mount at /workspace
  # The repo root is bind-mounted to /workspace, so replace the repo root prefix with /workspace
  $VarsInContainer = $resolvedVars -replace [regex]::Escape($RepoRoot), '/workspace'
  # Normalize Windows backslashes to POSIX for the Linux container
  $VarsInContainer = $VarsInContainer -replace '\\','/'
  $PackerArgs += @('-var-file', $VarsInContainer)
}

# Run packer inside container
$WorkDirInContainer = '/workspace/packer'
$RepoBind = "${RepoRoot}:/workspace"

# Docker socket path inside Linux containers
$DockerSock = '/var/run/docker.sock'

$RunArgs = @(
  'run', '--rm', '-it',
  '-v', $RepoBind,
  '-v', "${RepoRoot}/.packer.d:/root/.packer.d",
  '-v', "${DockerSock}:${DockerSock}",
  '-w', $WorkDirInContainer,
  '-e', 'PACKER_LOG=1',
  'ansible-packer:local'
)

Write-Host "Running: packer init template.pkr.hcl"
docker @RunArgs init $TemplateFile

if ($Template -eq 'docker') {
  Write-Host "Running: packer validate $TemplateFile"
  docker @RunArgs validate $TemplateFile
}
elseif ($Template -eq 'proxmox-lxc') {
  if ($VarsFile) {
    Write-Host "Running: packer validate -var-file (container) $VarsFile => $VarsInContainer $TemplateFile"
    $resolvedVars = (Resolve-Path $VarsFile).Path
    $VarsInContainer = $resolvedVars -replace [regex]::Escape($RepoRoot), '/workspace'
    $VarsInContainer = $VarsInContainer -replace '\\','/'
    docker @RunArgs validate '-var-file' $VarsInContainer $TemplateFile
  } else {
    Write-Host "Skipping validate for proxmox-lxc (no -VarsFile provided)."
  }
}

Write-Host "Running: packer $($PackerArgs -join ' ') $TemplateFile"
docker @RunArgs @PackerArgs $TemplateFile
