# Creates a local virtual environment and installs dependencies.

$ErrorActionPreference = "Stop"

# Create venv if missing
if (!(Test-Path ".venv")) {
  python -m venv .venv
}

# Upgrade pip
.\.venv\Scripts\python -m pip install --upgrade pip

# Install client deps
.\.venv\Scripts\pip install -r requirements.txt

# Install proxy deps (so proxy can run locally too)
.\.venv\Scripts\pip install -r proxy\requirements.txt

Write-Host "Setup complete."
Write-Host "Run client: '.\.venv\Scripts\python src\main.py' or 'python -m src.main'"
Write-Host "Run proxy:  .\.venv\Scripts\uvicorn proxy.server:app --host 127.0.0.1 --port 8000"
