$ErrorActionPreference = "Stop"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $PSScriptRoot "backups"

if (!(Test-Path -Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

$zipName = "GigBoss_Alpha_v1_$timestamp.zip"
$zipPath = Join-Path $backupDir $zipName

Write-Host "Creating GigBoss Save State: $zipName"

$itemsToZip = Get-ChildItem -Path "android", "backend", "dashboard", "*.ps1", "*.py"
Compress-Archive -Path $itemsToZip.FullName -DestinationPath $zipPath -Force

Write-Host "Save State successful! Backup located at: $zipPath"
