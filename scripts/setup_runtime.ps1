<#
.SYNOPSIS
  One-time setup of the bundled embeddable Python runtime used by a packaged
  build to launch game subprocesses.

.DESCRIPTION
  Downloads the official Windows embeddable Python distribution, extracts it
  to runtime/python/, configures its `._pth` file so `Lib\site-packages` is
  on sys.path, bootstraps pip via get-pip.py, and installs the project's
  runtime dependencies into the bundled interpreter using `--target` so the
  install location is unambiguous.

  Run this ONCE before your first packaged build, and again only if you want
  to change Python versions or refresh installed packages. Running `python
  main.py` from source does NOT require this -- the launcher falls back to
  the active interpreter when runtime/python/python.exe is absent.

.NOTES
  - Internet access required (pulls from python.org and pypi).
  - ~30 MB of disk in runtime/python/ when finished.
  - Idempotent: rerun to refresh; pass -Force to wipe and reinstall.
#>

param(
    [string]$PythonVersion = "3.11.9",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Repo root is the parent of this scripts/ folder, regardless of cwd.
$RepoRoot   = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $RepoRoot "runtime\python"
$SitePkgs   = Join-Path $RuntimeDir "Lib\site-packages"

if ($Force -and (Test-Path $RuntimeDir)) {
    Write-Host "Removing existing $RuntimeDir ..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $RuntimeDir
}

# --- 1. Download + extract the embeddable distribution ----------------------
if (-not (Test-Path (Join-Path $RuntimeDir "python.exe"))) {
    New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

    $ZipName = "python-$PythonVersion-embed-amd64.zip"
    $ZipUrl  = "https://www.python.org/ftp/python/$PythonVersion/$ZipName"
    $ZipPath = Join-Path $env:TEMP $ZipName

    Write-Host "Downloading $ZipUrl ..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath

    Write-Host "Extracting to $RuntimeDir ..." -ForegroundColor Cyan
    Expand-Archive -Path $ZipPath -DestinationPath $RuntimeDir -Force
    Remove-Item $ZipPath
}
else {
    Write-Host "Embeddable Python already present at $RuntimeDir." -ForegroundColor Green
}

# --- 2. Configure the _pth so site-packages is on sys.path ------------------
# The default embeddable `_pth` lists `pythonNN.zip` and `.` only, with
# `import site` commented out. Rewrite it explicitly so `Lib\site-packages`
# is on sys.path regardless of whether site.main() is invoked.
$PthFile = Get-ChildItem -Path $RuntimeDir -Filter "python*._pth" | Select-Object -First 1
if ($null -eq $PthFile) {
    throw "Could not find python*._pth in $RuntimeDir."
}
$PythonStem = [System.IO.Path]::GetFileNameWithoutExtension($PthFile.Name)
$PthContent = @(
    "$PythonStem.zip",
    ".",
    "Lib\site-packages",
    "",
    "import site"
) -join "`r`n"
Write-Host "Writing $($PthFile.Name) with site-packages on sys.path ..." -ForegroundColor Cyan
Set-Content -Path $PthFile.FullName -Value $PthContent -Encoding ASCII

# Ensure site-packages dir exists so `import site` finds something to add.
New-Item -ItemType Directory -Force -Path $SitePkgs | Out-Null

$PythonExe = Join-Path $RuntimeDir "python.exe"

# --- 3. Bootstrap pip into the embedded interpreter -------------------------
$PipModuleDir = Join-Path $SitePkgs "pip"
if (-not (Test-Path $PipModuleDir)) {
    Write-Host "Bootstrapping pip via get-pip.py ..." -ForegroundColor Cyan
    $GetPip = Join-Path $env:TEMP "get-pip.py"
    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $GetPip
    & $PythonExe $GetPip --no-warn-script-location
    if ($LASTEXITCODE -ne 0) { throw "get-pip.py failed (exit $LASTEXITCODE)." }
    Remove-Item $GetPip
}

# Sanity-check pip is now actually inside the embedded site-packages.
if (-not (Test-Path $PipModuleDir)) {
    throw "pip did not install into $PipModuleDir. Inspect $RuntimeDir manually."
}

# --- 4. Install requirements into the embedded site-packages ----------------
# Use --target so the install location is unambiguous. This avoids pip
# silently choosing the user site-packages or a system Python.
$Reqs = Join-Path $RepoRoot "requirements.txt"
Write-Host "Installing requirements into $SitePkgs ..." -ForegroundColor Cyan
& $PythonExe -m pip install --upgrade --target $SitePkgs -r $Reqs
if ($LASTEXITCODE -ne 0) { throw "pip install failed (exit $LASTEXITCODE)." }

# --- 5. Verify --------------------------------------------------------------
Write-Host ""
Write-Host "Verifying bundled runtime ..." -ForegroundColor Cyan
& $PythonExe --version
& $PythonExe -c "import pygame; print('pygame', pygame.version.ver)"
if ($LASTEXITCODE -ne 0) {
    throw "Bundled interpreter cannot import pygame. Setup did not succeed."
}

Write-Host ""
Write-Host "Done. Bundled runtime at $RuntimeDir" -ForegroundColor Green
