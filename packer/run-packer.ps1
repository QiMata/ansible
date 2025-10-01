param(
  [Parameter(HelpMessage="Playbook path relative to src/ (e.g. playbooks/base.yml)")]
  [string]$Playbook,
  [ValidateSet('postgresql-node','mariadb-node','elasticsearch-node','minio-node','neo4j-node','docker-host','k3s-node','jenkins-agent','haproxy','keepalived','bind9','apt-mirror','container-registry')]
  [string]$Image,
  [switch]$All,
  [string[]]$Images,
  [string[]]$AnsibleExtraArgs,
  [string]$AnsibleExtraArgsJson,
  [switch]$Become,
  [string]$Limit,
  [string]$BaseImage = "ubuntu:22.04",
  [ValidateSet('docker','proxmox-lxc')]
  [string]$Template = 'docker',
  [string]$VarsFile,
  [string]$TemplateName,
  [string]$TemplateNamePrefix,
  [switch]$StopOnError,
  [switch]$NoTty
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
# If running in aggregate mode (-All), iterate images and invoke this script for each
if ($All.IsPresent) {
  $allImagesList = @('postgresql-node','mariadb-node','elasticsearch-node','minio-node','neo4j-node','docker-host','k3s-node','jenkins-agent','haproxy','keepalived','bind9','apt-mirror','container-registry')
  if ($Images -and $Images.Count -gt 0) { $allImagesList = $Images }

  $overallOk = $true
  foreach ($img in $allImagesList) {
    Write-Host "==== Building image: $img (Template=$Template) ====" -ForegroundColor Cyan
    $args = @('-NoProfile','-File', $PSCommandPath, '-Template', $Template, '-Image', $img)
    if ($Become.IsPresent)   { $args += '-Become' }
    if ($NoTty.IsPresent)    { $args += '-NoTty' }
    if ($VarsFile)           { $args += @('-VarsFile', $VarsFile) }
    if ($Limit)              { $args += @('-Limit', $Limit) }
    if ($TemplateNamePrefix) { $args += @('-TemplateName', "${TemplateNamePrefix}-$img") }
    if ($AnsibleExtraArgsJson) { $args += @('-AnsibleExtraArgsJson', $AnsibleExtraArgsJson) }
    elseif ($AnsibleExtraArgs) { $args += @('-AnsibleExtraArgs') + $AnsibleExtraArgs }

    & pwsh @args
    if ($LASTEXITCODE -ne 0) {
      Write-Warning "Build failed for $img (exit $LASTEXITCODE)"
      $overallOk = $false
      if ($StopOnError.IsPresent) { exit $LASTEXITCODE }
    }
  }

  if ($overallOk) { exit 0 } else { exit 1 }
}

# If -Image was provided, map it to a playbook path
if ($Image) {
  $Playbook = "images/$Image/playbook.yml"
}

# Validate playbook path for both templates when provided
if ($Playbook) {
  $PlaybookPath = Join-Path $SrcDir $Playbook
  if (!(Test-Path $PlaybookPath)) { throw "Playbook not found: $PlaybookPath" }
}

# For docker template require a playbook
if ($Template -eq 'docker' -and -not $Playbook) {
  throw "-Playbook or -Image is required for Template=docker"
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

if ($Playbook) {
  if ($Template -eq 'docker') {
    $PackerArgs += @('-var', "playbook_file=$Playbook", '-var', "base_image=$BaseImage")
  } elseif ($Template -eq 'proxmox-lxc') {
    $PackerArgs += @('-var', "playbook_file=$Playbook")
  }
}

if ($Become.IsPresent) {
  $PackerArgs += @('-var', 'become=true')
}

if ($AnsibleExtraArgsJson) {
  $PackerArgs += @('-var', "ansible_extra_args=$AnsibleExtraArgsJson")
}
elseif ($AnsibleExtraArgs -and $AnsibleExtraArgs.Count -gt 0) {
  # Convert to JSON array string, e.g. [\"-e\",\"env=dev\"]
  $extraArgsJson = ($AnsibleExtraArgs | ConvertTo-Json -Compress)
  $PackerArgs += @('-var', "ansible_extra_args=$extraArgsJson")
}

# Optional template_name override (Proxmox LXC)
if ($TemplateName) {
  $PackerArgs += @('-var', "template_name=$TemplateName")
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

# Optional -var-file; if not provided and proxmox-lxc, auto-pick the first *.pkrvars.hcl (excluding example)
if ($Template -eq 'proxmox-lxc') {
  if (-not $VarsFile) {
    $candidates = Get-ChildItem -Path $PackerDir -Filter '*.pkrvars.hcl' | Where-Object { $_.Name -notlike '*.example' }
    if ($candidates.Count -gt 0) { $VarsFile = $candidates[0].FullName }
  }
  if ($VarsFile) {
    if (!(Test-Path $VarsFile)) { throw "Vars file not found: $VarsFile" }
    $resolvedVars = (Resolve-Path $VarsFile).Path
    $VarsInContainer = $resolvedVars -replace [regex]::Escape($RepoRoot), '/workspace'
    $VarsInContainer = $VarsInContainer -replace '\\','/'
    $PackerArgs += @('-var-file', $VarsInContainer)
  } else {
    Write-Warning "No -VarsFile provided and none auto-detected in 'packer/'. Falling back to src/docker/.env if present."
    $envPath = Join-Path $SrcDir 'docker/.env'
    if (Test-Path $envPath) {
      $envContent = Get-Content $envPath | Where-Object { $_ -and ($_ -notmatch '^\s*#') }
      $envMap = @{}
      foreach ($line in $envContent) {
        if ($line -match '^(?<k>[^=]+)=(?<v>.*)$') { $envMap[$Matches.k.Trim()] = $Matches.v.Trim() }
      }
      # Map to Packer vars
      if ($envMap.ContainsKey('PROXMOX_URL')) {
        $url = $envMap['PROXMOX_URL']
        if ($url -notmatch '/api2/json$') { $url = ($url.TrimEnd('/')) + '/api2/json' }
        $PackerArgs += @('-var', "proxmox_url=$url")
      }
      if ($envMap.ContainsKey('PROXMOX_VALIDATE_CERTS')) {
        $insecure = ($envMap['PROXMOX_VALIDATE_CERTS'].ToLower() -eq 'false')
        $PackerArgs += @('-var', "proxmox_insecure=$($insecure.ToString().ToLower())")
      }
      if ($envMap.ContainsKey('PROXMOX_NODE')) { $PackerArgs += @('-var', "proxmox_node=$($envMap['PROXMOX_NODE'])") }
      if ($envMap.ContainsKey('PROXMOX_TOKEN_ID') -and $envMap['PROXMOX_TOKEN_ID']) {
        $PackerArgs += @('-var', "proxmox_token_id=$($envMap['PROXMOX_TOKEN_ID'])")
      }
      if ($envMap.ContainsKey('PROXMOX_TOKEN_SECRET') -and $envMap['PROXMOX_TOKEN_SECRET']) {
        $PackerArgs += @('-var', "proxmox_token_secret=$($envMap['PROXMOX_TOKEN_SECRET'])")
      }
      if ($envMap.ContainsKey('PROXMOX_USER') -and $envMap['PROXMOX_USER']) {
        $PackerArgs += @('-var', "proxmox_username=$($envMap['PROXMOX_USER'])")
      }
      if ($envMap.ContainsKey('PROXMOX_PASSWORD') -and $envMap['PROXMOX_PASSWORD']) {
        $PackerArgs += @('-var', "proxmox_password=$($envMap['PROXMOX_PASSWORD'])")
      }
      if ($envMap.ContainsKey('TEMPLATE_STORAGE') -and $envMap.ContainsKey('TEMPLATE')) {
        $ost = "$($envMap['TEMPLATE_STORAGE']):vztmpl/$($envMap['TEMPLATE'])"
        $PackerArgs += @('-var', "lxc_ostemplate=$ost")
      }
      if ($envMap.ContainsKey('STORAGE')) { $PackerArgs += @('-var', "rootfs_storage=$($envMap['STORAGE'])") }
      if ($envMap.ContainsKey('DISK_SIZE')) {
        $ds = $envMap['DISK_SIZE'] -replace 'G','' -replace 'g',''
        if ($ds -match '^[0-9]+$') { $PackerArgs += @('-var', "rootfs_size=$ds") }
      }
      if ($envMap.ContainsKey('MEMORY')) { $PackerArgs += @('-var', "lxc_memory=$($envMap['MEMORY'])") }
      if ($envMap.ContainsKey('CORES')) { $PackerArgs += @('-var', "lxc_cores=$($envMap['CORES'])") }
      if ($envMap.ContainsKey('NETWORK')) {
        if ($envMap['NETWORK'] -match 'bridge=([^,]+)') { $PackerArgs += @('-var', "network_bridge=$($Matches[1])") }
      }
      # SSH / LXC password
      $PackerArgs += @('-var', 'ssh_username=root')
      if ($envMap.ContainsKey('CONTAINER_PASSWORD')) {
        $PackerArgs += @('-var', "ssh_password=$($envMap['CONTAINER_PASSWORD'])", '-var', "lxc_password=$($envMap['CONTAINER_PASSWORD'])")
      }
      # Reasonable defaults
      $PackerArgs += @('-var', 'features_nesting=true')
    } else {
      Write-Warning "src/docker/.env not found; cannot derive Proxmox vars. Provide -VarsFile."
    }
  }
}

# Run packer inside container
$WorkDirInContainer = '/workspace/packer'
$RepoBind = "${RepoRoot}:/workspace"

# Docker socket path inside Linux containers
$DockerSock = '/var/run/docker.sock'

$RunArgs = @('run','--rm')
if (-not $NoTty.IsPresent) { $RunArgs += '-it' }
$RunArgs += @(
  '-v', $RepoBind,
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
