$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$AASISTRoot = Join-Path $ProjectRoot "external\aasist"
$SetupTemp = Join-Path $ProjectRoot "tmp\setup-temp"
New-Item -ItemType Directory -Force -Path $SetupTemp | Out-Null
$env:TEMP = $SetupTemp
$env:TMP = $SetupTemp

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "A setup command failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $AASISTRoot "models\AASIST.py"))) {
    Write-Host "Downloading the official AASIST source and pretrained checkpoint..."
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $AASISTRoot) | Out-Null
    Invoke-Checked { git clone --depth 1 https://github.com/clovaai/aasist.git $AASISTRoot }
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "Creating .venv with the installed Python..."
    Invoke-Checked { python -m venv (Join-Path $ProjectRoot ".venv") }
}

$VenvPipPackage = Join-Path $ProjectRoot ".venv\Lib\site-packages\pip"
if (-not (Test-Path -LiteralPath $VenvPipPackage)) {
    Write-Host "Bootstrapping pip inside .venv..."
    Invoke-Checked { & $VenvPython -m ensurepip --upgrade --default-pip }
}

Write-Host "Upgrading packaging tools..."
Invoke-Checked { & $VenvPython -m pip install --upgrade pip setuptools wheel }

Write-Host "Installing CUDA-enabled PyTorch..."
Invoke-Checked { & $VenvPython -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128 }

Write-Host "Installing this project and test dependencies..."
Invoke-Checked { & $VenvPython -m pip install -e "$ProjectRoot[dev]" }

Write-Host "Setup complete. Run:"
Write-Host ".\.venv\Scripts\python.exe scripts\check_environment.py"
