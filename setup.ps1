# PowerShell script to set up the virtual environment and install dependencies
Write-Host "Setting up Mach24 Flask Application..." -ForegroundColor Green

# Activate virtual environment if it exists, create it if it doesn't
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists. Removing it to create a clean one..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

Write-Host "Creating a new virtual environment..." -ForegroundColor Cyan
python -m venv .venv

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "To run the application, use: python main.py" -ForegroundColor Green
