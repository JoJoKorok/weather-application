param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]] $Args
)

# Project root = one level above /tests
$ROOT = Split-Path -Parent $PSScriptRoot

# Make "src" importable
$env:PYTHONPATH = $ROOT

# Use venv python if it exists, otherwise fallback to "python"
$PY = Join-Path $ROOT ".venv\Scripts\python.exe"
if (-not (Test-Path $PY)) { $PY = "python" }

& $PY -m pytest $Args
exit $LASTEXITCODE