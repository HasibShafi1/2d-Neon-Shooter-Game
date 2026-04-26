# Set up a Python virtual environment and install requirements
Write-Host "Creating virtual environment..."
python -m venv .venv

Write-Host "Activating virtual environment..."
# Note: In PowerShell, you execute the activation script like this:
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Setup complete."
