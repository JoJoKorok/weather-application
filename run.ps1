$ErrorActionPreference = "Stop"

if (!(Test-Path ".venv")) {
  .\setup.ps1
}

.\.venv\Scripts\python src\main.py
