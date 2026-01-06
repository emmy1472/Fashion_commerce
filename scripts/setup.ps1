<#
PowerShell setup script for the project.
Creates a virtual environment named `env1` (if not exists), activates it, and installs pinned requirements.
Run from the repository root in PowerShell:

    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; .\scripts\setup.ps1

#>

Param(
    [switch]$InstallDev
)

Write-Host "Checking for Python..."
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Error "Python not found in PATH. Install Python 3.11+ and retry."
    exit 1
}

$venvDir = "env1"
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment '$venvDir'..."
    python -m venv $venvDir
}

Write-Host "Activating virtual environment..."
.\$venvDir\Scripts\Activate.ps1

Write-Host "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if ($InstallDev) {
    if (Test-Path requirements-dev.txt) {
        python -m pip install -r requirements-dev.txt
    } else {
        Write-Warning "requirements-dev.txt not found."
    }
}

Write-Host "Setup complete. To activate the venv in future: .\env1\Scripts\Activate.ps1"
Write-Host "To run tests: python socialcom\manage.py test -v 2"
