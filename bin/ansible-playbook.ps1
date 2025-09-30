param(
    [string]$WorkDir = "$env:USERPROFILE\dev\workspace\qimata",
    [string]$SshPrivateKey = "ansible-dev_id_rsa",
    [string]$RemoteUser = "ansible",
    [SecureString]$VaultPasswordFile = "vault_pass.txt",
    [string]$AnsibleImage = "ansible:latest",
    [switch]$Help
)

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

# Derive additional paths
$AnsibleWorkDir = Join-Path $WorkDir "qimata-ansible/ansible"
$SshKeyDir      = Join-Path $WorkDir "ssh/ansible"
$VaultDir       = Join-Path $WorkDir "vault"

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
Write-Host "  Extra Ansible Args:    $ExtraArgs"
Write-Host ""

# Run Docker
docker run -it `
    -v "${AnsibleWorkDir}:/ansible" `
    -v "${VaultDir}/${VaultPasswordFile}:/${VaultPasswordFile}" `
    -v "${SshKeyDir}/${SshPrivateKey}:/${SshPrivateKey}" `
    -e "SSH_PRIVATE_KEY=/${SshPrivateKey}" `
    -e "REMOTE_USER=${RemoteUser}" `
    -e "ANSIBLE_HOST_KEY_CHECKING=False" `
    -e "ANSIBLE_VAULT_PASSWORD_FILE=/${VaultPasswordFile}" `
    -e "ANSIBLE_CONFIG=/ansible/ansible.cfg" `
    -w "/ansible" `
    --rm $AnsibleImage `
    ansible-playbook $ExtraArgs
