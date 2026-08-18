# EMS-OPG Windows installer.
#
# Run this AFTER a successful build, from the project root:
#
#     uv run pyinstaller EMS-OPG.spec
#     powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
#
# Moves the built app out of dist\EMS-OPG\ into a clean per-user install
# folder (%LOCALAPPDATA%\Programs\EMS-OPG\) and drops a single shortcut on
# the Desktop pointing at the exe inside it - so the Desktop only ever
# shows one icon, not the whole runtime folder (Python DLLs, frontend
# assets, etc). Re-running this script replaces a previous install.

$ErrorActionPreference = "Stop"

$BuildOutput = Join-Path $PSScriptRoot "..\dist\EMS-OPG"
$ProgramsDir = Join-Path $env:LOCALAPPDATA "Programs"
$InstallDir = Join-Path $ProgramsDir "EMS-OPG"

if (-not (Test-Path $BuildOutput)) {
    Write-Error "Build output not found at $BuildOutput - run 'uv run pyinstaller EMS-OPG.spec' first."
    exit 1
}

if (Test-Path $InstallDir) {
    Write-Host "Removing previous install at $InstallDir..."
    Remove-Item -Recurse -Force $InstallDir
}

New-Item -ItemType Directory -Force -Path $ProgramsDir | Out-Null

Write-Host "Installing to $InstallDir..."
Move-Item -Path $BuildOutput -Destination $InstallDir

$ExePath = Join-Path $InstallDir "EMS-OPG.exe"
$ShortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "EMS-OPG.lnk"

Write-Host "Creating Desktop shortcut at $ShortcutPath..."
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = $ExePath
$Shortcut.Description = "EMS Operations and Production Gateway"
$Shortcut.Save()

Write-Host ""
Write-Host "Done."
Write-Host "  Installed to:      $InstallDir"
Write-Host "  Desktop shortcut:  $ShortcutPath"
