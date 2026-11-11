$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
function Invoke-Checked {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Echec : $Exe $Arguments" }
}
$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Version = $null
    foreach ($Candidate in @("3.11", "3.12")) {
        try {
            & py "-$Candidate" --version 2>$null
            if ($LASTEXITCODE -eq 0) { $Version = $Candidate; break }
        } catch { continue }
    }
    if (-not $Version) { throw "Installez Python 3.11 ou 3.12 avec le lanceur py." }
    Invoke-Checked -Exe "py" -Arguments @("-$Version", "-m", "venv", ".venv")
}
Invoke-Checked -Exe $Python -Arguments @("-c", "import sys; assert sys.version_info[:2] in [(3,11),(3,12)], 'Version .venv incompatible'")
Invoke-Checked -Exe $Python -Arguments @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Checked -Exe $Python -Arguments @("-m", "pip", "install", "-r", "requirements.txt", "-r", "requirements-dev.txt")
if (-not (Test-Path ".env")) { Invoke-Checked -Exe $Python -Arguments @("-m", "ticket_agent", "config") }
Invoke-Checked -Exe $Python -Arguments @("-m", "ticket_agent", "train")
Invoke-Checked -Exe $Python -Arguments @("-m", "ticket_agent", "evaluate")
Invoke-Checked -Exe $Python -Arguments @("scripts/check_setup.py")
Write-Host "Pret. Lancez scripts\lancer_web.bat"
