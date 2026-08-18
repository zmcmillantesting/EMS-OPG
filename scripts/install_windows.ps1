# EMS-OPG Windows installer.
#
# Run this AFTER a successful build, from the project root:
#
#     uv run pyinstaller EMS-OPG.spec
#     powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
#
# Copies the built app out of dist\EMS-OPG\ into a clean per-user install
# folder (%LOCALAPPDATA%\Programs\EMS-OPG\) and drops a single shortcut on
# the Desktop pointing at the exe inside it - so the Desktop only ever
# shows one icon, not the whole runtime folder (Python DLLs, frontend
# assets, etc). Re-running this script replaces a previous install.
#
# This copies rather than moves dist\EMS-OPG\ - when running from a USB
# drive or network share to install onto several machines, the source is
# meant to be reused for the next machine, not consumed by the first one.
#
# The actual copy uses robocopy, not Copy-Item/Move-Item. This build has
# deeply nested paths (pythonnet\runtime\...) that, once combined with an
# already-long destination under AppData\Local\Programs\..., have tripped
# both Move-Item ("directory not empty" - a cross-volume move does a
# copy-then-delete-source, and the delete step can fail if antivirus
# briefly locks a freshly-copied file) and Copy-Item ("Illegal characters
# in path" - Windows PowerShell 5.1's file cmdlets are known to be
# unreliable with long combined paths). robocopy is the Windows-native
# tool built specifically to handle long paths and locked-file retries
# robustly, and sidesteps this whole class of problem.

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

$RobocopyLog = Join-Path $env:TEMP "ems-opg-install-robocopy.log"

Write-Host "Installing to $InstallDir..."
robocopy $BuildOutput $InstallDir /E /R:3 /W:2 /NFL /NDL /NJH /NP | Out-Null

robocopy $BuildOutput $InstallDir /E /R:5 /W:3 /NJH /NJS /NP /LOG:$RobocopyLog | Out-Null
# robocopy's exit code is a bitmask, not a simple 0/1 - anything under 8
# means some form of success (0-7 cover "nothing to copy" through "some
# files copied/mismatched but no real failure"); 8+ is a genuine failure.
if ($LASTEXITCODE -ge 8) {
    Write-Host ""
    Write-Host "Errors from the robocopy log:"
    Select-String -Path $RobocopyLog -Pattern "ERROR" | ForEach-Object {
        Write-Host "  $($_.Line.Trim())"
    }
    Write-Host ""
    Write-Host "Full log: $RobocopyLog"

    exit 1
}

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