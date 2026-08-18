# EMS-OPG Windows installer.
#
# Run this AFTER a successful build, from the project root:
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
# Moving also isn't reliable across drives/volumes to begin with: a
# cross-volume Move-Item does a copy-then-delete-source internally, and
# the delete step can fail with "directory not empty" if antivirus or
# another process briefly holds a lock on a freshly-copied file - exactly
# the failure this used to hit on E:\dist\EMS-OPG\pythonnet\runtime.

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
Copy-Item -Path $BuildOutput -Destination $InstallDir -Recurse -Force
