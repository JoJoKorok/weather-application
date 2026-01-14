# Runs pytest from the project root using the project's venv.

$ErrorActionPreference = "Stop"

# Moves from /tests back to repo root.
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location -Path $repoRoot

# Uses repo root venv python if available, otherwise falls back to system python.
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    & $venvPython -m pytest @args
} else {
    python -m pytest @args
}
