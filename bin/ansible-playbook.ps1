param(
    [string]$WorkDir,
    [string]$SshPrivateKey,
    [string]$RemoteUser,
    [string]$VaultPasswordFile,
    [string]$AnsibleImage,
    [switch]$Help
)

# Determine the repository root from the script location so defaults work for
# any clone location.
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

$WorkDir = if ($WorkDir) { $WorkDir } elseif ($env:WORK_DIR) { $env:WORK_DIR } else { $repoRoot }
$SshPrivateKey = if ($SshPrivateKey) { $SshPrivateKey } elseif ($env:SSH_PRIVATE_KEY) { $env:SSH_PRIVATE_KEY } else { 'ansible-dev_id_rsa' }
$RemoteUser = if ($RemoteUser) { $RemoteUser } elseif ($env:REMOTE_USER) { $env:REMOTE_USER } else { 'ansible' }
$VaultPasswordFile = if ($VaultPasswordFile) { $VaultPasswordFile } elseif ($env:ANSIBLE_VAULT_PASSWORD_FILE) { $env:ANSIBLE_VAULT_PASSWORD_FILE } else { 'vault_pass.txt' }
$AnsibleImage = if ($AnsibleImage) { $AnsibleImage } elseif ($env:ANSIBLE_IMAGE) { $env:ANSIBLE_IMAGE } else { 'ansible:latest' }
$ansibleHostKeyChecking = if ($env:ANSIBLE_HOST_KEY_CHECKING) { $env:ANSIBLE_HOST_KEY_CHECKING } else { 'False' }

<#
.SYNOPSIS
    Runs the Ansible Docker container with parameterized paths and environment variables.

.DESCRIPTION
    This script mirrors the functionality of the Bash version by:
    - Accepting parameters for key paths, files, and Docker image.
    - Passing any extra arguments to ansible-playbook (e.g. playbook name, tags, etc.).
#>

if ($Help) {
    Write-Host "Usage: .\Run-Ansible.ps1 [parameters] -- [ansible-playbook arguments]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -WorkDir <path>             Default: $($WorkDir)"
    Write-Host "  -SshPrivateKey <file>       Default: $($SshPrivateKey)"
    Write-Host "  -RemoteUser <user>          Default: $($RemoteUser)"
    Write-Host "  -AnsibleImage <image>       Default: $($AnsibleImage)"
    Write-Host "  -Help                       Show this usage information"
    Write-Host ""
    Write-Host "All parameters after '--' will be forwarded to ansible-playbook."
    return
}

# Derive additional paths relative to the repository location unless overridden
$AnsibleWorkDir = if ($env:ANSIBLE_WORK_DIR) { $env:ANSIBLE_WORK_DIR } else { $WorkDir }
$SshKeyDir      = if ($env:SSH_KEY_DIR) { $env:SSH_KEY_DIR } else { Join-Path $repoRoot 'ssh/ansible' }
$VaultDir       = if ($env:ANSIBLE_VAULT_DIR) { $env:ANSIBLE_VAULT_DIR } else { Join-Path $repoRoot 'vault' }

# Gather any extra args to pass to ansible-playbook
# Everything after "--" goes into $ExtraArgs
$splitIndex = $args.IndexOf('--')
if ($splitIndex -eq -1) {
    $ExtraArgs = $args
} else {
    $ExtraArgs = $args[$splitIndex+1..($args.Count - 1)]
}

# Display configuration (optional)
Write-Host "Configuration:"
Write-Host "  WorkDir:               $WorkDir"
Write-Host "  AnsibleWorkDir:        $AnsibleWorkDir"
Write-Host "  SshPrivateKey:         $SshPrivateKey"
Write-Host "  SshKeyDir:             $SshKeyDir"
Write-Host "  RemoteUser:            $RemoteUser"
Write-Host "  VaultDir:              $VaultDir"
Write-Host "  VaultPasswordFile:     $VaultPasswordFile"
Write-Host "  AnsibleImage:          $AnsibleImage"
Write-Host "  AnsibleHostKeyChecking: $ansibleHostKeyChecking"
Write-Host "  Extra Ansible Args:    $ExtraArgs"
Write-Host ""

# Run Docker
docker run -it `
    -v "${AnsibleWorkDir}:/ansible" `
    -v "${VaultDir}/${VaultPasswordFile}:/${VaultPasswordFile}" `
    -v "${SshKeyDir}/${SshPrivateKey}:/${SshPrivateKey}" `
    -e "SSH_PRIVATE_KEY=/${SshPrivateKey}" `
    -e "REMOTE_USER=${RemoteUser}" `
    -e "ANSIBLE_HOST_KEY_CHECKING=${ansibleHostKeyChecking}" `
    -e "ANSIBLE_VAULT_PASSWORD_FILE=/${VaultPasswordFile}" `
    --rm $AnsibleImage `
    ansible-playbook $ExtraArgs
