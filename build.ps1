<#
.SYNOPSIS
  Produce a distributable build of the Coding Club Arcade launcher.

.DESCRIPTION
  Cleans previous build artifacts, runs PyInstaller against arcade.spec, then
  copies the games/ tree and the bundled runtime/ next to the exe so the
  launcher can spawn game subprocesses against real on-disk files.

  The output is dist/ArcadeCabinet/ -- a self-contained folder you can zip
  and hand to a non-technical user. They double-click ArcadeCabinet.exe.

.NOTES
  Prerequisites (one-time):
    1. pip install -r requirements-build.txt
    2. .\scripts\setup_runtime.ps1
#>

param(
    [switch]$SkipRuntimeCheck
)

$ErrorActionPreference = "Stop"

$RepoRoot  = $PSScriptRoot
$DistDir   = Join-Path $RepoRoot "dist\ArcadeCabinet"
$BuildDir  = Join-Path $RepoRoot "build"
$Runtime   = Join-Path $RepoRoot "runtime"
$Games     = Join-Path $RepoRoot "games"
$Assets    = Join-Path $RepoRoot "assets"
$Settings  = Join-Path $RepoRoot "settings.py"

# Sanity check: the bundled runtime must exist or the packaged exe will not
# be able to launch any games. Skipping is allowed for a quick UI-only build.
if (-not $SkipRuntimeCheck) {
    if (-not (Test-Path (Join-Path $Runtime "python\python.exe"))) {
        Write-Host "ERROR: runtime\python\python.exe not found." -ForegroundColor Red
        Write-Host "Run .\scripts\setup_runtime.ps1 first, or pass -SkipRuntimeCheck." -ForegroundColor Yellow
        exit 1
    }
}

# Verify PyInstaller is importable in the active interpreter.
& python -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller not installed in the active interpreter." -ForegroundColor Red
    Write-Host "Run: pip install -r requirements-build.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "Cleaning previous build artifacts ..." -ForegroundColor Cyan
if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }
if (Test-Path (Join-Path $RepoRoot "dist")) { Remove-Item -Recurse -Force (Join-Path $RepoRoot "dist") }

Write-Host "Running PyInstaller ..." -ForegroundColor Cyan
& python -m PyInstaller --noconfirm arcade.spec
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Copy games/ and runtime/ next to the exe. These are kept OUTSIDE the
# PyInstaller archive so games run from real folders (correct cwd, easy to
# update, student games can be dropped in without rebuilding).
Write-Host "Copying assets/ into $DistDir ..." -ForegroundColor Cyan
Copy-Item -Recurse -Force $Assets (Join-Path $DistDir "assets")

Write-Host "Copying settings.py into $DistDir ..." -ForegroundColor Cyan
Copy-Item -Force $Settings (Join-Path $DistDir "settings.py")

Write-Host "Copying games/ into $DistDir ..." -ForegroundColor Cyan
Copy-Item -Recurse -Force $Games (Join-Path $DistDir "games")

if (Test-Path $Runtime) {
    Write-Host "Copying runtime/ into $DistDir ..." -ForegroundColor Cyan
    Copy-Item -Recurse -Force $Runtime (Join-Path $DistDir "runtime")
}

Write-Host ""
Write-Host "Build complete." -ForegroundColor Green
Write-Host "Distributable folder: $DistDir" -ForegroundColor Green
Write-Host "Run ArcadeCabinet.exe inside that folder to test." -ForegroundColor Green
