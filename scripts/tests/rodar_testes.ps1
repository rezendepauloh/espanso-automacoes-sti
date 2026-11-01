# Arquivo: scripts/tests/rodar_testes.ps1
# Wrapper PowerShell para a Suíte Unificada de Testes do Espanso Automações STI

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$TestsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunAllPy = Join-Path $TestsDir "run_all.py"

# Detecta interpretador Python disponível
$pythonCmd = "python3"
if (-not (Get-Command "python3" -ErrorAction SilentlyContinue)) {
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } else {
        Write-Host "ERRO: Interpretador Python (python3 ou python) não encontrado no PATH." -ForegroundColor Red
        exit 1
    }
}

& $pythonCmd "$RunAllPy"
exit $LASTEXITCODE
