# Run from project root: .\scripts\setup_wayu_pilot.ps1
# Creates an isolated CPU-only environment. Does not install into .venv,
# download TTS weights, generate speech, or modify existing data/manifests.
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $Executable"
    }
}

$bootstrapPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $bootstrapPython)) {
    throw 'Prepare the main .venv first, or use an existing Python 3.11 environment (see README).'
}
$bootstrapDir = Join-Path $projectRoot 'tmp/wayu-bootstrap'
$uvExe = Join-Path $bootstrapDir 'bin/uv.exe'
if (-not (Test-Path -LiteralPath $uvExe)) {
    Invoke-Checked -Executable $bootstrapPython -Arguments @(
        '-m', 'pip', 'install', '--target', $bootstrapDir, 'uv==0.12.23'
    )
}

$previousCache = $env:UV_CACHE_DIR
$previousPythonDir = $env:UV_PYTHON_INSTALL_DIR
try {
    $env:UV_CACHE_DIR = Join-Path $projectRoot 'tmp/wayu-uv-cache'
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $projectRoot 'tmp/wayu-python'
    $wayuPython = Join-Path $projectRoot '.venv-wayu/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $wayuPython)) {
        Invoke-Checked -Executable $uvExe -Arguments @('python', 'install', '3.11.17', '--no-bin')
        $basePython = Join-Path $env:UV_PYTHON_INSTALL_DIR 'cpython-3.11.17-windows-x86_64-none/python.exe'
        Invoke-Checked -Executable $uvExe -Arguments @('venv', '.venv-wayu', '--python', $basePython)
    }
    Invoke-Checked -Executable $wayuPython -Arguments @(
        '-c', 'import sys; assert sys.version_info[:2] == (3, 11)'
    )
    Invoke-Checked -Executable $uvExe -Arguments @(
        'pip', 'install', '--python', $wayuPython, 'torch==2.11.0',
        '--index-url', 'https://download.pytorch.org/whl/cpu'
    )
    Invoke-Checked -Executable $uvExe -Arguments @(
        'pip', 'install', '--python', $wayuPython, '-r', 'configs/cvtts/wayu-pilot-requirements.txt'
    )
    Invoke-Checked -Executable $uvExe -Arguments @('pip', 'check', '--python', $wayuPython)
    Write-Host 'Ready. Select .venv-wayu as the kernel in common_voice_wayu_tts_pilot.ipynb.'
    Write-Host 'Do not delete tmp/wayu-python: the environment uses that Python installation.'
} finally {
    $env:UV_CACHE_DIR = $previousCache
    $env:UV_PYTHON_INSTALL_DIR = $previousPythonDir
}
